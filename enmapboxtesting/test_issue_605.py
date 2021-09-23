# -*- coding: utf-8 -*-
"""
***************************************************************************
    test_issue_605
    ---------------------
    Date                 :
    Copyright            : (C) 2021 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming


import unittest
import xmlrunner
from qgis.core import QgsProject, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, \
    QgsLayerTree, QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterDefinition
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QResource
from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.gui.enmapboxgui import EnMAPBox, EnMAPBoxSplashScreen
from enmapbox.gui.docks import *
from enmapbox.gui.mapcanvas import *
from enmapbox.gui import *

class TestIssue(EnMAPBoxTestCase):

    def tearDown(self):

        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox):
            emb.close()

        assert EnMAPBox.instance() is None

        QgsProject.instance().removeAllMapLayers()

        super().tearDown()

    def test_instance_pure(self):
        EMB = EnMAPBox(load_other_apps=False, load_core_apps=False)

        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(EMB, EnMAPBox.instance())

        self.showGui([qgis.utils.iface.mainWindow(), EMB.ui])

    def test_issue_605(self):
        """
        see https://bitbucket.org/hu-geomatics/enmap-box/issues/605
        """
        EMB = EnMAPBox(load_core_apps=False, load_other_apps=False)
        import os
        os.environ.setdefault('DEBUG', 'True')
        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)
        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(EMB, EnMAPBox.instance())

        #
        if False:
            EMB.loadExampleData()
        else:
            import enmapboxtestdata
            #sources = [enmapboxtestdata.enmap,
            #           enmapboxtestdata.landcover_polygons,
            #           enmapboxtestdata.landcover_points,
            #           enmapboxtestdata.library,
            #           re.sub(r'\.sli$', '.gpkg', enmapboxtestdata.library),
            #           enmapboxtestdata.enmap_srf_library
            #           ]

            sources = [TestObjects.createVectorLayer(),
                       TestObjects.createVectorLayer(),
                       TestObjects.createVectorLayer(),
                       TestObjects.createVectorLayer(),
                       # TestObjects.createVectorLayer()
                       ]
            sources = [TestObjects.createRasterLayer(),
                       TestObjects.createRasterLayer(),
                       TestObjects.createRasterLayer(),
                       TestObjects.createRasterLayer(),
                       # TestObjects.createVectorLayer()
                       ]

            dSources = EMB.addSources(sources)

        EMB.ui.show()

        for i, s in enumerate(EMB.dataSources()):
            print(f'{i + 1}: {s}')

        print('Remove all datasources:')
        EMB.dataSourceTreeView().onRemoveAllDataSources()
        print('All datasources removed')
        self.assertTrue(len(EMB.dataSources()) == 0)
        # import qgis.utils
        # QgsProject.instance()
        # qgis.utils.iface.actionSaveProject().trigger()
        # qgis.utils.iface.mainWindow()
        # self.showGui([EMB.ui])

    def test_treeModel(self):
        from enmapbox.externals.qps.models import TreeView, TreeModel, TreeNode

        model = TreeModel()

        view = TreeView()
        view.setModel(model)

        gn = TreeNode()
        model.rootNode().appendChildNodes(gn)

        subnodes = list()
        for i in range(10):
            node = TreeNode()
            gn.appendChildNodes(node)
            subnodes.append(node)

        view.show()

        for n in subnodes:
            gn.removeChildNodes(n)

        #self.showGui(view)
if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
