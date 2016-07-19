import lamos.cubebuilder.cube
import lamos.cubebuilder.applier
import datetime
from hub.collections import Bunch
import hub.numpy.ma
import os
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive
import numpy

def getCube(name, inputs, bbl=None):

    # return cube if already exist...
    if inputs.__dict__.has_key(name):
        result = inputs.__dict__[name]
    # ...or create and cache it otherwise
    else:
        if   name=='ndvi' : result = (inputs.timeseries_nir-inputs.timeseries_red).__truediv__(inputs.timeseries_nir+inputs.timeseries_red)
        elif name=='vis'  : result = inputs.timeseries_blue/3+inputs.timeseries_green/3+inputs.timeseries_red/3
        elif name=='ir'   : result = inputs.timeseries_nir/3 +inputs.timeseries_swir1/3+inputs.timeseries_swir2/3
        elif name=='invalid' : result = inputs.timeseries_cfmask != 0
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
    for xi,yi in zip(x,y): print xi, ',', round(yi,2)

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

    mask = getCube('mask', inputs, info.bbl)
    cloudFractionVector = numpy.sum(mask, axis=1, keepdims=True)/float(mask.shape[1])
    clearFractionVector = 1.-cloudFractionVector

    scoreA = clearFractionVector
    scoreB = scoreTargetDoy(inputs, inmeta, info)
    score = scoreA*scoreB
    return score

def scoreCosBeta(inputs, inmeta, info):

    # sza - solar zenith angle
    # tsa - terrain slope angle
    # saa - solar azimuth angle
    # taa - topographic aspect angles
    # cosBeta = cos(sza)*cos(tsa)+sin(sza)*sin(tsa)*cos(saa-taa)

    # todo check correct usage of degrees/rads ask Patrick, need to convert!
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
    distances = [__builtins__.min((doy-targetDoy),(doy-365-targetDoy),(doy+365-targetDoy))  for doy in doys]
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
    min = __builtins__.max(distances)
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

          #(scoreHazeOptimizedTransformation, {}, 0.75),
          #(scoreNDVI,                        {}, 0.25),
          #(scoreSensor,                      {}, 0.75),
          #(scoreSynopticity,                 {}, 0.75),
          (scoreTargetDoy,                   {}, 1.00),
          #(scoreTargetYear,                  {}, 1.00)
          #(scoreThermal,                     {}, 0.50)
        ])

    return scoreEnsemble(inputs, inmeta, info, ufuncs=ufuncs, uargs=uargs, weights=weights)


class DateParameters():
    def __init__(self, targetDate, bufferDays, bufferYears):
        self.targetDate = targetDate
        self.targetDoy  = (targetDate-datetime.date(targetDate.year,1,1)).days
        self.bufferDays = bufferDays
        self.bufferYears = bufferYears
        self.intervals = list()
        for yearOffset in range(-bufferYears,bufferYears+1):
            self.intervals.append((datetime.date(targetDate.year+yearOffset,targetDate.month,targetDate.day) - datetime.timedelta(bufferDays), # first date
                                   datetime.date(targetDate.year+yearOffset,targetDate.month,targetDate.day) + datetime.timedelta(bufferDays))) # last date

    def matchInputDates(self, dates):
        validDates = numpy.zeros_like(dates, numpy.bool)
        for first, last in self.intervals:
            validDates += (dates >= first) * (dates <= last)
        return validDates

class QualityCompositeParameters():

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


class CompositingApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        # prepare some meta infos
        import hub.datetime
        inputDates = numpy.array(getMeta('date', inmetas))
        inputDoys = numpy.array(getMeta('doy', inmetas)).astype(numpy.int16)
        inputSceneIDs = numpy.array(inmetas.timeseries_cfmask.getMetadataItem('SceneID'))
        inputSensorInfos = numpy.array([[sceneID[2],sceneID[3:6],sceneID[6:9]] for sceneID in inputSceneIDs], dtype=numpy.int16)
        bands, samples, lines = inputs.timeseries_cfmask.shape

        # cast to float and set invalid observations to NaN
        invalid = getCube('invalid', inputs)
        invalidAll = numpy.all(invalid, axis=0)
        for key in ['timeseries_'+name for name in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']]:
            inputs.__dict__[key] = inputs.__dict__[key].astype(numpy.float32)
            inputs.__dict__[key][invalid] = numpy.NaN

        # calculate quality composites
        for qualityCompositeParameters in otherArgs.qualityCompositeParametersList:

            # - calculate valid date range around target date
            bbl = qualityCompositeParameters.dateParameters.matchInputDates(inputDates)

            if bbl.any():

                # - calculate quality score
                info2 = Bunch()
                info2.targetDate = qualityCompositeParameters.dateParameters.targetDate
                info2.bbl = bbl
                qualityCube = scorePG(inputs, inmetas, info2)
                assert bbl.sum() == qualityCube.shape[0], 'inconsistent score cube, check scoring function: '+ qualityCompositeParameters.qualityParameters.scoreFunction.__name__

                # - find best observation
                qualityCube[invalid] = -numpy.Inf
                bestObs = numpy.nanargmax(qualityCube, axis=0)
                bestObs[invalidAll] = 0


                # - create composite
                cubes = [inputs.sr[key][bbl] for key in otherArgs.bandNamesSubset]
                cubes.append(inputDoys.reshape((-1,1))[bbl]) # add Flag:doy
                cubes.append(inputSensorInfos[:,0:1][bbl])   # add Flag:sensor
                cubes.append(inputSensorInfos[:,1:2][bbl])   # add Flag:path
                cubes.append(inputSensorInfos[:,2:3][bbl])   # add Flag:row
                cubes.append((qualityCube*10000).astype(numpy.int16))# add Flag:score

                # - create composite cube
                qualityCompositeCube = hub.numpy.ma.qualityCompositeCube(cubes,  qualityCube)

                # - fill masked values with -9999
                qualityCompositeCube = qualityCompositeCube.filled(-9999)

                # - convert back to 3d cubes
                qualityCompositeCube = hub.numpy.ma.unflatten(qualityCompositeCube, samples, lines)

            else:
                # - handle special case when no observation is available
                shape = (len(otherArgs.bandNamesSubset)+5, samples, lines)
                qualityCompositeCube = numpy.full(shape, dtype=numpy.int16, fill_value=-9999)
                print('Warning: No Observation available for target date '+qualityCompositeParameters.getTargetDate()+'.')

            outputs.qualityComposites[qualityCompositeParameters.getName()] = qualityCompositeCube



    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):

        outmetas.vi_ndvi = inmetas.timeseries_cfmask
        outmetas.vi_ndvi.setNoDataValue(-1)


    def __init__(self, infolder, outfolder, compressed=False):

        Applier.__init__(self, compressed=compressed)
        self.composites = list()
        self.infolder = infolder
        self.outfolder = outfolder
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                      productName='timeseries',
                                      imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask'],
                                      extension='.img'))


    def appendComposite(self, year, month, day, bufferDays, bufferYears=0):

        targetDate = datetime.date(year, month, day)
        dateParameters = DateParameters(targetDate, bufferDays, bufferYears)
        compositeParameters = QualityCompositeParameters(dateParameters)
        self.composites.append(compositeParameters)

        self.appendOutput(ApplierOutput(folder=self.outfolder,
                                        productName='composite', imageNames=[compositeParameters.getName()], extension='.img'))

    def apply(self):

        self.otherArgs.qualityCompositeParametersList = self.composites
        Applier.apply(self)
        return MGRSArchive(self.outputs[0].folder)


def test():

    applier = CompositingApplier(infolder=r'c:\work\data\gms\landsatTimeseriesMGRS',
                                 outfolder=r'c:\work\data\gms\landsatComposites',
                                 compressed=False)
    applier.controls.setWindowXsize(100)
    applier.controls.setWindowYsize(100)

    for year in [2000]:
        for month in [1]:
            day = 1
            bufferDays = 183
            bufferYears = 30
            applier.appendComposite(year=year, month=month, day=day,
                                    bufferYears = bufferYears, bufferDays=bufferDays)

    archive = applier.apply()
    archive.info()


if __name__ == '__main__':

    import hub.timing
    hub.timing.tic()
    test()
    hub.timing.toc()
