
import os, re, io, tempfile

from osgeo import gdal
import numpy as np
import unittest
from unittest import TestCase
from reclassifyapp.reclassify import *
from enmapbox.gui.classificationscheme import ClassificationScheme
from enmapbox.gui.utils import *
APP = initQgisApplication()
from enmapbox.gui.utils import initQgisApplication

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
        cls.pathClassTemp = os.path.join(cls.testDir, 'classificationTemp.bsq')
        drv = gdal.GetDriverByName('ENVI')
        drv.CreateCopy(cls.pathClassA, cls.classA)
        #drv.CreateCopy(cls.pathClassB, cls.classB)

        cls.qgsApp = initQgisApplication()

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

    def test_hubflow_reclassify(self):
        pathSrc = self.pathClassA
        pathDst = self.pathClassTemp

        import hubflow.core
        classification = hubflow.core.Classification(pathSrc)
        # do not add the unclassified class
        newNames = ['No Class', 'Class B']
        newDef = hubflow.core.ClassDefinition(names=newNames)

        classification.reclassify(filename=pathDst,
                                  classDefinition=newDef,
                                  mapping={0:0,1:1,2:1})
        ds = gdal.Open(pathDst)
        band = ds.GetRasterBand(1)
        classNames = band.GetCategoryNames()
        self.assertEqual(newNames, classNames)

    def test_reclassify(self):
        csDst = ClassificationScheme.create(2)
        csDst[1].setName('Test Class')

        dsSrc = self.classA
        csSrc = ClassificationScheme.fromRasterImage(dsSrc)
        LUT = {0:0, 1:1, 2:1}

        dsDst = reclassify(dsSrc, '', csDst, LUT, drvDst='MEM')
        csDst2 = ClassificationScheme.fromRasterImage(dsDst)
        self.assertIsInstance(csDst2, ClassificationScheme)
        self.assertEqual(csDst,csDst2 )



    def test_dialog(self):
        from reclassifyapp.reclassifydialog import ReclassifyDialog
        ui1 = ReclassifyDialog()
        ui1.show()


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

if __name__ == "__main__":

    unittest.main()
