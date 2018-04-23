# -*- coding: utf-8 -*-

"""
***************************************************************************
    classificationscheme.py

    Methods and Objects to describe raster classifications
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
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
from osgeo import gdal
from enmapbox.gui.utils import loadUI, gdalDataset, nextColor

from itertools import cycle

DEFAULT_UNCLASSIFIEDCOLOR = QColor('black')
DEFAULT_FIRST_COLOR = QColor('#a6cee3')

def hasClassification(pathOrDataset):
    """
    This function tests if a gdal-readable raster data set contains
    categorical information that can be used to retrieve a ClassificationScheme
    :param pathOrDataset: string | gdal.Dataset
    :return: True | False
    """

    if isinstance(pathOrDataset, gdal.Dataset):
        ds = pathOrDataset
    elif (isinstance(pathOrDataset, str) or isinstance(pathOrDataset, unicode)) \
            and os.path.exists(pathOrDataset):
        ds = gdal.Open(pathOrDataset)
    else:
        return False

    for b in range(ds.RasterCount):
        band = ds.GetRasterBand(b + 1)
        assert isinstance(band, gdal.Band)
        if band.GetCategoryNames() or band.GetColorTable():
            return True
    return False


def getTextColorWithContrast(c):
    assert isinstance(c, QColor)
    if c.lightness() < 0.5:
        return QColor('white')
    else:
        return QColor('black')


class ClassInfo(QObject):
    sigSettingsChanged = pyqtSignal()

    def __init__(self, label=0, name=None, color=None, parent=None):
        super(ClassInfo, self).__init__(parent)

        if name is None:
            name = 'Unclassified' if label == 0 else 'Class {}'.format(label)

        if color is None:
            if label == 0:
                color = DEFAULT_UNCLASSIFIEDCOLOR
            else:
                color = DEFAULT_FIRST_COLOR


        self.mName = name
        self.mLabel = label
        self.mColor = color
        if color:
            self.setColor(color)

    def setLabel(self, label):
        assert isinstance(label, int)
        assert label >= 0
        self.mLabel = label
        self.sigSettingsChanged.emit()

    def label(self):
        return self.mLabel

    def color(self):
        return QColor(self.mColor)

    def name(self):
        return self.mName

    def setColor(self, color):
        assert isinstance(color, QColor)
        self.mColor = color
        self.sigSettingsChanged.emit()

    def setName(self, name):
        assert isinstance(name, str)
        self.mName = name
        self.sigSettingsChanged.emit()

    def icon(self, *args):
        if len(args) == 0:
            args = (QSize(20, 20),)

        pm = QPixmap(*args)
        pm.fill(self.mColor)
        return QIcon(pm)

    def clone(self):
        return ClassInfo(name=self.mName, color=self.mColor)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, ClassInfo):
            return False
        return other.mName == self.mName and \
               other.mLabel == self.mLabel and \
               other.mColor == self.mColor

    def __repr__(self):
        return 'ClassInfo' + self.__str__()

    def __str__(self):
        return '{} "{}"'.format(self.mLabel, self.mName, str(self.mColor.toRgb()))


class ClassificationScheme(QObject):
    @staticmethod
    def create(n):
        """
        Create a ClassificationScheme with n classes (including 'Unclassified' with label = 0)
        :param n: number of classes including 'Unclassified'
        :return: ClassificationScheme
        """
        s = ClassificationScheme()
        s.createClasses(n)
        return s

    @staticmethod
    def fromRasterBand(band):
        assert isinstance(band, gdal.Band)
        cat = band.GetCategoryNames()
        ct = band.GetColorTable()
        if cat is None or len(cat) == 0:
            return None
        scheme = ClassificationScheme()
        classes = []
        for i, catName in enumerate(cat):
            cli = ClassInfo(name=catName, label=i)
            if ct is not None:
                cli.setColor(QColor(*ct.GetColorEntry(i)))
            classes.append(cli)
        scheme.addClasses(classes)
        return scheme


    @staticmethod
    def fromRasterImage(path, bandIndex=None):
        ds = gdalDataset(path)
        assert ds is not None

        if bandIndex is None:
            for b in range(ds.RasterCount):
                band = ds.GetRasterBand(b + 1)
                cat = band.GetCategoryNames()

                if cat != None:
                    bandIndex = b
                    break
                s = ""
            if bandIndex is None:
                return None


        assert bandIndex >= 0 and bandIndex < ds.RasterCount
        band = ds.GetRasterBand(bandIndex + 1)
        return ClassificationScheme.fromRasterBand(band)

    @staticmethod
    def fromVectorFile(self, path, fieldClassName='classname', fieldClassColor='classColor'):
        raise NotImplementedError('ClassificationScheme.fromVectorFile(...)')

    sigClassesRemoved = pyqtSignal(list)
    sigClassRemoved = pyqtSignal(ClassInfo, int)
    sigClassAdded = pyqtSignal(ClassInfo, int)
    sigClassesAdded = pyqtSignal(list)

    def __init__(self):
        super(ClassificationScheme, self).__init__()
        self.mClasses = []

    def clear(self):
        removed = self.mClasses[:]
        del self.mClasses[:]

    def clone(self):
        cs = ClassificationScheme()
        classes = [c.clone() for c in self.mClasses]
        cs.addClasses(classes)
        return cs

    def __getitem__(self, slice):
        return self.mClasses[slice]

    def __delitem__(self, slice):
        classes = self[slice]
        self.removeClasses(classes)

    def __contains__(self, item):
        return item in self.mClasses

    def __len__(self):
        return len(self.mClasses)

    def __iter__(self):
        return iter(self.mClasses)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not (isinstance(other, ClassificationScheme) and len(self) == len(other)):
            return False
        return all(self[i] == other[i] for i in range(len(self)))

    def __str__(self):
        return self.__repr__() + '{} classes'.format(len(self))

    def range(self):
        """
        Returns the class label range (min,max)
        """
        labels = self.classLabels()
        return min(labels), max(labels)

    def index(self, classInfo):
        """
        returns the index of this classInfo
        :param classInfo:
        :return: int
        """
        assert isinstance(classInfo, ClassInfo)
        return self.mClasses.index(classInfo)

    def classNames(self):
        """
        :return: [list-of-class-names (str)]
        """
        return [str(c.mName) for c in self.mClasses]

    def classColors(self):
        """
        :return: [list-of-class-colors (QColor)]
        """
        return [QColor(c.mColor) for c in self.mClasses]

    def classColorArray(self):
        """
        Returns the RGBA class-colors as array [nClasses,4]
        """
        return np.asarray([c.color().getRgb() for c in self])

    def gdalColorTable(self):
        """
        Returns the GDAL Color Table related to this classScheme
        :return: gdal.Colortable
        """
        ct = gdal.ColorTable()
        for i, c in enumerate(self):
            assert isinstance(c, ClassInfo)
            ct.SetColorEntry(i, c.mColor.getRgb())
        return ct

    def classLabels(self):
        """
        :return: [list-of-class-labels (int)]
        """
        return [c.mLabel for c in self.mClasses]

    def resetLabels(self):
        """
        Resets class labels to the classInfo position within the classSchema
        """
        for i, c in enumerate(self.mClasses):
            c.setLabel(i)

    def removeClasses(self, classes):
        for c in classes:
            assert c in self.mClasses
            i = self.mClasses.index(c)
            self.mClasses.remove(c)
            self.sigClassRemoved.emit(c, i)
        self.sigClassesRemoved.emit(classes[:])

    def removeClass(self, c):
        self.removeClasses([c])

    def createClasses(self, n):
        for i in range(n):
            l = len(self)
            if l == 0:
                color = QColor('black')
                name = 'Unclassified'
            else:
                if l == 1:
                    color = DEFAULT_FIRST_COLOR
                else:
                    color = nextColor(self[-1].color())
                name = 'Class {}'.format(l)
            c = ClassInfo(label=l, name=name, color=color)
            self.addClass(c)


    def addClasses(self, classes, index=None):
        if len(classes) > 0:
            if index is None:
                index = len(self.mClasses)
            addedClasses = []
            for i, c in enumerate(classes):
                assert isinstance(c, ClassInfo)
                j = index + i
                c.setLabel(j)
                c.sigSettingsChanged.connect(self.onClassInfoSettingChanged)
                addedClasses.append(c)
                self.mClasses.insert(j, c)
                self.sigClassAdded.emit(c,j)
            self.sigClassesAdded.emit(addedClasses)

    sigClassInfoChanged = pyqtSignal(ClassInfo)

    def onClassInfoSettingChanged(self, *args):
        self.sigClassInfoChanged.emit(self.sender())

    def addClass(self, c, index=None):
        assert isinstance(c, ClassInfo)
        self.addClasses([c], index=index)

    def saveToRaster(self, path, bandIndex=0):

        ds = gdal.Open(path)
        assert ds is not None
        assert ds.RasterCount < bandIndex
        band = ds.GetRasterBand(bandIndex + 1)
        ct = gdal.ColorTable()
        cat = []
        for i, classInfo in enumerate(self.mClasses):
            c = classInfo.mColor
            cat.append(classInfo.mName)
            assert isinstance(c, QColor)
            rgba = (c.red(), c.green(), c.blue(), c.alpha())
            ct.SetColorEntry(i, *rgba)

        band.SetColorTable(ct)
        band.SetCategoryNames(cat)

        ds = None

    def toString(self, sep=';'):
        lines = [sep.join(['class_value', 'class_name', 'R', 'G', 'B', 'A'])]
        for classInfo in self.mClasses:
            c = classInfo.mColor
            info = [classInfo.mValue, classInfo.mName, c.red(), c.green(), c.blue(), c.alpha()]
            info = ['{}'.format(v) for v in info]

            lines.append(sep.join(info))
        return '\n'.join(lines)

    def saveToCsv(self, path, sep=';'):
        lines = self.toString(sep=sep)
        file = open(path, 'w')
        file.write(lines)
        file.close()


class ClassificationSchemeComboBoxItemModel(QAbstractListModel):
    def __init__(self, scheme, parent=None):
        super(ClassificationSchemeComboBoxItemModel, self).__init__(parent)
        assert isinstance(scheme, ClassificationScheme)
        self.mScheme = scheme

        self.mScheme.sigClassesAdded.connect(self.onClassesInserted)
        self.mScheme.sigClassesRemoved.connect(self.onClassRemoved)
        self.mScheme.sigClassInfoChanged.connect(self.onClassInfoChanged)

    def onClassInfoChanged(self, classInfo):
        i = self.mScheme.index(classInfo)
        idx = self.createIndex(i, 0)
        self.dataChanged.emit(idx, idx)

    def onClassesInserted(self, classes, index=None):
        classes = [c for c in classes if c in self.mScheme]

        for c in classes:
            i = self.mScheme.index(c)
            self.beginInsertRows(QModelIndex(), i, i)
            self.endInsertRows()

    def onClassRemoved(self, classInfo, index):
        assert isinstance(classInfo, ClassInfo)
        assert isinstance(index, int)
        self.beginRemoveRows(QModelIndex(), index, index)
        self.endInsertRows()


    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.mScheme)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def getClassInfoFromIndex(self, index):
        if index.isValid():
            return self.mScheme[index.row()]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if (index.row() >= len(self.mScheme)) or (index.row() < 0):
            return None

        classInfo = self.getClassInfoFromIndex(index)
        value = None
        if role == Qt.DisplayRole:
            value = '{} {}'.format(classInfo.mLabel, classInfo.mName)
        if role == Qt.DecorationRole:
            value = classInfo.icon(QSize(20, 20))

        if role == Qt.UserRole:
            value = classInfo
        return value


class ClassificationSchemeTableModel(QAbstractTableModel):
    def __init__(self, scheme, parent=None):
        self.cLABEL = 'Label'
        self.cNAME = 'Name'
        self.cCOLOR = 'Color'
        self.columnNames = [self.cLABEL, self.cNAME, self.cCOLOR]
        assert isinstance(scheme, ClassificationScheme)
        super(ClassificationSchemeTableModel, self).__init__(parent)

        self.valLabel = QIntValidator(0, 99999)

        self.mSchema0 = scheme.clone()
        self.scheme = scheme
        self.scheme.sigClassRemoved.connect(self.onClassRemoved)
        self.scheme.sigClassAdded.connect(self.onClassAdded)

    def onClassRemoved(self, classInfo, index):
        assert isinstance(classInfo, ClassInfo)
        assert classInfo not in self.scheme
        assert isinstance(index, int)
        self.beginRemoveRows(QModelIndex(), index, index)
        self.endRemoveRows()

    def onClassAdded(self, classInfo, index):
        assert isinstance(classInfo, ClassInfo)
        assert isinstance(index, int)
        self.beginInsertRows(QModelIndex(), index, index)
        self.endInsertRows()

    def removeClasses(self, classes):
        self.scheme.removeClasses(classes)


    def insertClasses(self, classes, i=None):
        self.scheme.addClasses(classes, index=i)

    def insertClass(self, c, i=None):
        assert isinstance(c, ClassInfo)
        self.insertClasses([c], i=i)

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.scheme.clear()
        self.endRemoveRows()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.scheme)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columnNames)

    def getIndexFromClassInfo(self, classInfo):
        return self.createIndex(self.scheme.mClasses.index(classInfo), 0)

    def getClassInfoFromIndex(self, index):
        if index.isValid():
            return self.scheme[index.row()]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if role is None or not index.isValid():
            return None

        columnName = self.columnNames[index.column()]

        classInfo = self.getClassInfoFromIndex(index)
        assert isinstance(classInfo, ClassInfo)

        value = None
        if role == Qt.DisplayRole:
            if columnName == self.cLABEL:
                value = classInfo.mLabel
            elif columnName == self.cNAME:
                value = classInfo.mName
            elif columnName == self.cCOLOR:
                value = classInfo.mColor
            else:
                s = ""
        if role == Qt.BackgroundRole:
            if columnName == self.cCOLOR:
                return QBrush(classInfo.mColor)
        if role == Qt.ForegroundRole:
            if columnName == self.cCOLOR:
                return getTextColorWithContrast(classInfo.mColor)
        if role == Qt.EditRole:
            if columnName == self.cLABEL:
                value = classInfo.mLabel
            elif columnName == self.cNAME:
                value = classInfo.mName

        if role == Qt.UserRole:
            return classInfo
        return value

    def setData(self, index, value, role=None):
        if role is None or not index.isValid():
            return None

        columnName = self.columnNames[index.column()]

        classInfo = self.getClassInfoFromIndex(index)
        assert isinstance(classInfo, ClassInfo)

        if role == Qt.EditRole:
            if columnName == self.cNAME and len(value) > 0:
                # do not accept empty strings
                classInfo.setName(str(value))
                return True
            if columnName == self.cCOLOR and isinstance(value, QColor):
                classInfo.setColor(value)
                return True
            if columnName == self.cLABEL and \
                            self.valLabel.validate(str(value), 0)[0] == QValidator.Acceptable:
                classInfo.setLabel(int(value))
                return True
        return False

    def sort(self, col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        columnName = self.columnNames[col]
        rev = order == Qt.DescendingOrder

        if columnName == self.cLABEL:
            self.scheme.mClasses.sort(key=lambda c: c.mLabel, reverse=rev)
        if columnName == self.cNAME:
            self.scheme.mClasses.sort(key=lambda c: c.mName, reverse=rev)

        self.layoutChanged.emit()

    def flags(self, index):
        if index.isValid():
            columnName = self.columnNames[index.column()]
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
            if columnName in [self.cLABEL, self.cNAME]:  # allow check state
                flags = flags | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            return flags
            # return item.qt_flags(index.column())
        return None

    def headerData(self, col, orientation, role):
        if Qt is None:
            return None
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columnNames[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None


class ClassificationWidgetDelegates(QStyledItemDelegate):
    def __init__(self, tableView, parent=None):
        assert isinstance(tableView, QTableView)
        super(ClassificationWidgetDelegates, self).__init__(parent=parent)
        self.tableView = tableView
        self.tableView.doubleClicked.connect(self.onDoubleClick)
        # self.tableView.model().rowsInserted.connect(self.onRowsInserted)

    def onDoubleClick(self, idx):
        model = self.tableView.model()
        classInfo = model.getClassInfoFromIndex(idx)
        if idx.column() == model.columnNames.index(model.cCOLOR):

            w1 = QColorDialog(classInfo.mColor, self.tableView)
            w1.exec_()
            if w1.result() == QDialog.Accepted:
                c = w1.getColor()
                model.setData(idx, c, role=Qt.EditRole)

    def getColumnName(self, index):
        assert index.isValid()
        assert isinstance(index.model(), ClassificationSchemeTableModel)
        return index.model().columnNames[index.column()]

    def createEditor(self, parent, option, index):
        cname = self.getColumnName(index)
        model = index.model()
        assert isinstance(model, ClassificationSchemeTableModel)
        w = None
        if False and cname == model.cCOLOR:
            classInfo = model.getClassInfoFromIndex(index)
            w = QgsColorButton(parent, 'Class {}'.format(classInfo.mName))
            w.setColor(QColor(index.data()))
            w.colorChanged.connect(lambda: self.commitData.emit(w))
        return w

    def setEditorData(self, editor, index):
        cname = self.getColumnName(index)
        model = index.model()
        assert isinstance(model, ClassificationSchemeTableModel)

        classInfo = model.getClassInfoFromIndex(index)
        assert isinstance(classInfo, ClassInfo)
        if False and cname == model.cCOLOR:
            lastColor = classInfo.mColor
            assert isinstance(editor, QgsColorButton)
            assert isinstance(lastColor, QColor)
            editor.setColor(QColor(lastColor))
            editor.setText('{},{},{}'.format(lastColor.red(), lastColor.green(), lastColor.blue()))

    def setModelData(self, w, model, index):
        cname = self.getColumnName(index)
        model = index.model()
        assert isinstance(model, ClassificationSchemeTableModel)

        if False and cname == model.cCOLOR:
            assert isinstance(w, QgsColorButton)
            if index.data() != w.color():
                model.setData(index, w.color(), Qt.EditRole)


class ClassificationSchemeWidget(QWidget, loadUI('classificationscheme.ui')):
    def __init__(self, parent=None, classificationScheme=None):
        super(ClassificationSchemeWidget, self).__init__(parent)
        self.setupUi(self)

        self.mScheme = ClassificationScheme()
        self.schemeModel = ClassificationSchemeTableModel(self.mScheme, self)

        if classificationScheme is not None:
            self.setClassificationScheme(classificationScheme)


        #self.tableClassificationScheme.verticalHeader().setMovable(True)
        self.tableClassificationScheme.verticalHeader().setDragEnabled(True)
        self.tableClassificationScheme.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)
        #self.tableClassificationScheme.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.tableClassificationScheme.setModel(self.schemeModel)
        self.tableClassificationScheme.doubleClicked.connect(self.onTableDoubleClick)
        self.tableClassificationScheme.resizeColumnsToContents()
        self.selectionModel = QItemSelectionModel(self.schemeModel)
        self.selectionModel.selectionChanged.connect(self.onSelectionChanged)
        self.onSelectionChanged()  # enable/disabel widgets depending on a selection
        self.tableClassificationScheme.setSelectionModel(self.selectionModel)

        # self.delegate = ClassificationWidgetDelegates(self.tableClassificationScheme)
        # self.tableClassificationScheme.setItemDelegateForColumn(2, self.delegate)


        self.btnLoadClasses.clicked.connect(self.loadClasses)
        self.btnRemoveClasses.clicked.connect(self.removeSelectedClasses)
        self.btnAddClasses.clicked.connect(lambda: self.createClasses(1))

    def onTableDoubleClick(self, idx):
        model = self.tableClassificationScheme.model()
        classInfo = model.getClassInfoFromIndex(idx)
        if idx.column() == model.columnNames.index(model.cCOLOR):
            c = QColorDialog.getColor(classInfo.mColor, self.tableClassificationScheme, \
                                      'Set class color')
            model.setData(idx, c, role=Qt.EditRole)

    def onSelectionChanged(self, *args):
        self.btnRemoveClasses.setEnabled(self.selectionModel is not None and
                                         len(self.selectionModel.selectedRows()) > 0)

    def createClasses(self, n):
        classes = []
        #s = ClassificationScheme()
        #s.createClasses(n)
        self.mScheme.createClasses(n)
        #self.schemeModel.insertClasses(s[:])

    def removeSelectedClasses(self):
        model = self.tableClassificationScheme.model()
        indices = reversed(self.selectionModel.selectedRows())
        classes = [self.schemeModel.getClassInfoFromIndex(idx) for idx in indices]
        self.schemeModel.removeClasses(classes)

    def loadClasses(self, *args):
        from enmapbox.gui.settings import qtSettingsObj
        settings = qtSettingsObj()
        settingsKey = 'DEF_DIR_ClassificationSchemeWidget.loadClasses'
        defDir = settings.value(settingsKey, None)
        path, _ = QFileDialog.getOpenFileName(self, 'Select Raster File', directory=defDir)
        if os.path.exists(path):
            settings.setValue(settingsKey, os.path.dirname(path))
            try:
                scheme = ClassificationScheme.fromRasterImage(path)
                if scheme is not None:
                    self.appendClassificationScheme(scheme)
            except Exception as ex:
                QMessageBox.critical(self, "Unable to load class info", str(ex))


    def appendClassificationScheme(self, classificationScheme):
        assert isinstance(classificationScheme, ClassificationScheme)
        self.schemeModel.insertClasses([c for c in classificationScheme])

    def setClassificationScheme(self, classificationScheme):
        assert isinstance(classificationScheme, ClassificationScheme)
        self.schemeModel.clear()
        self.appendClassificationScheme(classificationScheme)

    def classificationScheme(self):
        return self.mScheme


class ClassificationSchemeDialog(QgsDialog):
    @staticmethod
    def getClassificationScheme(*args, **kwds):
        """
        Opens a dialog to edit a ClassificationScheme
        :param args:
        :param kwds:
        :return: None | ClassificationScheme
        """
        d = ClassificationSchemeDialog(*args, **kwds)
        d.exec_()

        if d.result() == QDialog.Accepted:
            return d.classificationScheme()
        else:
            return None

    def __init__(self, parent=None, classificationScheme=None, title='Specify Classification Scheme'):
        super(ClassificationSchemeDialog, self).__init__(parent=parent, \
                                                         buttons=QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.w = ClassificationSchemeWidget(parent=self, classificationScheme=classificationScheme)
        self.setWindowTitle(title)
        self.btOk = QPushButton('Ok')
        self.btCancel = QPushButton('Cancel')
        buttonBar = QHBoxLayout()
        # buttonBar.addWidget(self.btCancel)
        # buttonBar.addWidget(self.btOk)
        l = self.layout()
        l.addWidget(self.w)
        l.addLayout(buttonBar)
        # self.setLayout(l)

        if isinstance(classificationScheme, ClassificationScheme):
            self.setClassificationScheme(classificationScheme)
        s = ""

    def classificationScheme(self):
        return self.w.classificationScheme()

    def setClassificationScheme(self, classificationScheme):
        assert isinstance(classificationScheme, ClassificationScheme)
        self.w.setClassificationScheme(classificationScheme)


if __name__ == '__main__':

    from enmapbox.gui.utils import initQgisApplication

    app = initQgisApplication()
    scheme = ClassificationSchemeDialog.getClassificationScheme()
    ci = ClassificationScheme.create(4)
    print(ci.classColorArray())

    app.exec_()
