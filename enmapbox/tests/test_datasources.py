# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.gui.sandbox import initQgisEnvironment
from enmapbox.gui.utils import *
QGIS_APP = initQgisEnvironment()
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *
from hubflow.types import *

class testclassData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        from enmapbox.gui.utils import DIR_REPO, jp, mkdir
        dirTmp = jp(DIR_REPO, 'tmp')
        mkdir(dirTmp)

        from enmapboxtestdata import enmap, landcover

        classes = numpy.max(Vector(filename=landcover).uniqueValues(
            attribute=''))

        classDefinition = ClassDefinition(classes=classes)

        image = Image(filename=self.getParameterValue('image'))

        vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover,
                                                    classDefinition=classDefinition,
                                                    idAttribute='Level_2_ID', minWinnerCoverage=0.5)
        gtClassification = vectorClassification.rasterizeAsClassification(
            classificationFilename=join(outdir, 'gtClassification.img'), grid=image.pixelGrid,
            oversampling=10, overwrite=overwrite)

        vectorClassification = VectorClassification(filename=landcover,
                                                    #idAttribute=,
                                                    #minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                    #minWinnerCoverage=self.getParameterValue('minWinnerCoverage'),
                                                    #classDefinition=classDefinition
                                                    )
        pathDst = jp(dirTmp, 'classification.img')
        vectorClassification.rasterizeAsClassification(classificationFilename=pathDst)


    def setUp(self):


        pass

    def tearDown(self):
        pass

    def test_hubflowtypes(self):
        p = r'D:\Repositories\QGIS_Plugins\enmap-box\tmp\classificationSample'
        ds = DataSourceFactory.Factory(p)
        self.assertIsInstance(ds, HubFlowDataSource)

        s = ""

if __name__ == "__main__":

    t = testclassData()
    t.test_hubflowtypes()

    #unittest.main()



