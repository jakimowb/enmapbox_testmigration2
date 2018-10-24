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

import os, json, pickle
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

MIMEDATA_KEY = 'hub-classscheme'

def hasClassification(pathOrDataset):
    """
    This function tests if a gdal-readable raster data set contains
    categorical information that can be used to retrieve a ClassificationScheme
    :param pathOrDataset: string | gdal.Dataset
    :return: True | False
    """

    if isinstance(pathOrDataset, gdal.Dataset):
        ds = pathOrDataset
    elif isinstance(pathOrDataset, str) and os.path.exists(pathOrDataset):
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


    def setLabel(self, label:int):
        """
        Sets the label value.
        :param label: int, must be >= 0
        """
        assert isinstance(label, int)
        assert label >= 0
        self.mLabel = label
        self.sigSettingsChanged.emit()

    def label(self)->int:
        """
        Returns the class label values
        :return: int
        """
        return self.mLabel

    def color(self)->QColor:
        """
        Returns the class color.
        :return: QColor
        """
        return QColor(self.mColor)

    def name(self)->str:
        """
        Returns the class name
        :return: str
        """
        return self.mName

    def setColor(self, color:QColor):
        """
        Sets the class color.
        :param color: QColor
        """
        assert isinstance(color, QColor)
        self.mColor = color
        self.sigSettingsChanged.emit()

    def setName(self, name:str):
        """
        Sets thes class name
        :param name: str
        """
        assert isinstance(name, str)
        self.mName = name
        self.sigSettingsChanged.emit()


    def pixmap(self, *args)->QPixmap:
        """
        Returns a QPixmap. Default size is 20x20px
        :param args: QPixmap arguments.
        :return: QPixmap
        """
        if len(args) == 0:
            args = (QSize(20, 20),)

        pm = QPixmap(*args)
        pm.fill(self.mColor)
        return pm

    def icon(self, *args)->QIcon:
        """
        Returns the class color as QIcon
        :param args: QPixmap arguments
        :return: QIcon
        """
        return QIcon(self.pixmap(*args))

    def clone(self):
        """
        Create a copy of this ClassInfo
        :return: ClassInfo
        """
        return ClassInfo(name=self.mName, color=self.mColor)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, ClassInfo):
            return False
        return other.mName == self.mName and \
               other.mLabel == self.mLabel and \
               other.mColor.getRgb() == self.mColor.getRgb()

    def __repr__(self):
        return 'ClassInfo' + self.__str__()

    def __str__(self):
        return '{} "{}" ({})'.format(self.mLabel, self.mName, self.mColor.name())

    def json(self)->str:
        return json.dumps([self.label(), self.name(), self.color().name()])

    def fromJSON(self, jsonString:str):
        try:
            label, name, color = json.loads(jsonString)
            color = QColor(color)
            return ClassInfo(label=label, name=name, color=color)
        except:
            return None

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
    def fromRasterBand(band:gdal.Band):
        """
        Reads the ClassificationScheme of a gdal.Band
        :param band: gdal.Band
        :return: ClassificationScheme, None if classes are undefined.
        """
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
        """
        Reads a ClassificationScheme from a gdal.Dataset
        :param path: str with path to gdal.Dataset or gdal.Dataset instances
        :param bandIndex: int with band index
        :return: ClassificationScheme
        """
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


    sigClassesRemoved = pyqtSignal(list, list)
    #sigClassRemoved = pyqtSignal(ClassInfo, int)
    #sigClassAdded = pyqtSignal(ClassInfo, int)
    sigClassesAdded = pyqtSignal(list, list)
    sigNameChanged = pyqtSignal(str)

    def __init__(self, name:str='Classification'):
        super(ClassificationScheme, self).__init__()
        self.mClasses = []
        self.mName = name


    def setName(self, name:str=''):
        b = name != self.mName
        self.mName = name
        if b:
            self.sigNameChanged.emit(self.mName)

    def name(self)->str:
        return self.mName

    def json(self)->str:
        data = {'name':self.mName,
                'classes':[(c.label(), c.name(), c.color().name()) for c in self]
                }

        return json.dumps(data)

    def pickle(self):
        return pickle.dumps(self.json())

    @staticmethod
    def fromPickle(pkl):
        try:
            jsonStr = pickle.loads(pkl)
            return ClassificationScheme.fromJSON(jsonStr)
        except Exception as ex:
            print(ex)
        return None


    @staticmethod
    def fromJSON(jsonStr:str):
        try:
            data = json.loads(jsonStr)
            cs = ClassificationScheme(name= data['name'])
            for classData in data['classes']:
                label, name, colorName = classData
                cs.addClass(ClassInfo(label=label, name=name, color=QColor(colorName)))
            return cs
        except Exception as ex:
            print(ex)
            return None


    def clear(self):
        """
        Removes all ClassInfos
        """
        removed = self.mClasses[:]
        del self.mClasses[:]
        self.sigClassesRemoved.emit(removed)

    def clone(self):
        """
        Create a copy of this ClassificationScheme
        :return:
        """
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
        """
        Removes multiple ClassInfo
        :param classes: [list-of-ClassInfo]
        """

        removedIndices = []
        for c in classes:
            assert c in self.mClasses
            removedIndices.append(self.mClasses.index(c))
        removedIndices = list(reversed(sorted(removedIndices)))
        removedClasses = []
        for i in removedIndices:
            c = self.mClasses[i]
            self.mClasses.remove(c)
            removedClasses.append(c)

        self.sigClassesRemoved.emit(removedClasses, removedIndices)

    def removeClass(self, c):
        """
        Removes a single ClassInfo.
        :param c: ClassInfo
        """
        self.removeClasses([c])

    def createClasses(self, n:int):
        """
        Creates n new classes with default initialization
        :param n: int, number of classes to add.
        """
        assert isinstance(n, int)
        assert n >= 0
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
        """
        Adds / inserts a list of ClassInfos
        :param classes: [list-of-ClassInfo]
        :param index: int, index to insert the first of the new classes.
                           defaults to len(ClassificationScheme)

        """
        if len(classes) > 0:
            if index is None:
                index = len(self.mClasses)

            index = max(index, 0)

            addedClasses = []
            addedIndices = []
            for i, c in enumerate(classes):
                assert isinstance(c, ClassInfo)
                j = index + i
                self.mClasses.insert(j, c)
                c.sigSettingsChanged.connect(self.onClassInfoSettingChanged)
                addedClasses.append(c)
                addedIndices.append(j)
            self.updateLabels()
                #self.sigClassAdded.emit(c,j)
            self.sigClassesAdded.emit(addedClasses, addedIndices)

    def updateLabels(self):
        for i, c in enumerate(self.mClasses):
            c.setLabel(i)

    sigClassInfoChanged = pyqtSignal(ClassInfo)

    def onClassInfoSettingChanged(self, *args):
        self.sigClassInfoChanged.emit(self.sender())

    def addClass(self, c, index=None):
        """
        Adds a ClassInfo
        :param c: ClassInfo
        :param index: int, index to add the ClassInfo. Defaults to the end.
        """
        assert isinstance(c, ClassInfo)
        self.addClasses([c], index=index)


    def saveToRaster(self, path, bandIndex=0):
        """
        Saves this ClassificationScheme to an raster image
        :param path: path (str) of raster image or gdal.Dataset instance
        :param bandIndex: band index of raster band to set this ClassificationScheme.
                          Defaults to 0 = the first band
        """
        if isinstance(path, str):
            ds = gdal.Open(path)
        elif isinstance(path, gdal.Dataset):
            ds = path

        assert isinstance(ds, gdal.Dataset)
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

    def toString(self, sep=';')->str:
        """
        A quick dump of all ClassInfos
        :param sep:
        :return: str
        """
        lines = [sep.join(['class_value', 'class_name', 'R', 'G', 'B', 'A'])]
        for classInfo in self.mClasses:
            c = classInfo.mColor
            info = [classInfo.mValue, classInfo.mName, c.red(), c.green(), c.blue(), c.alpha()]
            info = ['{}'.format(v) for v in info]

            lines.append(sep.join(info))
        return '\n'.join(lines)

    def saveToCsv(self, path, sep=';'):
        """
        Saves the ClassificationScheme as CSV table.
        :param path: str, path of CSV file
        :param sep: separator (';' by default)
        """
        lines = self.toString(sep=sep)
        with open(path, 'w') as f:
            f.write(lines)


    @staticmethod
    def fromCsv(path:str):
        """
        Read the ClassificationScheme from a CSV table
        :param path: str, path of CSV file
        :return: ClassificationScheme
        """
        raise NotImplementedError()

    def saveToQml(self, path):
        """
        Saves the class infos into a QML file
        :param path: str, path of QML file
        """
        raise NotImplementedError()

    @staticmethod
    def fromQml(path:str):
        """
        Reads a ClassificationScheme from a QML file.
        :param path: str, path to QML file
        :return: ClassificationScheme
        """
        raise NotImplementedError()

    @staticmethod
    def fromVectorLayer(layer:QgsVectorLayer, fieldClassName:str='classname'):
        """
        :param layer: QgsVectorLayer that contains a ClassificationScheme
        :param fieldClassName: field name with field that contains the class labels for which the ClassificationScheme is returned
        :return: ClassificationScheme
        """
        raise NotImplementedError('ClassificationScheme.fromVectorLayer(...)')


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


class ClassificationSchemeComboBox(QComboBox):

    def __init__(self, parent=None, classification:ClassificationScheme=None):
        super(ClassificationSchemeComboBox, self).__init__(parent)
        if not isinstance(classification, ClassificationScheme):
            classification = ClassificationScheme()
        self.mSchema = None
        self.mModel = None
        if classification:
            self.setClassificationScheme(classification)
        self.setModel(self.mModel)

    def setClassificationScheme(self, classScheme):

        if isinstance(classScheme, ClassificationScheme):
            self.mModel = ClassificationSchemeComboBoxItemModel(classScheme)
            self.setModel(self.mModel)
        else:
            self.mModel = None
            self.setModel(None)

    def classificationScheme(self)->ClassificationScheme:
        if isinstance(self.mModel, ClassificationSchemeComboBoxItemModel):
            pass

    def currentClassInfo(self)->ClassInfo:
        if isinstance(self.mModel, ClassificationSchemeComboBoxItemModel):
            i = self.currentIndex()
            if i >= 0 and i < len(self.m)


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
        self.scheme.sigClassesRemoved.connect(self.onClassesRemoved)
        self.scheme.sigClassesAdded.connect(self.onClassesAdded)

    def onClassesRemoved(self, classes, indices):
        for index in indices:
            self.beginRemoveRows(QModelIndex(), index, index)
            self.endRemoveRows()

    def onClassesAdded(self, classes, indices):

        self.beginResetModel()
        self.endResetModel()
        #self.beginInsertRows(QModelIndex(), index, index)
        #self.endInsertRows()

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
        if isinstance(index, QModelIndex):
            index = index.row()
        if isinstance(index, int):
            return self.scheme[index]
        return None

    def mimeData(self, indexes:list)->QMimeData:


        rows = []
        for idx in indexes:
            if isinstance(idx, QModelIndex) and idx.isValid():
                if idx.row() not in rows:
                    rows.append(idx.row())
        classes = [self.getClassInfoFromIndex(r) for r in rows]
        if len(classes) > 0:
            mimeData = QMimeData()
            cs = ClassificationScheme()
            cs.addClasses(classes)
            mimeData.setData(MIMEDATA_KEY, cs.pickle())
            mimeData.setText(cs.json())
            return mimeData
        return QMimeData()

    def dropMimeData(self, data:QMimeData, action:Qt.DropAction, row: int, column: int, parent: QModelIndex)->bool:

        if not parent.isValid():
            return False
        if not MIMEDATA_KEY in data.formats():
            return False

        try:
            cs = ClassificationScheme.fromPickle(bytes(data.data(MIMEDATA_KEY)))
            if len(cs) > 0:
                self.insertClasses(cs[:], i=row)
            return True
        except Exception as ex:
            print(ex)
            return False



    def canDropMimeData(self, data:QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex)->bool:
        if not parent.isValid():
            return False

        if MIMEDATA_KEY in data.formats():
            return True
        else:
            return False


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
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            #if columnName in [self.cLABEL, self.cNAME]:  # allow check state
            #    flags = flags | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            if columnName in [self.cNAME]:
                flags = flags | Qt.ItemIsEditable

            return flags
            # return item.qt_flags(index.column())
        return Qt.NoItemFlags

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

    sigValuesChanged = pyqtSignal()

    def __init__(self, parent=None, classificationScheme=None):
        super(ClassificationSchemeWidget, self).__init__(parent)
        self.setupUi(self)

        self.mScheme = ClassificationScheme()
        if classificationScheme is not None:
            self.setClassificationScheme(classificationScheme)

        self.schemeModel = ClassificationSchemeTableModel(self.mScheme, self)
        self.schemeModel.dataChanged.connect(lambda : self.sigValuesChanged())
        self.schemeModel.modelReset.connect(lambda : self.sigValuesChanged())
        self.schemeModel.rowsInserted.connect(lambda :self.sigValuesChanged())
        self.schemeModel.rowsRemoved.connect(lambda :self.sigValuesChanged())



        #self.tableClassificationScheme.verticalHeader().setMovable(True)
        assert isinstance(self.tableClassificationScheme, QTableView)
        #self.tableClassificationScheme.setAcceptDrops(True)
        #self.tableClassificationScheme.setDragDropMode(QAbstractItemView.InternalMove)
        #self.tableClassificationScheme.setDragEnabled(True)
        #self.tableClassificationScheme.setAcceptDrops(True)

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
        from enmapbox import enmapboxSettings
        settings = enmapboxSettings()
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


class ClassificationSchemeEditorWidgetWrapper(QgsEditorWidgetWrapper):

    def __init__(self, vl:QgsVectorLayer, fieldIdx:int, editor:QWidget, parent:QWidget):
        super(ClassificationSchemeEditorWidgetWrapper, self).__init__(vl, fieldIdx, editor, parent)

        self.mComboBox = None
        self.mDefaultValue = None

    def createWidget(self, parent: QWidget):
        #log('createWidget')
        w = ClassificationSchemeComboBox(parent)
        w.setVisible(True)
        return w

    def initWidget(self, editor:QWidget):
        #log(' initWidget')
        conf = self.config()

        if isinstance(editor, ClassificationSchemeComboBox):
            self.mComboBox = editor
            self.mComboBox.mModel.mScheme.clear()
            self.mComboBox.currentIndexChanged.connect(self.onValueChanged)
            #self.mComboBox.mModel.mScheme.addClasses()


    def onValueChanged(self, *args):
        self.valueChanged.emit(self.value())
        s = ""

    def valid(self, *args, **kwargs)->bool:
        return isinstance(self.mEditorWidget, ClassificationSchemeWidget) or isinstance(self.mComboBox, QComboBox)

    def value(self, *args, **kwargs):
        value = self.mDefaultValue
        if isinstance(self.mComboBox, ClassificationSchemeComboBox):
            v = self.mComboBox.selectedClassInfo()


        return value


    def setEnabled(self, enabled:bool):

        if self.mComboBox:
            self.mComboBox.setEnabled(enabled)


    def setValue(self, value):
        if isinstance(self.mComboBox, ClassificationSchemeComboBox):
            s = ""

        self.mDefaultValue = value


class ClassificationSchemeEditorConfigWidget(QgsEditorConfigWidget):

    def __init__(self, vl:QgsVectorLayer, fieldIdx:int, parent:QWidget):

        super(ClassificationSchemeEditorConfigWidget, self).__init__(vl, fieldIdx, parent)
        self.setupUi(self)

        self.mLastConfig = {}

    def config(self, *args, **kwargs)->dict:
        config = {'xUnitList':self.units('x'),
                  'yUnitList':self.units('y')
                  }
        return config

    def setConfig(self, config:dict):
        if 'xUnitList' in config.keys():
            self.setUnits('x', config['xUnitList'])

        if 'yUnitList' in config.keys():
            self.setUnits('y', config['yUnitList'])

        self.mLastConfig = config
        print('setConfig')

    def resetClassificationScheme(self):
        pass


class ClassificationSchemeWidgetFactory(QgsEditorWidgetFactory):

    def __init__(self, name:str):

        super(ClassificationSchemeWidgetFactory, self).__init__(name)

        self.mConfigurations = {}

    def configWidget(self, layer:QgsVectorLayer, fieldIdx:int, parent=QWidget)->ClassificationSchemeEditorConfigWidget:
        """
        Returns a SpectralProfileEditorConfigWidget
        :param layer: QgsVectorLayer
        :param fieldIdx: int
        :param parent: QWidget
        :return: SpectralProfileEditorConfigWidget
        """

        w = ClassificationSchemeEditorConfigWidget(layer, fieldIdx, parent)
        key = self.configKey(layer, fieldIdx)
        w.setConfig(self.readConfig(key))
        w.changed.connect(lambda : self.writeConfig(key, w.config()))
        return w

    def configKey(self, layer:QgsVectorLayer, fieldIdx:int):
        """
        Returns a tuple to be used as dictionary key to identify a layer field configuration.
        :param layer: QgsVectorLayer
        :param fieldIdx: int
        :return: (str, int)
        """
        return (layer.id(), fieldIdx)

    def create(self, layer:QgsVectorLayer, fieldIdx:int, editor:QWidget, parent:QWidget)->ClassificationSchemeEditorWidgetWrapper:
        """
        Create a ClassificationSchemeEditorWidgetWrapper
        :param layer: QgsVectorLayer
        :param fieldIdx: int
        :param editor: QWidget
        :param parent: QWidget
        :return: ClassificationSchemeEditorWidgetWrapper
        """
        w = ClassificationSchemeEditorWidgetWrapper(layer, fieldIdx, editor, parent)
        return w

    def writeConfig(self, key:tuple, config:dict):
        """
        :param key: tuple (str, int), as created with .configKey(layer, fieldIdx)
        :param config: dict with config values
        """
        self.mConfigurations[key] = config
        print('Save config')
        print(config)

    def readConfig(self, key:tuple):
        """
        :param key: tuple (str, int), as created with .configKey(layer, fieldIdx)
        :return: {}
        """
        if key in self.mConfigurations.keys():
            conf = self.mConfigurations[key]
        else:
            #return the very default configuration
            conf = {
            }
        print('Read config')
        print((key, conf))
        return conf

    def fieldScore(self, vl:QgsVectorLayer, fieldIdx:int)->int:
        """
        This method allows disabling this editor widget type for a certain field.
        0: not supported: none String fields
        5: maybe support String fields with length <= 400
        20: specialized support: String fields with length > 400

        :param vl: QgsVectorLayer
        :param fieldIdx: int
        :return: int
        """
        #log(' fieldScore()')
        field = vl.fields().at(fieldIdx)
        assert isinstance(field, QgsField)
        if field.type() == QVariant.String and field.name():
            return 20
        elif field.type() == QVariant.Int:
            return 20
        else:
            return 0 #no support



"""

EDITOR_WIDGET_REGISTRY_KEY = 'RasterClassification'
classificationSchemeEditorWidgetFactory = None
def registerClassificationSchemeEditorWidget():
    reg = QgsGui.editorWidgetRegistry()
    if not EDITOR_WIDGET_REGISTRY_KEY in reg.factories().keys():
        factory = ClassificationSchemeWidgetFactory(EDITOR_WIDGET_REGISTRY_KEY)
        reg.registerWidget(EDITOR_WIDGET_REGISTRY_KEY, factory)
    else:
        classificationSchemeEditorWidgetFactory = reg.factories()[EDITOR_WIDGET_REGISTRY_KEY]
"""