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

import pathlib
from qgis.core import *
from qgis.gui import *
from enmapbox.gui import *
from reclassifyapp import APP_DIR
from difflib import SequenceMatcher

from enmapbox.externals.qps.classification.classificationscheme import ClassificationMapLayerComboBox

class ReclassifyTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mColumNames = ['From', 'To']
        self.mDst: ClassificationScheme = None
        self.mSrc: ClassificationScheme = None

        self.mMapping = dict()

    def matchClassNames(self):
        LUT = dict()

        dstNames = list(set(self.mDst.classNames()))
        srcNames = list(set(self.mSrc.classNames()))

        for srcName in srcNames:
            similarity = [SequenceMatcher(None, dstName, srcName).ratio() for dstName in dstNames]
            sMax = max(similarity)
            if sMax > 0.75:
                LUT[srcName] = dstNames[similarity.index(sMax)]

        for srcName, dstName in LUT.items():
            i = self.mSrc.classNames().index(srcName)
            j = self.mDst.classNames().index(dstName)
            self.mMapping[self.mSrc[i]] = self.mDst[j]

    def setDestination(self, cs: ClassificationScheme):
        assert isinstance(cs, ClassificationScheme)
        self.beginResetModel()


        if isinstance(self.mDst, ClassificationScheme):
            try:
                self.mDst.sigClassesRemoved.disconnect(self.onDestinationClassesRemoved)
                self.mDst.dataChanged.disconnect(self.onDestinationDataChanged)
            except:
                pass

        self.mDst = cs
        self.mDst.sigClassesRemoved.connect(self.onDestinationClassesRemoved)
        self.mDst.dataChanged.connect(self.onDestinationDataChanged)
        self.mMapping.clear()
        # match similar class names
        if isinstance(self.mSrc, ClassificationScheme):
            # match on similar names
            self.matchClassNames()
        self.endResetModel()

    def destination(self) -> ClassificationScheme:
        return self.mDst

    def setSource(self, cs: ClassificationScheme):
        assert isinstance(cs, ClassificationScheme)

        self.beginResetModel()

        oldSrc = self.mSrc
        self.mSrc = cs
        self.mMapping.clear()
        if isinstance(oldSrc, ClassificationScheme):
            self.matchClassNames()
            try:
                oldSrc.sigClassesRemoved.disconnect(self.onSourceClassesRemoved)
                self.mSrc.dataChanged.disconnect(self.onSourceDataChanged)
            except:
                pass
        self.mSrc.sigClassesRemoved.connect(self.onSourceClassesRemoved)
        self.mSrc.dataChanged.connect(self.onSourceDataChanged)

        self.endResetModel()

    def onSourceDataChanged(self, idx0, idx1, roles):

        a = self.index(idx0.row(), 0)
        b = self.index(idx1.row(), 0 )

        self.dataChanged.emit(a,b, roles)

    def onDestinationDataChanged(self, a, b, roles):
        a = self.index(0, 1)
        b = self.index(self.rowCount()-1, 1)
        self.dataChanged.emit(a, b, roles)

    def onSourceClassesRemoved(self):
        to_remove = [s for s in self.mMapping.keys() if s not in self.mDst]
        for s in to_remove:
            self.mMapping.pop(s)

    def onDestinationClassesRemoved(self):
        dst = self.destination()
        to_remove = []
        for s, d in self.mMapping.items():
            if d not in dst:
                to_remove.append(s)
        for s in to_remove:
            self.mMapping.pop(s)
        pass


    def source(self) -> ClassificationScheme:
        return self.mSrc

    def rowCount(self, parent=None, *args, **kwargs):
        if not isinstance(self.mSrc, ClassificationScheme):
            return 0
        else:
            return len(self.mSrc)

    def summary(self) -> dict:
        s = dict()
        s['dstClassScheme'] = self.destination()
        LUT = dict()
        for c1, c2 in self.mMapping.items():
            LUT[c1.label()] = c2.label()
        s['labelLookup'] = LUT
        return s

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.mColumNames)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.mColumNames[section]
        return super(ReclassifyTableModel, self).headerData(section, orientation, role)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        col = index.column()
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if col == 1:
            flags |= Qt.ItemIsEditable
        return flags

    def data(self, index:QModelIndex, role=None):

        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if col == 0:
            idx0 = self.mSrc.index(row, 0)
            c = self.mSrc[row]
            assert isinstance(c, ClassInfo)
            if role == Qt.DisplayRole:
                return c.name()
            elif role == Qt.ToolTipRole:
                return 'Source class: {}'.format(c.name())
            elif role == Qt.DecorationRole:
                return c.icon()

        if col == 1:
            srcClass = self.mSrc[row]
            dstClass = self.mMapping.get(srcClass)
            if isinstance(dstClass, ClassInfo):
                if role == Qt.DisplayRole:
                    return dstClass.name()
                elif role == Qt.ToolTipRole:
                    return 'Destination class: {}'.format(dstClass.name())
                elif role == Qt.DecorationRole:
                    return dstClass.icon()

        return None

    def setData(self, index: QModelIndex, value, role=None):
        if not index.isValid():
            return False

        col = index.column()
        row = index.row()

        srcClass = self.mSrc[row]

        b = False
        if col == 1 and role == Qt.EditRole and isinstance(value, ClassInfo):
            if value in self.mDst[:]:
                self.mMapping[srcClass] = value
        if b:
            self.dataChanged.emit(index, index, [role])
        return b




class ReclassifyTableViewDelegate(QStyledItemDelegate):
    """

    """
    def __init__(self, tableView:QTableView, parent=None):
        assert isinstance(tableView, QTableView)
        super(ReclassifyTableViewDelegate, self).__init__(parent=parent)
        self.mTableView = tableView

    def sortFilterProxyModel(self) -> QSortFilterProxyModel:
        return self.mTableView.model()

    def reclassifyModel(self) -> ReclassifyTableModel:
        return self.sortFilterProxyModel().sourceModel()

    def setItemDelegates(self, tableView:QTableView):
        model = self.reclassifyModel()
        tableView.setItemDelegateForColumn(1, self)

    def createEditor(self, parent, option, index):
        pmodel = self.sortFilterProxyModel()
        tmodel = self.reclassifyModel()
        w = None
        tIdx = pmodel.mapToSource(index)
        assert isinstance(tIdx, QModelIndex)

        if index.isValid() and isinstance(tmodel, ReclassifyTableModel):
            if tIdx.column() == 1:
                w = ClassificationSchemeComboBox(classification=tmodel.destination(), parent=parent)
        return w

    def checkData(self, index, w, value):
        assert isinstance(index, QModelIndex)
        tModel = self.reclassifyModel()
        if index.isValid() and isinstance(tModel, ReclassifyTableModel):
            #  todo: any checks?
            self.commitData.emit(w)

    def setEditorData(self, editor, proxyIndex):

        tModel = self.reclassifyModel()
        index = self.sortFilterProxyModel().mapToSource(proxyIndex)
        assert isinstance(index, QModelIndex)

        if index.isValid() and isinstance(tModel, ReclassifyTableModel):
            if index.column() == 1:
                assert isinstance(editor, ClassificationSchemeComboBox)
                c = index.data(Qt.UserRole)
                editor.setCurrentClassInfo(c)

    def setModelData(self, w, bridge, proxyIndex):
        index = self.sortFilterProxyModel().mapToSource(proxyIndex)
        assert isinstance(index, QModelIndex)
        tModel = self.reclassifyModel()
        if index.isValid() and isinstance(tModel, ReclassifyTableModel):
            if index.column() == 1 and isinstance(w, ClassificationSchemeComboBox):
                tModel.setData(index, w.currentClassInfo(), Qt.EditRole)


class ReclassifyDialog(QDialog):
    """Constructor."""
    def __init__(self, parent=None):
        super(ReclassifyDialog, self).__init__(parent, Qt.Window)
        path = pathlib.Path(__file__).parent / 'reclassifydialog.ui'
        loadUi(path, self)

        assert isinstance(self.mapLayerComboBox, ClassificationMapLayerComboBox)
        assert isinstance(self.tableView, QTableView)
        assert isinstance(self.dstClassificationSchemeWidget, ClassificationSchemeWidget)

        self.mModel = ReclassifyTableModel()
        self.mProxyModel = QSortFilterProxyModel()
        self.mProxyModel.setSourceModel(self.mModel)
        self.tableView.setModel(self.mProxyModel)
        self.mTableViewDelegate = ReclassifyTableViewDelegate(self.tableView)
        self.mTableViewDelegate.setItemDelegates(self.tableView)

        self.mapLayerComboBox.setAllowEmptyLayer(True)
        self.mapLayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
        excluded = [p for p in QgsProviderRegistry.instance().providerList() if p not in ['gdal']]
        self.mapLayerComboBox.setExcludedProviders(excluded)
        self.mapLayerComboBox.setShowCrs(False)

        # now define all the logic behind the UI which can not be defined in the QDesigner
        assert isinstance(self.dstFileWidget, QgsFileWidget)
        self.dstFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        self.dstFileWidget.setConfirmOverwrite(True)


        assert isinstance(self.widgetOutputOptions, QgsRasterFormatSaveOptionsWidget)
        self.widgetOutputOptions.setType(QgsRasterFormatSaveOptionsWidget.Full)
        self.widgetOutputOptions.setProvider('gdal')
        self.widgetOutputOptions.setFormat('GTIFF')
        self.widgetOutputOptions.setRasterFileName('reclassifified.tif')
        self.dstFileWidget.fileChanged.connect(self.widgetOutputOptions.setRasterFileName)

        #self.dstClassificationSchemeWidget.classificationScheme().sigClassesAdded.connect(self.refreshTransformationTable)
        #self.dstClassificationSchemeWidget.classificationScheme().sigClassesRemoved.connect(self.refreshTransformationTable)
        self.mDstClassSchemeInitialized = False

        self.mapLayerComboBox.layerChanged.connect(self.onSourceRasterChanged)
        self.mapLayerComboBox.currentIndexChanged.connect(self.validate)


        self.btnSelectSrcfile.setDefaultAction(self.actionAddRasterSource)
        self.dstFileWidget.fileChanged.connect(self.validate)

        def onAddRaster(*args):
            filter = QgsProviderRegistry.instance().fileRasterFilters()
            file, filter = QFileDialog.getOpenFileName(filter=filter)

            if len(file) > 0:
                self.setSrcRasterLayer(file)

        self.actionAddRasterSource.triggered.connect(onAddRaster)
        self.onSourceRasterChanged()

    def onSourceRasterChanged(self):
        lyr = self.mapLayerComboBox.currentLayer()
        cs_final = ClassificationScheme()
        if isinstance(lyr, QgsRasterLayer):
            cs = ClassificationScheme.fromMapLayer(lyr)
            if isinstance(cs, ClassificationScheme) and len(cs) > 0:
                cs_final = cs
                if not self.mDstClassSchemeInitialized:
                    self.setDstClassificationScheme(cs)
                    self.mDstClassSchemeInitialized = True

        self.mModel.setSource(cs_final)
        self.validate()

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
        self.mModel.setDestination(self.dstClassificationSchemeWidget.classificationScheme())

    def dstClassificationScheme(self) -> ClassificationScheme:
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

    def dstRaster(self) -> str:
        """
        Returns the destination raster path
        :return: str
        """
        return self.dstFileWidget.filePath()

    def srcRasterLayer(self) -> QgsRasterLayer:
        lyr = self.mapLayerComboBox.currentLayer()
        if isinstance(lyr, QgsRasterLayer):
            return lyr
        else:
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

    def setSrcRasterLayer(self, src: QgsRasterLayer) -> bool:
        """
        Adds a new source raster
        :param src: object
        :return:
        """
        assert isinstance(src, QgsRasterLayer)
        QgsProject.instance().addMapLayer(src)
        assert isinstance(self.mapLayerComboBox, QgsMapLayerComboBox)
        for i in range(self.mapLayerComboBox.count()):
            if self.mapLayerComboBox.layer(i) == src:
                self.mapLayerComboBox.setCurrentIndex(i)
                return True
        return False

    def srcClassificationScheme(self) -> ClassificationScheme:
        """
        Reuturns the ClassificationScheme of the selected source raster
        :return: ClassificationScheme
        """
        lyr = self.srcRasterLayer()
        if isinstance(lyr, QgsRasterLayer):
            return ClassificationScheme.fromMapLayer(lyr)
        else:
            return None

    def createClassInfoComboBox(self, classScheme):
        assert isinstance(classScheme, ClassificationScheme)
        box = ClassificationSchemeComboBox(classification=classScheme)
        box.setAutoFillBackground(True)

        return box



    def validate(self):
        """
        Validates GUI inputs and enabled/disabled buttons accordingly.
        """
        isOk = True
        isOk &= len(self.mapLayerComboBox.currentText()) > 0
        isOk &= len(self.dstClassificationSchemeWidget.classificationScheme()) > 0
        isOk &= len(self.dstFileWidget.filePath()) > 0
        isOk &= self.mModel.rowCount() > 0

        btnAccept = self.buttonBox.button(QDialogButtonBox.Ok)
        btnAccept.setEnabled(isOk)


    def reclassificationSettings(self) -> dict:
        """
        Returns the re-classification settings
        :return: dict with {pathSrc:str, pathDst:str, labelLookup:dict, dstClassScheme:ClassificationScheme
        """
        summary = self.mModel.summary()
        summary['pathSrc'] = self.srcRasterLayer().source()
        summary['pathDst'] = self.dstRaster()
        return summary






