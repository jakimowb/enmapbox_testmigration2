import unittest
from unittest import TestCase
from enmapbox.gui.utils import *
APP = initQgisApplication()

class BugTests(TestCase):


    def test_reclassify_issue203(self):
        #see https://bitbucket.org/hu-geomatics/enmap-box/issues/203/hubflow-reclassify-unclassified-class-name
        import hubflow
        import hubflow.core
        classA = TestObjects.inMemoryClassification()
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
