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


from qgis.core import *
from qgis.gui import *
from enmapbox.gui import *
from reclassifyapp import APP_DIR

loadUi = lambda name: loadUIFormClass(os.path.join(APP_DIR, name))



class ReclassifyDialog(QDialog, loadUi('reclassifydialog.ui')):
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

        self.mSrcClassScheme = None
        #now define all the logic behind the UI which can not be defined in the QDesigner
        self.initUiElements()

    def initUiElements(self):

        self.tbDstFile.textChanged.connect(self.validate)
        self.mapLayerComboBox.currentIndexChanged.connect(self.validate)

        def onAddRaster(*args):
            filter = QgsProviderRegistry.instance().fileRasterFilters()
            file, filter = QFileDialog.getOpenFileName()

            if len(file) > 0:
                self.addSrcRaster(file)

        def onSetDstFile(*args):
            filter = QgsProviderRegistry.instance().fileRasterFilters()
            file, filter = QFileDialog.getSaveFileName(self, 'Output classification raster', self.tbDstFile.text(), filter=filter)

            if len(file) > 0:
                self.tbDstFile.setText(file)

        self.btnSelectSrcfile.clicked.connect(onAddRaster)
        self.btnSelectDstFile.clicked.connect(onSetDstFile)
        self.widgetDstFile.setType(QgsRasterFormatSaveOptionsWidget.Full)
        self.widgetDstFile.setProvider('gdal')
        self.widgetDstFile.setFormat('GTIFF')
        self.widgetDstFile.setRasterFileName('reclassifified.tif')

        self.dstClassificationSchemeWidget.classificationScheme().sigClassesAdded.connect(self.refreshTransformationTable)
        self.dstClassificationSchemeWidget.classificationScheme().sigClassesRemoved.connect(self.refreshTransformationTable)
        #self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.mapLayerComboBox.currentIndexChanged.connect(self.refreshTransformationTable)


        #start validation if content changes in...
        self.tbDstFile.textChanged.connect(self.validate)


        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapBox = EnMAPBox.instance()

        if isinstance(enmapBox, EnMAPBox):
            for src in sorted(enmapBox.dataSources('RASTER')):
                self.addSrcRaster(src)

        self.validate()

    def setDstClassification(self, classScheme):
        """
        Sets the destination ClassificationScheme
        :param classScheme: path of classification file or ClassificationScheme
        """
        if isinstance(classScheme, str) and os.path.isfile(classScheme):
            classScheme = ClassificationScheme.fromRasterImage(classScheme)
        self.dstClassificationSchemeWidget.setClassificationScheme(classScheme)


    def setDstRaster(self, path:str):
        """
        Sets the path of the reclassified raster
        :param path: str
        """
        self.tbDstFile.setText(path)
        self.widgetDstFile.setRasterFileName(path)


    def addSrcRaster(self, src):
        """
        Adds a new source raster
        :param src: object
        :return:
        """
        addedItems = [self.mapLayerComboBox.itemData(i, role=Qt.UserRole) for
                      i in range(self.mapLayerComboBox.count())]
        if hasClassification(src) and src not in addedItems:
            bn = os.path.basename(src)
            self.mapLayerComboBox.addItem(bn, src)

            assert isinstance(self.dstClassificationSchemeWidget, ClassificationSchemeWidget)
            if len(self.dstClassificationSchemeWidget.classificationScheme())== 0:
                try:
                    scheme = ClassificationScheme.fromRasterImage(src)
                    if len(scheme) > 0:
                        self.dstClassificationSchemeWidget.setClassificationScheme(scheme)
                except:
                    pass


            self.validate()



    def srcClassificationScheme(self):
        return self.mSrcClassScheme

    def srcClassificationPath(self):
        assert isinstance(self.mapLayerComboBox, QComboBox)
        i = self.mapLayerComboBox.currentIndex()
        path = self.mapLayerComboBox.itemData(i, Qt.UserRole)
        return path

    def createClassInfoComboBox(self, classScheme):
        assert isinstance(classScheme, ClassificationScheme)
        box = ClassificationSchemeComboBox(classification=classScheme)
        box.setAutoFillBackground(True)

        return box



    def refreshTransformationTable(self, *args):

        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        from difflib import SequenceMatcher

        path = self.srcClassificationPath()
        if not hasClassification(path):
            self.mSrcClassScheme = None
        else:
            self.mSrcClassScheme = ClassificationScheme.fromRasterImage(path)
            dstClassScheme = self.dstClassificationSchemeWidget.classificationScheme()
            dstClassNames = [c.mName for c in dstClassScheme]
            assert isinstance(self.tableWidget, QTableWidget)
            #self.tableWidget.setColumnCount(2)
            self.tableWidget.setRowCount(len(self.mSrcClassScheme))
            itemFlags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            for iRow, c in enumerate(self.mSrcClassScheme):
                assert isinstance(c, ClassInfo)
                text = '{} {}'.format(c.mLabel, c.mName)
                pm = QPixmap(20, 20)
                pm.fill(c.mColor)
                icon = QIcon(pm)

                item1 = QTableWidgetItem()
                #item1.setText(text)
                item1.setFlags(itemFlags)
                item1.setData(Qt.DisplayRole, text)
                item1.setData(Qt.DecorationRole, icon)
                item1.setData(Qt.UserRole, iRow)

                #item1.setIcon(icon)
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
        self.validate()


    def validate(self):
        """
        Validates GUI inputs and enabled/disabled buttons accordingly.
        """
        isOk = True
        isOk &= self.mapLayerComboBox.currentIndex() > -1
        isOk &= len(self.dstClassificationSchemeWidget.classificationScheme()) > 0
        isOk &= len(self.tbDstFile.text()) > 0
        isOk &= self.tableWidget.rowCount() > 0

        btnAccept = self.buttonBox.button(QDialogButtonBox.Ok)
        btnAccept.setEnabled(isOk)


    def reclassificationSettings(self)->dict:
        """
        Returns the re-classification settings
        :return: dict with {pathSrc:str, pathDst:str, labelLookup:dict, dstClassScheme:ClassificationScheme
        """
        pathSrc = self.mapLayerComboBox.itemData(self.mapLayerComboBox.currentIndex())
        pathDst = self.tbDstFile.text()
        LUT = dict()
        dstScheme = None
        for i in range(self.tableWidget.rowCount()):
            cbox = self.tableWidget.cellWidget(i, 1)
            assert isinstance(cbox, ClassificationSchemeComboBox)
            cDst = cbox.currentClassInfo()
            iSrc = self.tableWidget.item(i,0).data(Qt.UserRole)
            if not dstScheme:
                dstScheme = cbox.classificationScheme().clone()
            cSrc = self.mSrcClassScheme[iSrc]

            LUT[cSrc.label()] = cDst.label()
            #print((cSrc.label(),'->',cDst.label()))
        if isinstance(dstScheme, ClassificationScheme):
            return {'pathSrc': pathSrc, 'pathDst': pathDst, 'labelLookup': LUT,
                    'dstClassScheme':dstScheme}
        else:
            return {}






