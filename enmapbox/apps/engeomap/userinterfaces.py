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

import os
import collections
import time
from qgis.gui import QgsFileWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#from PIL import Image
from enmapbox.gui.utils import loadUIFormClass
from engeomap import APP_DIR

""""
Use the QtDesigner to design a GUI and save it as *.ui file
The example.ui can get compiled and loaded at runtime.
"""""

pathUi = os.path.join(APP_DIR, 'engeomap_base.ui')
pathUi2 = os.path.join(APP_DIR, 'busyqt4.ui')
pathreadui = os.path.join(APP_DIR, 'ready_kl_bu.png')
pathbusyui = os.path.join(APP_DIR, 'busy_kl_bu.png')


def checkstatus(objectus):
    if objectus.isChecked():
        nd = 1
    else:
        nd = 0
    return nd


def button_paths(objectus):
    path = objectus


def selectFile(objectt):
    feil = QtWidgets.QFileDialog.getOpenFileName()
    objectt.setText(feil[0])
    objectt.show()
    return None


def display_busy(anzeige, imnam):
    label = QLabel(anzeige)
    pixelmap = QPixmap(imnam)
    label.setPixmap(pixelmap)
    anzeige.resize(pixelmap.width(), pixelmap.height())
    anzeige.show()


class EnGeoMAPGUI(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(EnGeoMAPGUI, self).__init__(parent)
        self.setupUi(self)
        self.imready = pathreadui
        self.imbusy = pathbusyui
        self.enmap_data.clicked.connect(self.selectFile1)
        self.choose_lib.clicked.connect(self.selectFile2)
        self.choose_csv.clicked.connect(self.selectFile3)
        self.buttonBox.accepted.connect(self.startAlgorithm)  # Button Box
        self.buttonBox.rejected.connect(self.close)

    def display_all(self, imnam):
        label = QLabel(self.bild)
        pixelmap = QPixmap(imnam)
        label.setPixmap(pixelmap)
        self.bild.resize(pixelmap.width(), pixelmap.height())
        self.bild.show()

    def selectFile1(self):
        self.input_image.setText(QFileDialog.getOpenFileName()[0])

    def selectFile2(self):
        self.speclib.setText(QFileDialog.getOpenFileName()[0])

    def selectFile3(self):
        self.colormap.setText(QFileDialog.getOpenFileName()[0])

    def collectParameters(self):
        """
        Collect the parameterization from the UI elements.
        :return: dictionary (dict) with parameters
        """
        p = dict()
        L = []
        p['vnirt'] = self.vnir_thresh.toPlainText()
        p['swirt'] = self.swir_thresh.toPlainText()
        p['fit_thresh'] = self.fit_thresh.toPlainText()
        p['mixminerals'] = self.ixminerals.toPlainText()
        # p['enmap'] = checkstatus(self.enmap_psf)
        # p['hyperion'] = checkstatus(self.hyperion_psf)
        p['laboratory'] = checkstatus(self.lab_image)
        p['liblab'] = checkstatus(self.lab_lib)
        p['image'] = self.input_image.text()
        p['library'] = self.speclib.text()
        p['farbe'] = self.colormap.text()
        p['ende'] = self.imbusy
        #  L.append()
        return p

    def startAlgorithm(self):
        params = self.collectParameters()
        from engeomap.algorithms import engeomapp_headless
        from engeomap.algorithms import mapper_fullrange
        engeomapp_headless(params)
        mapper_fullrange(params)
