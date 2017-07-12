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
from enmapbox.gui.utils import loadUIFormClass
from __init__ import APP_DIR
loadUi = lambda name: loadUIFormClass(os.path.join(APP_DIR, name))


class ReclassifyDialog(QDialog, loadUi('reclassifywidget.ui')):
    """Constructor."""
    def __init__(self, parent=None):
        super(ReclassifyDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Important!
        self.setupUi(self)

        #now define all the logic behind the UI which can not be defined in the QDesigner
        self.initUiElements()

    def initUiElements(self):
        pass

    def startReclassification(self):
        pass

