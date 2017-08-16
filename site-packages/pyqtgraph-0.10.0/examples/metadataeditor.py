# -*- coding: utf-8 -*-
"""
This example demonstrates the use of pyqtgraph's parametertree system. This provides
a simple way to generate user interfaces that control sets of parameters. The example
demonstrates a variety of different parameter types (int, float, list, etc.)
as well as some customized parameter types

"""

import initExample ## Add path to library (just for examples; you do not need this)

#import pyqtgraph as pg
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyqtgraph.Qt import QtCore, QtGui

from osgeo import osr
from hub.gdal.api import *

app = QtGui.QApplication([])
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

import time

class Win(QtGui.QWidget):

    inDS = None

    params = []
    params.append({'name': 'General', 'type': 'group', 'children': []})
    params.append({'name': 'Coordinate Reference System', 'type': 'group', 'children': []})
    params.append({'name': 'Bands', 'type': 'group', 'children': []})
    params.append({'name': 'Other', 'type': 'group', 'children': []})

    generalChildren = []
    crsChildren = []
    bandChildren = []
    otherChildren = []

    t = ParameterTree()

    # Reads metadata from given file and dynamically populates the parameter var
    p = Parameter.create(name='params', type='group', children=params)


    def __init__(self, parent=None):
        super(Win, self).__init__(parent=parent)
        self.setLayout(QtGui.QGridLayout())
        layout = self.layout()
        self.ptree = ParameterTree()

        # select input file name via QFileDialog in case the file is not open in the enmap box yet
        self.inputFile = QComboBox()
        self.inputFile.currentIndexChanged.connect(
            lambda: self.comboIndexChanged()
        )

        self.selectInputFile = QPushButton('...')
        self.selectInputFile.clicked.connect(
            lambda: self.fileFound(self.inputFile)
        )
        self.t.setWindowTitle('pyqtgraph example: Parameter Tree')

        savebtn = QPushButton("Save Changes")
        savebtn.clicked.connect(
            lambda : self.saveMetadata()
        )

        # select input file name via QFileDialog in case the file is not open in the enmap box yet
        closebtn = QPushButton("Discard/Close ERROR")
        closebtn.clicked.connect(self.close)

        layout.addWidget(QtGui.QLabel("Select file and view/edit related metadata."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile, 1, 6, 1, 2)
        layout.addWidget(self.t, 2, 0, 1, 8)
        layout.addWidget(savebtn, 3, 0, 1, 4)
        layout.addWidget(closebtn, 3, 4, 1, 4)

        self.resize(800,800)

        self.t.setParameters(self.p, showTop=False)
        self.p.sigTreeStateChanged.connect(self.change)

        ## test save/restore
        s = self.p.saveState()
        self.p.restoreState(s)

        # Too lazy for recursion:
        for child in self.p.children():
            child.sigValueChanging.connect(self.valueChanging)
            for ch2 in child.children():
                ch2.sigValueChanging.connect(self.valueChanging)

    def fileFound(self, inputFile):
        self.inputFile.addItem(QFileDialog.getOpenFileName(self, 'Input image'))
        counter = self.inputFile.count()
        self.inputFile.setCurrentIndex(counter - 1)

    def comboIndexChanged(self):
        if self.validatePath():
            self.inDS = gdal.Open(str(self.inputFile.currentText()))
            params = self.setMetadataTree()
            self.populateMetadata(params)

    def setMetadataTree(self):
        from osgeo import osr

        self.generalChildren.append({'name': 'File Path', 'type': 'str', 'value': self.inputFile.currentText(), 'readonly': True})
        self.generalChildren.append({'name': 'File Type', 'type': 'str', 'value': self.inDS.GetDriver().ShortName, 'readonly': True})
        self.generalChildren.append({'name': 'Byte Order', 'type': 'str', 'value': '?', 'readonly': True})
        self.generalChildren.append(
            {'name': 'Data Type', 'type': 'str', 'value': gdal.GetDataTypeName(self.inDS.GetRasterBand(1).DataType),
             'readonly': True})
        self.generalChildren.append({'name': 'Interleave', 'type': 'str', 'value': '?', 'readonly': True})
        self.generalChildren.append({'name': 'Samples', 'type': 'int', 'value': self.inDS.RasterXSize, 'readonly': True})
        self.generalChildren.append({'name': 'Lines', 'type': 'int', 'value': self.inDS.RasterYSize, 'readonly': True})
        self.generalChildren.append({'name': 'Number of Bands', 'type': 'int', 'value': self.inDS.RasterCount, 'readonly': True})
        self.generalChildren.append({'name': 'Pixel Size', 'type': 'str',
                                'value': str(self.inDS.GetGeoTransform()[1]) + ' x ' + str(-1 * self.inDS.GetGeoTransform()[5]),
                                'readonly': True})
        self.generalChildren.append({'name': 'Default Bands', 'type': 'str', 'value': '?', 'readonly': True})
        self.generalChildren.append({'name': 'Description', 'type': 'str', 'value': self.inDS.GetDescription(), 'readonly': True})

        self.nodataValue = self.inDS.GetRasterBand(1).GetNoDataValue()
        for index in range(1, self.inDS.RasterCount):
            if self.inDS.GetRasterBand(index).GetNoDataValue() != self.nodataValue:
                self.nodataValue = str('is defined per band. type here to set nodata value for all bands.')
                break

        self.generalChildren.append({'name': 'Image NoData Value', 'type': 'str', 'value': str(self.nodataValue)})

        prj = self.inDS.GetProjection()
        srs = osr.SpatialReference(wkt=prj)

        if (srs.GetAuthorityName('projcs') and srs.GetAuthorityCode('projcs')):
            id = srs.GetAuthorityName('projcs') + srs.GetAuthorityCode('projcs')
        else:
            id = ''

        self.crsChildren.append({'name': 'Name', 'type': 'str', 'value': srs.GetAttrValue('projcs'), 'readonly': True})
        self.crsChildren.append({'name': 'AuthID', 'type': 'str', 'value': id, 'readonly': True})
        self.crsChildren.append({'name': 'Datum', 'type': 'str', 'value': srs.GetAttrValue('datum'), 'readonly': True})
        self.crsChildren.append({'name': 'Spheroid', 'type': 'str', 'value': srs.GetAttrValue('spheroid'), 'readonly': True})
        self.crsChildren.append({'name': 'Map Units', 'type': 'str', 'value': srs.GetAttrValue('unit'), 'readonly': True})

        xmin = self.inDS.GetGeoTransform()[0] - self.inDS.GetGeoTransform()[2]
        ymin = self.inDS.GetGeoTransform()[3] - self.inDS.GetGeoTransform()[4]
        xmax = xmin + self.inDS.RasterXSize * self.inDS.GetGeoTransform()[1]
        ymax = ymin + self.inDS.RasterXSize * self.inDS.GetGeoTransform()[5]
        boundingBox = [xmin, ymin, xmax, ymax]

        self.crsChildren.append({'name': 'Bounding Box', 'type': 'str', 'value': str(boundingBox), 'readonly': True})

        # if srs.IsProjected:
        # crsChildren.append({'name': 'False Easting', 'type': 'str', 'value': srs.GetAttrNode('parameter'), 'readonly': True})
        # crsChildren.append({'name': 'False Northing', 'type': 'str', 'value': srs.GetAttrValue('parameter', 3), 'readonly': True})
        # crsChildren.append({'name': 'Central Meridian', 'type': 'str', 'value': srs.GetAttrValue('parameter', 5), 'readonly': True})
        # crsChildren.append({'name': 'Scale Factor', 'type': 'str', 'value': parameters, 'readonly': True})
        # crsChildren.append({'name': 'Latitude of Origin', 'type': 'str', 'value': parameters, 'readonly': True})

        for index in range(1, self.inDS.RasterCount):
            band = self.inDS.GetRasterBand(index)

            wl = band.GetMetadataItem('wavelength')#, pszDomain='ENVI')
            wlu = band.GetMetadataItem('wavelength unit') #, domain='ENVI')
            self.bandChildren.append({'name': 'Band ' + str(index), 'type': 'group', 'children': [
                {'name': 'Band', 'type': 'int', 'value': band.GetBand(), 'readonly': True},
                {'name': 'Wavelength', 'type': 'str', 'value': str(wl), 'readonly': True},
                {'name': 'Wavelength Unit', 'type': 'str', 'value': str(wlu), 'readonly': True},
                {'name': 'Band NoData Value', 'type': 'str', 'value': str(band.GetNoDataValue()),
                 'readonly': False},
                {'name': 'Description', 'type': 'str', 'value': band.GetDescription(),
                 'readonly': True}
            ]})

        self.otherChildren.append({'name': 'Other', 'type': 'str', 'value': '?', 'readonly': True})

        self.params[0].update({'children': self.generalChildren})
        self.params[1].update({'children': self.crsChildren})
        self.params[2].update({'children': self.bandChildren})
        self.params[3].update({'children': self.otherChildren})

        return self.params

    def valueChanging(param, value):
        print("Value changing (not finalized): %s %s" % (param, value))

    def save(self):
        global state
        state = self.p.saveState()

    def restore(self):
        global state
        add = self.p['Save/Restore functionality', 'Restore State', 'Add missing items']
        rem = self.p['Save/Restore functionality', 'Restore State', 'Remove extra items']
        self.p.restoreState(state, addChildren=add, removeChildren=rem)

    # p.param('Save/Restore functionality', 'Save State').sigActivated.connect(save)
    # p.param('Save/Restore functionality', 'Restore State').sigActivated.connect(restore)

    def populateMetadata(self, params):
        self.p = Parameter.create(name='params', type='group', children=params)
        self.p.sigTreeStateChanged.connect(self.change)
        self.t.setParameters(self.p, showTop=False)

    def validatePath(self, *args, **kwds):
        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True
        if sender == self.inputFile:
            path = self.inputFile.currentText()
            #print(path)
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

    ## If anything changes in the tree, print a message
    def change(self, param, changes):
        #print(param)
        # print("tree changes:")
        for param, change, data in changes:
            path = self.p.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()

            #print('  parameter: %s'% childName)
            #print('  change:    %s'% change)
            #print('  data:      %s'% str(data))
            #print('  ----------')

            # If overall image noata is changed, check if it is a number. if it is, overwrite all band nodata values. if it is not, set to None and overwrite band nodata values
            if ("Image NoData Value" in childName):
                try:
                    start = time.time()
                    float(data)
                    self.generalChildren[11]['value'] = str(data)
                    for index in range(0, self.inDS.RasterCount - 1):
                        self.bandChildren[index]['children'][3]['value'] = str(data) # band no data value, mind position 3!

                except ValueError:
                    self.generalChildren[11]['value'] = 'None'

                else:
                    self.params[0].update({'children': self.generalChildren})
                    self.params[2].update({'children': self.bandChildren})
                    self.p = Parameter.create(name='params', type='group', children=self.params)
                    self.t.setParameters(self.p, showTop=False)
                    self.p.sigTreeStateChanged.connect(self.change)
                    print("time")
                    end = time.time()
                    print(end - start)

            elif("Band NoData Value" in childName):
                try:
                    float(data)

                    # get band number  that is modified!
                    bandNbr = [int(s) for s in path[1].split() if s.isdigit()]
                    #print(bandNbr)
                    self.bandChildren[(bandNbr + 1)[0]]['children'][3]['value'] = str(data)  # band no data value, mind position 3!

                    self.generalChildren[11]['value'] = 'None'
                except ValueError:
                    bandNbr = [int(s) for s in path[1].split() if s.isdigit()]
                    self.bandChildren[(bandNbr + 1)[0]]['children'][3]['value'] = 'None'  # band no data value, mind position 3!

                else:
                    self.params[0].update({'children': self.generalChildren})
                    self.params[2].update({'children': self.bandChildren})
                    self.p = Parameter.create(name='params', type='group', children=self.params)
                    self.t.setParameters(self.p, showTop=False)
                    self.p.sigTreeStateChanged.connect(self.change)

    def saveMetadata(self):

        #({'name': 'Default Bands', 'type': 'str', 'value': '?', 'readonly': True})
        #({'name': 'Description', 'type': 'str', 'value': '?', 'readonly': True})

        # Set NoData Values
        for index in range(1, self.inDS.RasterCount):

            #print(index)
            #print(self.bandChildren[index - 1]['children'][3]['value'])

            try:
                self.inDS.GetRasterBand(index).SetNoDataValue(float(self.bandChildren[index - 1]['children'][3]['value']))
            except:
                self.inDS.GetRasterBand(index).DeleteNoDataValue()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication.instance()
        w = Win()
        w.show()
        app.exec_()