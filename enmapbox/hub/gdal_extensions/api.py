__author__ = 'janzandr'
import numpy
import osgeo
from gdalconst import *

import gdal
from enmapbox.hub.collections import Bunch


def geoInfo(file):
    result = Bunch()
    dataset = gdal.Open(file, GA_ReadOnly)
    result.geoTransform = numpy.array(dataset.GetGeoTransform())
    result.projection = dataset.GetProjection()
    result.rasterSize = numpy.array((dataset.RasterXSize, dataset.RasterYSize))
    result.pixelSize = result.geoTransform[[1,5]]
    result.pixelTie  = result.geoTransform[[2,4]]
    result.geoTie  = result.geoTransform[[0,3]]
    result.ul = result.geoTie+result.rasterSize*result.pixelTie
    result.lr = result.ul+result.rasterSize*result.pixelSize
    result.boundingBox = numpy.append(result.ul, result.lr)

def readCube(filename):
    driver = gdal.GetDriverByName('MEM')
    dataset = driver.CreateCopy('', gdal.Open(filename))
    cube = dataset.ReadAsArray(xoff=0, yoff=0, xsize=dataset.RasterXSize, ysize=dataset.RasterYSize)
    return cube

def writeCube(cube, filename, srsfilename=None, nodatavalue=None):
    enmapbox.hub.file.mkfiledir(filename)
    #bands, lines, samples  = cube.shape
    '''
    GDALType = osgeo.gdal_array.NumericTypeCodeToGDALTypeCode(cube.dtype)
    driver = gdal.GetDriverByName('ENVI')
    dataset = driver.Create(filename, samples, lines, bands, GDALType)
    for i in range(bands):
        band = dataset.GetRasterBand(i + 1)
        band.WriteArray(cube[i])
    dataset = None
    '''
    if srsfilename == None:
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format='ENVI')
    else:
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format='ENVI', prototype=gdal.Open(srsfilename))

    # set no data value
    if nodatavalue != None:
        # set GDAL no data value
        for band in [datasource.GetRasterBand(b+1) for b in range(datasource.RasterCount)]:
            band.SetNoDataValue(nodatavalue)
        # set ENVI data ignore value
        datasource.SetMetadataItem('data_ignore_value', str(nodatavalue), 'ENVI')
        datasource.FlushCache()
    datasource = None


if __name__ == '__main__':
    filename = r'H:\EuropeanDataCube\testCaseAR\cubes\32\32UNB\band2.vrt'
    cube = readCube(filename)
    print(cube.shape)
    writeCube(cube,r't:\testCube.img', filename, nodatavalue=-9999)
    print('...done')
