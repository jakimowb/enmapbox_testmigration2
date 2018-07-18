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
from qgis.core import QgsProcessingAlgorithm, QgsProcessingFeedback, QgsProcessingContext, QgsProcessingParameterRasterLayer, QgsProcessingParameterRasterDestination, QgsProcessingParameterNumber, QgsRasterLayer

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

        return [ExampleGeoAlgorithm()]

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

        # log parameters
        rasterLayer = self.parameterAsRasterLayer(parameters, 'pathInput', context)
        assert isinstance(rasterLayer, QgsRasterLayer)
        feedback.pushInfo(str(rasterLayer))

        value = self.parameterAsDouble(parameters, 'value', context)
        assert isinstance(value, float)
        feedback.pushInfo(str(value))

        filename = self.parameterAsFileOutput(parameters, 'pathOutput', context)
        assert isinstance(filename, str)
        feedback.pushInfo(str(filename))

        # return output dictionary
        outputs = {'pathOutput': filename}
        return outputs



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