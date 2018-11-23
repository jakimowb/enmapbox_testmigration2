import unittest
from unittest import TestCase
from enmapboxtesting import initQgisApplication, TestObjects
from reclassifyapp.reclassify import *
from enmapbox.gui.classification.classificationscheme import ClassificationScheme
from enmapbox.gui.utils import *
APP = initQgisApplication()

SHOW_GUI = True
class TestReclassify(TestCase):

    @classmethod
    def setUpClass(cls):
        from tempfile import mkdtemp
        cls.testDir = mkdtemp(prefix='TestDir')
        cls.classA = TestObjects.inMemoryImage(nc=3)
        cls.classB = TestObjects.inMemoryImage(nc=3)

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

        r = classification.reclassify(filename=pathDst,
                                  classDefinition=newDef,
                                  mapping={0:0,1:1,2:1})
        ds = gdal.Open(pathDst)
        band = ds.GetRasterBand(1)
        classNames = band.GetCategoryNames()
        self.assertEqual(newNames, classNames)

    def test_reclassify(self):

        csDst = ClassificationScheme.create(2)
        csDst[0].setName('Not specified')
        csDst[1].setName('Test Class')


        LUT = {0:0, 1:1, 2:1}
        classA = TestObjects.inMemoryImage()
        self.assertIsInstance(classA, gdal.Dataset)
        pathSrc = classA.GetFileList()[0]
        pathDst = '/vsimem/testresult.tif'
        print('src path: {}'.format(pathSrc))
        print('src dims (nb, nl, ns) = ({},{},{})'.format(
            classA.RasterCount, classA.RasterYSize, classA.RasterXSize))
        print('src geotransform: {}'.format(classA.GetGeoTransform()))
        print('src projection: {}'.format(classA.GetProjectionRef()))
        print('src classes: {}'.format(classA.GetRasterBand(1).GetCategoryNames()))
        print('dst path: {}'.format(pathDst))
        print('dst classes: {}'.format(csDst.classNames()))
        dsDst = reclassify(pathSrc, pathDst, csDst, LUT, drvDst='GTiff')
        csDst2 = ClassificationScheme.fromRasterImage(dsDst)
        self.assertIsInstance(csDst2, ClassificationScheme)
        self.assertEqual(csDst,csDst2 )



    def test_dialog(self):
        from reclassifyapp.reclassifydialog import ReclassifyDialog
        dialog = ReclassifyDialog()
        dialog.show()


        dialog.addSrcRaster(self.pathClassA)
        dialog.setDstRaster(os.path.join(self.testDir, 'testclass.bsq'))
        from enmapbox.gui.classification.classificationscheme import ClassificationScheme
        cs = ClassificationScheme.create(2)
        cs[1].setName('Foobar')
        dialog.setDstClassification(cs)

        settings = dialog.reclassificationSettings()
        self.assertTrue(all(k in settings.keys() for k in ['labelLookup','dstClassScheme','pathDst','pathSrc']))

        if SHOW_GUI:
            APP.exec_()
        dialog.close()

        dsDst = reclassify(drvDst='ENVI', **settings)

        self.assertIsInstance(dsDst, gdal.Dataset)
        cs2 = ClassificationScheme.fromRasterImage(dsDst)
        dsDst = None
        cs3 = ClassificationScheme.fromRasterImage(settings['pathDst'])

        self.assertIsInstance(cs2, ClassificationScheme)
        self.assertIsInstance(cs3, ClassificationScheme)
        self.assertEqual(cs, cs2, msg='Expected:\n{}\nbut got:\n{}'.format(cs.toString(), cs2.toString()))
        self.assertEqual(cs, cs3, msg='Expected:\n{}\nbut got:\n{}'.format(cs.toString(), cs3.toString()))

if __name__ == "__main__":

    SHOW_GUI = False
    unittest.main()
