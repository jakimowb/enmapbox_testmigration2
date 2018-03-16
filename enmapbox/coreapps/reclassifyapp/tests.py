
import os, re, io, tempfile

from osgeo import gdal
import numpy as np
from unittest import TestCase
from reclassifyapp.reclassify import *
from enmapbox.gui.classificationscheme import ClassificationScheme



class TestReclassify(TestCase):

    @classmethod
    def setUpClass(cls):
        from enmapbox.gui.utils import initQgisApplication
        from enmapbox.gui.utils import TestObjects
        from tempfile import mkdtemp
        cls.testDir = mkdtemp(prefix='TestDir')
        cls.classA = TestObjects.inMemoryClassification(3)
        cls.classB = TestObjects.inMemoryClassification(3)

        cls.pathClassA = os.path.join(cls.testDir, 'classificationA.bsq')
        #cls.pathClassB = os.path.join(cls.testDir, 'classificationB.bsq')
        drv = gdal.GetDriverByName('ENVI')
        drv.CreateCopy(cls.pathClassA, cls.classA)
        #drv.CreateCopy(cls.pathClassB, cls.classB)

        cls.qgsApp = initQgisEnvironment()

    @classmethod
    def tearDownClass(cls):
        cls.classA = None
        cls.classB = None
        #todo: remove temp files
        #if os.path.exists(cls.testDir):
        #    os.remove(cls.testDir)


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reclassify(self):
        csDst = ClassificationScheme.create(2)
        csDst[1].setName('Test Class')

        dsSrc = self.classA
        csSrc = ClassificationScheme.fromRasterImage(dsSrc)
        LUT = {0:0, 1:1, 2:1}

        dsDst = reclassify(dsSrc, '', LUT, drvDst='MEM', dstClassScheme=csDst)
        csDst2 = ClassificationScheme.fromRasterImage(dsDst)
        self.assertIsInstance(csDst2, ClassificationScheme)
        self.assertEqual(csDst,csDst2 )

    def test_dialog(self):
        from reclassifyapp.reclassifydialog import ReclassifyDialog
        ui1 = ReclassifyDialog()
        ui1.show()

        from enmapbox.testdata.UrbanGradient import EnMAP
        ui1.addSrcRaster(self.pathClassA)
        ui1.setDstRaster(os.path.join(self.testDir, 'testclass.bsq'))
        from enmapbox.gui.classificationscheme import ClassificationScheme
        cs = ClassificationScheme.create(2)
        cs[1].setName('Foobar')
        ui1.setDstClassification(cs)

        settings = ui1.reclassificationSettings()
        self.assertTrue(all(k in settings.keys() for k in ['labelLookup','dstClassScheme','pathDst','pathSrc']))
        ui1.close()
        dsDst = reclassify(drvDst='ENVI', **settings)

        self.assertIsInstance(dsDst, gdal.Dataset)
        cs2 = ClassificationScheme.fromRasterImage(dsDst)
        dsDst = None
        cs3 = ClassificationScheme.fromRasterImage(settings['pathDst'])

        self.assertEqual(cs, cs2)
        self.assertEqual(cs, cs3)

