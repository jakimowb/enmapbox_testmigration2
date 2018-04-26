# -*- coding: utf-8 -*-

"""
***************************************************************************
    minimumexample/exampleapp.py

    This module defines the interactions between an application and
    the EnMAPBox.
    ---------------------
    Date                 : Juli 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
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

import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QHBoxLayout, QLabel, QPushButton
from enmapbox.gui.applications import EnMAPBoxApplication
from qgis.core import *


VERSION = '0.0.1'
LICENSE = 'GNU GPL-3'
APP_DIR = os.path.dirname(__file__)

APP_NAME = 'My First EnMAPBox App'

class ExampleEnMAPBoxApp(EnMAPBoxApplication):
    """
    This Class inherits from an EnMAPBoxApplication
    """
    def __init__(self, enmapBox, parent=None):
        super(ExampleEnMAPBoxApp, self).__init__(enmapBox, parent=parent)

        #specify the name of this app
        self.name = APP_NAME

        #specify a version string

        self.version = VERSION

        #specify a licence under which you distribute this application
        self.licence = LICENSE

    def icon(self):
        """
        This function returns the QIcon of your Application
        :return: QIcon()
        """
        return QIcon(os.path.join(APP_DIR, 'icon.png'))

    def menu(self, appMenu):
        """
        Returns a QMenu that will be added to the parent `appMenu`
        :param appMenu:
        :return: QMenu
        """
        assert isinstance(appMenu, QMenu)
        """
        Specify menu, submenus and actions that become accessible from the EnMAP-Box GUI
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """

        # this way you can add your QMenu/QAction to an other menu entry, e.g. 'Tools'
        # appMenu = self.enmapbox.menu('Tools')

        menu = appMenu.addMenu('My Example App')
        menu.setIcon(self.icon())

        #add a QAction that starts a process of your application.
        #In this case it will open your GUI.
        a = menu.addAction('Show ExampleApp GUI')
        assert isinstance(a, QAction)
        a.triggered.connect(self.startGUI)
        appMenu.addMenu(menu)

        return menu

    def geoAlgorithms(self):
        """
        This function returns the QGIS Processing Framework GeoAlgorithms specified by your application
        :return: [list-of-GeoAlgorithms]
        """

        return [ExampleGeoAlgorithm(), ExampleAlgorithmWithManyWidgets()]

    def startGUI(self, *args):
        """
        Opens a GUI
        :param args:
        :return:
        """

        w = ExampleAppGUI()
        w.show()


class ExampleAppGUI(QWidget):
    """
    A minimal graphical user interface
    """
    def __init__(self, parent=None):
        super(ExampleAppGUI, self).__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(os.path.join(APP_DIR, 'icon.png')))
        self.setMinimumWidth(400)
        l = QHBoxLayout()
        l.addWidget(QLabel('Hello World'))
        self.btn = QPushButton('Click me')

        #clicking the button will print "Hello World" to the python CLI
        self.btn.clicked.connect(lambda: print('Hello World'))
        l.addWidget(self.btn)
        self.setLayout(l)



class ExampleGeoAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):

        super(ExampleGeoAlgorithm, self).__init__()
        s = ""

    def createInstance(self):
        return ExampleGeoAlgorithm()

    def name(self):
        return 'exmaplealg'

    def displayName(self):
        return 'Example Algorithm'

    def groupId(self):

        return 'exampleapp'

    def group(self):
        return APP_NAME

    def initAlgorithm(self, configuration=None):
        self.addParameter(QgsProcessingParameterRasterLayer('pathInput', 'The Input Dataset'))
        self.addParameter(QgsProcessingParameterNumber('value','The value', QgsProcessingParameterNumber.Double, 1, False, 0.00, 999999.99))
        self.addParameter(QgsProcessingParameterRasterDestination('pathOutput', 'The Output Dataset'))

    def processAlgorithm(self, parameters, context, feedback):

        assert isinstance(parameters, dict)
        assert isinstance(context, QgsProcessingContext)
        assert isinstance(feedback, QgsProcessingFeedback)

        outputs = {}
        return outputs

class ExampleAlgorithmWithManyWidgets(QgsProcessingAlgorithm):

    P_RASTER = 'raster'
    P_RASTER_BAND = 'raster_band'
    P_VECTOR = 'vector'
    P_VECTOR_FIELD = 'vector_field'
    P_MAP = 'map'
    P_FILE = 'file'
    P_FOLDER = 'folder'
    P_INTEGER = 'integer'
    P_FLOAT = 'float'
    P_STRING = 'string'
    P_BOOLEAN= 'boolean'
    P_ENUM = 'enum'
    P_OUTPUT_RASTER = 'outraster'
    P_OUTPUT_VECTOR = 'outvector'
    P_OUTPUT_FILE = 'outfile'
    P_OUTPUT_FOLDER = 'outfolder'

    def group(self):
        return APP_NAME

    def name(self):
        return 'ExampleAlgorithmWithManyWidgets'

    def displayName(self):
        return 'Example Algorithm with many Widgets'

    def createInstance(self, *args, **kwargs):
        return type(self)()

    def initAlgorithm(self, configuration=None):

        # some example widgets that can be used; for full list see https://qgis.org/api/annotated.html

        # - different input widgets
        self.addParameter(QgsProcessingParameterRasterLayer(name=self.P_RASTER, description='Raster Layer',
                                                            optional=True))

        self.addParameter(QgsProcessingParameterBand(name=self.P_RASTER_BAND, description='Raster Layer Band',
                                                     defaultValue=0, parentLayerParameterName=self.P_RASTER,
                                                     optional=True))

        self.addParameter(QgsProcessingParameterVectorLayer(name=self.P_VECTOR, description='Vector Layer',
                                                            defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterField(name=self.P_VECTOR_FIELD, description='Vector Layer Field',
                                                      parentLayerParameterName=self.P_VECTOR,
                                                      type=QgsProcessingParameterField.Any,
                                                      allowMultiple=False, defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterMapLayer(name=self.P_MAP, description='Map Layer',
                                                         defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterFile(name=self.P_FILE, description='File',
                                                     behavior=QgsProcessingParameterFile.File, extension='',
                                                     defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterFile(name=self.P_FOLDER, description='Folder',
                                                     behavior=QgsProcessingParameterFile.Folder,
                                                     defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterNumber(name=self.P_INTEGER, description='Integer',
                                                       type=QgsProcessingParameterNumber.Integer,
                                                       defaultValue=0, optional=False, minValue=0, maxValue=10))

        self.addParameter(QgsProcessingParameterNumber(name=self.P_FLOAT, description='Float',
                                                       type=QgsProcessingParameterNumber.Double,
                                                       defaultValue=0.0, optional=False, minValue=0, maxValue=10))

        self.addParameter(QgsProcessingParameterString(name=self.P_STRING, description='String',
                                                       defaultValue='Hello World', multiLine=False, optional=False))

        self.addParameter(QgsProcessingParameterBoolean(name=self.P_BOOLEAN, description='Boolean',
                                                        defaultValue=True, optional=False))

        self.enumOptions = ['A', 'B', 'C']
        self.addParameter(QgsProcessingParameterEnum(name=self.P_ENUM, description='Enum',
                                                     options=self.enumOptions, allowMultiple=False, defaultValue=0,
                                                     optional=False))

        # - different output widgets

        # raster, vector, map, file, folder
        self.addParameter(QgsProcessingParameterRasterDestination(name=self.P_OUTPUT_RASTER,
                                                                  description='Output Raster'))
        self.addParameter(QgsProcessingParameterVectorDestination(name=self.P_OUTPUT_VECTOR,
                                                            description='Output Vector'))
        self.addParameter(QgsProcessingParameterFileDestination(name=self.P_OUTPUT_FILE,
                                                                description='Output File',
                                                                fileFilter='txt'))
        self.addParameter(QgsProcessingParameterFolderDestination(name=self.P_OUTPUT_FOLDER,
                                                                  description='Output Folder', optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        assert isinstance(parameters, dict)
        assert isinstance(context, QgsProcessingContext)
        assert isinstance(feedback, QgsProcessingFeedback)

        # print all parameters to log
        for key in sorted(parameters):
            feedback.pushInfo('{} = {}'.format(key, repr(parameters[key])))

        # create output files
        rasterFilename = str(self.parameterAsOutputLayer(parameters, self.P_OUTPUT_RASTER, context))
        vectorFilename = str(self.parameterAsOutputLayer(parameters, self.P_OUTPUT_VECTOR, context))
        fileFilename = parameters[self.P_OUTPUT_FILE]
        folderFilename = parameters[self.P_OUTPUT_FOLDER]
        # - here comes your fancy processing algorithm!!!
        with open(rasterFilename, 'w'): pass # is not really a raster file :-)
        with open(vectorFilename, 'w'): pass # is not really a vector file :-)
        with open(fileFilename, 'w'): pass
        os.makedirs(folderFilename)

        # return outputs
        return {self.P_OUTPUT_RASTER: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_VECTOR: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_FILE: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_FOLDER: parameters[self.P_OUTPUT_RASTER]}

    def shortHelpString(self, *args, **kwargs):
        text = '<p>Here comes the HTML documentation.</p>'\
               '<h3>With Headers...</h3>'\
               '<p>and Hyperlinks: <a href="www.google.de">Google</a></p>'

        return text

    def helpString(self):
        return self.shortHelpString()

    def helpUrl(self, *args, **kwargs):
        return 'www.google.de'


if __name__ == '__main__':


    from enmapbox.gui.utils import initQgisApplication

    #this will initialize the QApplication/QgsApplication which runs in the background
    #see https://qgis.org/api/classQgsApplication.html for details
    qgsApp = initQgisApplication()


    if False: #test GUI without EnMAP-Box
        w = ExampleAppGUI()
        w.show()

    else:
        from enmapbox.gui.enmapboxgui import EnMAPBox

        EB = EnMAPBox(None)
        EB.run()
        EB.openExampleData(mapWindows=2)
        app = ExampleEnMAPBoxApp(EB)
        EB.addApplication(app)

    #start the GUI thread
    qgsApp.exec_()