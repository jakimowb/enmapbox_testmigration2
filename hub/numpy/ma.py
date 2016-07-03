import numpy
#import scipy
import scipy.stats.mstats

def flatten(cube3d):
    cube2d = cube3d.reshape((cube3d.shape[0],-1))
    return cube2d

def unflatten(cube2d, samples, lines):
    cube3d = cube2d.reshape((cube2d.shape[0],samples,lines))
    return cube3d

def argPercentilesBand(cube, percentages):
    """

    :param cube: Flat cube.
    :param percentages:
    :return: List of bands holding the band indices for the requested percentiles.
    """
    assert cube.ndim == 2

    # if only percentiles for min or max are required use faster argmin/argmax functions
    onlyMinMax = numpy.array([p==0 or p==100 for p in percentages]).all()
    result = list()
    if onlyMinMax:
        for percentage in percentages:
            if percentage==0:   argBand = numpy.ma.argmin(cube, axis=0)
            if percentage==100: argBand = numpy.ma.argmax(cube, axis=0)
            result.append(argBand)
    else:
        probabilities = [v/100. for v in percentages]
        percentilesCube = scipy.stats.mstats.mquantiles(cube, probabilities, axis=0)
        for percentilesBand in percentilesCube:
            rankedCube = numpy.ma.abs(cube-percentilesBand.reshape((1,-1)))
            argminBand = numpy.ma.argmin(rankedCube, axis=0)
            result.append(argminBand)
    return result

def compositeBand(cube, argBand):
    """

    :param cube:
    :param argBand:
    :return: Band composite from band indices given by argBand.
    """
    assert cube.ndim == 2
    bands, samples = cube.shape
    result = cube[argBand.reshape((1,-1)),numpy.arange(samples).reshape((-1,samples))]
    return result

def qualityCompositeCube(cubes, qualityCube, stack=True):
    """

    :param cubes:
    :param scoreCube:
    :return: A dict of quality composites. One composite for each requested percentiles. Keys are given by 'percentages'
    """
    argBand = argPercentilesBand(qualityCube, percentages=[100])[0]
    mask =  compositeBand(qualityCube.mask, argBand)
    composite = list()
    for cube in cubes:
        band = compositeBand(cube, argBand)
        composite.append(numpy.ma.array(band, mask=mask))
    if stack: composite = numpy.ma.vstack(composite)

    return composite

def statisticsCompositeCube(cube, statisticsParameters, stack=True):

    composite = list()
    bandNames = statisticsParameters.getBandNames()

    # mask outliers if needed
    if statisticsParameters.trange is None:
        mask = False
    else:
        mask = (cube < statisticsParameters.trange[0]) + (cube > statisticsParameters.trange[1])
    mcube = numpy.ma.array(cube, mask=mask)

    # calculate some statistics (see http://docs.scipy.org/doc/numpy-1.8.1/reference/routines.ma.html#arithmetics)
    for statistic in statisticsParameters.statistics:
        if statistic=='distribution':
            probabilities = [v/100. for v in statisticsParameters.distributionPercentages]
            composite.append(scipy.stats.mstats.mquantiles(mcube, probabilities, axis=0))
        elif statistic=='median':
            composite.append(numpy.ma.median(mcube, axis=0))
        elif statistic=='mean':
            composite.append(numpy.ma.mean(mcube, axis=0))
        elif statistic=='stdev':
            composite.append(numpy.ma.std(mcube, axis=0))

    # prepare result and return
    # - cast to output dtype if needed
    for icube,i in zip(composite,range(len(composite))):
        if statisticsParameters.dscale is not None: icube *= statisticsParameters.dscale
        if statisticsParameters.dtype is not None: icube = icube.astype(statisticsParameters.dtype)
        composite[i] = icube

    # - stack if needed
    if stack: composite = numpy.ma.vstack(composite)

    return composite, bandNames

if __name__ == '__main__':
    ma = numpy.ma.array([[10,10,10],[20,20,20]],mask=[[1,0,0],[1,0,1]])

    print ma
    print
    print qualityCompositeCube([ma,ma], [0,100], ma)
    #print statisticsCompositeCube(ma, percentages=[0,100], mean=True, dtype=numpy.int16)
