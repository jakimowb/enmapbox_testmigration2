from osgeo import gdal
from qgis._core import QgsCoordinateReferenceSystem, Qgis, QgsRasterLayer

import numpy as np

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.raster import RasterReader
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.testcase import TestCase
from enmapboxtestdata import enmap


class TestDriver(TestCase):

    def test_enmap(self):
        ds = gdal.Open(enmap)
        array = ds.ReadAsArray()
        layer = QgsRasterLayer(enmap)
        outraster = Driver('c:/vsimem/enmap.tif').createFromArray(array, extent=layer.extent(), crs=layer.crs())
        outraster.setNoDataValue(-99)
        outraster.setMetadataItem('a', 42)

    def test_createSinglePixel_3Band_PseudoRaster(self):
        shape = (3, 5, 5)
        array = np.array(list(range(np.product(shape)))).reshape(shape)
        array[:, 0, 0] = -1
        outraster = Driver('c:/vsimem/raster.bsq').createFromArray(array)
        outraster.setNoDataValue(1, -1)
        outraster.setMetadataItem('a', 42)
        return
        raster = RasterReader(outraster.source())

        crs: QgsCoordinateReferenceSystem = raster.crs()
        self.assertFalse(crs.isValid())
        self.assertEqual(1, raster.xSize())
        self.assertEqual(1, raster.ySize())
        self.assertEqual(3, raster.bandCount())
        self.assertArrayEqual(raster.array(), array)

    def test_createRaster_withDifferentDataTypes(self):
        for dtype in [np.uint8, np.float32, np.float64, np.int16, np.int32, np.uint16, np.uint32]:
            array = np.array([[[0]]], dtype=dtype)
            raster = Driver().createFromArray(array)
            self.assertEqual(raster.array()[0].dtype, array.dtype)

    def test_createRaster_withDifferentFormats(self):
        for format in ['ENVI', 'GTiff']:
            array = np.array([[[1]], [[2]], [[3]]])
            raster = Driver(format=format).createFromArray(array)
            lead = raster.array()
            self.assertEqual(lead[0].dtype, array.dtype)
            self.assertArrayEqual(lead, array)

    def test_createRaster_likeExistingRaster(self):
        shape = 3, 5, 6
        raster1 = Driver().createFromArray(np.zeros(shape))
        raster2 = Driver().createLike(raster1)
        self.assertEqual(raster1.extent(), raster2.extent())
        self.assertEqual(raster1.xSize(), raster2.xSize())
        self.assertEqual(raster1.ySize(), raster2.ySize())
        self.assertEqual(raster1.bandCount(), raster2.bandCount())

    def test_createRaster_likeExistingRaster_butDifferentBandCount_andDataType(self):
        shape = 3, 5, 6
        raster1 = Driver().createFromArray(np.zeros(shape))
        raster2 = Driver().createLike(raster1, nBands=1, dataType=Qgis.Byte)
        self.assertEqual(1, raster2.bandCount())
        self.assertEqual(Qgis.Byte, raster2.dataType(1))
