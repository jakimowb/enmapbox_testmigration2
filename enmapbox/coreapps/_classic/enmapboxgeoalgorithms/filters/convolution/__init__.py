from enmapboxgeoalgorithms.estimators import parseFolder

def parseSpatialKernel():
    return parseFolder(package='enmapboxgeoalgorithms.filters.convolution.spatial')

def parseSpectralKernel():
    return parseFolder(package='enmapboxgeoalgorithms.filters.convolution.spectral')

