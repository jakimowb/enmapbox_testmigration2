        # -*- coding: utf-8 -*-
"""
/***************************************************************************
                              EO Time Series Viewer
                              -------------------
        begin                : 2015-08-20
        git sha              : $Format:%H$
        copyright            : (C) 2017 by HU-Berlin
        email                : benjamin.jakimow@geo.hu-berlin.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# noinspection PyPep8Naming

import os, sys, re, io, importlib, uuid, warnings
import sip
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from .externals.qps.testing import TestObjects, WFS_Berlin, WMS_GMAPS, WMS_OSM
import qgis.utils
import numpy as np
from osgeo import gdal, ogr, osr


from enmapbox.gui.utils import file_search
from enmapbox import DIR_TESTDATA
from unittest import TestCase

SHOW_GUI = True

def initQgisApplication(*args, loadProcessingFramework=True, **kwds)->QgsApplication:
    """
    Initializes a QGIS Environment
    :return: QgsApplication instance of local QGIS installation
    """
    if isinstance(QgsApplication.instance(), QgsApplication):
        return QgsApplication.instance()
    else:
        from .externals.qps.testing import initQgisApplication
        app = initQgisApplication(*args, loadProcessingFramework=loadProcessingFramework, **kwds)

        import enmapbox
        enmapbox.initEnMAPBoxResources()
        if loadProcessingFramework:
            enmapbox.initEnMAPBoxProcessingProvider()
        enmapbox.initEditorWidgets()
        return app

class TestObjects(TestObjects):
    """
    Creates objects to be used for testing. It is preferred to generate objects in-memory.
    """

    @staticmethod
    def enmapboxApplication():
        from enmapbox.gui.applications import EnMAPBoxApplication
        from enmapbox import EnMAPBox
        assert isinstance(EnMAPBox.instance(), EnMAPBox), 'Please initialize an EnMAP-Box instance first'

        def testAlgorithm(self, *args):
            v = 'Hello World'
            print(v)
            return v

        class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
            """
            Exemplary implementation of a QgsProcessingAlgorithm.
            See https://qgis.org/api/classQgsProcessingAlgorithm.html for API documentation
            """
            def __init__(self):
                super(ExampleProcessingAlgorithm, self).__init__()

            def createInstance(self) -> QgsProcessingAlgorithm:
                """
                Creates a new instance of the algorithm class.
                :return: QgsProcessingAlgorithm
                """
                return ExampleProcessingAlgorithm()

            def name(self) -> str:
                return 'examplealgorithm'

            def displayName(self):
                return 'Minimal Example Algorithm'

            def groupId(self) -> str:
                """
                Returns the unique ID of the group this algorithm belongs to.
                :return: str
                """
                return 'testgroup'

            def group(self) -> str:
                """
                Returns the name of the group this algorithm belongs to.
                :return: str
                """
                return 'testgroup'

            def initAlgorithm(self, configuration: dict = None):
                """
                Initializes the algorithm using the specified configuration.
                :param configuration: dict
                """
                self.addParameter(QgsProcessingParameterRasterLayer('pathInput', 'The Input Dataset'))
                self.addParameter(
                    QgsProcessingParameterNumber('value', 'The value', QgsProcessingParameterNumber.Double, 1, False,
                                                 0.00, 999999.99))
                self.addParameter(QgsProcessingParameterRasterDestination('pathOutput', 'The Output Dataset'))

            def processAlgorithm(self, parameters: dict, context: QgsProcessingContext,
                                 feedback: QgsProcessingFeedback):
                """
                Runs the algorithm using the specified parameters.
                :param parameters: dict
                :param context: QgsProcessingContext
                :param feedback: QgsProcessingFeedback
                :return: dict
                """
                assert isinstance(parameters, dict)
                assert isinstance(context, QgsProcessingContext)
                assert isinstance(feedback, QgsProcessingFeedback)

                results = testAlgorithm(parameters)
                outputs = {'results': results}
                return outputs

        class ExampleApp(EnMAPBoxApplication):

            def __init__(self, enmapbox:EnMAPBox, parent):
                super(ExampleApp, self).__init__(enmapbox, parent)

                self.name = 'TestApp'
                self.licence = 'GPL-3'
                self.version = '0.8.15'
                self.description = 'test app'

            def icon(self)->QIcon:
                return EnMAPBox.getIcon()

            def menu(self, parentMenu)->QMenu:

                assert isinstance(parentMenu, QMenu)
                action = parentMenu.addAction('Hello')
                action.triggered.connect(testAlgorithm)
                return parentMenu

            def processingAlgorithms(self)->list:


                return [ExampleProcessingAlgorithm()]

        emb = EnMAPBox.instance()
        return ExampleApp(emb, emb.ui)


    @staticmethod
    def processingAlgorithm():

        from qgis.core import QgsProcessingAlgorithm

        class TestProcessingAlgorithm(QgsProcessingAlgorithm):

            def __init__(self):
                super(TestProcessingAlgorithm, self).__init__()
                s = ""

            def createInstance(self):
                return TestProcessingAlgorithm()

            def name(self):
                return 'exmaplealg'

            def displayName(self):
                return 'Example Algorithm'

            def groupId(self):
                return 'exampleapp'

            def group(self):
                return 'TEST APPS'

            def initAlgorithm(self, configuration=None):
                self.addParameter(QgsProcessingParameterRasterLayer('pathInput', 'The Input Dataset'))
                self.addParameter(
                    QgsProcessingParameterNumber('value', 'The value', QgsProcessingParameterNumber.Double, 1, False,
                                                 0.00, 999999.99))
                self.addParameter(QgsProcessingParameterRasterDestination('pathOutput', 'The Output Dataset'))

            def processAlgorithm(self, parameters, context, feedback):
                assert isinstance(parameters, dict)
                assert isinstance(context, QgsProcessingContext)
                assert isinstance(feedback, QgsProcessingFeedback)


                outputs = {}
                return outputs

        return TestProcessingAlgorithm()



class QgsPluginManagerMockup(QgsPluginManagerInterface):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def addPluginMetadata(self, *args, **kwargs):
        super().addPluginMetadata(*args, **kwargs)

    def addToRepositoryList(self, *args, **kwargs):
        super().addToRepositoryList(*args, **kwargs)

    def childEvent(self, *args, **kwargs):
        super().childEvent(*args, **kwargs)

    def clearPythonPluginMetadata(self, *args, **kwargs):
        #super().clearPythonPluginMetadata(*args, **kwargs)
        pass

    def clearRepositoryList(self, *args, **kwargs):
        super().clearRepositoryList(*args, **kwargs)

    def connectNotify(self, *args, **kwargs):
        super().connectNotify(*args, **kwargs)

    def customEvent(self, *args, **kwargs):
        super().customEvent(*args, **kwargs)

    def disconnectNotify(self, *args, **kwargs):
        super().disconnectNotify(*args, **kwargs)

    def isSignalConnected(self, *args, **kwargs):
        return super().isSignalConnected(*args, **kwargs)

    def pluginMetadata(self, *args, **kwargs):
        super().pluginMetadata(*args, **kwargs)

    def pushMessage(self, *args, **kwargs):
        super().pushMessage(*args, **kwargs)

    def receivers(self, *args, **kwargs):
        return super().receivers(*args, **kwargs)

    def reloadModel(self, *args, **kwargs):
        super().reloadModel(*args, **kwargs)

    def sender(self, *args, **kwargs):
        return super().sender(*args, **kwargs)

    def senderSignalIndex(self, *args, **kwargs):
        return super().senderSignalIndex(*args, **kwargs)

    def showPluginManager(self, *args, **kwargs):
        super().showPluginManager(*args, **kwargs)

    def timerEvent(self, *args, **kwargs):
        super().timerEvent(*args, **kwargs)


class PythonRunnerImpl(QgsPythonRunner):
    """
    A Qgs PythonRunner implementation
    """

    def __init__(self):
        super(PythonRunnerImpl, self).__init__()


    def evalCommand(self, cmd:str, result:str):
        try:
            o = compile(cmd)
        except Exception as ex:
            result = str(ex)
            return False
        return True

    def runCommand(self, command, messageOnError=''):
        try:
            o = compile(command, 'fakemodule', 'exec')
            exec(o)
        except Exception as ex:
            messageOnError = str(ex)
            command = ['{}:{}'.format(i+1, l) for i,l in enumerate(command.splitlines())]
            print('\n'.join(command), file=sys.stderr)
            raise ex
            return False
        return True


