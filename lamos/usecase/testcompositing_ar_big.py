import numpy
import yaml
import lamos.cubebuilder.cube
import lamos.cubebuilder.applier
import datetime
from hub.collections import Bunch
import hub.numpy.ma
import os

def getCube(name, inputs, bbl=None):

    # return cube if already exist...
    if inputs.sr.has_key(name):
        result = inputs.sr[name]
    # ...or create and cache it otherwise
    else:
        if   name=='ndvi' : result = (inputs.sr.nir-inputs.sr.red).__truediv__(inputs.sr.nir+inputs.sr.red)
        elif name=='vis'  : result = inputs.sr.blue/3+inputs.sr.green/3+inputs.sr.red/3
        elif name=='ir'   : result = inputs.sr.nir/3 +inputs.sr.swir1/3+inputs.sr.swir2/3
        elif name=='mask' : result = (inputs.sr.bandcfmask != 0) * (inputs.sr.bandcfmask != 1)
        else:
            raise Exception('Unknown cube requested: '+name)
        inputs.sr[name] = result

    # subset bands if needed and return cube
    if bbl is None:
        return result
    else:
        return result[bbl]

def getCubeFromVector(vector, inputs, bbl=None):

    # reshape vector and subset required bands
    vectorCube = numpy.array(vector).reshape(-1,1)[bbl]

    # broadcast to full cube size and apply mask
    mask = getCube('mask', inputs, bbl)
    cube = numpy.ma.array(numpy.ones_like(mask)*vectorCube, mask=mask) # todo: in numpy v1.10 could use numpy.broadcast_to()
    return cube

def getMeta(name, inmeta):

    # return cube if already exist...
    if inmeta.sr.has_key(name):
        result = inmeta.sr[name]
    # ...or create and cache it otherwise
    else:
        if   name=='date': result = [yaml.load(acqDate.replace("'",'')) for acqDate in inmeta.sr.bandcfmask.getMetadataItem('AcqDate')]
        elif name=='doy':  result = [(date-datetime.date(date.year,1,1)).days for date in getMeta('date', inmeta)]
        elif name == 'year': result = [date.year for date in getMeta('date', inmeta)]
        elif name == 'sensor':  result = inmeta.sr.band2.getMetadataItem('Sensor')
        else:
            raise Exception('Unknown metadate requested: '+name)
        inmeta.sr[name] = result

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

# Set up the function to be applied
def compositingDoit(info, inputs, outputs, inmeta, otherArgs=None):

    # prepare inputs
    # - acquisition time as date array and gregorian days array
    # NOTE: fix data set headers and remove the s.replace() stuff
    inputDates = numpy.array([yaml.load(acqDate.replace("'",'')) for acqDate in inmeta.sr.bandcfmask.getMetadataItem('AcqDate')])
    inputDoys = numpy.array([(date-datetime.date(date.year,1,1)).days for date in inputDates]).astype(numpy.int16)
    inputDatesGregorian =  numpy.array([date.toordinal() for date in inputDates])
    inputSceneIDs = numpy.array([sceneID.replace("'"," ").replace(' ','') for sceneID in inmeta.sr.bandcfmask.getMetadataItem('SceneID')])
    inputSensorInfos = numpy.array([[sceneID[2],sceneID[3:6],sceneID[6:9]] for sceneID in inputSceneIDs], dtype=numpy.int16)

    bands, samples, lines = inputs.sr.bandcfmask.shape

    # - create mask that excludes everythink that is not clear land or clear water,
    #   and apply it to the input data

    for key, cube in inputs.sr.items():
        inputs.sr[key] = numpy.ma.array(inputs.sr[key], mask=getCube('mask', inputs))

    # - remap band numbers to more meaningful names
    for bandNumber, bandName in zip(otherArgs.bandNumbersSubset, otherArgs.bandNamesSubset):
        inputs.sr[bandName] = inputs.sr['band'+str(bandNumber)]

    # - flatten 3d cubes to 2d
    for key in inputs.sr:
        inputs.sr[key] = hub.numpy.ma.flatten(inputs.sr[key])

    # - todo: fill missing observations for 'aerosol' band
    assert not inputs.sr.has_key('aerosol'), 'not yet implemented/needed'

    # calculate quality composites
    for qualityCompositeParameters in otherArgs.qualityCompositeParametersList:

        # - calculate valid date range around target date
        bbl = qualityCompositeParameters.dateParameters.matchInputDates(inputDates)

        if bbl.any():
            # - call scoring function
            info2 = Bunch()
            info2.targetDate = qualityCompositeParameters.dateParameters.targetDate
            info2.bbl = bbl
            qualityCube = qualityCompositeParameters.scoreFunction(inputs, inmeta, info2, **qualityCompositeParameters.args)
            assert bbl.sum() == qualityCube.shape[0], 'inconsistent score cube, check scoring function: '+ qualityCompositeParameters.qualityParameters.scoreFunction.__name__

            # - prepare list of input band cubes for compositing, each input cube will represent a band in the resulting composite cube
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

    # calculate statistics composites
    for statisticsCompositeParameters in otherArgs.statisticsCompositeParametersList:

        # - calculate valid date range around target date
        bbl = statisticsCompositeParameters.dateParameters.matchInputDates(inputDates)

        if bbl.any():


            # - create VIS or IR band on the fly if needed
            bandName = statisticsCompositeParameters.statisticsParameters.bandName
            cube = getCube(bandName, inputs, bbl)

            # - create composite cube
            statisticsCompositeCube, dummy = hub.numpy.ma.statisticsCompositeCube(cube, statisticsCompositeParameters.statisticsParameters)

            # - fill masked values with -9999
            statisticsCompositeCube = statisticsCompositeCube.filled(-9999)

            # - convert back to 3d cubes
            outputs.statisticsComposites[statisticsCompositeParameters.getName()] = hub.numpy.ma.unflatten(statisticsCompositeCube, samples, lines)

        else:
            # - handle special case when no observation is available
            raise Exception('ToDO no valid observations!!!')
            #shape = (len(otherArgs.bandNamesSubset) + 5, samples, lines)
            #qualityCompositeCube = numpy.full(shape, dtype=numpy.int16, fill_value=-9999)
            print('Warning: No Observation available for target date ' + statisticsCompositeParameters.getTargetDate() + '.')


# Set up the function to specify output metadata
def compositingMeta(inmeta, outmeta, otherArgs=None):

    # set metadate for quality composites
    # - use R,G,B = 'nir', 'swir1', 'red' as default bands (corresponding virtual sensor bands are 8,10,4)
    default_bands = [otherArgs.bandNamesSubset.index('nir')+1, otherArgs.bandNamesSubset.index('swir1')+1, otherArgs.bandNamesSubset.index('red')+1]
    for (key, gdalMeta), acquisition_time in zip(outmeta.qualityComposites.items(), otherArgs.outfiles_qualityComposites_acquisition_time):
        gdalMeta.setNoDataValue(-9999)
        #gdalMeta.setMetadataItem('default_bands', default_bands)
        gdalMeta.setMetadataItem('acquisition time', acquisition_time)
        gdalMeta.setMetadataItem('wavelength units', 'nanometers')
        gdalMeta.setMetadataItem('wavelength', otherArgs.wavelengthSubset+5*[99999], mapToBands=True) # set flag bands wavelength to 99,999
        bbl = len(otherArgs.bandNamesSubset)*[1] + 5*[0] # mark flag bands as bad bands to exclude them from ENVI Z Plot
        gdalMeta.setMetadataItem('bbl', bbl, mapToBands=True)
        gdalMeta.setBandNames(otherArgs.bandNamesSubset+['Flag:doy','Flag:sensor','Flag:path','Flag:row','Flag:score'])

    # set metadate for statistics composites
    acquisition_times =otherArgs.outfiles_statisticsComposites_acquisition_time
    band_namess =otherArgs.outfiles_statisticsComposites_band_names
    for (key, gdalMeta), acquisition_time, band_names in zip(outmeta.statisticsComposites.items(), acquisition_times, band_namess):
        gdalMeta.setNoDataValue(-9999)
        gdalMeta.setMetadataItem('acquisition time', acquisition_time)
        gdalMeta.setBandNames(band_names)

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
    def __init__(self, dateParameters, scoreFunction, args):
        self.dateParameters = dateParameters
        self.scoreFunction = scoreFunction
        self.args = args

    def getName(self):
        return self.scoreFunction.__name__+'_'+str(self.dateParameters.targetDate)+'_'+str(self.dateParameters.bufferDays*2)+'d_'+str(self.dateParameters.bufferYears*2+1)+'y'

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


def composite(rootdir, mgrstiles, qualityCompositeParametersList=[], statisticsCompositeParametersList=[]):

    # container for all additional information needed
    otherArgs = Bunch()
    otherArgs.qualityCompositeParametersList = qualityCompositeParametersList
    otherArgs.statisticsCompositeParametersList = statisticsCompositeParametersList

    # Set up input and output filenames.
    infiles  = lamos.cubebuilder.applier.CubenameAssociations()
    outfiles = lamos.cubebuilder.applier.CubenameAssociations()
    bandNumbers     = [ 1,         2,      3,       4,     8,     10,      11]
    bandNames       = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    wavelengthLower = [ 430,       450,    530,     640,   850,   1570,    2110]
    wavelengthUpper = [ 450,       510,    590,     670,   880,   1600,    2290]
    wavelength = [(lower+upper)/2 for lower, upper in zip(wavelengthLower,wavelengthUpper)]

    otherArgs.bandNamesSubset  = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    otherArgs.bandNumbersSubset = [bandNumbers[bandNames.index(bandName)] for bandName in otherArgs.bandNamesSubset]
    otherArgs.wavelengthSubset =  [ wavelength[bandNames.index(bandName)] for bandName in otherArgs.bandNamesSubset]

    # prepare applier inputs and outputs
#    rootdir = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR_Small'
#    rootdir = r'\\141.20.140.91\RAM_Disk\testCaseAR_Small'
    # - infiles
    inBandNames = ['band'+str(bandNumber) for bandNumber in otherArgs.bandNumbersSubset]
    infiles.sr  = (os.path.join(rootdir, 'cubes'), inBandNames+['bandcfmask'])

    # - outfiles for qualityComposites
    outfiles.qualityComposites = (os.path.join(rootdir, 'composites'),
                                  [param.getName() for param in qualityCompositeParametersList])
    otherArgs.outfiles_qualityComposites_acquisition_time = [param.getTargetDate() for param in qualityCompositeParametersList]

    # - outfiles for statisticsComposites
    outfiles.statisticsComposites = (os.path.join(rootdir, 'composites'),
                                    [param.getName() for param in statisticsCompositeParametersList])
    otherArgs.outfiles_statisticsComposites_acquisition_time = [param.getTargetDate() for param in statisticsCompositeParametersList]
    otherArgs.outfiles_statisticsComposites_band_names = [param.getBandNames() for param in statisticsCompositeParametersList]


    # Set up tiles to be processed
    #mgrstiles = ['32UNB', '32UNC', '32UND', '32UPB', '32UPC', '32UPD', '32UQB', '32UQC', '32UQD', '33UTS', '33UTT', '33UTU', '33UUS', '33UUT', '33UUU', '33UVS', '33UVT', '33UVU']
    #mgrstiles = ['32UPB']
    #mgrstiles = ['32UQB']

    # Set up processing controls (creates ENVI Files per default)
    controls = lamos.cubebuilder.applier.ApplierControls()
    #controls.rios.windowysize = 100

    # Apply the function to the inputs, creating the outputs.
    lamos.cubebuilder.applier.apply(compositingDoit, compositingMeta, infiles, outfiles, mgrstiles, controls=controls, otherArgs=otherArgs, verbose=True)

def test_ar():

#    sys.exit()
    # create some quality observation composites...
    qualityCompositeParametersList = list()
    for year in [2012,2013,2014]: # for some years,
        for month in range(1,13): #[2,5,8,11]:  # for the four seasons (winter, spring, summer, autumn)
            day = 15              #   - target day is the center of the season
            bufferDays = 45       #   - use observations plus/minus 45 days (i.e. 3 month overall)
            bufferYear= 1        #   - also use observations from plus/minus one year (i.e. 3 years overall)
            targetDate = datetime.date(year,month,day)
            dateParameters =     DateParameters(targetDate, bufferDays, bufferYear)
            # for all target dates create the following observation composites...
            scoreFunction = scorePG
            args = {}
            qualityCompositeParametersList.append(QualityCompositeParameters(dateParameters, scoreFunction, args))

    # create some statistics composites...
    statisticsCompositeParametersList = list()
    for year in [2012,2013,2014]: # for some years, take all observations of this year
        month, day  = 7, 1    #   - target day is the center of the year
        bufferDays = 183      #   - use observations plus/minus 183 days (i.e. ~1 year overall)
        bufferYear = 0        #   - do not use observations from other years
        dateParameters = DateParameters(datetime.date(year,month,day), bufferDays, bufferYear)
        # for all target dates create the following statistics composites...
        for  bandName,  statistics,       trange in [
            ['nir', ['distribution','mean','stdev'], None]]:


#            ['ndvi',  ['distribution'],   None],         # ...NDVI distribution (min,q25,median,q75,max)
#            ['ir',    ['median', 'mean'], None],         # ...median/mean for infrared region 'ir' = ('nir'+'swir1'+'swir2')/3
#            ['vis',   ['median', 'mean'], None],         # ...median/mean for visible region 'vis' = ('blue'+'green'+'red')/3
#            ['swir1', ['stdev'],          [1000,8000]]]: # ...trimmed stddev for swir

            dtype = numpy.int16                          # cast all results to int16
            dscale = 1000 if bandName=='ndvi' else None  # in case of NDVI, apply scale factor of 1000 before casting to int16
            statisticsParameters = StatisticsParameters(bandName, statistics, trange, dtype=dtype, dscale=dscale)
            statisticsCompositeParametersList.append(StatisticsCompositeParameters(dateParameters, statisticsParameters))

    # doit
    rootdir = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR_Small'
    rootdir = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR_Big'
    mgrstiles = ['32UQB']
    mgrstiles = ['32UNB', '32UNC', '32UND', '32UPB', '32UPC', '32UPD', '32UQB', '32UQC', '32UQD', '33UTS', '33UTT', '33UTU', '33UUS','33UUT', '33UUU', '33UVS', '33UVT', '33UVU']
    mgrstiles = mgrstiles[10:11]

    composite(rootdir, mgrstiles, qualityCompositeParametersList[5:6], statisticsCompositeParametersList)

def test_cs():

    # create some quality observation composites...
    qualityCompositeParametersList = list()
    for year in [1987,2012]: # for some years,
        for month in [7]: #[2,5,8,11]:  # for the four seasons (winter, spring, summer, autumn)
            day = 15              #   - target day is the center of the season
            bufferDays = 180       #   - use observations plus/minus 45 days (i.e. 3 month overall)
            bufferYear= 0        #   - also use observations from plus/minus one year (i.e. 3 years overall)
            targetDate = datetime.date(year,month,day)
            dateParameters =     DateParameters(targetDate, bufferDays, bufferYear)
            # for all target dates create the following observation composites...
            scoreFunction = scorePG
            args = {}
            qualityCompositeParametersList.append(QualityCompositeParameters(dateParameters, scoreFunction, args))

    # create some statistics composites...
    statisticsCompositeParametersList = list()
    for year in [1987,2012]: # for some years, take all observations of this year
        month, day  = 7, 1    #   - target day is the center of the year
        bufferDays = 183      #   - use observations plus/minus 183 days (i.e. ~1 year overall)
        bufferYear = 1        #   - do not use observations from other years
        dateParameters = DateParameters(datetime.date(year,month,day), bufferDays, bufferYear)
        # for all target dates create the following statistics composites...
        for  bandName,  statistics,       trange in [
            ['blue', ['mean', 'stdev'], None],
            ['green', ['mean', 'stdev'], None],
            ['red', ['mean', 'stdev'], None],
            ['nir', ['mean', 'stdev'], None],
            ['swir1', ['mean', 'stdev'], None],
            ['swir2', ['mean', 'stdev'], None]]:
#            ['blue', ['distribution', 'mean', 'stdev'], None],
#            ['green', ['distribution', 'mean', 'stdev'], None],
#            ['red', ['distribution', 'mean', 'stdev'], None],
#            ['nir', ['distribution', 'mean', 'stdev'], None],
#            ['swir1', ['distribution', 'mean', 'stdev'], None],
#            ['swir2', ['distribution', 'mean', 'stdev'], None]]:

            #            ['ndvi',  ['distribution'],   None],         # ...NDVI distribution (min,q25,median,q75,max)
#            ['ir',    ['median', 'mean'], None],         # ...median/mean for infrared region 'ir' = ('nir'+'swir1'+'swir2')/3
#            ['vis',   ['median', 'mean'], None],         # ...median/mean for visible region 'vis' = ('blue'+'green'+'red')/3
#            ['swir1', ['stdev'],          [1000,8000]]]: # ...trimmed stddev for swir

            dtype = numpy.int16                          # cast all results to int16
            dscale = 1000 if bandName=='ndvi' else None  # in case of NDVI, apply scale factor of 1000 before casting to int16
            statisticsParameters = StatisticsParameters(bandName, statistics, trange, dtype=dtype, dscale=dscale)
            statisticsCompositeParametersList.append(StatisticsCompositeParameters(dateParameters, statisticsParameters))

    # doit
    rootdir = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseCS'
    mgrstiles = ['33UUQ']
    mgrstiles = ['33UUQ', '33UVQ', '33UUP', '33UVP']
    composite(rootdir, mgrstiles, qualityCompositeParametersList[0:1], statisticsCompositeParametersList)

if __name__ == '__main__':
#    test_ar()

    import cProfile
    cProfile.run('test_ar()', sort=2)
