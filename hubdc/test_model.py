from __future__ import print_function
from tempfile import gettempdir
from os.path import join, exists, basename, dirname
import numpy
from unittest import TestCase

from hubdc.model import *
from hubdc.testdata import LT51940232010189KIS01, LT51940242010189KIS01, BrandenburgDistricts, root

outdir = join(gettempdir(), 'hubdc_test')
ds = openRaster(LT51940232010189KIS01.cfmask)
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


class TestDriver(TestCase):
    def test_Driver(self):
        self.assertIsInstance(obj=Driver(name='ENVI').gdalDriver(), cls=gdal.Driver)
        self.assertRaises(excClass=errors.InvalidGDALDriverError, callableObj=Driver, name='not a valid driver name')

    def test_equal(self):
        d1 = Driver('ENVI')
        d2 = Driver('GTiff')
        d3 = Driver('ENVI')
        self.assertTrue(d1.equal(d3))
        self.assertFalse(d1.equal(d2))

    def test_create(self):
        self.assertIsInstance(obj=Driver('MEM').create(grid=grid), cls=Raster)


class TestBand(TestCase):
    def test_readAsArray(self):
        ds = openRaster(LT51940232010189KIS01.cfmask)
        band = ds.band(0)
        self.assertIsInstance(obj=band, cls=Band)
        self.assertIsInstance(obj=band.readAsArray(), cls=numpy.ndarray)
        self.assertIsInstance(
            obj=band.readAsArray(grid=ds.grid().subset(offset=Pixel(x=0, y=0), size=Size(x=10, y=10))),
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


class TestDataset(TestCase):
    def test_projection(self):
        self.assertIsInstance(obj=ds.projection(), cls=Projection)

    def test_resolution(self):
        self.assertIsInstance(obj=ds.resolution(), cls=Resolution)

    def test_extent(self):
        self.assertIsInstance(obj=ds.extent(), cls=Extent)

    def test_grid(self):
        self.assertIsInstance(obj=ds.grid(), cls=Grid)

    def test_spatialExtent(self):
        self.assertIsInstance(obj=ds.spatialExtent(), cls=SpatialExtent)

    def test_bands(self):
        for band in ds.bands():
            self.assertIsInstance(obj=band, cls=Band)


'''
    def test_getFormat(self):
        self.fail()

    def test_readAsArray(self):
        self.fail()

    def test_writeArray(self):
        self.fail()

    def test_flushCache(self):
        self.fail()

    def test_close(self):
        self.fail()

    def test_getBand(self):
        self.fail()

    def test_setNoDataValues(self):
        self.fail()

    def test_getNoDataValues(self):
        self.fail()

    def test_setNoDataValue(self):
        self.fail()

    def test_getNoDataValue(self):
        self.fail()

    def test_setDescription(self):
        self.fail()

    def test_getDescription(self):
        self.fail()

    def test_getMetadataDomainList(self):
        self.fail()

    def test_setMetadataItem(self):
        self.fail()

    def test_getMetadataItem(self):
        self.fail()

    def test_getMetadataDict(self):
        self.fail()

    def test_setMetadataDict(self):
        self.fail()

    def test_getMetadataDomain(self):
        self.fail()

    def test_copyMetadata(self):
        self.fail()

    def test_setENVIAcquisitionTime(self):
        self.fail()

    def test_writeENVIHeader(self):
        self.fail()

    def test_warp(self):
        self.fail()

    def test_warpOptions(self):
        self.fail()

    def test_translate(self):
        self.fail()

    def test_xsize(self):
        self.fail()

    def test_ysize(self):
        self.fail()

    def test_zsize(self):
        self.fail()

    def test_shape(self):
        self.fail()
'''
