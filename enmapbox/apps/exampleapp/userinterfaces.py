# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/userinterfaces.py

    Some exemplary (graphical) user interfaces, making use of the Qt framework.
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

import os, collections
from qgis.gui import QgsFileWidget
from PyQt4.QtGui import *
from PyQt4.QtCore import *

""""
Use the QtDesigner to design a GUI and save it as *.ui file
The example.ui can get compiled and loaded at runtime.
"""""
from enmapbox.gui.utils import loadUIFormClass
from __init__ import APP_DIR
pathUi = os.path.join(APP_DIR, 'example.ui')


class ExampleGUI(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(ExampleGUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Important!
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.startAlgorithm)
        self.buttonBox.rejected.connect(self.close)

    def collectParameters(self):
        """
        Collect the parameterization from the UI elements.
        :return: dictionary (dict) with parameters
        """
        p = dict()
        p['parameter1'] = self.comboBoxParameter1.currentText()
        p['parameter2'] = None
        return p

    def startAlgorithm(self):
        params = self.collectParameters()
        from algorithms import dummyAlgorithm
        dummyAlgorithm(**params)

