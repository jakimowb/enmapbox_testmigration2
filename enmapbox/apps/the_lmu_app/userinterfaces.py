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
pathUi = os.path.join(APP_DIR, 'gui1.ui')


class GUI1(QDialog, loadUIFormClass(pathUi)):


    #call self.sigFileCreated.emit(path-to-file)
    #to inform others that GUI1 or an algorithm called by GUI1 has created any new file
    sigFileCreated = pyqtSignal(str)


    def __init__(self, parent=None):
        super(GUI1, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Important!
        self.setupUi(self)
        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnOk.clicked.connect(self.startAlgorithm)
        self.btnCanceled = self.buttonBox.button(QDialogButtonBox.Cancel)
        self.btnCanceled.clicked.connect(self.close)

    def startAlgorithm(self, *args):

        from the_lmu_app.algorithms import dummyAlgorithm
        dummyAlgorithm(*args)

        #close this widget when done
        self.close()

