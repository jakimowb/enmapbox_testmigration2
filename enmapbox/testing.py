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
import qps.testing
import qgis.utils
import numpy as np
from osgeo import gdal, ogr, osr
import enmapboxtestdata

from enmapbox.gui.utils import file_search
from enmapbox import DIR_TESTDATA
from unittest import TestCase

SHOW_GUI = True

def initQgisApplication(*args, **kwds)->QgsApplication:
    """
    Initializes a QGIS Environment
    :return: QgsApplication instance of local QGIS installation
    """
    if isinstance(QgsApplication.instance(), QgsApplication):
        return QgsApplication.instance()
    else:

        app = qps.testing.initQgisApplication(*args, **kwds)

        from enmapbox import initEnMAPBoxProcessingProvider
        initEnMAPBoxProcessingProvider()

        return app

        if not 'QGIS_PREFIX_PATH' in os.environ.keys():
            raise Exception('env variable QGIS_PREFIX_PATH not set')

        if sys.platform == 'darwin':
            # add location of Qt Libraries
            assert '.app' in qgis.__file__, 'Can not locate path of QGIS.app'
            PATH_QGIS_APP = re.search(r'.*\.app', qgis.__file__).group()
            QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns']))
            QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns', 'qgis']))

        qgsApp = qgis.testing.start_app()

        # initialize things not done by qgis.test.start_app()...
        if not isinstance(qgisResourceDir, str):
            parentDir = os.path.dirname(os.path.dirname(__file__))
            resourceDir = os.path.join(parentDir, 'qgisresources')
            if os.path.exists(resourceDir):
                qgisResourceDir = resourceDir

        if isinstance(qgisResourceDir, str) and os.path.isdir(qgisResourceDir):
            modules = [m for m in os.listdir(qgisResourceDir) if re.search(r'[^_].*\.py', m)]
            modules = [m[0:-3] for m in modules]
            for m in modules:
                mod = importlib.import_module('qgisresources.{}'.format(m))
                if "qInitResources" in dir(mod):
                    mod.qInitResources()

        # initiate a PythonRunner instance if None exists
        if not QgsPythonRunner.isValid():
            r = PythonRunnerImpl()
            QgsPythonRunner.setInstance(r)

        from qgis.analysis import QgsNativeAlgorithms
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

        # import processing
        # p = processing.classFactory(iface)
        if not isinstance(qgis.utils.iface, QgisInterface):

            iface = QgisMockup()
            qgis.utils.initInterface(sip.unwrapinstance(iface))
            assert iface == qgis.utils.iface
            """
            import processing
            processing.Processing.initialize()
            import processing
            import pkgutil
            prefix = str(processing.__name__ + '.')
            for importer, modname, ispkg in pkgutil.walk_packages(processing.__path__, prefix=prefix):
                try:
                    module = __import__(modname, fromlist="dummy")
                    if hasattr(module, 'iface'):
                        print(modname)
                        module.iface = iface
                except:
                    pass
            """
        # set 'home_plugin_path', which is required from the QGIS Plugin manager
        qgis.utils.home_plugin_path = os.path.join(QgsApplication.instance().qgisSettingsDirPath(),
                                                   *['python', 'plugins'])

        # initiate the QGIS processing framework

        from processing.core.Processing import Processing
        Processing.initialize()

        #
        providers = QgsProviderRegistry.instance().providerList()
        for p in ['DB2', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'delimitedtext', 'gdal', 'geonode', 'gpx', 'mdal', 'memory', 'mesh_memory', 'mssql', 'ogr', 'oracle', 'ows', 'postgres', 'spatialite', 'virtual', 'wcs', 'wms']:
            if p not in providers:
                warnings.warn('Missing QGIS provider "{}"'.format(p), Exception)

        from enmapbox import initEnMAPBoxProcessingProvider
        initEnMAPBoxProcessingProvider()

        return qgsApp



class TestObjects(qps.testing.TestObjects):
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


