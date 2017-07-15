from __future__ import absolute_import
import os, re, io, tempfile

from osgeo import gdal

from unittest import TestCase
from enmapbox.gui.sandbox import initQgisEnvironment
qgsApp = initQgisEnvironment()
from reclassifyapp.reclassify import *

from enmapbox.gui.classificationscheme import ClassificationScheme

class TestObjects():

    TEST_DIR = None
    @staticmethod
    def testDir():
        if TestObjects.TEST_DIR is None:
            TestObjects.TEST_DIR = tempfile.mkdtemp(prefix='EnMAPBoxTests', suffix='reclassifyapp')
        else:
            return TestObjects.TEST_DIR

    @staticmethod
    def inMemoryClassification(n=3, nl=10, ns=20, nb=1):
        scheme = ClassificationScheme()
        scheme.createClasses(n)

        drv = gdal.GetDriverByName('MEM')
        assert isinstance(drv, gdal.Driver)

        ds = drv.Create('', ns, nl, bands=nb, eType=gdal.GDT_Byte)

        assert isinstance(ds, gdal.Dataset)
        for b in range(1,nb+1):
            band = ds.GetRasterBand(b)
            array = np.zeros((nl, ns), dtype=np.uint8)-1
            array[0,0] = 0
            array[-1,-1] = n-1
            x = np.arange(0, array.shape[1])
            y = np.arange(0, array.shape[0])
            # mask invalid values
            array = np.ma.masked_invalid(array)
            xx, yy = np.meshgrid(x, y)
            # get only the valid values
            x1 = xx[~array.mask]
            y1 = yy[~array.mask]
            newarr = array[~array.mask]
            from scipy import interpolate
            GD1 = interpolate.griddata((x1, y1), newarr.ravel(),
                                       (xx, yy), method='linear')
            assert isinstance(band, gdal.Band)
            band.SetCategoryNames(scheme.classNames())
            band.SetColorTable(scheme.gdalColorTable())

        return ds




class TestReclassify(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testDir = ''
        cls.classA = TestObjects.inMemoryClassification()
        cls.classB = TestObjects.inMemoryClassification()



    @classmethod
    def tearDownClass(cls):
        cls.classA = None
        cls.classB = None
        os.remove(cls.testDir)


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_addClassesFromFile(self):
        pass

    def test_removeClasses(self):
        pass

    def test_writeReclassifiedImage(self):
        pass
