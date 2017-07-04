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

"""
This example shows how to use PyQt to create a UI programmatically. 
"""
class MyNDVIUserInterface(QDialog):

    """
    QSignals can be used to communicate between objects and accross threads.
    We use it to signalize if a new file was created
    """
    sigFileCreated = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyNDVIUserInterface, self).__init__(parent)
        self.initWidgets()
        self.initInteractions()
        self.setWindowTitle('My NDVI GUI')
        self.setWindowIcon(QIcon(os.path.join(APP_DIR,'icon.png')))

        s = ""
    SUPPORTED_GDALDRIVERS = {
        'ENVI':'ENVI (*.bsq)',
        'GTiff':'GeoTIFF (*.tif)'
    }

    def initWidgets(self):
        mainLayout = QGridLayout(self)
        self.setLayout(mainLayout)

        self.btnSetInputFile = QPushButton('...', self)
        self.btnSetOutputFile = QPushButton('...', self)
        self.tbInputFile = QLineEdit(self)
        self.tbInputFile.setPlaceholderText('Set input image')
        self.tbOutputFile = QLineEdit(self)
        self.tbOutputFile.setPlaceholderText('Set output image')

        mainLayout.addWidget(QLabel('Input'), 0, 0)
        mainLayout.addWidget(self.tbInputFile, 0, 1)
        mainLayout.addWidget(self.btnSetInputFile, 0, 2)

        box = QHBoxLayout()
        self.sbRedBand = QSpinBox(self)
        self.sbRedBand.setMinimum(1)
        self.sbNIRBand = QSpinBox(self)
        self.sbNIRBand.setMinimum(1)

        box.addWidget(QLabel('Red Band'))
        box.addWidget(self.sbRedBand)
        box.addWidget(QLabel('NIR Band'))
        box.addWidget(self.sbNIRBand)
        # within a horizontal box, the spacer pushes widgets to it's left
        box.addSpacerItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Expanding))
        mainLayout.addLayout(box, 1, 1, 1, 2)  # span 2nd (index 1) and 3rd (+ 1) column

        mainLayout.addWidget(QLabel('Output'), 2, 0)
        mainLayout.addWidget(self.tbOutputFile, 2, 1)
        mainLayout.addWidget(self.btnSetOutputFile, 2, 2)

        self.outputFormat = QComboBox()
        for driver, description in MyNDVIUserInterface.SUPPORTED_GDALDRIVERS.items():
            self.outputFormat.addItem(description, driver)
        from qgis.gui import QgsRasterFormatSaveOptionsWidget
        self.outputOptions = QgsRasterFormatSaveOptionsWidget(parent=self,
                                                              type=QgsRasterFormatSaveOptionsWidget.Default)
        box = QHBoxLayout()
        self.outputOptions.setFormat('GTiff')
        self.outputOptions.setRasterFileName('foobar.bqs')
        box.addWidget(QLabel('Format'))
        box.addWidget(self.outputFormat)
        box.addSpacerItem(QSpacerItem(0,0,hPolicy=QSizePolicy.Expanding))
        mainLayout.addLayout(box, 3, 1, 1, 2)
        mainLayout.addWidget(self.outputOptions, 4, 1, 2,2)

        box = QHBoxLayout()
        self.btAccept = QPushButton('Accept', self)
        self.btCancel = QPushButton('Cancel', self)
        self.btAccept.clicked.connect(self.runCalculations)
        box.addSpacerItem(QSpacerItem(0,0, hPolicy=QSizePolicy.Expanding))
        box.addWidget(self.btCancel)
        box.addWidget(self.btAccept)
        mainLayout.addLayout(box, 6, 1, 1, 2)

    def validateParameters(self, *args, **kwds):
        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True
        if sender == self.tbInputFile:
            path = self.tbInputFile.text()
            from osgeo import gdal
            ds = gdal.Open(path)

            if ds is None:
                style = 'QLineEdit {{ background-color: {} }}'.format(hexRed)
                self.tbInputFile.setStyleSheet(style)
                result = False
            else:
                style = 'QLineEdit {{ }}'.format(hexGreen)
                self.tbInputFile.setStyleSheet(style)
                self.sbRedBand.setMaximum(ds.RasterCount)
                self.sbNIRBand.setMaximum(ds.RasterCount)

        if sender == self.tbOutputFile:
            pathDst = self.tbInputFile.text()
            if len(path) is 0:
                result = False

        self.btAccept.setEnabled(result)



    def initInteractions(self):
        self.tbInputFile.textChanged.connect(self.validateParameters)
        self.sbRedBand.valueChanged.connect(self.validateParameters)
        self.sbNIRBand.valueChanged.connect(self.validateParameters)

        #select input file name via QFileDialog
        self.btnSetInputFile.clicked.connect(
            lambda : self.tbInputFile.setText(
                QFileDialog.getOpenFileName(self, 'Input image'))
        )

        # select output file name via QFileDialog
        self.btnSetOutputFile.clicked.connect(
            lambda: self.tbOutputFile.setText(
                QFileDialog.getSaveFileName(self, 'NDVI image'))
        )

        self.outputFormat.currentIndexChanged.connect(
            lambda : self.outputOptions.setFormat(
                self.outputFormat.itemData(
                    self.outputFormat.currentIndex()
                )
            )
        )
        self.outputFormat.setCurrentIndex(0)

        self.btAccept.clicked.connect(self.accept)
        self.btCancel.clicked.connect(self.reject)



    def runCalculations(self):
        from exampleapp.algorithms import ndvi
        fileSrc = self.tbInputFile.text()
        fileDst = self.tbOutputFile.text()

        try:
            #run your algorithm
            ndvi(fileSrc, fileDst,
                 redBandNumber=self.sbRedBand.value(),
                 nirBandNumber=self.sbNIRBand.value())

            #signalize that a new file was created.
            self.sigFileCreated.emit(fileDst)
        except Exception as ex:
            #in case of exceptions, provide let the user know what happened
            import qgis.utils
            QMessageBox.critical(self, "Error", ex.message)




""""
Use the QtDesigner to design a GUI and save it as *.ui file
The example.ui can get compiled and loaded at runtime.
"""""
from enmapbox.gui.utils import loadUIFormClass
from __init__ import APP_DIR
pathUi = os.path.join(APP_DIR, 'example.ui')


class MyAppUserInterface(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(MyAppUserInterface, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Important!
        self.setupUi(self)

        #now define all the logic behind the UI which can not be defined in the QDesigner
        self.initUiElements()
        self.radioButtonSet1.setChecked(True)
        self.updateSummary()

    def initUiElements(self):
        self.radioButtonSet1.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.radioButtonSet2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.buttonBox.accepted.connect(self.updateSummary)

        #update summary if any parameter was changed
        self.stackedWidget.currentChanged.connect(self.updateSummary)
        self.colorButtonP1.colorChanged.connect(self.updateSummary)

        for spinBox in self.findChildren(QAbstractSpinBox):
            spinBox.editingFinished.connect(self.updateSummary)
        for comboBox in self.findChildren(QComboBox):
            comboBox.currentIndexChanged.connect(self.updateSummary)

    def startAlgorithm(self):
        params = self.collectParameters()
        from algorithms import dummyAlgorithm
        dummyAlgorithm(params)

    def collectParameters(self):
        params = collections.OrderedDict()
        params['file'] = self.comboBoxMapLayer.currentLayer()

        if self.radioButtonSet1.isChecked():
            params['mode'] = 'mode 1'
            params['parameter 1'] = self.comboBoxP1.currentText()
            params['color '] = self.colorButtonP1.color().getRgb()

        elif self.radioButtonSet2.isChecked():
            params['mode'] = 'mode 2'
            params['parameter 1'] = self.doubleSpinBox.value()
            params['parameter 2'] = self.comboBoxP2.currentText()
        return params

    def updateSummary(self, *args):
        info = []
        params = self.collectParameters()
        for parameterName, parameterValue in params.items():
            info.append('{} = {}'.format(parameterName, parameterValue))

        self.textBox.setPlainText('\n'.join(info))


