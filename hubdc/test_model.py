from __future__ import print_function
from tempfile import gettempdir
from os.path import join, exists, basename, dirname
import numpy
from unittest import TestCase

from hubdc.model import *
from hubdc.testdata import LT51940232010189KIS01, LT51940242010189KIS01, BrandenburgDistricts, root

outdir = join(gettempdir(), 'hubdc_test')
raster = openRaster(LT51940232010189KIS01.cfmask)
vector = openVector(filename=BrandenburgDistricts.shp)
grid = openRaster(LT51940232010189KIS01.cfmask).grid()


class Test(TestCase):
    def test_Open(self):
        self.assertIsInstance(obj=openRaster(filename=LT51940232010189KIS01.cfmask), cls=Raster)
        self.assertRaises(excClass=errors.FileNotExistError, callableObj=openRaster, filename='not a valid file')
        self.assertRaises(excClass=errors.InvalidGDALDatasetError, callableObj=openRaster,
                          filename=LT51940232010189KIS01.root)

    def test_OpenLayer(self):
        self.assertIsInstance(obj=openVector(filename=BrandenburgDistricts.shp), cls=Vector)
        self.assertRaises(excClass=errors.FileNotExistError, callableObj=openRaster, filename='not a valid file')
        self.assertRaises(excClass=errors.InvalidOGRDataSourceError, callableObj=openVector,
                          filename=LT51940232010189KIS01.root)

    def test_Create(self):
        self.assertIsInstance(obj=createRaster(grid=grid), cls=Raster)

    def test_repr(self):
        print(RasterCreationOptions(options={'INTERLEAVE': 'BAND'}))
        print(RasterDriver(name='MEM'))
        print(MEMDriver())
        print(ENVIBSQDriver())
        print(ENVIBIPDriver())
        print(ENVIBILDriver())
        print(ErdasDriver())
        print(GTiffDriver())
        print(grid.extent())
        print(Resolution(x=30, y=30))
        print(Projection.WGS84())
        print(Projection.WGS84WebMercator())
        print(Projection.UTM(zone=33))
        print(Projection.UTM(zone=33, north=False))
        print(Pixel(x=0, y=0))
        print(grid.extent().geometry())
        print(grid.spatialExtent().geometry())
        print(Point(x=0, y=0))
        print(SpatialPoint(x=0, y=0, projection=Projection.WGS84()))
        print(Size(x=10, y=20))
        print(grid)
        print(raster)
        print(raster.band(index=0))
        print(vector)


class TestDriver(TestCase):
    def test_Driver(self):
        self.assertIsInstance(obj=RasterDriver(name='ENVI').gdalDriver(), cls=gdal.Driver)
        self.assertRaises(excClass=errors.InvalidGDALDriverError, callableObj=RasterDriver,
                          name='not a valid driver name')

    def test_equal(self):
        d1 = ENVIBSQDriver()
        d2 = GTiffDriver()
        d3 = RasterDriver('ENVI')
        self.assertTrue(d1.equal(d3))
        self.assertFalse(d1.equal(d2))

    def test_create(self):
        self.assertIsInstance(obj=RasterDriver('MEM').create(grid=grid), cls=Raster)


class TestRasterBand(TestCase):
    def test_readAsArray(self):
        ds = openRaster(LT51940232010189KIS01.cfmask)
        band = ds.band(0)
        self.assertIsInstance(obj=band, cls=RasterBand)
        self.assertIsInstance(obj=band.readAsArray(), cls=numpy.ndarray)
        self.assertIsInstance(
            obj=band.readAsArray(grid=ds.grid().subset(offset=Pixel(x=0, y=0), size=Size(x=10, y=10), trim=True)),
            cls=numpy.ndarray)
        self.assertRaises(excClass=errors.AccessGridOutOfRangeError, callableObj=band.readAsArray,
                          grid=ds.grid().subset(offset=Pixel(x=-1, y=-1), size=Size(x=10, y=10)))
        self.assertRaises(excClass=errors.AccessGridOutOfRangeError, callableObj=band.readAsArray,
                          grid=ds.grid().subset(offset=Pixel(x=-10, y=-10), size=Size(x=10, y=10)))
        a = band.readAsArray()
        b = band.readAsArray(grid=ds.grid().subset(offset=Pixel(x=0, y=0), size=ds.grid().size()))
        self.assertTrue(numpy.all(a == b))

    def test_writeArray(self):
        ds = createRaster(grid=grid)
        band = ds.band(index=0)
        array2d = numpy.full(shape=grid.shape(), fill_value=42)
        array3d = numpy.full(shape=grid.shape(), fill_value=42)
        band.writeArray(array=array2d)
        band.writeArray(array=array3d)
        band.writeArray(array=array3d, grid=grid)
        self.assertRaises(excClass=errors.ArrayShapeMismatchError, callableObj=band.writeArray, array=array2d[:10, :10])
        band.writeArray(array=array2d[:10, :10], grid=grid.subset(offset=Pixel(x=0, y=0), size=Size(x=10, y=10)))
        band.writeArray(array=array2d[:10, :10], grid=grid.subset(offset=Pixel(x=-5, y=-5), size=Size(x=10, y=10)))
        band.writeArray(array=array2d[:10, :10], grid=grid.subset(offset=Pixel(x=0, y=0), size=Size(x=10, y=10)))
        band.writeArray(array=array2d[:10, :10][None], grid=grid.subset(offset=Pixel(x=0, y=0), size=Size(x=10, y=10)))

        self.assertRaises(excClass=errors.AccessGridOutOfRangeError, callableObj=band.writeArray, array=array2d,
                          grid=grid.subset(offset=Pixel(x=10, y=10), size=grid.size()))

    def test_setMetadataItem(self):
        ds = createRaster(grid=grid)
        band = ds.band(index=0)
        band.setMetadataItem(key='my key', value=42, domain='ENVI')
        self.assertEqual(band.metadataItem(key='my key', domain='ENVI', dtype=int), 42)

    def test_metadataItem(self):
        self.test_setMetadataItem()

    def test_copyMetadata(self):
        ds = createRaster(grid=grid)
        ds2 = createRaster(grid=grid)
        band = ds.band(index=0)
        band2 = ds2.band(index=0)
        band.setMetadataItem(key='my key', value=42, domain='ENVI')
        band2.copyMetadata(other=band)
        self.assertEqual(band2.metadataItem(key='my key', domain='ENVI', dtype=int), 42)

    def test_setNoDataValue(self):
        ds = createRaster(grid=grid)
        band = ds.band(index=0)
        self.assertEqual(band.noDataValue(default=123), 123)
        band.setNoDataValue(value=42)
        self.assertEqual(band.noDataValue(default=123), 42)

    def test_noDataValue(self):
        self.test_setNoDataValue()

    def test_setDescription(self):
        ds = createRaster(grid=grid)
        band = ds.band(index=0)
        band.setDescription(value='Hello')
        self.assertEqual(band.description(), 'Hello')

    def test_description(self):
        self.test_setDescription()

    def test_metadataDomainList(self):
        ds = createRaster(grid=grid)
        band = ds.band(index=0)
        band.setMetadataItem(key='my key', value=42, domain='ENVI')
        band.setMetadataItem(key='my key', value=42, domain='xyz')
        gold = {'ENVI', 'xyz'}
        lead = set(band.metadataDomainList())
        self.assertSetEqual(gold, lead)

    def test_fill(self):
        ds = createRaster(grid=grid)
        band = ds.band(index=0)
        band.fill(value=42)
        array = band.readAsArray()
        self.assertTrue(numpy.all(array == 42))


class TestRaster(TestCase):
    def test(self):
        self.assertIsInstance(obj=raster.grid(), cls=Grid)
        for band in raster.bands():
            self.assertIsInstance(obj=band, cls=RasterBand)
        self.assertIsInstance(raster.driver(), RasterDriver)
        self.assertIsInstance(raster.readAsArray(), np.ndarray)
        self.assertIsInstance(raster.readAsArray(grid=grid), np.ndarray)

        raster2 = createRasterFromArray(grid=grid, array=np.ones(shape=grid.shape()))
        #        raster2 = createRasterFromArray(grid=grid, array=np.ones(shape=grid.shape()[1:]))
        raster2 = createRasterFromArray(grid=grid, array=[np.ones(shape=grid.shape(), dtype=np.bool)])
        raster2.setNoDataValue(value=-9999)
        raster2.noDataValue()
        raster2.setDescription(value='Hello')
        raster2.description()
        raster2.copyMetadata(other=raster)
        raster2.setMetadataItem(key='a', value=42, domain='my domain')
        raster2.setMetadataItem(key='b', value=[1, 2, 3], domain='my domain')
        raster2.metadataItem(key='a', domain='my domain')
        raster2.metadataItem(key='b', domain='my domain')
        raster2.setMetadataDict(metadataDict=raster2.metadataDict())
        import datetime
        raster2.setAcquisitionTime(acquisitionTime=datetime.datetime(2010, 12, 31))
        print(raster2.acquisitionTime())

        raster2.warp(grid=raster2.grid())
        raster2.translate(grid=raster2.grid())
        grid2 = Grid(extent=grid.spatialExtent(), resolution=Resolution(x=400, y=400))
        raster2.translate(grid=grid2)
        raster2.array()
        grid2 = Grid(extent=grid.spatialExtent().reproject(targetProjection=Projection.UTM(zone=33)),
                     resolution=grid.resolution())
        raster2.array(grid=grid2)
        raster2.dtype()
        raster2.flushCache()
        raster2.close()

        raster2 = createRasterFromArray(grid=grid, array=[np.ones(shape=grid.shape(), dtype=np.bool)],
                                        filename=join(outdir, 'zeros.tif'), driver=GTiffDriver())
        raster2.writeENVIHeader()
        raster2 = createRasterFromArray(grid=grid, array=[np.ones(shape=grid.shape(), dtype=np.bool)],
                                        filename=join(outdir, 'zeros.img'), driver=ENVIBSQDriver())
        raster2.writeENVIHeader()

    def test_createVRT(self):
        createVRT(filename=join(outdir, 'stack1.vrt'), rastersOrFilenames=[raster, raster])
        createVRT(filename=join(outdir, 'stack2.vrt'), rastersOrFilenames=[LT51940232010189KIS01.cfmask] * 2)

    def test_buildOverviews(self):
        buildOverviews(filename=join(outdir, 'stack1.vrt'), minsize=128)


class TestVector(TestCase):
    def test(self):
        gridSameProjection = Grid(extent=vector.spatialExtent(), resolution=Resolution(x=1, y=1))
        vector.rasterize(grid=grid)
        vector.rasterize(grid=gridSameProjection, noDataValue=-9999)
        vector.featureCount()
        vector.fieldCount()
        vector.fieldNames()
        vector.fieldTypeNames()


class TestExtent(TestCase):
    def test(self):
        extent = grid.extent()
        Extent.fromGeometry(geometry=extent.geometry())
        extent.upperLeft()
        extent.upperRight()
        extent.lowerLeft()
        extent.lowerRight()


class TestSpatialExtent(TestCase):
    def test(self):
        spatialExtent = grid.spatialExtent()
        spatialExtent.upperLeft()
        spatialExtent.upperRight()
        spatialExtent.lowerLeft()
        spatialExtent.lowerRight()
        spatialExtent.reproject(targetProjection=Projection.WGS84(), sourceProjection=spatialExtent.projection())
        spatialExtent.intersects(other=spatialExtent)
        spatialExtent.intersection(other=spatialExtent)
        spatialExtent.union(other=spatialExtent)


class TestSpatialGeometry(TestCase):
    def test(self):
        spatialGeometry = grid.spatialExtent().geometry()
        spatialGeometry.intersection(other=spatialGeometry)
        spatialGeometry.within(other=spatialGeometry)
        SpatialGeometry.fromVector(vector=openVector(filename=BrandenburgDistricts.shp))


class TestResolution(TestCase):
    def test_Resolution(self):
        resolution = Resolution(x=30, y=30)
        self.assertTrue(resolution.equal(other=Resolution(x=30, y=30)))
        self.assertFalse(resolution.equal(other=Resolution(x=10, y=10)))


class TestGrid(TestCase):
    def test(self):
        Grid(extent=grid.spatialExtent(), resolution=grid.resolution())
        grid.equal(other=grid)
        grid.reproject(other=grid)
        grid.pixelBuffer(buffer=1)
        grid.subgrids(size=Size(x=256, y=256))

    def test_coordinates(self):
        grid = Grid(extent=Extent(xmin=0, xmax=3, ymin=0, ymax=2), resolution=Resolution(x=1, y=1),
                    projection=Projection.WGS84())
        xgold = np.array([[0.5, 1.5, 2.5], [0.5, 1.5, 2.5]])
        ygold = np.array([[1.5, 1.5, 1.5], [0.5, 0.5, 0.5]])
        self.assertTrue(np.all(grid.xMapCoordinatesArray() == xgold))
        self.assertTrue(np.all(grid.yMapCoordinatesArray() == ygold))

        xgold = np.array([[0, 1, 2], [0, 1, 2]])
        ygold = np.array([[0, 0, 0], [1, 1, 1]])

        self.assertTrue(np.all(grid.xPixelCoordinatesArray() == xgold))
        self.assertTrue(np.all(grid.yPixelCoordinatesArray() == ygold))

        subgrid = grid.subset(offset=Pixel(x=1, y=1), size=Size(x=2, y=1))
        subxgold = xgold[1:, 1:]
        subygold = ygold[1:, 1:]

        print(subgrid.xPixelCoordinatesArray())
        print(subgrid.yPixelCoordinatesArray())

        self.assertTrue(np.all(np.equal(subgrid.xPixelCoordinatesArray(offset=1), subxgold)))
        self.assertTrue(np.all(np.equal(subgrid.yPixelCoordinatesArray(offset=1), subygold)))


class TestSpatialPoint(TestCase):
    def test(self):
        wgs84 = Projection.WGS84()
        p = SpatialPoint(x=0, y=0, projection=wgs84)
        self.assertIsInstance(p.geometry(), Geometry)
        self.assertIsInstance(p.reproject(sourceProjection=wgs84, targetProjection=wgs84), Point)
        self.assertIsInstance(p.geometry(), SpatialGeometry)
        self.assertFalse(p.withinExtent(extent=grid.spatialExtent()))


def test_deriveDriverFromFileExtension():
    for ext in ['bsq', 'bip', 'bil', 'tif', 'img']:
        filename = join(outdir, 'file.' + ext)
        driver = RasterDriver.fromFilename(filename=filename)
        print(driver)

    try:
        RasterDriver.fromFilename(filename='file.xyz')
    except AssertionError as error:
        print(str(error))

    for ext in ['shp', 'gpkg']:
        filename = join(outdir, 'file.' + ext)
        driver = VectorDriver.fromFilename(filename=filename)
        print(driver)

    try:
        VectorDriver.fromFilename(filename='file.xyz')
    except AssertionError as error:
        print(str(error))

