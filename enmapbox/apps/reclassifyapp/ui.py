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
from qgis.gui import QgsFileWidget, QgsRasterFormatSaveOptionsWidget

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.utils import loadUIFormClass
from enmapbox.gui.classificationscheme import *
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

        assert isinstance(self.mapLayerComboBox, QComboBox)
        assert isinstance(self.tableWidget, QTableWidget)
        assert isinstance(self.dstClassificationSchemeWidget, ClassificationSchemeWidget)

        #now define all the logic behind the UI which can not be defined in the QDesigner
        self.initUiElements()

    def initUiElements(self):

        self.tbDstFile.textChanged.connect(self.validateSettings)
        self.mapLayerComboBox.currentIndexChanged.connect(self.validateSettings)

        self.buttonBox.accepted.connect(self.accepted.emit)
        self.buttonBox.rejected.connect(self.rejected.emit)
        self.accepted.connect(self.startReclassification)

        self.btnSelectSrcfile.clicked.connect(lambda:self.addSrcRaster(QFileDialog.getOpenFileName()))
        self.btnSelectDstFile.clicked.connect(lambda:self.tbDstFile.setText(QFileDialog.getSaveFileName()))
        self.widgetDstFile.setType(QgsRasterFormatSaveOptionsWidget.LineEdit)
        self.widgetDstFile.setProvider('gdal')
        self.widgetDstFile.setFormat('GTIFF')
        self.widgetDstFile.setRasterFileName('reclassifified.bsq')

        self.dstClassificationSchemeWidget.classificationScheme().sigClassesAdded.connect(self.refreshTransformationTable)
        self.dstClassificationSchemeWidget.classificationScheme().sigClassesRemoved.connect(self.refreshTransformationTable)

        self.mapLayerComboBox.currentIndexChanged.connect(self.refreshTransformationTable)

        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()

        if isinstance(enmapBox, EnMAPBox):
            for src in sorted(enmapBox.dataSources('RASTER')):
                self.addSrcRaster(src)

        self.validateSettings()

    def setDstRaster(self,path):
        self.tbDstFile.setText(path)

    def addSrcRaster(self, src):
        addedItems = [self.mapLayerComboBox.itemData(i, role=Qt.UserRole) for
                      i in range(self.mapLayerComboBox.count())]
        if hasClassification(src) and src not in addedItems:
            bn = os.path.basename(src)
            self.mapLayerComboBox.addItem(bn, src)
        self.validateSettings()

    def currentSrcClassification(self):
        assert isinstance(self.mapLayerComboBox, QComboBox)
        i = self.mapLayerComboBox.currentIndex()
        path = self.mapLayerComboBox.itemData(i, Qt.UserRole)
        return path

    def createClassInfoComboBox(self, classScheme):
        assert isinstance(classScheme, ClassificationScheme)
        box = QComboBox()
        box.setAutoFillBackground(True)
        box.setModel(ClassificationSchemeComboBoxItemModel(classScheme))

        return box



    def refreshTransformationTable(self, *args):
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        from difflib import SequenceMatcher

        path = self.currentSrcClassification()
        if hasClassification(path):
            srcClassScheme = ClassificationScheme.fromRasterImage(path)
            dstClassScheme = self.dstClassificationSchemeWidget.classificationScheme()
            dstClassNames = [c.mName for c in dstClassScheme]
            assert isinstance(self.tableWidget, QTableWidget)
            #self.tableWidget.setColumnCount(2)
            self.tableWidget.setRowCount(len(srcClassScheme))
            itemFlags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            for iRow, c in enumerate(srcClassScheme):
                assert isinstance(c, ClassInfo)
                text = '{} {}'.format(c.mLabel, c.mName)
                item1 = QTableWidgetItem()
                item1.setText(text)
                item1.setFlags(itemFlags)
                item1.setData(0,c)
                pm = QPixmap(20,20)
                pm.fill(c.mColor)
                item1.setIcon(QIcon(pm))
                #item1.setBackground(QBrush(c.mColor))
                #item1.setForeground(getTextColorWithContrast(c.mColor))
                cbox = self.createClassInfoComboBox(dstClassScheme)

                #select the combobox item to the most similar class name
                if len(dstClassScheme) > 0:
                    similarity = [SequenceMatcher(None, c.mName, dName).ratio() for dName in dstClassNames]
                    sMax = max(similarity)
                    if sMax > 0.75:
                        cbox.setCurrentIndex(similarity.index(sMax))

                self.tableWidget.setItem(iRow, 0, item1)
                self.tableWidget.setCellWidget(iRow, 1, cbox)
        self.validateSettings()

    def validateSettings(self):
        okButton = self.buttonBox.button(QDialogButtonBox.Ok)

        isOk = True
        isOk &= self.mapLayerComboBox.currentIndex() > -1
        isOk &= len(self.dstClassificationSchemeWidget.classificationScheme()) > 0
        isOk &= len(self.tbDstFile.text()) > 0
        isOk &= self.tableWidget.rowCount() > 0
        okButton.setEnabled(isOk)


    def collectReclassificationSettings(self):
        pathSrc = self.mapLayerComboBox
        pathDst = self.tbDstFile.text()
        LUT = dict()

        for i in range(self.tableWidget.rowCount()):
            cSrc = self.tableWidget.item(i,0).data(0)
            cDst = self.tableWidget.cellWidget(i,1).data(0)


            s = ""



    def startReclassification(self):
        settings = self.collectReclassificationSettings()
        s = ""
        pass

