from __future__ import absolute_import
import tempfile, os, sys
from unittest import TestCase

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
        from enmapbox.gui.classificationscheme import ClassificationScheme
        from osgeo import gdal
        import numpy as np
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




class TestClassificationScheme(TestCase):

    @classmethod
    def setUpClass(cls):
        from tempfile import mkdtemp
        cls.testDir = mkdtemp(prefix='EnMAPBoxTests', suffix='ClassifcationScheme')
        cls.classA = TestObjects.inMemoryClassification()
        cls.classB = TestObjects.inMemoryClassification()

        s = ""

    @classmethod
    def tearDownClass(cls):
        os.removedirs(cls.testDir)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_classInfo(self):
        from enmapbox.gui.classificationscheme import ClassInfo
        from PyQt4.QtGui import QColor
        name = 'Class1'
        color = QColor('green')
        label = 2
        c = ClassInfo(name=name, color=color, label = label)
        self.assertIs(name, c.name())
        self.assertIs(label, c.label())
        self.assertIs(color.getRgb(), c.color().getRgb())
        self.assertNotIsInstance(color, c.color())

        c = ClassInfo()
        self.assertIs(c.name(), 'Unclassified')
        self.assertIs(c.getRgb(), QColor('black').getRgb())
        self.assertIs(c.label(), 0)

        sigStore = []
        def onSignal(*args):

            sigStore.append(*args)

        c.sigSettingsChanged.connect(onSignal)
        c.setLabel('Other Name')
        self.assertTrue(c in sigStore)

    def test_addClassesFromFile(self):
        pass

    def test_removeClasses(self):
        pass

    def test_writeReclassifiedImage(self):
        pass
