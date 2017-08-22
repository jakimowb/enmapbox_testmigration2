# -*- coding: utf-8 -*-

"""
***************************************************************************
    metadataeditorapp/metadataeditor.py

    Package definition.
    ---------------------
    Date                 : August 2017
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

from qgis.gui import QgsFileWidget, QgsRasterFormatSaveOptionsWidget

import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyqtgraph.Qt import QtCore, QtGui

from hub.gdal.api import *

app = QtGui.QApplication([])
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from enmapbox.gui.enmapboxgui import EnMAPBox

from objbrowser import browse

import time

class NoDataValue(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'str'
        opts['value'] = 0
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChild({'name': 'Image NoData Value', 'type': opts['type'], 'value': opts['value'], 'siPrefix': True})
        self.a = self.param('Image NoData Value')

    def getParameter(self):
        return self.a

class DefaultBands(pTypes.GroupParameter):
    def __init__(self, dataset, rastercount, **opts):
        #opts['type'] = 'int'
        #opts['value'] = 0
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChildren([
            {'name': 'Red', 'type': 'int', 'value': dataset[0], 'limits': (0, rastercount)},
            {'name': 'Green', 'type': 'int', 'value': dataset[1], 'limits': (0, rastercount)},
            {'name': 'Blue', 'type': 'int', 'value': dataset[2], 'limits': (0, rastercount)},
            {'name': 'Alpha', 'type': 'int', 'value': dataset[3], 'limits': (0, rastercount)},
        ])

        self.redParam = self.param('Red')
        self.greenParam = self.param('Green')
        self.blueParam = self.param('Blue')
        self.alphaParam = self.param('Alpha')

    def getRedParameter(self):
        return self.redParam

    def getGreenParameter(self):
        return self.greenParam

    def getBlueParameter(self):
        return self.blueParam

    def getAlphaParameter(self):
        return self.alphaParam

class Bands(pTypes.GroupParameter):
    def __init__(self, dataset, ind, **opts):

        c = [
            dict(name = 'Band Number', type = 'str', value = str(ind), readonly = True),
            dict(name = 'Band Name', type = 'str', value = dataset.GetDescription(), readonly = True),
            dict(name = 'Wavelength', type = 'str', value = dataset.GetMetadataItem('wavelength'), readonly = True),
            dict(name = 'Wavelength Unit', type = 'str', value = dataset.GetMetadataItem('wavelength_units'), readonly = True),
            dict(name = 'Band NoData Value', type = 'str', value = dataset.GetNoDataValue(), readonly = False),
        ]

        opts['type'] = 'group'
        opts['children'] = c

        pTypes.GroupParameter.__init__(self, **opts)

        self.a = self.param('Band NoData Value')

    def getParameter(self):
        return self.a

## This is the list of free metadata domains
class FreeMetadataDomains(pTypes.GroupParameter):
    def __init__(self, dataset, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add Domain"
        opts['renamable'] = True
        opts['removable'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        if dataset != None:
            a = dataset.GetMetadataDomainList()
            for index in range(0, len(a) - 1):
                theseChildren = dataset.GetMetadata(domain=a[index])
                orderedChildren = collections.OrderedDict(sorted(theseChildren.items()))

                data = FreeMetadata(name=a[index], dataset=orderedChildren)

                self.addChild(data)

    def addNew(self):
        self.addChild(FreeMetadata(name="New Domain %d" % (len(self.childs) + 1), dataset = None))

## This is a list of metadata within a domain
class FreeMetadata(pTypes.GroupParameter):
    def __init__(self, dataset, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add Parameter"
        pTypes.GroupParameter.__init__(self, **opts)

        if dataset != None:
            for jndex in range(0, len(dataset)):
                self.addChild({'name': str(dataset.keys()[jndex]), 'type': 'str',
                         'value': dataset.values()[jndex], 'readonly': False, 'renamable': True,
                         'removable': True})

    def addNew(self):
        self.addChild(dict(name="New Parameter %d" % (len(self.childs) + 1), type='str', value='', removable=True,
                            renamable=True))


class Win(QtGui.QDialog):

    inDS = None

    params = []

    bandNoDataValues = []
    nodataValue = None

    ndv = None
    bandc2 = []

    generalChildren = []
    crsChildren = []
    otherChildren = []

    redBand = None
    greenBand = None
    blueBand = None
    alphaBand = None

    t = ParameterTree()

    def __init__(self, parent=None):
        super(Win, self).__init__(parent=parent)

        self.setLayout(QtGui.QGridLayout())
        layout = self.layout()

        # select input file name via QFileDialog in case the file is not open in the enmap box yet
        self.inputFile = QComboBox()
        self.inputFile.currentIndexChanged.connect(lambda: self.comboIndexChanged())

        self.selectInputFile = QPushButton('...')
        self.selectInputFile.clicked.connect(lambda: self.fileFound(self.inputFile))

        savebtn = QPushButton("Save Changes")
        savebtn.clicked.connect(self.saveMetadata)

        # select input file name via QFileDialog in case the file is not open in the enmap box yet
        closebtn = QPushButton("Discard/Close ERROR")
        closebtn.clicked.connect(self.close)

        layout.addWidget(QtGui.QLabel("Select file and view/edit related metadata."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile, 1, 6, 1, 2)
        layout.addWidget(self.t, 2, 0, 1, 8)
        layout.addWidget(savebtn, 3, 0, 1, 4)
        layout.addWidget(closebtn, 3, 4, 1, 4)

        self.resize(600,600)

        enmapBox = EnMAPBox.instance()

        if isinstance(enmapBox, EnMAPBox):
            for src in sorted(enmapBox.dataSources('RASTER')):
                self.addSrcRaster(src)

    def addSrcRaster(self, src):
        addedItems = [self.inputFile.itemData(i, role=Qt.UserRole) for
            i in range(self.inputFile.count())]
        if src not in addedItems: #hasClassification(src) and src not in addedItems:
            bn = os.path.basename(src)
            self.inputFile.addItem(src) #(bn, src)
        self.validatePath(src)

    def fileFound(self, inputFile):
        self.inputFile.addItem(QFileDialog.getOpenFileName(self, 'Input image', directory = "/Workspaces/QGIS-Plugins/enmap-box/enmapbox/testdata"))
        counter = self.inputFile.count()
        self.inputFile.setCurrentIndex(counter - 1)

    def comboIndexChanged(self):
        if self.validatePath(str(self.inputFile.currentText())):
            self.inDS = gdal.Open(str(self.inputFile.currentText()))
            params = self.setMetadataTree()
            self.populateMetadata(params)

    def ndvChanged(self, i, data):
        try:
            float(data)
            for index in range(0, len(self.bandc2)):
                self.bandc2[index].getParameter().setValue(self.ndv.getParameter().value())

        except ValueError:
            True

    def bandNdvChanged(self, i, data):
        print(self.ndv.getParameter().value())
        if data != self.ndv.getParameter().value():
            self.ndv.getParameter().setValue(str('is defined per band. type here to set nodata value for all bands.'))

    def defaultRedChanged(self, i, data):
        self.redBand = data
        print "red changed"

    def defaultGreenChanged(self, i, data):
        self.greenBand = data
        print "green changed"

    def defaultBlueChanged(self, i, data):
        self.blueBand = data
        print "blue changed"

    def defaultAlphaChanged(self, i, data):
        self.alphaBand = data
        print "alpha changed"

    def setMetadataTree(self):
        from osgeo import osr

        start = time.time()

        ####Initialise parameter collection
        self.params = [
            {'name': 'General', 'type': 'group', 'children': []},
            {'name': 'Image NoData Value', 'type': 'group', 'children': []},
            {'name': 'Coordinate Reference System', 'type': 'group', 'children': []},
            {'name': 'Bands', 'type': 'group', 'children': []},
            {'name': 'Free Metadata by Domain (right click to rename and remove)', 'type': 'group', 'children': []}
        ]

        # Set projection related metadata
        prj = self.inDS.GetProjection()
        srs = osr.SpatialReference(wkt=prj)

        if (srs.GetAuthorityName('projcs') and srs.GetAuthorityCode('projcs')):
            id = srs.GetAuthorityName('projcs') + srs.GetAuthorityCode('projcs')
        else:
            id = ''

        xmin = self.inDS.GetGeoTransform()[0] - self.inDS.GetGeoTransform()[2]
        ymin = self.inDS.GetGeoTransform()[3] - self.inDS.GetGeoTransform()[4]
        xmax = xmin + self.inDS.RasterXSize * self.inDS.GetGeoTransform()[1]
        ymax = ymin + self.inDS.RasterXSize * self.inDS.GetGeoTransform()[5]
        boundingBox = [xmin, ymin, xmax, ymax]

        self.crsChildren = [
            {'name': 'Name', 'type': 'str', 'value': srs.GetAttrValue('projcs'), 'readonly': True},
            {'name': 'AuthID', 'type': 'str', 'value': id, 'readonly': True},
            {'name': 'Datum', 'type': 'str', 'value': srs.GetAttrValue('datum'), 'readonly': True},
            {'name': 'Spheroid', 'type': 'str', 'value': srs.GetAttrValue('spheroid'), 'readonly': True},
            {'name': 'Map Units', 'type': 'str', 'value': srs.GetAttrValue('unit'), 'readonly': True},
            {'name': 'Bounding Box', 'type': 'str', 'value': str(boundingBox), 'readonly': True},
        ]

        # if srs.IsProjected:
        # crsChildren.append({'name': 'False Easting', 'type': 'str', 'value': srs.GetAttrNode('parameter'), 'readonly': True})
        # crsChildren.append({'name': 'False Northing', 'type': 'str', 'value': srs.GetAttrValue('parameter', 3), 'readonly': True})
        # crsChildren.append({'name': 'Central Meridian', 'type': 'str', 'value': srs.GetAttrValue('parameter', 5), 'readonly': True})
        # crsChildren.append({'name': 'Scale Factor', 'type': 'str', 'value': parameters, 'readonly': True})
        # crsChildren.append({'name': 'Latitude of Origin', 'type': 'str', 'value': parameters, 'readonly': True})

        # Set free metadata section
        domains = FreeMetadataDomains(name='Free Metadata by Domain (right click to rename and remove)', dataset = self.inDS)

        # Set NodataValues
        self.ndv = NoDataValue(name='NoData Value')
        self.ndv.getParameter().sigValueChanged.connect(lambda param, data: self.ndvChanged(0, data))

        self.nodataValue = self.inDS.GetRasterBand(1).GetNoDataValue()
        self.ndv.getParameter().setValue(str(self.nodataValue))

        # Set individual band information
        self.bandc2 = []

        self.redBand = 0
        self.greenBand = 0
        self.blueBand = 0
        self.alphaBand = 0

        for index in range(1, self.inDS.RasterCount):
            band = self.inDS.GetRasterBand(index)

            self.currentBand = Bands(name=('Band ' + str(index)), dataset=band, ind = index)
            self.currentBand.getParameter().sigValueChanged.connect(lambda param, data: self.bandNdvChanged(index, data))
            self.bandc2.append(self.currentBand)

            if band.GetNoDataValue() != self.nodataValue:
                self.nodataValue = str('is defined per band. type here to set nodata value for all bands.')
                self.ndv.getParameter().setValue(str('is defined per band. type here to set nodata value for all bands.'))
                break

            print "color_load"
            print band.GetRasterColorInterpretation()
            if int(band.GetRasterColorInterpretation()) == 3:
                print "check red"
                print self.redBand
                self.redBand = index
            elif band.GetRasterColorInterpretation() == 4:
                print "check green"
                print self.greenBand
                self.greenBand = index
            elif band.GetRasterColorInterpretation() == 5:
                print "check blue"
                print self.blueBand
                self.blueBand = index
            elif band.GetRasterColorInterpretation() == 6:
                print "check alpha"
                print self.alphaBand
                self.alphaBand = index

        ## Set general metadata
        defaultBands = DefaultBands(name='Default Bands', dataset=[self.redBand, self.greenBand, self.blueBand, self.alphaBand], rastercount=self.inDS.RasterCount)
        defaultBands.getRedParameter().sigValueChanged.connect(lambda param, data: self.defaultRedChanged(index, data))
        defaultBands.getGreenParameter().sigValueChanged.connect(lambda param, data: self.defaultGreenChanged(index, data))
        defaultBands.getBlueParameter().sigValueChanged.connect(lambda param, data: self.defaultBlueChanged(index, data))
        defaultBands.getAlphaParameter().sigValueChanged.connect(lambda param, data: self.defaultAlphaChanged(index, data))

        self.generalChildren = [
            {'name': 'File Path', 'type': 'str', 'value': self.inputFile.currentText(), 'readonly': True},
            {'name': 'File Type', 'type': 'str', 'value': self.inDS.GetDriver().ShortName, 'readonly': True},
            {'name': 'Data Type', 'type': 'str', 'value': gdal.GetDataTypeName(self.inDS.GetRasterBand(1).DataType), 'readonly': True},
            {'name': 'Samples', 'type': 'int', 'value': self.inDS.RasterXSize, 'readonly': True},
            {'name': 'Lines', 'type': 'int', 'value': self.inDS.RasterYSize, 'readonly': True},
            {'name': 'Number of Bands', 'type': 'int', 'value': self.inDS.RasterCount, 'readonly': True},
            {'name': 'Pixel Size', 'type': 'str',
                                     'value': str(self.inDS.GetGeoTransform()[1]) + ' x ' + str(
                                         -1 * self.inDS.GetGeoTransform()[5]),
                                     'readonly': True},
            defaultBands,
            {'name': 'Description', 'type': 'str', 'value': self.inDS.GetDescription(), 'readonly': False},
            ]

        # Fill parameter tree
        self.params[0].update({'children': self.generalChildren})
        self.params[1] = self.ndv
        self.params[2].update({'children': self.crsChildren})
        self.params[3].update({'children': self.bandc2})
        self.params[4] = domains

        end = time.time()
        print("setup time")
        print(end-start)

        return self.params

    def populateMetadata(self, params):
        self.p = Parameter.create(name='params', type='group', children=params)
        browse(params)
        #browse(self.p)
        self.t.setParameters(self.p, showTop=False)

    def validatePath(self, dataset, *args, **kwds):
        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True
        if sender == self.inputFile:
            path = self.inputFile.currentText()
            from osgeo import gdal
            ds = gdal.Open(str(path))

            if ds is None:
                style = 'QComboBox {{ background-color: {} }}'.format(hexRed)
                self.inputFile.setStyleSheet(style)
                result = False
            else:
                style = 'QComboBox {{ }}'.format(hexGreen)
                self.inputFile.setStyleSheet(style)

            return result

    def saveMetadata(self):
        # Set NoData Values
        for index in range(1, self.inDS.RasterCount):
            try:
                self.inDS.GetRasterBand(index).SetNoDataValue(float(self.bandc2[index - 1].getParameter().value()))
            except:
                self.inDS.GetRasterBand(index).DeleteNoDataValue()

        # Set default bands
        if self.redBand != 0:
            print "reeedd"
            print self.redBand
            print self.inDS.GetRasterBand(self.redBand)
            self.inDS.GetRasterBand(self.redBand).SetRasterColorInterpretation(int(3))
            c= self.inDS.GetRasterBand(self.redBand).GetRasterColorInterpretation()
            print c
        if self.greenBand != 0:
            self.inDS.GetRasterBand(self.redBand).SetRasterColorInterpretation(4)
        if self.blueBand != 0:
            self.inDS.GetRasterBand(self.redBand).SetRasterColorInterpretation(5)
        if self.alphaBand != 0:
            self.inDS.GetRasterBand(self.redBand).SetRasterColorInterpretation(6)

        # Save free metadata
        for domain in range(0, len(self.params[4].children())):
            d = self.params[4].children()[domain].name()
            for datum in range(0, len(self.params[4].children()[domain].children())):
                n = self.params[4].children()[domain].children()[datum].name()
                v = self.params[4].children()[domain].children()[datum].value()
                self.inDS.SetMetadataItem(str(n), str(v), str(d))

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication.instance()
        w = Win()
        w.show()
        app.exec_()