import unittest
from unittest import TestCase
from enmapbox.gui.utils import *
APP = initQgisApplication()

class BugTests(TestCase):

    def test_loadsynthmix(self):

        exception = None
        try:
            from enmapboxapplications.synthmixapp.core import SynthmixApp
        except Exception as ex:
            exception = ex
        self.assertTrue(exception == None, msg='import raised:\n{}'.format(exception))

    def test_enmapboxcoreapps(self):

        from enmapbox import EnMAPBox, EnMAPBoxApplication

        enmapBox = EnMAPBox(None)
        self.assertIsInstance(enmapBox, EnMAPBox)

        from reclassifyapp import enmapboxApplicationFactory as factory1
        apps = factory1(enmapBox)
        self.assertIsInstance(apps, list)
        for app in apps:
            self.assertIsInstance(app, EnMAPBoxApplication)


        from enmapbox.coreapps.reclassifyapp import enmapboxApplicationFactory as factory2
        apps = factory2(enmapBox) #this fails
        self.assertIsInstance(apps, list)
        self.assertTrue(len(apps) > 0)
        for app in apps:
            self.assertIsInstance(app, EnMAPBoxApplication)


    def test_hubflowcoreClassDefinition(self):
        import hubflow.core
        names = ['Foo','Bar']
        classes = hubflow.core.ClassDefinition(names=names)

        self.assertTrue(classes.name(0) in [None, 'Unclassified', 'unclassified'])
        for i, name in enumerate(names):
            self.assertTrue(name == classes.name(i+1))


    def test_reclassify_issue203(self):
        #see https://bitbucket.org/hu-geomatics/enmap-box/issues/203/hubflow-reclassify-unclassified-class-name
        import hubflow.core
        classA = TestObjects.inMemoryImage()
        self.assertIsInstance(classA, gdal.Dataset)
        print('old names: {}'.format(classA.GetRasterBand(1).GetCategoryNames()))
        pathSrc = classA.GetFileList()[0]
        pathDst = '/vsimem/testoutput.tif'
        classification = hubflow.core.Classification(pathSrc)
        newNames = ['Not specified', 'Class X']
        lookup = {0:0,1:1,2:1}
        # do not add the unclassified class
        newDef = hubflow.core.ClassDefinition(names=newNames)
        print(newDef)
        classification.reclassify(filename=pathDst,
                                  classDefinition=newDef,
                                  mapping=lookup)

        dsNew = gdal.Open(pathDst)
        self.assertIsInstance(dsNew, gdal.Dataset)
        writtenNames = dsNew.GetRasterBand(1).GetCategoryNames()
        self.assertIsInstance(writtenNames, list)
        self.assertListEqual(writtenNames, newNames, msg='Names not equal: \nshould be:{}\nwritten: {}'.format(newNames, writtenNames))

if __name__ == "__main__":

    unittest.main()
