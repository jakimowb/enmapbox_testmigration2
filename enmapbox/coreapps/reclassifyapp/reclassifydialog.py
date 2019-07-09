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
        super(ReclassifyDialog, self).__init__(parent, Qt.Window)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Important!
        self.setupUi(self)

        assert isinstance(self.mapLayerComboBox, QgsMapLayerComboBox)
        assert isinstance(self.tableWidget, QTableWidget)
        assert isinstance(self.dstClassificationSchemeWidget, ClassificationSchemeWidget)

        self.mapLayerComboBox.setAllowEmptyLayer(True)
        self.mapLayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
        excluded = [p for p in QgsProviderRegistry.instance().providerList() if p not in ['gdal']]
        self.mapLayerComboBox.setExcludedProviders(excluded)
        self.mapLayerComboBox.setShowCrs(False)
        self.mapLayerComboBox.currentIndexChanged.connect(self.validate)


        #now define all the logic behind the UI which can not be defined in the QDesigner
        assert isinstance(self.dstFileWidget, QgsFileWidget)
        self.dstFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        self.dstFileWidget.setConfirmOverwrite(True)

        assert isinstance(self.widgetOutputOptions, QgsRasterFormatSaveOptionsWidget)
        self.widgetOutputOptions.setType(QgsRasterFormatSaveOptionsWidget.Full)
        self.widgetOutputOptions.setProvider('gdal')
        self.widgetOutputOptions.setFormat('GTIFF')
        self.widgetOutputOptions.setRasterFileName('reclassifified.tif')
        self.dstFileWidget.fileChanged.connect(self.widgetOutputOptions.setRasterFileName)

        self.dstClassificationSchemeWidget.classificationScheme().sigClassesAdded.connect(self.refreshTransformationTable)
        self.dstClassificationSchemeWidget.classificationScheme().sigClassesRemoved.connect(self.refreshTransformationTable)

        self.mapLayerComboBox.currentIndexChanged.connect(self.refreshTransformationTable)
        self.mapLayerComboBox.currentIndexChanged.connect(self.validate)

        self.btnSelectSrcfile.setDefaultAction(self.actionAddRasterSource)
        self.dstFileWidget.fileChanged.connect(self.validate)


        def onAddRaster(*args):
            filter = QgsProviderRegistry.instance().fileRasterFilters()
            file, filter = QFileDialog.getOpenFileName(filter=filter)

            if len(file) > 0:
                self.setSrcRaster(file)

        self.actionAddRasterSource.triggered.connect(onAddRaster)


    def loadEnMAPBoxSources(self):

        try:
            from enmapbox.gui.enmapboxgui import EnMAPBox
            enmapBox = EnMAPBox.instance()

            if isinstance(enmapBox, EnMAPBox):
                for src in sorted(enmapBox.dataSources('RASTER')):
                    self.setSrcRaster(src)

            self.validate()
        except Exception as ex:
            print(ex, file=sys.stderr)


    def setDstClassificationPath(self, path:str):
        """
        Sets the output path.
        :param path:
        :return:
        """
        assert isinstance(self.dstFileWidget, QgsFileWidget)
        self.dstFileWidget.setFilePath(path)

    def setDstClassificationScheme(self, classScheme:ClassificationScheme):
        """
        Sets the destination ClassificationScheme
        :param classScheme: path of classification file or ClassificationScheme
        """
        if isinstance(classScheme, str) and os.path.isfile(classScheme):
            classScheme = ClassificationScheme.fromRasterImage(classScheme)
        self.dstClassificationSchemeWidget.setClassificationScheme(classScheme)

    def dstClassificationScheme(self)->ClassificationScheme:
        """
        Returns the targeted classification scheme.
        :return: ClassificationScheme
        """
        return self.dstClassificationSchemeWidget.classificationScheme()

    def setDstRaster(self, path: str):
        """
        Sets the output path
        :param path: str
        """
        self.dstFileWidget.setFilePath(path)

    def dstRaster(self)->str:
        """
        Returns the destination raster path
        :return: str
        """
        return self.dstFileWidget.filePath()

    def knownRasterSources(self)->list:
        """
        Returns a list of known raster sources
        :return: [list-of-str]
        """

        assert isinstance(self.mapLayerComboBox, QgsMapLayerComboBox)

        sources = []
        for i in range(self.mapLayerComboBox.count()):
            data = self.mapLayerComboBox.itemData(i, role=Qt.UserRole)
            if isinstance(data, str) and len(data) > 0:
                sources.append(data)

        sources += self.mapLayerComboBox.additionalItems()
        return sources

    def srcRaster(self)->str:
        """
        Returns the currently selected source raster
        :return: str
        """
        lyr = self.mapLayerComboBox.currentLayer()
        if isinstance(lyr, QgsRasterLayer):
            return lyr.source()

        text = self.mapLayerComboBox.currentText()
        if len(text) > 0:
            return text
        return None


    def selectSource(self, src:str):
        """
        Selects the raster
        :param src:
        :return:
        """
        assert isinstance(self.mapLayerComboBox, QgsMapLayerComboBox)
        for i in [self.mapLayerComboBox.findText(src), self.mapLayerComboBox.findData(src)]:
            if i > -1:
                self.mapLayerComboBox.setCurrentIndex(i)

    def setSrcRaster(self, src)->bool:
        """
        Adds a new source raster
        :param src: object
        :return:
        """
        knownSources = self.knownRasterSources()
        assert isinstance(self.mapLayerComboBox, QgsMapLayerComboBox)


        if src in knownSources:
            self.selectSource(src)
            return

        if hasClassification(src):
            additionals = self.mapLayerComboBox.additionalItems()
            bn = os.path.basename(src)
            additionals.append(src)
            self.mapLayerComboBox.setAdditionalItems(additionals)

            assert isinstance(self.dstClassificationSchemeWidget, ClassificationSchemeWidget)
            if len(self.dstClassificationSchemeWidget.classificationScheme())== 0:
                try:
                    scheme = ClassificationScheme.fromRasterImage(src)
                    if len(scheme) > 0:
                        self.dstClassificationSchemeWidget.setClassificationScheme(scheme)
                except:
                    pass


            self.selectSource(src)
            return True
        return False


    def srcClassificationScheme(self)->ClassificationScheme:
        """
        Reuturns the ClassificationScheme of the selected source raster
        :return: ClassificationScheme
        """
        path = self.srcRaster()
        if isinstance(path, str):
            return ClassificationScheme.fromRasterImage(path)
        else:
            return None

    def createClassInfoComboBox(self, classScheme):
        assert isinstance(classScheme, ClassificationScheme)
        box = ClassificationSchemeComboBox(classification=classScheme)
        box.setAutoFillBackground(True)

        return box



    def refreshTransformationTable(self, *args):

        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        from difflib import SequenceMatcher


        # clear the table widget
        assert isinstance(self.tableWidget, QTableWidget)
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)

        self.mSrcClassScheme = self.srcClassificationScheme()
        if not isinstance(self.mSrcClassScheme, ClassificationScheme):
            return

        dstClassScheme = self.dstClassificationSchemeWidget.classificationScheme()
        dstClassNames = [c.mName for c in dstClassScheme]

        self.tableWidget.setRowCount(len(self.mSrcClassScheme))
        itemFlags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        for iRow, c in enumerate(self.mSrcClassScheme):
            assert isinstance(c, ClassInfo)
            text = '{} {}'.format(c.mLabel, c.mName)
            item1 = QTableWidgetItem()
            item1.setFlags(itemFlags)
            item1.setData(Qt.DisplayRole, text)
            item1.setData(Qt.DecorationRole, c.icon())
            item1.setData(Qt.UserRole, iRow)

            cbox = self.createClassInfoComboBox(dstClassScheme)

            # select the combobox item with most similar class name
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
        isOk &= len(self.mapLayerComboBox.currentText()) > 0
        isOk &= len(self.dstClassificationSchemeWidget.classificationScheme()) > 0
        isOk &= len(self.dstFileWidget.filePath()) > 0
        isOk &= self.tableWidget.rowCount() > 0

        btnAccept = self.buttonBox.button(QDialogButtonBox.Ok)
        btnAccept.setEnabled(isOk)


    def reclassificationSettings(self)->dict:
        """
        Returns the re-classification settings
        :return: dict with {pathSrc:str, pathDst:str, labelLookup:dict, dstClassScheme:ClassificationScheme
        """
        pathSrc = self.srcRaster()
        pathDst = self.dstRaster()



        LUT = dict()
        srcScheme = self.srcClassificationScheme()
        dstScheme = self.dstClassificationScheme()
        for i in range(self.tableWidget.rowCount()):
            cbox = self.tableWidget.cellWidget(i, 1)
            assert isinstance(cbox, ClassificationSchemeComboBox)
            cDst = cbox.currentClassInfo()
            iSrc = self.tableWidget.item(i,0).data(Qt.UserRole)
            cSrc = srcScheme[iSrc]

            LUT[cSrc.label()] = cDst.label()

        if isinstance(dstScheme, ClassificationScheme):
            return {'pathSrc': pathSrc, 'pathDst': pathDst, 'labelLookup': LUT,
                    'dstClassScheme':dstScheme}
        else:
            return {}






