from __future__ import print_function
import gdal, osr
import numpy
from rios.pixelgrid import PixelGridDefn
from osgeo import gdal_array
from hub.timing import tic, toc
from hub.gdal.api import GDALMeta

def getTestData():
    filename = r'C:\Work\data\gms\landsatMGRS\33U\UT\LC81940242015235LGN00\LC81940242015235LGN00_qa.vrt'
    filename = r'C:\Work\data\Hymap_Berlin-B_Regression-GroundTruth'
    filename = r'C:\Work\data\Hymap_Berlin-A_Classification-GroundTruth'

    ds = gdal.Open(filename)
    projection = ds.GetProjectionRef()
    geotransform = ds.GetGeoTransform()
    cube = ds.ReadAsArray(xoff=0, yoff=0, xsize=ds.RasterXSize, ysize=ds.RasterYSize)
    if cube.ndim == 2: cube = cube[None]
    meta = GDALMeta(datacource=ds)
    noDataValue = meta.getNoDataValue()
    ds = None
    return cube, meta, projection, geotransform, noDataValue

def numpyArrayToGDALMemoryDatasource(array, projection, geotransform, noDataValue=None):

    assert isinstance(array, numpy.ndarray)
    assert array.ndim == 3
    bands, ysize, xsize = array.shape
    eType = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
    ds = gdal.GetDriverByName('MEM').Create('', xsize, ysize, bands, eType)
    #ds = gdal.GetDriverByName('ENVI').Create(r'c:\work\testWarpSource.bsq', xsize, ysize, bands, eType)

    ds.SetGeoTransform(geotransform)
    ds.SetProjection(projection)
    for i in range(ds.RasterCount):
        rb = ds.GetRasterBand(i + 1)
        if noDataValue is not None:
            rb.SetNoDataValue(noDataValue)
        rb.WriteArray(array[i])

    return ds

def GDALDatasourceToNumpyArray(ds):

    projection = ds.GetProjectionRef()
    geotransform = ds.GetGeoTransform()
    cube = ds.ReadAsArray(xoff=0, yoff=0, xsize=ds.RasterXSize, ysize=ds.RasterYSize)
    noDataValues = [ds.GetRasterBand(i+1).GetNoDataValue() for i in range(ds.RasterCount)]
    return cube, projection, geotransform, noDataValues

def initWarpedGDALMemoryDatasource(ds, xRes, yRes, xAnchor, yAnchor, projection):

    # calculate pixel grid for warped datasource
    ingrid = PixelGridDefn(projection=ds.GetProjectionRef(), geotransform=ds.GetGeoTransform(),
                           ncols=ds.RasterXSize, nrows=ds.RasterYSize)

    gridAnchored = PixelGridDefn(xMin=xAnchor, xMax=xAnchor+xRes, xRes=xRes,
                                    yMin=yAnchor, yMax=yAnchor+yRes, yRes=yRes,
                                    projection=str(projection))

    grid = ingrid.reproject(targetGrid=gridAnchored)
    geotransform = grid.makeGeoTransform()

    # init output data source
    ysize, xsize = grid.getDimensions()
    bands = ds.RasterCount
    eType = ds.GetRasterBand(1).DataType
    outds = gdal.GetDriverByName('MEM').Create('', xsize, ysize, bands, eType)
    #outds = gdal.GetDriverByName('ENVI').Create(r'c:\work\testWarpTarget.bsq', xsize, ysize, bands, eType)
    outds.SetGeoTransform(geotransform)
    outds.SetProjection(projection)
    for rb, outrb in [(ds.GetRasterBand(i+1), outds.GetRasterBand(i+1)) for i in range(ds.RasterCount)]:
        noDataValue = rb.GetNoDataValue()
        if noDataValue is not None:
            outrb.SetNoDataValue(noDataValue)
            outrb.Fill(noDataValue)

    return outds

def reproject(inds, outds, resampling):
    gdal.ReprojectImage(inds, outds, inds.GetProjectionRef(), outds.GetProjectionRef(), resampling)

def test():

    # create test data from file (this will be provided by PyFlink)
    cube, meta, projection, geotransform, noDataValue = getTestData()

    # parameters for reprojection
    outprojection = osr.SpatialReference()
    outprojection.ImportFromEPSG(3035)
    outprojection = str(outprojection) # WKT projection string
    xAnchor = 4770400.0
    yAnchor = 3149700.0
    xRes = geotransform[1]
    yRes = abs(geotransform[5])
    resampling = gdal.GRA_NearestNeighbour

    # do the warping
    ds = numpyArrayToGDALMemoryDatasource(cube, projection, geotransform, noDataValue)
    outds = initWarpedGDALMemoryDatasource(ds, xRes, yRes, xAnchor, yAnchor, outprojection)
    reproject(ds, outds, resampling)

    # grap the numpy array from the warped datasource
    outcube, outprojection, outgeotransform, outNoDataValues =  GDALDatasourceToNumpyArray(outds)

    # copy metadata
    outmeta = GDALMeta(datacource=outds)
    outmeta.copyMetadata(meta)
    outmeta.writeMetaToDatasource(outds)

    # clean up
    ds = None
    outds = None

if __name__ == '__main__':
    tic()
    test()
    toc()