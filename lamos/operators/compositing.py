import datetime

import hub.nan1d.percentiles
import hub.numpy.ma
import numpy
from hub.collections import Bunch
from lamos.processing.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint


def getCube(name, inputs, bbl=None):

    # return cube if already exist...
    if name in inputs.__dict__:
        result = inputs.__dict__[name]
    elif 'timeseries_'+name in inputs.__dict__:
        result = inputs.__dict__['timeseries_'+name]

    # ...or create and cache it otherwise
    else:
        if   name=='ndvi'    : result = (inputs.timeseries_nir-inputs.timeseries_red).__truediv__(inputs.timeseries_nir+inputs.timeseries_red)
        elif name=='nbr'     : result = (inputs.timeseries_nir-inputs.timeseries_swir2).__truediv__(inputs.timeseries_nir+inputs.timeseries_swir2)
        elif name=='vis'     : result = inputs.timeseries_blue/3+inputs.timeseries_green/3+inputs.timeseries_red/3
        elif name=='ir'      : result = inputs.timeseries_nir/3 +inputs.timeseries_swir1/3+inputs.timeseries_swir2/3
        elif name=='invalid' : result = inputs.timeseries_cfmask > 1
        elif name=='tcb':
            coeff = [0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303]
            result = numpy.zeros_like(inputs.timeseries_cfmask, dtype=numpy.float32)
            for i, name in enumerate(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']):
                result += coeff[i] * inputs.__dict__['timeseries_' + name]
        elif name=='tcg':
            coeff = [-0.1603, -0.2819, -0.4934, 0.7940, 0.0002, 0.1446]
            result = numpy.zeros_like(inputs.timeseries_cfmask, dtype=numpy.float32)
            for i, name in enumerate(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']):
                result += coeff[i] * inputs.__dict__['timeseries_' + name]
        elif name=='tcw':
            coeff = [0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109]
            result = numpy.zeros_like(inputs.timeseries_cfmask, dtype=numpy.float32)
            for i, name in enumerate(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']):
                result += coeff[i] * inputs.__dict__['timeseries_' + name]


        else:
                raise Exception('Unknown cube requested: '+name)
        inputs.__dict__[name] = result

    # subset bands if needed and return cube
    if bbl is None:
        return result
    else:
        return result[bbl]

def getCubeFromVector(vector, inputs, bbl=None):

    # reshape vector and subset required bands
    vectorCube = numpy.array(vector, dtype=numpy.float32).reshape(-1, 1, 1)[bbl]

    # broadcast to full cube size and apply mask
    invalid = getCube('invalid', inputs, bbl)
    cube = numpy.ones_like(invalid, dtype=numpy.float32)*vectorCube
    cube[invalid] = numpy.NaN
    return cube

def getMeta(name, inmetas):

    if   name=='date': result = [hub.datetime.Date.fromText(acqDate) for acqDate in inmetas.timeseries_cfmask.getMetadataItem('AcqDate')]
    elif name=='doy':  result = [date.doy for date in getMeta('date', inmetas)]
    elif name == 'year': result = [date.year for date in getMeta('date', inmetas)]
    elif name == 'sensor':  result = inmetas.timeseries_cfmask.getMetadataItem('Sensor')
    else: raise Exception('Unknown metadate requested: '+name)
    return result

def scaleLinearMinMax(index, min, max, trim=True):

    # scale index from range [min,max] to score range [0%,100%]
    result = (index-min)/numpy.float32(max-min)
    if trim: numpy.clip(result, 0, 1, result)
    return result

def fLogistic(x, m, s):
    # f(x) = 1/(1+exp(-s*(x-m)))
    return 1./(1.+numpy.exp(-s*(x-m)))

def scaleLogistic(x, m, s):
    x = x.astype(numpy.float32)
    result = fLogistic(x, m, s)
    return result

def scaleLogisticMinMax(x, min, max):
    s = 2 * 2.944 / (max - min) # set s, so that min/max matches the 95% range of the sigmoid
    m = (min+max)/2.
    return scaleLogistic(x, m, s)

def fRBF(x, m, s):
    numpy.seterr(all='ignore')
    return numpy.exp( -((x-m)/s)**2 )

def scaleRBF(x, m, s):
    # rbf(x) = exp(|(x-m)/-s|^2)
    x = x.astype(numpy.float32)
    result = fRBF(x, m, s)
    return result

def scaleRBFMinMax(x, min, max):
    s = (max - min)/4. # set s, so that min/max matches the 95% range of the RBF
    m = (min+max)/2.
    return scaleRBF(x, m, s)

def plotScaleFunctions():
    x = numpy.arange(-5,5.1,0.1)
    min, max = -3, 3
    plotScaleFunction(x, scaleRBFMinMax(x, min, max))
    plotScaleFunction(x, scaleLogisticMinMax(x, min, max))
    plotScaleFunction(x, scaleLinearMinMax(x, min, max))

def plotScaleFunction(x, y):
    for xi,yi in zip(x,y): print(xi, ',', round(yi,2))

    import matplotlib.pyplot as plt
    plt.plot(x, y, linewidth=2)
    plt.show()

def scoreCloudDistance(inputs, inmeta, info):

    # todo waiting for Dirk (in m?)
    index = getCube('distToCloud', inputs, info.bbl)

#    logistisch min=0 max=500x30m
    #score = scaleLogistic(index, min, max)
    #return score

    pass

def scoreHazeOptimizedTransformation(inputs, inmeta, info):

    blue = getCube('blue', inputs, info.bbl)
    red = getCube('red', inputs, info.bbl)
    index = blue - 5000. * red - 800.

    min = index.max()
    max = index.min()
    score = scaleLinearMinMax(index, min, max)
    return score

def scoreThermal(inputs, inmeta, info):

    # todo build cube for 'tir' -> vrtBand12 (as definined by Dirk)
    index = getCube('tir', inputs, info.bbl)

    min = 0
    max = 6000
    score = scaleLinearMinMax(index, min, max)
    return score

def scoreAerosolOpticalThickness(inputs, inmeta, info):

    # todo build cube for 'atmos_opacity'
    index = getCube('atmos_opacity', inputs, info.bbl)

    min = 10000
    max = 0
    score = scaleLinearMinMax(index, min, max)
    return score

def scoreSensor(inputs, inmeta, info):

    # set score of ETM scenes after SLC-off 50%
    # set all other scores to 100%
    slcOffDate = datetime.date(2003,5,31)
    scoreVector = [0.3 if (sensor=='ETM' and date>=slcOffDate) else 1.
              for sensor,date in zip(getMeta('sensor', inmeta), getMeta('date', inmeta))]

    score = getCubeFromVector(scoreVector, inputs, info.bbl)
    return score

def scoreSynopticity(inputs, inmeta, info):

    raise Exception('')
    # this is not really a good implementation, because the data tile can be arbitrary small
    # and the cloud fraction is more and more meaningless

    mask = getCube('mask', inputs, info.bbl)
    cloudFractionVector = numpy.sum(numpy.sum(mask, axis=1, keepdims=True), axis=2, keepdims=True)/float(mask.shape[1]*mask.shape[2])
    clearFractionVector = 1.-cloudFractionVector

    scoreA = clearFractionVector
    scoreB = scoreTargetDoy(inputs, inmeta, info)
    score = scoreA*scoreB
    return score

def scoreCosBeta(inputs, inmeta, info):

    # todo talk to Dirk were slope/aspect data is coming from

    # sza - solar zenith angle
    # tsa - terrain slope angle
    # saa - solar azimuth angle
    # taa - topographic aspect angles
    # cosBeta = cos(sza)*cos(tsa)+sin(sza)*sin(tsa)*cos(saa-taa)

    degreeToRadiance = 0.0174533
    tsa = getCube('slope', inputs, info.bbl)*degreeToRadiance
    taa = getCube('aspect', inputs, info.bbl)*degreeToRadiance
    sunElevation = numpy.array(getMeta('SunElevation', inmeta), dtype=numpy.float32).reshape(-1,1)
    sza = (90.-sunElevation)*degreeToRadiance

    saa = numpy.array(getMeta('SunAzimuth', inmeta), dtype=numpy.float32).reshape(-1,1)*degreeToRadiance
    cosBeta  = numpy.cos(sza)*numpy.cos(tsa)
    cosBeta += numpy.sin(sza)*numpy.sin(tsa)*numpy.cos(saa-taa)
    beta = numpy.arccos(cosBeta)

    min=numpy.pi
    max=0
    score = scaleLinearMinMax(beta, min, max)
    return score

def scoreNDVI(inputs, inmeta, info):

    index = getCube('ndvi', inputs, info.bbl)

    min=-1
    max=+1
    score = scaleLinearMinMax(index, min, max)
    return score

def scoreTargetDoy(inputs, inmeta, info):

    # calculate doys
    targetDoy = (info.targetDate-datetime.date(info.targetDate.year,1,1)).days
    doys = getMeta('doy', inmeta)

    # calc distances to target doy
    # - need to consider 3 cases and take the minimum of all
    distances = [numpy.min(((doy - targetDoy), (doy - 365 - targetDoy), (doy + 365 - targetDoy))) for doy in doys]

    # - create index cube
    index = getCubeFromVector(distances, inputs, info.bbl)

    min=-45
    max=45
    score = scaleRBFMinMax(index, min, max)
    return score

def scoreTargetYear(inputs, inmeta, info):

    # calculate distance to target year
    distances = [abs(year-info.targetDate.year) for year in getMeta('year', inmeta)]
    # - create index cube
    index = getCubeFromVector(distances, inputs, info.bbl)

    # translate to scores
    min = numpy.max(distances)
    max = 0
    score = scaleLinearMinMax(index, min, max)
    return score

def scoreEnsemble(inputs, inmeta, info, ufuncs=[], uargs=[], weights=[]):

    assert len(ufuncs) == len(uargs) and len(ufuncs) == len(weights), 'inconsistent inputs'

    # scale weights to assure sum of weights are equal to 1
    ws = [float(weight)/sum(weights) for weight in weights]

    # calculate weighted average
    score = ufuncs[0](inputs, inmeta, info, **uargs[0]) * ws[0]
    for ufunc,uarg,w in zip(ufuncs,uargs,ws):
        score += ufunc(inputs, inmeta, info, **uarg) * w

    return score

def scorePG(inputs, inmeta, info):
    ufuncs, uargs, weights = zip(
        *[
          #(scoreAerosolOpticalThickness,     {}, 0.75),
          #(scoreCloudDistance,               {}, 0.75),
          #(scoreCosBeta,                     {}, 0.50),

          (scoreHazeOptimizedTransformation, {}, 0.75),
          (scoreNDVI,                        {}, 0.25),
          #(scoreSensor,                      {}, 0.75),
          #(scoreSynopticity,                 {}, 0.75),
          (scoreTargetDoy,                   {}, 1.00),
          (scoreTargetYear,                  {}, 1.00)
          #(scoreThermal,                     {}, 0.50)
        ])

    return scoreEnsemble(inputs, inmeta, info, ufuncs=ufuncs, uargs=uargs, weights=weights)


class DateParameters():
    def __init__(self, date1, date2, bufferYears):
        self.date1 = date1
        self.date2 = date2
        self.bufferYears = bufferYears
        self.intervals = list()
        for yearOffset in range(-bufferYears, bufferYears+1):
            self.intervals.append(((datetime.date(date1.year + yearOffset, date1.month, date1.day)),
                                   (datetime.date(date2.year + yearOffset, date2.month, date2.day))))

    def matchInputDates(self, dates):
        validDates = numpy.zeros_like(dates, numpy.bool)
        for first, last in self.intervals:
            validDates += (dates >= first) * (dates <= last)
        return validDates


    def getName(self):
        return str(self.date1) + '_to_' + str(self.date2) + '_' + str(self.bufferYears * 2 + 1) + 'y'


    def getTargetDate(self):
        return self.date1 + (self.date2-self.date1)/2


'''class QualityCompositeParameters():

    def __init__(self, dateParameters):
        self.dateParameters = dateParameters

    def getName(self):
        return str(self.dateParameters.targetDate)+'_'+str(self.dateParameters.bufferDays*2)+'d_'+str(self.dateParameters.bufferYears*2+1)+'y'

    def getTargetDate(self):
        return str(self.dateParameters.targetDate)


class StatisticsParameters:

    def __init__(self, bandName, statistics, trange=None, dtype=None, dscale=None):
        assert set(statistics).issubset(['distribution','median','mean','stdev'])
        self.distributionPercentages = [0,25,50,75,100]
        self.bandName = bandName
        self.statistics = statistics
        self.trange = trange
        self.dtype = dtype
        self.dscale = dscale

    def getBandNames(self):
        result = list()
        for statistic in self.statistics:
            if statistic=='distribution':
                for percentage in self.distributionPercentages:
                    result.append('p'+str(percentage))
            else:
                result.append(statistic)
        return result

class StatisticsCompositeParameters():

    def __init__(self, dateParameters, statisticsParameters):
        self.dateParameters = dateParameters
        self.statisticsParameters = statisticsParameters

    def getName(self):
        return 'statistics_'+self.statisticsParameters.bandName+'_'+str(self.dateParameters.targetDate)+'_'+str(self.dateParameters.bufferDays*2)+'days_'+str(self.dateParameters.bufferYears*2+1)+'years'

    def getTargetDate(self):
        return str(self.dateParameters.targetDate)

    def getBandNames(self):
        return self.statisticsParameters.getBandNames()
'''

def zvalue_from_index(arr, ind):

    nB, nL, nS = arr.shape
    idx = nS * nL * ind + nS * numpy.arange(nL)[:, None] + numpy.arange(nS)[None, :]
    return numpy.take(arr, idx)


class CompositingApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        # prepare some meta infos
        inputDates = numpy.array(getMeta('date', inmetas))
        inputDoys = numpy.array(getMeta('doy', inmetas)).astype(numpy.int16)
        #inputSceneIDs = numpy.array(inmetas.timeseries_cfmask.getMetadataItem('SceneID'))
        #inputSensorInfos = numpy.array([[sceneID[2],sceneID[3:6],sceneID[6:9]] for sceneID in inputSceneIDs], dtype=numpy.int16)
        bands, samples, lines = inputs.timeseries_cfmask.shape

        # cast to float and set invalid observations to NaN
        invalidValues = getCube('invalid', inputs)
        invalidPixel = numpy.all(invalidValues, axis=0)

        # calculate quality composites
        for dateParameters in otherArgs.dateParameters:

            # - calculate valid date range around target date
            bbl = dateParameters.matchInputDates(inputDates)

            if bbl.any():

                # - calculate quality score
                info2 = Bunch()
                info2.targetDate = dateParameters.getTargetDate()
                info2.bbl = bbl
                qualityCube = scorePG(inputs, inmetas, info2)
                assert bbl.sum() == qualityCube.shape[0], 'inconsistent score cube, check scoring function: '

                # - find best observation
                qualityCube[invalidValues[bbl]] = -numpy.Inf
                bestObs = numpy.nanargmax(qualityCube, axis=0)
                bestObs[invalidPixel] = 0

                # - create composite
                result = list()
                for key in ['timeseries_' + name for name in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']]:
                    band = zvalue_from_index(arr=inputs.__dict__[key], ind=bestObs)
                    band[invalidPixel] = -9999
                    result.append(band.reshape((1, samples, lines)))

                result = numpy.vstack(result)

            else:

                # - handle special case when no observation is available
                shape = (6, samples, lines)
                result = numpy.full(shape, dtype=numpy.int16, fill_value=-9999)
                #print('Warning: No Observation available for target date: '+str(dateParameters.getTargetDate()))

            outputs.__dict__['composite_'+dateParameters.getName()] = result


    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):
        for dateParameters in otherArgs.dateParameters:
            outmeta = outmetas.__dict__['composite_'+dateParameters.getName()]
            outmeta.setNoDataValue(-9999)
            outmeta.setMetadataItem('acquisition time', dateParameters.getTargetDate())
            outmeta.setMetadataItem('wavelength units', 'nanometers')
            outmeta.setMetadataItem('wavelength', [480, 560, 655, 865, 1585, 2200])#+5*[99999]) # set flag bands wavelength to 99,999
            bbl = 6*[1] #+ 5*[0] # mark flag bands as bad bands to exclude them from ENVI Z Plot
            outmeta.setMetadataItem('bbl', bbl)
            outmeta.setBandNames(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])#+['Flag:doy','Flag:sensor','Flag:path','Flag:row','Flag:score'])


    def __init__(self, infolder, outfolder, inextension, footprints=None, compressed=False, of='ENVI'):

        Applier.__init__(self, footprints=footprints, of=of)
        self.dateParameters = list()
        self.infolder = infolder
        self.outfolder = outfolder
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                      productName='timeseries',
                                      imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask'],
                                      extension=inextension))

        self.otherArgs.dateParameters = self.dateParameters

    def appendDateParameters(self, date1, date2, bufferYears=0):

        assert isinstance(date1, datetime.date)
        assert isinstance(date2, datetime.date)

        dateParameters = DateParameters(date1=date1, date2=date2, bufferYears=bufferYears)
        self.dateParameters.append(dateParameters)
        self.appendOutput(ApplierOutput(folder=self.outfolder,
                                        productName='composite', imageNames=[dateParameters.getName()], extension='.img'))

class StatisticsApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        # prepare some meta infos
        inputDates = numpy.array(getMeta('date', inmetas))

        # cast to float and set invalid observations to NaN
        invalidValues = getCube('invalid', inputs)
        invalidPixel = numpy.all(invalidValues, axis=0)

        for key in ['timeseries_'+name for name in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']]:
            inputs.__dict__[key] = inputs.__dict__[key].astype(numpy.float32)
            inputs.__dict__[key][invalidValues] = numpy.NaN

        bands, samples, lines = inputs.timeseries_cfmask.shape

        # calculate statistics
        for dateParameters in otherArgs.dateParameters:

            # - calculate valid date range around target date
            bbl = dateParameters.matchInputDates(inputDates)

            if bbl.any():

                # calculate statistics
                #for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr']:
                for key in otherArgs.variables:

                    input = getCube(name=key, inputs=inputs, bbl=bbl)
                    if key in ['ndvi', 'nbr']:
                        input *= 10000

                    # - percentiles
                    statistics = hub.nan1d.percentiles.nanpercentiles(input, otherArgs.percentiles, copy=True)

                    # - moments
                    if otherArgs.mean:
                        statistics.append(numpy.nanmean(input, axis=0, dtype=numpy.float32, keepdims=True))
                    if otherArgs.stddev:
                        statistics.append(numpy.nanstd(input, axis=0, dtype=numpy.float32, keepdims=True))

                    for i, band in enumerate(statistics):
                        band = band.astype(numpy.int16)
                        band[invalidPixel[None]] = -30000
                        statistics[i] = band

                    output = numpy.vstack(statistics)
                    outputs.__dict__['statistics_' + key + '_' + dateParameters.getName()] = output

            else:
                # - handle special case when no observation is available
                #for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr']:
                for key in otherArgs.variables:
                    outbands = len(otherArgs.percentiles) + otherArgs.mean + otherArgs.stddev
                    shape = (outbands, samples, lines)
                    output = numpy.full(shape, dtype=numpy.int16, fill_value=-30000)
                    outputs.__dict__['statistics_' + key + '_' + dateParameters.getName()] = output

                    #print('Warning: No Observation available for target date: '+str(dateParameters.getTargetDate()))



            # - valid observation counts
            outputs.__dict__['statistics_count_' + dateParameters.getName()] = numpy.sum(numpy.logical_not(getCube('invalid', inputs, bbl)), axis=0, dtype=numpy.int16, keepdims=True)

    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):

        for dateParameters in otherArgs.dateParameters:
            bandNames = otherArgs.percentileNames
            if otherArgs.mean: bandNames.append('mean')
            if otherArgs.stddev: bandNames.append('stddev')

            for key in otherArgs.variables:
                outmeta = outmetas.__dict__['statistics_'+key+'_'+dateParameters.getName()]
                outmeta.setNoDataValue(-30000)
                outmeta.setMetadataItem('acquisition time', dateParameters.getTargetDate())
                outmeta.setBandNames(bandNames)

            outmeta = outmetas.__dict__['statistics_count_' + dateParameters.getName()]
            outmeta.setMetadataItem('acquisition time', dateParameters.getTargetDate())
            outmeta.setBandNames(['valid observations'])

    def __init__(self, infolder, outfolder, inextension, footprints=None, of='ENVI',
                 percentiles=[0,5,25,50,75,95,100],
                 variables=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr'],
                 mean=True, stddev=True):

        Applier.__init__(self, footprints=footprints, of=of)
        self.dateParameters = list()
        self.infolder = infolder
        self.outfolder = outfolder
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                      productName='timeseries',
                                      imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask'],
                                      extension=inextension))

        self.otherArgs.dateParameters = self.dateParameters
        self.otherArgs.percentiles = percentiles
        def percentileName(p):
            if p == 0: return 'min'
            elif p == 50: return 'median'
            elif p == 100: return 'max'
            else: return 'p'+str(p)
        self.otherArgs.percentileNames = [percentileName(p) for p in percentiles]
        self.otherArgs.variables = variables
        self.otherArgs.mean = mean
        self.otherArgs.stddev = stddev

    def appendDateParameters(self, date1, date2, bufferYears=0):

        assert isinstance(date1, datetime.date)
        assert isinstance(date2, datetime.date)

        dateParameters = DateParameters(date1=date1, date2=date2, bufferYears=bufferYears)
        self.dateParameters.append(dateParameters)
        #for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr', 'count']:
        for key in self.otherArgs.variables+['count']:
            self.appendOutput(ApplierOutput(folder=self.outfolder,
                                            productName='statistics', imageNames=[key+'_'+dateParameters.getName()], extension=self.outextension))


def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    infolder = r'c:\work\data\gms\landsatTimeseriesMGRS'
    outfolder= r'c:\work\data\gms\composites'

    mgrsFootprints = ['33UUT']

    years = [2000]#, 2001]
    months = [2]#,5,8,11]
    days = [15]
    bufferDays = 190
    bufferYears = 30
    applier = CompositingApplier(infolder=infolder, outfolder=outfolder, inextension='.img', compressed=False,
                                 years=years, months=months, days=days,
                                 bufferDays=bufferDays, bufferYears=bufferYears,
                                 footprints=mgrsFootprints)


    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()

    applier = StatisticsApplier(infolder=infolder, outfolder=outfolder, inextension='.img', compressed=False,
                                 years=years, months=months, days=days,
                                 bufferDays=bufferDays, bufferYears=bufferYears,
                                 footprints=mgrsFootprints)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()

if __name__ == '__main__':

    import hub.timing
    hub.timing.tic()
    test()
    hub.timing.toc()
