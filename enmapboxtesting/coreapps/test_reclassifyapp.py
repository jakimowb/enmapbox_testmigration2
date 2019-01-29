import unittest
from unittest import TestCase
from enmapbox.testing import initQgisApplication, TestObjects
import enmapboxtestdata
from reclassifyapp.reclassify import *
from enmapbox.gui import ClassificationScheme
from enmapbox.gui.utils import *
QGIS_APP = initQgisApplication()

SHOW_GUI = True

class TestReclassify(TestCase):

    @classmethod
    def setUpClass(cls):
        from tempfile import mkdtemp
        cls.testDir = mkdtemp(prefix='TestDir')
        cls.classA = TestObjects.inMemoryImage(nc=2)
        cls.classB = TestObjects.inMemoryImage(nc=5)

        cls.pathClassA = cls.classA.GetDescription()
        cls.pathClassB = cls.classB.GetDescription()
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
        import hubflow.core
        from enmapbox.testing import TestObjects
        dsSrc = TestObjects.inMemoryImage(10,20,nc=5)
        self.assertIsInstance(dsSrc, gdal.Dataset)
        classNamesOld = ['Unclassified', 'Class 1', 'Class 2', 'Class 3', 'Class 4']
        self.assertEqual(dsSrc.GetRasterBand(1).GetCategoryNames(), classNamesOld)
        pathSrc = dsSrc.GetFileList()[0]
        self.assertTrue(pathSrc.startswith('/vsimem/'))

        pathResultFiles = []
        for i, ext in enumerate(['bsq','BSQ', 'bil','BIL', 'bip','BIP', 'tif', 'TIF', 'tiff', 'TIFF', 'gtiff', 'GTIFF']):

            pathDst = r'/vsimem/testclasstiff{}.{}'.format(i, ext)

            classification = hubflow.core.Classification(pathSrc)
            oldDef = classification.classDefinition()
            self.assertEqual(oldDef.names(), classNamesOld[1:])

            newNames = ['No Class', 'Class B', 'Class D']
            newColors = [QColor('black'), QColor('yellow'), QColor('brown')]

            # this works
            c = hubflow.core.Color(QColor('black'))

            # but this does'nt
            #newDef = hubflow.core.ClassDefinition(names=newNames[1:], colors=newColors[1:])


            newDef = hubflow.core.ClassDefinition(names=newNames[1:], colors=[c.name() for c in newColors[1:]])
            newDef.setNoDataNameAndColor(newNames[0], QColor('yellow'))

            #driver = guessRasterDriver(pathDst)
            r = classification.reclassify(filename=pathDst,
                                      classDefinition=newDef,
                                      mapping={0:0,1:1,2:1})#,
                                        #outclassificationDriver=driver)


            ds = gdal.Open(pathDst)

            self.assertIsInstance(ds, gdal.Dataset)
            if re.search('\.(bsq|bil|bip)$', pathDst, re.I):
                self.assertTrue(ds.GetDriver().ShortName == 'ENVI'
                        , msg='Not opened with ENVI driver, but {}: {}'.format(ds.GetDriver().ShortName, pathDst))
            elif re.search('\.g?tiff?$', pathDst, re.I):
                self.assertTrue(ds.GetDriver().ShortName == 'GTiff'
                        , msg='Not opened with GTiff driver, but {}: {}'.format(ds.GetDriver().ShortName, pathDst))
            elif re.search('\.vrt$', pathDst, re.I):
                self.assertTrue(ds.GetDriver().ShortName == 'VRT'
                        , msg='Not opened with VRT driver, but {}: {}'.format(ds.GetDriver().ShortName, pathDst))
            else:
                self.fail('Unknown extension {}'.format(pathDst))
            pathResultFiles.append(pathDst)

        for pathDst in pathResultFiles:
            ds = gdal.Open(pathDst)
            band = ds.GetRasterBand(1)
            self.assertIsInstance(band.GetCategoryNames(), list, msg='Failed to set category names to "{}"'.format(pathDst))
            self.assertEqual(newNames, band.GetCategoryNames(), msg='Failed to set all category names to "{}"'.format(pathDst))

    def test_hubflowrasterdriverguess(self):



        self.assertIsInstance(guessRasterDriver('foo.bsq'), hubflow.core.ENVIBSQDriver)
        self.assertIsInstance(guessRasterDriver('foo.bip'), hubflow.core.ENVIBIPDriver)
        self.assertIsInstance(guessRasterDriver('foo.bil'), hubflow.core.ENVIBILDriver)
        self.assertIsInstance(guessRasterDriver('foo.vrt'), hubflow.core.VRTDriver)
        self.assertIsInstance(guessRasterDriver('foo.tif'), hubflow.core.GTiffDriver)
        self.assertIsInstance(guessRasterDriver('foo.tiff'), hubflow.core.GTiffDriver)
        self.assertIsInstance(guessRasterDriver('foo.gtiff'), hubflow.core.GTiffDriver)



    def test_reclassify(self):

        csDst = ClassificationScheme.create(2)
        csDst[0].setName('Not specified')
        csDst[1].setName('Test Class')


        LUT = {0:0, 1:1, 2:1}
        classA = TestObjects.inMemoryImage()
        self.assertIsInstance(classA, gdal.Dataset)
        pathSrc = classA.GetFileList()[0]
        pathDst = '/vsimem/testresult.bsq'
        print('src path: {}'.format(pathSrc))
        print('src dims (nb, nl, ns) = ({},{},{})'.format(
            classA.RasterCount, classA.RasterYSize, classA.RasterXSize))
        print('src geotransform: {}'.format(classA.GetGeoTransform()))
        print('src projection: {}'.format(classA.GetProjectionRef()))
        print('src classes: {}'.format(classA.GetRasterBand(1).GetCategoryNames()))
        print('dst path: {}'.format(pathDst))
        print('dst classes: {}'.format(csDst.classNames()))
        dsDst = reclassify(pathSrc, pathDst, csDst, LUT, drvDst='ENVI')
        csDst2 = ClassificationScheme.fromRasterImage(dsDst)
        self.assertIsInstance(csDst2, ClassificationScheme)
        self.assertEqual(csDst,csDst2 )



    def test_dialog(self):
        from reclassifyapp.reclassifydialog import ReclassifyDialog
        dialog = ReclassifyDialog()
        self.assertIsInstance(dialog, ReclassifyDialog)


        self.assertIs(dialog.srcRaster(), None)
        self.assertListEqual(dialog.knownRasterSources(), [])

        dialog.setSrcRaster(self.pathClassA)
        self.assertListEqual(dialog.knownRasterSources(), [self.pathClassA])
        self.assertEqual(dialog.srcRaster(), self.pathClassA)
        dialog.setSrcRaster(self.pathClassB)
        self.assertEqual(dialog.srcRaster(), self.pathClassB)
        dialog.setSrcRaster(self.pathClassA)
        self.assertEqual(dialog.srcRaster(), self.pathClassA)



        dialog.setDstRaster(os.path.join(self.testDir, 'testclass.bsq'))
        dstCS = ClassificationScheme.create(2)
        dstCS[1].setName('Foobar')
        dialog.setDstClassificationScheme(dstCS)
        self.assertEqual(dstCS, dialog.dstClassificationScheme())

        settings = dialog.reclassificationSettings()
        for key in ['labelLookup','dstClassScheme','pathDst','pathSrc']:
            self.assertTrue(key in settings.keys(), msg='Missing setting key "{}"'.format(key))

        if SHOW_GUI:
            dialog.show()
            QGIS_APP.exec_()

        dstCS = dialog.dstClassificationScheme()
        dialog.close()

        dsDst = reclassify(drvDst='ENVI', **settings)

        self.assertIsInstance(dsDst, gdal.Dataset)
        cs2 = ClassificationScheme.fromRasterImage(dsDst)
        dsDst = None
        cs3 = ClassificationScheme.fromRasterImage(settings['pathDst'])

        self.assertIsInstance(cs2, ClassificationScheme)
        self.assertIsInstance(cs3, ClassificationScheme)
        self.assertEqual(cs2, cs3)
        self.assertEqual(dstCS, cs2, msg='Expected:\n{}\nbut got:\n{}'.format(dstCS.toString(), cs2.toString()))
        self.assertEqual(dstCS, cs3, msg='Expected:\n{}\nbut got:\n{}'.format(dstCS.toString(), cs3.toString()))

if __name__ == "__main__":

    SHOW_GUI = False
    unittest.main()