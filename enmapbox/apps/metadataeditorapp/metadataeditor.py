# -*- coding: utf-8 -*-
"""
This example demonstrates the use of pyqtgraph's parametertree system. This provides
a simple way to generate user interfaces that control sets of parameters. The example
demonstrates a variety of different parameter types (int, float, list, etc.)
as well as some customized parameter types

"""

#import initExample ## Add path to library (just for examples; you do not need this)

from qgis.gui import QgsFileWidget, QgsRasterFormatSaveOptionsWidget

import os

#import pyqtgraph as pg
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyqtgraph.Qt import QtCore, QtGui

from osgeo import osr
from hub.gdal.api import *

import multiprocessing as mp

app = QtGui.QApplication([])
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from enmapbox.gui.enmapboxgui import EnMAPBox

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
        opts['type'] = 'int'
        opts['value'] = 0
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

class BandLoader(QObject):
    def __init__(self, resultArray, dataset, *args, **kwds):
        super(BandLoader, self).__init__(*args, **kwds)
        print("test")

        self.nProcesses = 2
        self.jobid = 0

        self.pool = None
        self.MGR = mp.Manager()
        self.APPLYRESULTS = []
        self.ar = resultArray
        #self.APPLYRESULTS = resultArray
        self.resultQueue = self.MGR.Queue()
        self.cancelEvent = self.MGR.Event()

        self.ds = dataset

        self.queueChecker = QTimer()
        self.queueChecker.setInterval(3000)
        self.queueChecker.timeout.connect(self.checkQueue)

        #split number of bands into list

        print("dataset: ")
        print(self.ds)

        print("dataset bands")
        print(self.ds.RasterCount)
        files = []
        for index in range(1, self.ds.RasterCount):
            files.append(self.ds.GetRasterBand(index))
            #print(files)

        print "files"
        print(files)
        #files = pathList[:]
        workPackages = list()
        i = 0
        while(len(files)) > 0:
            if len(workPackages) <= i:
                workPackages.append([])
            workPackages[i].append(files.pop(0))
            i = i + 1 if i < self.nProcesses - 1 else 0

        self.pool = mp.Pool(self.nProcesses)

        del self.APPLYRESULTS[:]

        self.queueChecker.start()

        for i, workPackage in enumerate(workPackages):
            args = (workPackage, self.jobid, i, self.resultQueue, resultArray, self.cancelEvent)
            if False:  # todo: ???
                r = self.pool.apply_async(self.loadBands, args=args, callback=self.checkQueue)
                self.APPLYRESULTS.append(r)
            else:
                self.checkQueue(self.loadBands(*args)) ### todo ???
        self.pool.close()

    def checkQueue(self, *args):

        while not self.resultQueue.empty():
            md = self.resultQueue.get()
            self.onPixelLoaded(md)

        if all([w.ready() for w in self.APPLYRESULTS]):
            print('All done')

            del self.APPLYRESULTS[:]
            self.queueChecker.stop()
            #if not self.cancelEvent.is_set():
                #self.sigLoadingFinished.emit()
        elif self.cancelEvent.is_set():
            self.queueChecker.stop()
            #self.sigLoadingCanceled.emit()

    #@QtCore.pyqtSlot(PixelLoaderResult)
    def onPixelLoaded(self, data):
    #    assert isinstance(data, PixelLoaderResult)
        if data.jobId != self.jobid:
            #do not return results from previous jobs...
            #print('got thread results from {} but need {}...'.format(jobid, self.jobid))
            return
        else:
            self.filesList.remove(data.source)
            self.sigPixelLoaded.emit(self.nMax - len(self.filesList), self.nMax, data)

            if len(self.filesList) == 0:
                self.sigLoadingFinished.emit()



    def loadBands(self, paths, jobid, poolWorker, resultArray, q, cancelEvent):

        print("paths")
        print(paths)
        for i, path in enumerate(paths):
            if cancelEvent.is_set():
                print "canceled"
                return "Canceled"

            #R = PixelLoaderResult(jobid, poolWorker, geom, path)
            currentBand = Bands(name=('Band ' + str(jobid)), dataset=self.ds.GetRasterBand(jobid + 1), ind=jobid)

            self.ar.append(currentBand)

            try:
                #todo: append band information to bandc2 as children
                print "dataset"
                #print(dataset)
                print "count"
                #print(dataset.RasterCount)
                for index in range(1, self.ds.RasterCount):
                    band = self.ds.GetRasterBand(index)
                    print "Band"
                    print(band)

                    currentBand = Bands(name=('Band ' + str(index)), dataset=band, ind=index)
                    print "current Band"
                    print(currentBand)
                    #currentBand.getParameter().sigValueChanged.connect(
                    #    lambda param, data: self.bandNdvChanged(index, data))
                    resultArray.append(currentBand)
                    print "resultArray"
                    print(resultArray)

                    #if band.GetNoDataValue() != self.nodataValue:
                    #    self.nodataValue = str('is defined per band. type here to set nodata value for all bands.')
                    #    self.ndv.getParameter().setValue(
                    #        str('is defined per band. type here to set nodata value for all bands.'))
                    #    break

            except:
                print("bands could not be loaded")

        return "Finished"


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

        print(self)
        #str(ind)
        #dataset.GetDescription()
        #dataset.GetMetadataItem('wavelength')

        #c = [
        #    dict(name = 'Band Number', type = 'str', value = str(ind), readonly = True),
        #    dict(name = 'Band Name', type = 'str', value = dataset.GetDescription(), readonly = True),
        #    dict(name = 'Wavelength', type = 'str', value = dataset.GetMetadataItem('wavelength'), readonly = True),
        #    dict(name = 'Wavelength Unit', type = 'str', value = dataset.GetMetadataItem('wavelength_units'), readonly = True),
        #    dict(name = 'Band NoData Value', type = 'str', value = dataset.GetNoDataValue(), readonly = False),
        #]

        #self.create(name='params', type='group', children=c)

        #self.addChildren([
            #{'name': 'Band Number', 'type': 'str', 'value': str(ind), 'readonly': True},
            #{'name': 'Band Name', 'type': 'str', 'value': dataset.GetDescription(),
            # 'readonly': True},
            #{'name': 'Wavelength', 'type': 'str', 'value': dataset.GetMetadataItem('wavelength'), 'readonly': True},
            #{'name': 'Wavelength Unit', 'type': 'str', 'value': dataset.GetMetadataItem('wavelength_units'),
            # 'readonly': True},
        #    {'name': 'Band NoData Valu', 'type': 'str', 'value': dataset.GetNoDataValue(),
        #     'readonly': False},
        #    ])

        self.a = self.param('Band NoData Value')

    def getParameter(self):
        return self.a

## this group includes a menu allowing the user to add new parameters into its child list
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
                theseGrandchildren = dataset.GetMetadata(domain=a[index])
                orderedGrandchildren = collections.OrderedDict(sorted(theseGrandchildren.items()))

                domain = FreeMetadata(name=a[index], dataset=orderedGrandchildren)

                self.addChild(domain)

    def addNew(self):
        self.addChild(FreeMetadata(name="New Domain %d" % (len(self.childs) + 1), dataset = None))
        #self.addChild(
        #    dict(name="New Domain %d" % (len(self.childs) + 1), type='group', value='', removable=True,
        #        renamable=True))

## this group includes a menu allowing the user to add new parameters into its child list
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

        self.resize(600,600)

        self.t.setParameters(self.p, showTop=False)
        #self.p.sigTreeStateChanged.connect(self.change)

        ## test save/restore
        s = self.p.saveState()
        self.p.restoreState(s)

        enmapBox = EnMAPBox.instance()

        if isinstance(enmapBox, EnMAPBox):
            print("enmapbox found")
            for src in sorted(enmapBox.dataSources('RASTER')):
                print("raster found")
                self.addSrcRaster(src)

    def addSrcRaster(self, src):
        print("add function called")
        addedItems = [self.inputFile.itemData(i, role=Qt.UserRole) for
            i in range(self.inputFile.count())]
        if src not in addedItems: #hasClassification(src) and src not in addedItems:
            print("not yet added")
            bn = os.path.basename(src)
            self.inputFile.addItem(src) #(bn, src)
        self.validatePath(src)


        # Too lazy for recursion:
        #for child in self.p.children():
        #    child.sigValueChanging.connect(self.valueChanging)
        #    for ch2 in child.children():
        #        ch2.sigValueChanging.connect(self.valueChanging)

    def fileFound(self, inputFile):
        self.inputFile.addItem(QFileDialog.getOpenFileName(self, 'Input image'))
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
            print("value is not a number")
            #self.ndv.getParameter().setValue(str('value is not a number'))

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

        self.params = [
            {'name': 'General', 'type': 'group', 'children': []},
            {'name': 'Image NoData Value', 'type': 'group', 'children': []},
            {'name': 'Coordinate Reference System', 'type': 'group', 'children': []},
            {'name': 'Bands', 'type': 'group', 'children': []},
            {'name': 'Free Metadata by Domain (right click to rename and remove)', 'type': 'group', 'children': []}
        ]

        self.redBand = 0
        self.greenBand = 0
        self.blueBand = 0
        self.alphaBand = 0

        self.ndv = NoDataValue(name='NoData Value')
        self.ndv.getParameter().sigValueChanged.connect(lambda param, data: self.ndvChanged(0, data))

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

        domains = FreeMetadataDomains(name='Free Metadata by Domain (right click to rename and remove)', dataset = self.inDS)

        self.nodataValue = self.inDS.GetRasterBand(1).GetNoDataValue()
        self.ndv.getParameter().setValue(str(self.nodataValue))

        self.bandc2 = []

        #BandLoader(self.bandc2, self.inDS)
        # todo:
        # band loader async
        # in band loader: for all bands, load band info and append a band object
        # in band object, define sivaluechanged function.
        # establish getter for ndv.getparameter

        for index in range(1, self.inDS.RasterCount):
            band = self.inDS.GetRasterBand(index)

            self.currentBand = Bands(name=('Band ' + str(index)), dataset=band, ind = index)
            self.currentBand.getParameter().sigValueChanged.connect(lambda param, data: self.bandNdvChanged(index, data))
            self.bandc2.append(self.currentBand)

            if band.GetNoDataValue() != self.nodataValue:
                self.nodataValue = str('is defined per band. type here to set nodata value for all bands.')
                self.ndv.getParameter().setValue(str('is defined per band. type here to set nodata value for all bands.'))
                break

            #print "color_load"
            #print band
            #print band.GetRasterColorInterpretation()
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

        #print self.inDS.GetRasterBand(self.redBand)
        #print self.inDS
        #print self.inDS.GetDescription()
        #print self.inDS.SetDescription(str("test"))

        defaultBands = DefaultBands(name='Default Bands', dataset=[self.redBand, self.greenBand, self.blueBand, self.alphaBand], rastercount=self.inDS.RasterCount)
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

        defaultBands.getRedParameter().sigValueChanged.connect(lambda param, data: self.defaultRedChanged(index, data))
        defaultBands.getGreenParameter().sigValueChanged.connect(lambda param, data: self.defaultGreenChanged(index, data))
        defaultBands.getBlueParameter().sigValueChanged.connect(lambda param, data: self.defaultBlueChanged(index, data))
        defaultBands.getAlphaParameter().sigValueChanged.connect(lambda param, data: self.defaultAlphaChanged(index, data))

        self.params[0].update({'children': self.generalChildren})
        self.params[1] = self.ndv
        self.params[2].update({'children': self.crsChildren})
        self.params[3].update({'children': self.bandc2})
        self.params[4] = domains

        end = time.time()
        print("setup time")
        print(end-start)

        return self.params

    #def valueChanging(param, value):
    #    print("Value changing (not finalized): %s %s" % (param, value))

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
        #self.p.sigTreeStateChanged.connect(self.change)
        self.t.setParameters(self.p, showTop=False)

    def validatePath(self, dataset, *args, **kwds):
        print("File List")
        print(dataset)
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
    #def change(self, param, changes):
    #    # print("tree changes:")
    #    for param, change, data in changes:
    #        path = self.p.childPath(param)
    #        if path is not None:
    #            childName = '.'.join(path)
    #        else:
    #            childName = param.name()

    def saveMetadata(self):

        # Set image description
        print self.inDS
        print self.inDS.GetDescription()
        self.inDS.SetDescription(str("bla"))
        print self.inDS.GetDescription()
        self.inDS.SetDescription(str("bla"))

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