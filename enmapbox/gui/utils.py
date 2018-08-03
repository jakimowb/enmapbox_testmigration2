# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapbox/gui/utils.py
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

import os, sys, importlib, tempfile, re, six, fnmatch, io, pickle, zipfile



from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
from PyQt5 import uic
from osgeo import gdal
import numpy as np
import enmapbox.gui

from enmapbox import messageLog
messageLog = messageLog

jp = os.path.join

DIR_ENMAPBOX = os.path.dirname(enmapbox.__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])
DIR_TESTDATA = os.path.join(DIR_ENMAPBOX, 'enmapboxtestdata')


#for python development only
DIR_QGISRESOURCES = jp(DIR_REPO, 'qgisresources')
if not os.path.isdir(DIR_QGISRESOURCES):
    DIR_QGISRESOURCES = None


REPLACE_TMP = True  # required for loading *.ui files directly

######### Lookup  tables
METRIC_EXPONENTS = {
    "nm": -9, "um": -6, u"µm": -6, "mm": -3, "cm": -2, "dm": -1, "m": 0, "hm": 2, "km": 3
}
# add synonyms
METRIC_EXPONENTS['nanometers'] = METRIC_EXPONENTS['nm']
METRIC_EXPONENTS['micrometers'] = METRIC_EXPONENTS['um']
METRIC_EXPONENTS['millimeters'] = METRIC_EXPONENTS['mm']
METRIC_EXPONENTS['centimeters'] = METRIC_EXPONENTS['cm']
METRIC_EXPONENTS['decimeters'] = METRIC_EXPONENTS['dm']
METRIC_EXPONENTS['meters'] = METRIC_EXPONENTS['m']
METRIC_EXPONENTS['hectometers'] = METRIC_EXPONENTS['hm']
METRIC_EXPONENTS['kilometers'] = METRIC_EXPONENTS['km']

LUT_WAVELENGTH = dict({'B': 480,
                       'G': 570,
                       'R': 660,
                       'NIR': 850,
                       'SWIR': 1650,
                       'SWIR1': 1650,
                       'SWIR2': 2150
                       })


def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)



NEXT_COLOR_HUE_DELTA_CON = 10
NEXT_COLOR_HUE_DELTA_CAT = 100
def nextColor(color, mode='cat'):
    """
    Reuturns another color
    :param color:
    :param mode:
    :return:
    """
    assert mode in ['cat','con']
    assert isinstance(color, QColor)
    hue, sat, value, alpha = color.getHsl()
    if mode == 'cat':
        hue += NEXT_COLOR_HUE_DELTA_CAT
    elif mode == 'con':
        hue += NEXT_COLOR_HUE_DELTA_CON
    if sat == 0:
        sat = 255
        value = 128
        alpha = 255
        s = ""
    while hue > 360:
        hue -= 360

    return QColor.fromHsl(hue, sat, value, alpha)


class TestObjects():
    @staticmethod
    def inMemoryClassification(n=3, nl=10, ns=20, nb=1, crs='EPSG:32632'):
        from enmapbox.gui.classificationscheme import ClassificationScheme
        scheme = ClassificationScheme()
        scheme.createClasses(n)

        drv = gdal.GetDriverByName('MEM')
        assert isinstance(drv, gdal.Driver)


        ds = drv.Create('', ns, nl, bands=nb, eType=gdal.GDT_Byte)

        if isinstance(crs, str):
            c = QgsCoordinateReferenceSystem(crs)
            ds.SetProjection(c.toWkt())

        step = int(np.ceil(float(nl) / len(scheme)))

        assert isinstance(ds, gdal.Dataset)
        for b in range(1, nb + 1):
            band = ds.GetRasterBand(b)
            array = np.zeros((nl, ns), dtype=np.uint8) - 1
            y0 = 0
            for i, c in enumerate(scheme):
                y1 = min(y0 + step, nl - 1)
                array[y0:y1, :] = c.label()
                y0 += y1 + 1
            band.SetCategoryNames(scheme.classNames())
            band.SetColorTable(scheme.gdalColorTable())
        ds.FlushCache()
        return ds

    @staticmethod
    def qgisInterfaceMockup():

        return QgisMockup()

    @staticmethod
    def createDropEvent(mimeData:QMimeData):
        """Creates a QDropEvent conaining the provided QMimeData"""
        return QDropEvent(QPointF(0, 0), Qt.CopyAction, mimeData, Qt.LeftButton, Qt.NoModifier)


    @staticmethod
    def processingAlgorithm():

        from qgis.core import QgsProcessingAlgorithm

        class TestProcessingAlgorithm(QgsProcessingAlgorithm):

            def __init__(self):
                super(TestProcessingAlgorithm, self).__init__()
                s = ""

            def createInstance(self):
                return TestProcessingAlgorithm()

            def name(self):
                return 'exmaplealg'

            def displayName(self):
                return 'Example Algorithm'

            def groupId(self):
                return 'exampleapp'

            def group(self):
                return 'TEST APPS'

            def initAlgorithm(self, configuration=None):
                self.addParameter(QgsProcessingParameterRasterLayer('pathInput', 'The Input Dataset'))
                self.addParameter(
                    QgsProcessingParameterNumber('value', 'The value', QgsProcessingParameterNumber.Double, 1, False,
                                                 0.00, 999999.99))
                self.addParameter(QgsProcessingParameterRasterDestination('pathOutput', 'The Output Dataset'))

            def processAlgorithm(self, parameters, context, feedback):
                assert isinstance(parameters, dict)
                assert isinstance(context, QgsProcessingContext)
                assert isinstance(feedback, QgsProcessingFeedback)


                outputs = {}
                return outputs

        return TestProcessingAlgorithm()



    @staticmethod
    def enmapBoxApplication():

        from enmapbox.gui.applications import EnMAPBoxApplication
        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapbox = EnMAPBox.instance()

        class TestApp(EnMAPBoxApplication):
            def __init__(self, enmapbox):
                super(TestApp, self).__init__(enmapbox)

                self.name = 'TestApp'
                self.licence = 'GPL-3'
                self.version = '-12345'

            def menu(self, appMenu:QMenu)->QMenu:
                menu = appMenu.addMenu('Test Menu')
                action = menu.addAction('Test Action')
                action.triggered.connect(self.onAction)
                return menu

            def onAction(self):
                print('TestApp action called')

            def processingAlgorithms(self):
                return [TestObjects.processingAlgorithm()]

        return TestApp(enmapbox)

class QgsPluginManagerMockup(QgsPluginManagerInterface):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def addPluginMetadata(self, *args, **kwargs):
        super().addPluginMetadata(*args, **kwargs)

    def addToRepositoryList(self, *args, **kwargs):
        super().addToRepositoryList(*args, **kwargs)

    def childEvent(self, *args, **kwargs):
        super().childEvent(*args, **kwargs)

    def clearPythonPluginMetadata(self, *args, **kwargs):
        #super().clearPythonPluginMetadata(*args, **kwargs)
        pass

    def clearRepositoryList(self, *args, **kwargs):
        super().clearRepositoryList(*args, **kwargs)

    def connectNotify(self, *args, **kwargs):
        super().connectNotify(*args, **kwargs)

    def customEvent(self, *args, **kwargs):
        super().customEvent(*args, **kwargs)

    def disconnectNotify(self, *args, **kwargs):
        super().disconnectNotify(*args, **kwargs)

    def isSignalConnected(self, *args, **kwargs):
        return super().isSignalConnected(*args, **kwargs)

    def pluginMetadata(self, *args, **kwargs):
        super().pluginMetadata(*args, **kwargs)

    def pushMessage(self, *args, **kwargs):
        super().pushMessage(*args, **kwargs)

    def receivers(self, *args, **kwargs):
        return super().receivers(*args, **kwargs)

    def reloadModel(self, *args, **kwargs):
        super().reloadModel(*args, **kwargs)

    def sender(self, *args, **kwargs):
        return super().sender(*args, **kwargs)

    def senderSignalIndex(self, *args, **kwargs):
        return super().senderSignalIndex(*args, **kwargs)

    def showPluginManager(self, *args, **kwargs):
        super().showPluginManager(*args, **kwargs)

    def timerEvent(self, *args, **kwargs):
        super().timerEvent(*args, **kwargs)


def qgisLayerTreeLayers() -> list:
    """
    Returns the layers shown in the QGIS LayerTree
    :return: [list-of-QgsMapLayers]
    """
    iface = qgisAppQgisInterface()
    if isinstance(iface, QgisInterface):
        return [ln.layer() for  ln in iface.layerTreeView().model().rootGroup().findLayers()]
    else:
        return []

class QgisMockup(QgisInterface):
    """
    A "fake" QGIS Desktop instance that should provide all the inferfaces a plugin developer might need (and nothing more)
    """

    def pluginManagerInterface(self)->QgsPluginManagerInterface:
        return self.mPluginManager

    @staticmethod
    def create()->QgisInterface:
        """
        Create the QgisMockup and sets the global variables
        :return: QgisInterface
        """

        iface = QgisMockup()

        import qgis.utils
        # import processing
        # p = processing.classFactory(iface)
        if not isinstance(qgis.utils.iface, QgisInterface):

            import processing
            qgis.utils.iface = iface
            processing.Processing.initialize()

            import pkgutil
            prefix = str(processing.__name__ + '.')
            for importer, modname, ispkg in pkgutil.walk_packages(processing.__path__, prefix=prefix):
                try:
                    module = __import__(modname, fromlist="dummy")
                    if hasattr(module, 'iface'):
                        print(modname)
                        module.iface = iface
                except:
                    pass
        #set 'home_plugin_path', which is required from the QGIS Plugin manager
        assert qgis.utils.iface == iface
        qgis.utils.home_plugin_path = os.path.join(QgsApplication.instance().qgisSettingsDirPath(), *['python', 'plugins'])
        return iface

    def __init__(self, *args):
        # QgisInterface.__init__(self)
        super(QgisMockup, self).__init__()

        self.mCanvas = QgsMapCanvas()
        self.mCanvas.blockSignals(False)
        self.mCanvas.setCanvasColor(Qt.black)
        self.mCanvas.extentsChanged.connect(self.testSlot)
        self.mLayerTreeView = QgsLayerTreeView()
        self.mRootNode = QgsLayerTree()
        self.mLayerTreeModel = QgsLayerTreeModel(self.mRootNode)
        self.mLayerTreeView.setModel(self.mLayerTreeModel)
        self.mLayerTreeMapCanvasBridge = QgsLayerTreeMapCanvasBridge(self.mRootNode, self.mCanvas)
        self.mLayerTreeMapCanvasBridge.setAutoSetupOnFirstLayer(True)

        import pyplugin_installer.installer
        PI = pyplugin_installer.instance()
        self.mPluginManager = QgsPluginManagerMockup()

        self.ui = QMainWindow()



        self.mMessageBar = QgsMessageBar()
        mainFrame = QFrame()

        self.ui.setCentralWidget(mainFrame)
        self.ui.setWindowTitle('QGIS Mockup')


        l = QHBoxLayout()
        l.addWidget(self.mLayerTreeView)
        l.addWidget(self.mCanvas)
        v = QVBoxLayout()
        v.addWidget(self.mMessageBar)
        v.addLayout(l)
        mainFrame.setLayout(v)
        self.ui.setCentralWidget(mainFrame)
        self.lyrs = []
        self.createActions()

    def iconSize(self, dockedToolbar=False):
        return QSize(30,30)

    def testSlot(self, *args):
        # print('--canvas changes--')
        s = ""

    def mainWindow(self):
        return self.ui


    def addToolBarIcon(self, action):
        assert isinstance(action, QAction)

    def removeToolBarIcon(self, action):
        assert isinstance(action, QAction)


    def addVectorLayer(self, path, basename=None, providerkey=None):
        if basename is None:
            basename = os.path.basename(path)
        if providerkey is None:
            bn, ext = os.path.splitext(basename)

            providerkey = 'ogr'
        l = QgsVectorLayer(path, basename, providerkey)
        assert l.isValid()
        QgsProject.instance().addMapLayer(l, True)
        self.mRootNode.addLayer(l)
        self.mLayerTreeMapCanvasBridge.setCanvasLayers()
        s = ""

    def legendInterface(self):
        return None

    def addRasterLayer(self, path, baseName=''):
        l = QgsRasterLayer(path, os.path.basename(path))
        self.lyrs.append(l)
        QgsProject.instance().addMapLayer(l, True)
        self.mRootNode.addLayer(l)
        self.mLayerTreeMapCanvasBridge.setCanvasLayers()
        return

        cnt = len(self.canvas.layers())

        self.canvas.setLayerSet([QgsMapCanvasLayer(l)])
        l.dataProvider()
        if cnt == 0:
            self.canvas.mapSettings().setDestinationCrs(l.crs())
            self.canvas.setExtent(l.extent())

            spatialExtent = SpatialExtent.fromMapLayer(l)
            # self.canvas.blockSignals(True)
            self.canvas.setDestinationCrs(spatialExtent.crs())
            self.canvas.setExtent(spatialExtent)
            # self.blockSignals(False)
            self.canvas.refresh()

        self.canvas.refresh()

    def createActions(self):
        m = self.ui.menuBar().addAction('Add Vector')
        m = self.ui.menuBar().addAction('Add Raster')

    def mapCanvas(self):
        return self.mCanvas

    def mapNavToolToolBar(self):
        super().mapNavToolToolBar()

    def messageBar(self, *args, **kwargs):
        return self.mMessageBar

    def rasterMenu(self):
        super().rasterMenu()

    def vectorMenu(self):
        super().vectorMenu()

    def viewMenu(self):
        super().viewMenu()

    def windowMenu(self):
        super().windowMenu()

    def zoomFull(self, *args, **kwargs):
        super().zoomFull(*args, **kwargs)


def createQgsField(name : str, exampleValue, comment:str=None):
    """
    Create a QgsField using a Python-datatype exampleValue
    :param name: field name
    :param exampleValue: value, can be any type
    :param comment: (optional) field comment.
    :return: QgsField
    """
    t = type(exampleValue)
    if t in [str]:
        return QgsField(name, QVariant.String, 'varchar', comment=comment)
    elif t in [bool]:
        return QgsField(name, QVariant.Bool, 'int', len=1, comment=comment)
    elif t in [int, np.int32, np.int64]:
        return QgsField(name, QVariant.Int, 'int', comment=comment)
    elif t in [float, np.double, np.float, np.float64]:
        return QgsField(name, QVariant.Double, 'double', comment=comment)
    elif isinstance(exampleValue, np.ndarray):
        return QgsField(name, QVariant.String, 'varchar', comment=comment)
    elif isinstance(exampleValue, list):
        assert len(exampleValue)> 0, 'need at least one value in provided list'
        v = exampleValue[0]
        prototype = createQgsField(name, v)
        subType = prototype.type()
        typeName = prototype.typeName()
        return QgsField(name, QVariant.List, typeName, comment=comment, subType=subType)
    else:
        raise NotImplemented()


def setQgsFieldValue(feature:QgsFeature, field, value):
    """
    Wrties the Python value v into a QgsFeature field, taking care of required conversions
    :param feature: QgsFeature
    :param field: QgsField | field name (str) | field index (int)
    :param value: any python value
    """

    if isinstance(field, int):
        field = feature.fields().at(field)
    elif isinstance(field, str):
        field = feature.fields().at(feature.fieldNameIndex(field))
    assert isinstance(field, QgsField)

    if value is None:
        value = QVariant.NULL
    if field.type() == QVariant.String:
        value = str(value)
    elif field.type() in [QVariant.Int, QVariant.Bool]:
        value = int(value)
    elif field.type() in [QVariant.Double]:
        value = float(value)
    else:
        raise NotImplementedError()

   # i = feature.fieldNameIndex(field.name())
    feature.setAttribute(field.name(), value)



def initQgisApplication(pythonPlugins=None, PATH_QGIS=None, qgisDebug=False, qgisResourceDir=None):
    """
    Initializes the QGIS Environment
    :return: QgsApplication instance of local QGIS installation
    """
    import site
    if pythonPlugins is None:
        pythonPlugins = []
    assert isinstance(pythonPlugins, list)

    if os.path.exists(os.path.join(DIR_REPO, 'qgisresources')):
        qgisResourceDir = os.path.join(DIR_REPO, 'qgisresources')
    if isinstance(qgisResourceDir, str):
        assert os.path.isdir(qgisResourceDir)
        import importlib, re
        modules = [m for m in os.listdir(qgisResourceDir) if re.search(r'[^_].*\.py', m)]
        modules = [m[0:-3] for m in modules]
        for m in modules:
            mod = importlib.import_module('qgisresources.{}'.format(m))
            if "qInitResources" in dir(mod):
                mod.qInitResources()

    envVar = os.environ.get('QGIS_PLUGINPATH', None)
    if isinstance(envVar, list):
        pythonPlugins.extend(re.split('[;:]', envVar))

    # make plugin paths available to QGIS and Python
    os.environ['QGIS_PLUGINPATH'] = ';'.join(pythonPlugins)
    os.environ['QGIS_DEBUG'] = '1' if qgisDebug else '0'
    for p in pythonPlugins:
        sys.path.append(p)

    if isinstance(QgsApplication.instance(), QgsApplication):

        return QgsApplication.instance()

    else:

        if PATH_QGIS is None:
            # find QGIS Path
            if sys.platform == 'darwin':
                # search for the QGIS.app
                import qgis, re
                assert '.app' in qgis.__file__, 'Can not locate path of QGIS.app'
                PATH_QGIS_APP = re.split(r'\.app[\/]', qgis.__file__)[0] + '.app'
                PATH_QGIS = os.path.join(PATH_QGIS_APP, *['Contents', 'MacOS'])

                if not 'GDAL_DATA' in os.environ.keys():
                    os.environ['GDAL_DATA'] = r'/Library/Frameworks/GDAL.framework/Versions/Current/Resources/gdal'

                QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns']))
                QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns', 'qgis']))


            else:
                # assume OSGeo4W startup
                PATH_QGIS = os.environ['QGIS_PREFIX_PATH']

        assert os.path.exists(PATH_QGIS)

        qgsApp = QgsApplication([], True)
        qgsApp.setPrefixPath(PATH_QGIS, True)
        qgsApp.initQgis()

        def printQgisLog(msg, tag, level):
            if tag not in ['Processing']:
                if tag in ['Python warning', 'warning']:
                    import re
                    if re.search('(Deprecation|Import)Warning', msg) is not None:
                        return
                    else:
                        return
                print(msg)

        QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

        return qgsApp




def guessDataProvider(src:str)->str:
    """
    Get an uri and guesses the QgsDataProvider for
    :param uri: str
    :return: str, provider key like 'gdal', 'ogr' or None
    """
    if re.search(r'\.(bsq|tiff?|jp2|jp2000|j2k|png)', src, re.I):
        return 'gdal'
    elif re.search(r'\.(sli|esl)$', src, re.I):  # probably a spectral library
        return 'enmapbox_speclib'
    elif re.search(r'\.(shp|gpkg|kml)$', src, re.I):  # probably a vector file
        return 'ogr'
    elif re.search(r'\.(txt|csv)$', src, re.I):  # probably normal text file
        return 'enmapbox_textfile'
    elif re.search(r'\.pkl$', src, re.I):
        return 'enmapbox_pkl'
    elif re.search(r'url=https?.*wfs', src, re.I):
        return 'WFS'
    return None


def settings():
    """
    Returns the QSettings object with EnMAPBox Settings
    :return:
    """
    print('DEPRECATED CALL enmapbox.gui.utils.settings()')
    from enmapbox.gui.settings import qtSettingsObj
    return qtSettingsObj()


def showMessage(message, title, level):
    v = QgsMessageViewer()
    v.setTitle(title)

    v.setMessage(message, QgsMessageOutput.MessageHtml \
        if message.startswith('<html>')
    else QgsMessageOutput.MessageText)

    v.showMessage(True)


def file_search(rootdir, pattern, recursive=False, ignoreCase=False):
    assert os.path.isdir(rootdir), "Path is not a directory:{}".format(rootdir)
    regType = type(re.compile('.*'))
    results = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if isinstance(pattern, regType):
                if pattern.search(file):
                    path = os.path.join(root, file)
                    results.append(path)

            elif (ignoreCase and fnmatch.fnmatch(file.lower(), pattern.lower())) \
                    or fnmatch.fnmatch(file, pattern):

                path = os.path.join(root, file)
                results.append(path)
        if not recursive:
            break
            pass

    return results


def gdalDataset(pathOrDataset, eAccess=gdal.GA_ReadOnly):
    """

    :param pathOrDataset: path or gdal.Dataset
    :return: gdal.Dataset
    """
    if not isinstance(pathOrDataset, gdal.Dataset):
        pathOrDataset = gdal.Open(pathOrDataset, eAccess)
    assert isinstance(pathOrDataset, gdal.Dataset), 'Can not read {} as gdal.Dataset'.format(pathOrDataset)
    return pathOrDataset


loadUI = lambda basename: loadUIFormClass(jp(DIR_UIFILES, basename))

# dictionary to store form classes and avoid multiple calls to read <myui>.ui
FORM_CLASSES = dict()



def loadUIFormClass(pathUi:str, from_imports=False, resourceSuffix:str='', fixQGISRessourceFileReferences=True):
    """
    Loads Qt UI files (*.ui) while taking care on QgsCustomWidgets.
    Uses PyQt4.uic.loadUiType (see http://pyqt.sourceforge.net/Docs/PyQt4/designer.html#the-uic-module)
    :param pathUi: *.ui file path
    :param from_imports:  is optionally set to use import statements that are relative to '.'. At the moment this only applies to the import of resource modules.
    :param resourceSuffix: is the suffix appended to the basename of any resource file specified in the .ui file to create the name of the Python module generated from the resource file by pyrcc4. The default is '_rc', i.e. if the .ui file specified a resource file called foo.qrc then the corresponding Python module is foo_rc.
    :return: the form class, e.g. to be used in a class definition like MyClassUI(QFrame, loadUi('myclassui.ui'))
    """

    RC_SUFFIX =  resourceSuffix
    assert os.path.exists(pathUi), '*.ui file does not exist: {}'.format(pathUi)


    if pathUi not in FORM_CLASSES.keys():
        #parse *.ui xml and replace *.h by qgis.gui
        doc = QDomDocument()

        #remove new-lines. this prevents uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
        #to mess up the *.ui xml

        f = open(pathUi, 'r')
        txt = f.read()
        f.close()

        dirUi = os.path.dirname(pathUi)

        locations = []

        for m in re.findall(r'(<include location="(.*\.qrc)"/>)', txt):
            locations.append(m)

        removed = []
        for t in locations:
            line, path = t
            if not os.path.isabs(path):
                p = os.path.join(dirUi, path)
            else:
                p = path

            if not os.path.isfile(p):
                removed.append(t)
                txt = txt.replace(line, '')

        if len(removed) > 0:
            print('None-existing resource file(s) in: {}'.format(pathUi), file=sys.stderr)
            for t in removed:
                line, path = t
                print('\t{}'.format(line), file=sys.stderr)

        #:/images/themes/default/console/iconRestoreTabsConsole.svg
        #resource="../../../../../QGIS-master/images/images.qrc"
        # <include location="../../../../../QGIS-master/images/images.qrc"/>
        doc.setContent(txt)

        # Replace *.h file references in <customwidget> with <class>Qgs...</class>, e.g.
        #       <header>qgscolorbutton.h</header>
        # by    <header>qgis.gui</header>
        # this is require to compile QgsWidgets on-the-fly
        elem = doc.elementsByTagName('customwidget')
        for child in [elem.item(i) for i in range(elem.count())]:
            child = child.toElement()
            className = str(child.firstChildElement('class').firstChild().nodeValue())
            if className.startswith('Qgs'):
                cHeader = child.firstChildElement('header').firstChild()
                cHeader.setNodeValue('qgis.gui')


        #collect resource file locations
        elems = doc.elementsByTagName('include')
        qrcPaths = []
        for i in range(elems.count()):
            node = elems.item(i).toElement()
            lpath = node.attribute('location')
            if len(lpath) > 0 and lpath.endswith('.qrc'):
                p = lpath
                if not os.path.isabs(lpath):
                    p = os.path.join(dirUi, lpath)
                else:
                    p = lpath
                qrcPaths.append(p)
        #for child in [elem.item(i) for i in range(elem.count())]:
        #    path = child.attributes().item(0).nodeValue()
        #    if path.endswith('.qrc'):
        #        qrcPathes.append(path)




        buffer = io.StringIO()  # buffer to store modified XML
        buffer.write(doc.toString())
        buffer.flush()
        buffer.seek(0)


        #make resource file directories available to the python path (sys.path)
        baseDir = os.path.dirname(pathUi)
        tmpDirs = []
        for qrcPath in qrcPaths:
            d = os.path.abspath(os.path.join(baseDir, qrcPath))
            d = os.path.dirname(d)
            if d not in sys.path:
                tmpDirs.append(d)
        sys.path.extend(tmpDirs)

        #load form class
        try:
            FORM_CLASS, _ = uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
        except SyntaxError as ex:
            FORM_CLASS, _ = uic.loadUiType(pathUi, resource_suffix=RC_SUFFIX)

        buffer.close()
        buffer = None
        FORM_CLASSES[pathUi] = FORM_CLASS

        #remove temporary added directories from python path
        for d in tmpDirs:
            sys.path.remove(d)

    return FORM_CLASSES[pathUi]



def typecheck(variable, type_):
    if isinstance(type_, list):
        for i in range(len(type_)):
            typecheck(variable[i], type_[i])
    else:
        assert isinstance(variable, type_)


from collections import defaultdict
import weakref


class KeepRefs(object):
    __refs__ = defaultdict(list)

    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst


def appendItemsToMenu(menu, itemsToAdd):
    """
    Appends items to QMenu "menu"
    :param menu: the QMenu to be extended
    :param itemsToAdd: QMenu or [list-of-QActions-or-QMenus]
    :return: menu
    """
    assert isinstance(menu, QMenu)
    if isinstance(itemsToAdd, QMenu):
        itemsToAdd = itemsToAdd.children()
    if not isinstance(itemsToAdd, list):
        itemsToAdd = [itemsToAdd]

    for item in itemsToAdd:
        if isinstance(item, QAction):
            item.setParent(menu)
            menu.addAction(item)
            s = ""
        elif isinstance(item, QMenu):
            # item.setParent(menu)
            sub = menu.addMenu(item.title())
            sub.setIcon(item.icon())
            appendItemsToMenu(sub, item.children()[1:])
        else:
            s = ""
    return menu


def allSubclasses(cls):
    """
    Returns all subclasses of class 'cls'
    Thx to: http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-class-given-its-name
    :param cls:
    :return:
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in allSubclasses(s)]


class PanelWidgetBase(QgsDockWidget):
    def __init__(self, parent):
        super(PanelWidgetBase, self).__init__(parent)
        self.setupUi(self)

    def _blockSignals(self, widgets, block=True):
        states = dict()
        if isinstance(widgets, dict):
            for w, block in widgets.items():
                states[w] = w.blockSignals(block)
        else:
            for w in widgets:
                states[w] = w.blockSignals(block)
        return states


def check_package(name, package=None, stop_on_error=False):
    try:
        importlib.import_module(name, package)
    except Exception as e:
        if stop_on_error:
            raise Exception('Unable to import package/module "{}"'.format(name))
        return False
    return True


def zipdir(pathDir, pathZip):
    """
    :param pathDir: directory to compress
    :param pathZip: path to new zipfile
    """
    # thx to https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    """
    import zipfile
    assert os.path.isdir(pathDir)
    zipf = zipfile.ZipFile(pathZip, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(pathDir):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()
    """
    relroot = os.path.abspath(os.path.join(pathDir, os.pardir))
    with zipfile.ZipFile(pathZip, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(pathDir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)


def convertMetricUnit(value, u1, u2):
    """converts value, given in unit u1, to u2"""
    assert u1 in METRIC_EXPONENTS.keys()
    assert u2 in METRIC_EXPONENTS.keys()

    e1 = METRIC_EXPONENTS[u1]
    e2 = METRIC_EXPONENTS[u2]

    return value * 10 ** (e1 - e2)


def displayBandNames(rasterSource, bands=None, leadingBandNumber=True):
    """
    Returns a list of readable band names from a raster source.
    Will use "Band 1"  ff no band name is defined.
    :param rasterSource: QgsRasterLayer | gdal.DataSource | str
    :param bands:
    :return:
    """

    if isinstance(rasterSource, str):
        return displayBandNames(QgsRasterLayer(rasterSource), bands=bands, leadingBandNumber=leadingBandNumber)
    if isinstance(rasterSource, QgsRasterLayer):
        if not rasterSource.isValid():
            return None
        else:
            return displayBandNames(rasterSource.dataProvider(), bands=bands, leadingBandNumber=leadingBandNumber)
    if isinstance(rasterSource, gdal.Dataset):
        #use gdal.Band.GetDescription() for band name
        results = []
        if bands is None:
            bands = range(1, rasterSource.RasterCount + 1)
        for band in bands:
            b = rasterSource.GetRasterBand(band)
            name = b.GetDescription()
            if len(name) == 0:
                name = 'Band {}'.format(band)
            if leadingBandNumber:
                name = '{}:{}'.format(band, name)
            results.append(name)
        return results
    if isinstance(rasterSource, QgsRasterDataProvider):
        if rasterSource.name() == 'gdal':
            ds = gdal.Open(rasterSource.dataSourceUri())
            return displayBandNames(ds, bands=bands, leadingBandNumber=leadingBandNumber)
        else:
            #in case of WMS and other data providers use QgsRasterRendererWidget::displayBandName
            results = []
            if bands is None:
                bands = range(1, rasterSource.bandCount() + 1)
            for band in bands:
                name = rasterSource.generateBandName(band)
                colorInterp ='{}'.format(rasterSource.colorInterpretationName(band))
                if colorInterp != 'Undefined':
                    name += '({})'.format(colorInterp)
                if leadingBandNumber:
                    name = '{}:{}'.format(band, name)
                results.append(name)

            return results

    return None


def defaultBands(dataset):
    """
    Returns a list of 3 default bands
    :param dataset:
    :return:
    """
    if isinstance(dataset, str):
        return defaultBands(gdal.Open(dataset))
    elif isinstance(dataset, QgsRasterDataProvider):
        return defaultBands(dataset.dataSourceUri())
    elif isinstance(dataset, QgsRasterLayer):
        return defaultBands(dataset.source())
    elif isinstance(dataset, gdal.Dataset):

        db = dataset.GetMetadataItem(str('default_bands'), str('ENVI'))
        if db != None:
            db = [int(n) for n in re.findall(r'\d+')]
            return db
        db = [0, 0, 0]
        cis = [gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand]
        for b in range(dataset.RasterCount):
            band = dataset.GetRasterBand(b + 1)
            assert isinstance(band, gdal.Band)
            ci = band.GetColorInterpretation()
            if ci in cis:
                db[cis.index(ci)] = b
        if db != [0, 0, 0]:
            return db

        rl = QgsRasterLayer(dataset.GetFileList()[0])
        defaultRenderer = rl.renderer()
        if isinstance(defaultRenderer, QgsRasterRenderer):
            db = defaultRenderer.usesBands()
            if len(db) == 0:
                return [0, 1, 2]
            if len(db) > 3:
                db = db[0:3]
            db = [b-1 for b in db]
        return db

    else:
        raise Exception()


def bandClosestToWavelength(dataset, wl, wl_unit='nm'):
    """
    Returns the band index of an image dataset closest to wavelength `wl`.
    :param dataset: str | gdal.Dataset
    :param wl: wavelength to search the closed band for
    :param wl_unit: unit of wavelength. Default = nm
    :return: band index | 0 of wavelength information is not provided
    """
    if isinstance(wl, str):
        assert wl.upper() in LUT_WAVELENGTH.keys(), wl
        return bandClosestToWavelength(dataset, LUT_WAVELENGTH[wl.upper()], wl_unit='nm')
    else:
        try:
            wl = float(wl)
            ds_wl, ds_wlu = parseWavelength(dataset)

            if ds_wl is None or ds_wlu is None:
                return 0


            if ds_wlu != wl_unit:
                wl = convertMetricUnit(wl, wl_unit, ds_wlu)
            return int(np.argmin(np.abs(ds_wl - wl)))
        except:
            pass
    return 0


def parseWavelength(dataset):
    """
    Returns the wavelength + wavelength unit of a dataset
    :param dataset:
    :return: (wl, wl_u) or (None, None), if not existing
    """

    wl = None
    wlu = None

    if isinstance(dataset, str):
        return parseWavelength(gdal.Open(dataset))
    elif isinstance(dataset, QgsRasterDataProvider):
        return parseWavelength(dataset.dataSourceUri())
    elif isinstance(dataset, QgsRasterLayer):
        return parseWavelength(dataset.source())
    elif isinstance(dataset, gdal.Dataset):

        for domain in dataset.GetMetadataDomainList():
            # see http://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html for supported wavelength units

            mdDict = dataset.GetMetadata_Dict(domain)

            for key, values in mdDict.items():
                key = key.lower()
                if re.search(r'wavelength$', key, re.I):
                    tmp = re.findall(r'\d*\.\d+|\d+', values)  # find floats
                    if len(tmp) != dataset.RasterCount:
                        tmp = re.findall(r'\d+', values)  # find integers
                    if len(tmp) == dataset.RasterCount:
                        wl = np.asarray([float(w) for w in tmp])

                if re.search(r'wavelength.units?', key):
                    if re.search('(Micrometers?|um)', values, re.I):
                        wlu = 'um'  # fix with python 3 UTF
                    elif re.search('(Nanometers?|nm)', values, re.I):
                        wlu = 'nm'
                    elif re.search('(Millimeters?|mm)', values, re.I):
                        wlu = 'nm'
                    elif re.search('(Centimeters?|cm)', values, re.I):
                        wlu = 'nm'
                    elif re.search('(Meters?|m)', values, re.I):
                        wlu = 'nm'
                    elif re.search('Wavenumber', values, re.I):
                        wlu = '-'
                    elif re.search('GHz', values, re.I):
                        wlu = 'GHz'
                    elif re.search('MHz', values, re.I):
                        wlu = 'MHz'
                    elif re.search('Index', values, re.I):
                        wlu = '-'
                    else:
                        wlu = '-'

        if wl is not None and len(wl) > dataset.RasterCount:
            wl = wl[0:dataset.RasterCount]

    return wl, wlu


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



def qgisAppQgisInterface()->QgisInterface:
    """
    Returns the QgisInterface of the QgisApp in case everything was started from within the QGIS Main Application
    :return: QgisInterface | None in case the qgis.utils.iface points to another QgisInterface (e.g. the EnMAP-Box itself)
    """
    try:
        import qgis.utils
        if not isinstance(qgis.utils.iface, QgisInterface):
            return None
        mainWindow = qgis.utils.iface.mainWindow()
        if not isinstance(mainWindow, QMainWindow) or mainWindow.objectName() != 'QgisApp':
            return None
        return qgis.utils.iface
    except:
        return None


def getDOMAttributes(elem):
    assert isinstance(elem, QDomElement)
    values = dict()
    attributes = elem.attributes()
    for a in range(attributes.count()):
        attr = attributes.item(a)
        values[attr.nodeName()] = attr.nodeValue()
    return values


def fileSizeString(num, suffix='B', div=1000):
    """
    Returns a human-readable file size string.
    thanks to Fred Cirera
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    :param num: number in bytes
    :param suffix: 'B' for bytes by default.
    :param div: divisor of num, 1000 by default.
    :return: the file size string
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < div:
            return "{:3.1f}{}{}".format(num, unit, suffix)
        num /= div
    return "{:.1f} {}{}".format(num, unit, suffix)


def geo2pxF(geo, gt):
    """
    Returns the pixel position related to a Geo-Coordinate in floating point precision.
    :param geo: Geo-Coordinate as QgsPoint
    :param gt: GDAL Geo-Transformation tuple, as described in http://www.gdal.org/gdal_datamodel.html
    :return: pixel position as QPointF
    """
    assert isinstance(geo, QgsPointXY)
    # see http://www.gdal.org/gdal_datamodel.html
    px = (geo.x() - gt[0]) / gt[1]  # x pixel
    py = (geo.y() - gt[3]) / gt[5]  # y pixel
    return QPointF(px,py)


def geo2px(geo, gt):
    """
    Returns the pixel position related to a Geo-Coordinate as integer number.
    Floating-point coordinate are casted to integer coordinate, e.g. the pixel coordinate (0.815, 23.42) is returned as (0,23)
    :param geo: Geo-Coordinate as QgsPointXY
    :param gt: GDAL Geo-Transformation tuple, as described in http://www.gdal.org/gdal_datamodel.html
    :return: pixel position as QPpint
    """
    px = geo2pxF(geo, gt)
    return QPoint(int(px.x()), int(px.y()))



def px2geo(px, gt):
    """
    Converts a pixel coordinate into a geo-coordinate
    :param px:
    :param gt:
    :return:
    """
    #see http://www.gdal.org/gdal_datamodel.html
    gx = gt[0] + px.x()*gt[1]+px.y()*gt[2]
    gy = gt[3] + px.x()*gt[4]+px.y()*gt[5]
    return QgsPointXY(gx,gy)


class SpatialPoint(QgsPointXY):
    """
    Object to keep QgsPoint and QgsCoordinateReferenceSystem together
    """

    @staticmethod
    def fromMapCanvasCenter(mapCanvas):
        assert isinstance(mapCanvas, QgsMapCanvas)
        crs = mapCanvas.mapSettings().destinationCrs()
        return SpatialPoint(crs, mapCanvas.center())

    @staticmethod
    def fromSpatialExtent(spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        crs = spatialExtent.crs()
        return SpatialPoint(crs, spatialExtent.center())

    def __init__(self, crs, *args):
        if not isinstance(crs, QgsCoordinateReferenceSystem):
            crs = QgsCoordinateReferenceSystem(crs)
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(SpatialPoint, self).__init__(*args)
        self.mCrs = crs

    def __hash__(self):
        return hash(str(self))

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs

    def crs(self):
        return self.mCrs

    def toPixelPosition(self, rasterDataSource, allowOutOfRaster=False):
        """
        Returns the pixel position of this SpatialPoint within the rasterDataSource
        :param rasterDataSource: gdal.Dataset
        :param allowOutOfRaster: set True to return out-of-raster pixel positions, e.g. QPoint(-1,0)
        :return: the pixel position as QPoint
        """
        ds = gdalDataset(rasterDataSource)
        ns, nl = ds.RasterXSize, ds.RasterYSize
        gt = ds.GetGeoTransform()

        pt = self.toCrs(ds.GetProjection())
        if pt is None:
            return None

        px = geo2px(pt, gt)
        if not allowOutOfRaster:
            if px.x() < 0 or px.x() >= ns:
                return None
            if px.y() < 0 or px.y() >= nl:
                return None
        return px

    def toCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        pt = QgsPointXY(self)

        if self.mCrs != crs:
            pt = saveTransform(pt, self.mCrs, crs)

        return SpatialPoint(crs, pt) if pt else None

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.crs().toWkt(), self.x(), self.y()), {}

    def __eq__(self, other):
        if not isinstance(other, SpatialPoint):
            return False
        return self.x() == other.x() and \
               self.y() == other.y() and \
               self.crs() == other.crs()

    def __copy__(self):
        return SpatialPoint(self.crs(), self.x(), self.y())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{} {} {}'.format(self.x(), self.y(), self.crs().authid())



def findParent(qObject, parentType, checkInstance=False):
    parent = qObject.parent()
    if checkInstance:
        while parent != None and not isinstance(parent, parentType):
            parent = parent.parent()
    else:
        while parent != None and type(parent) != parentType:
            parent = parent.parent()
    return parent


def createCRSTransform(src, dst):
    assert isinstance(src, QgsCoordinateReferenceSystem)
    assert isinstance(dst, QgsCoordinateReferenceSystem)
    t = QgsCoordinateTransform()
    t.setSourceCrs(src)
    t.setDestinationCrs(dst)
    return t

def saveTransform(geom, crs1, crs2):
    assert isinstance(crs1, QgsCoordinateReferenceSystem)
    assert isinstance(crs2, QgsCoordinateReferenceSystem)

    result = None
    if isinstance(geom, QgsRectangle):
        if geom.isEmpty():
            return None


        transform = QgsCoordinateTransform()
        transform.setSourceCrs(crs1)
        transform.setDestinationCrs(crs2)
        try:
            rect = transform.transformBoundingBox(geom);
            result = SpatialExtent(crs2, rect)
        except:
            messageLog('Can not transform from {} to {} on rectangle {}'.format( \
                crs1.description(), crs2.description(), str(geom)))

    elif isinstance(geom, QgsPointXY):

        transform = QgsCoordinateTransform();
        transform.setSourceCrs(crs1)
        transform.setDestinationCrs(crs2)
        try:
            pt = transform.transform(geom);
            result = SpatialPoint(crs2, pt)
        except:
            messageLog('Can not transform from {} to {} on QgsPointXY {}'.format( \
                crs1.description(), crs2.description(), str(geom)))
    return result

def scaledUnitString(num, infix=' ', suffix='B', div=1000):
    """
    Returns a human-readable file size string.
    thanks to Fred Cirera
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    :param num: number in bytes
    :param suffix: 'B' for bytes by default.
    :param div: divisor of num, 1000 by default.
    :return: the file size string
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < div:
            return "{:3.1f}{}{}{}".format(num, infix, unit, suffix)
        num /= div
    return "{:.1f}{}{}{}".format(num, infix, unit, suffix)


class SpatialExtent(QgsRectangle):
    """
    Object to keep QgsRectangle and QgsCoordinateReferenceSystem together
    """
    @staticmethod
    def fromMapCanvas(mapCanvas, fullExtent=False):
        assert isinstance(mapCanvas, QgsMapCanvas)

        if fullExtent:
            extent = mapCanvas.fullExtent()
        else:
            extent = mapCanvas.extent()
        crs = mapCanvas.mapSettings().destinationCrs()
        return SpatialExtent(crs, extent)

    @staticmethod
    def world():
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        ext = QgsRectangle(-180,-90,180,90)
        return SpatialExtent(crs, ext)


    @staticmethod
    def fromRasterSource(pathSrc):
        ds = gdalDataset(pathSrc)
        assert isinstance(ds, gdal.Dataset)
        ns, nl = ds.RasterXSize, ds.RasterYSize
        gt = ds.GetGeoTransform()
        crs = QgsCoordinateReferenceSystem(ds.GetProjection())

        xValues = []
        yValues = []
        for x in [0, ns]:
            for y in [0, nl]:
                px = px2geo(QPoint(x,y), gt)
                xValues.append(px.x())
                yValues.append(px.y())

        return SpatialExtent(crs, min(xValues), min(yValues),
                                  max(xValues), max(yValues))


    @staticmethod
    def fromLayer(mapLayer):
        assert isinstance(mapLayer, QgsMapLayer)
        extent = mapLayer.extent()
        crs = mapLayer.crs()
        return SpatialExtent(crs, extent)

    def __init__(self, crs, *args):
        if not isinstance(crs, QgsCoordinateReferenceSystem):
            crs = QgsCoordinateReferenceSystem(crs)
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(SpatialExtent, self).__init__(*args)
        self.mCrs = crs

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs

    def crs(self):
        return self.mCrs

    def toCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        box = QgsRectangle(self)
        if self.mCrs != crs:
            box = saveTransform(box, self.mCrs, crs)
        return SpatialExtent(crs, box) if box else None

    def spatialCenter(self):
        return SpatialPoint(self.crs(), self.center())

    def combineExtentWith(self, *args):
        if args is None:
            return
        elif isinstance(args[0], SpatialExtent):
            extent2 = args[0].toCrs(self.crs())
            self.combineExtentWith(QgsRectangle(extent2))
        else:
            super(SpatialExtent, self).combineExtentWith(*args)

        return self

    def setCenter(self, centerPoint, crs=None):

        if crs and crs != self.crs():
            trans = QgsCoordinateTransform(crs, self.crs())
            centerPoint = trans.transform(centerPoint)

        delta = centerPoint - self.center()
        self.setXMaximum(self.xMaximum() + delta.x())
        self.setXMinimum(self.xMinimum() + delta.x())
        self.setYMaximum(self.yMaximum() + delta.y())
        self.setYMinimum(self.yMinimum() + delta.y())

        return self

    def __cmp__(self, other):
        if other is None: return 1
        s = ""

    def upperRightPt(self):
        return QgsPointXY(*self.upperRight())

    def upperLeftPt(self):
        return QgsPointXY(*self.upperLeft())

    def lowerRightPt(self):
        return QgsPointXY(*self.lowerRight())

    def lowerLeftPt(self):
        return QgsPointXY(*self.lowerLeft())


    def upperRight(self):
        return self.xMaximum(), self.yMaximum()

    def upperLeft(self):
        return self.xMinimum(), self.yMaximum()

    def lowerRight(self):
        return self.xMaximum(), self.yMinimum()

    def lowerLeft(self):
        return self.xMinimum(), self.yMinimum()


    def __eq__(self, other):
        return self.toString() == other.toString()

    def __sub__(self, other):
        raise NotImplementedError()

    def __mul__(self, other):
        raise NotImplementedError()

    def __copy__(self):
        return SpatialExtent(self.crs(), QgsRectangle(self))

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.crs().toWkt(),
                                self.xMinimum(), self.yMinimum(),
                                self.xMaximum(), self.yMaximum()
                                ), {}


    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):

        return '{} {} {}'.format(self.upperLeft(), self.lowerRight(), self.crs().authid())


class IconProvider:
    """
    Provides icons
    """
    EnMAP_Logo = ':/enmapbox/icons/enmapbox.svg'
    Map_Link_Remove = ':/enmapbox/icons/link_open.svg'
    Map_Link = ':/enmapbox/icons/link_basic.svg'
    Map_Link_Center = ':/enmapbox/icons/link_center.svg'
    Map_Link_Extent = ':/enmapbox/icons/link_mapextent.svg'
    Map_Link_Scale = ':/enmapbox/icons/link_mapscale.svg'
    Map_Link_Scale_Center = ':/enmapbox/icons/link_mapscale_center.svg'
    Map_Zoom_In = ':/enmapbox/icons/mActionZoomOut.svg'
    Map_Zoom_Out = ':/enmapbox/icons/mActionZoomIn.svg'
    Map_Pan = ':/enmapbox/icons/mActionPan.svg'
    Map_Touch = ':/enmapbox/icons/mActionTouch.svg'
    File_RasterMask = ':/enmapbox/icons/filelist_mask.svg'
    File_RasterRegression = ':/enmapbox/icons/filelist_regression.svg'
    File_RasterClassification = ':/enmapbox/icons/filelist_classification.svg'
    File_Raster = ':/enmapbox/icons/filelist_image.svg'
    File_Vector_Point = ':/enmapbox/icons/mIconPointLayer.svg'
    File_Vector_Line = ':/enmapbox/icons/mIconLineLayer.svg'
    File_Vector_Polygon = ':/enmapbox/icons/mIconPolygonLayer.svg'

    Dock = ':/enmapbox/icons/viewlist_dock.svg'
    MapDock = ':/enmapbox/icons/viewlist_mapdock.svg'
    SpectralDock = ':/enmapbox/icons/viewlist_spectrumdock.svg'

    @staticmethod
    def resourceIconsPaths():
        import inspect
        return inspect.getmembers(IconProvider, lambda a: not (inspect.isroutine(a)) and a.startswith(':'))

    @staticmethod
    def icon(path):
        if path is None:
            path = IconProvider.EnMAP_Logo

        assert isinstance(path, str)
        icon = None
        if path in IconProvider.resourceIconsPaths():
            icon = QIcon(path)
        else:
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(path))

        return icon

    @staticmethod
    def test():
        required = set(['png', 'svg'])
        available = set([p for p in QImageReader.supportedImageFormats()])
        missing = required - available

        for name, uri in IconProvider.resourceIconsPaths():
            icon = QIcon(uri)
            w = h = 16
            s = icon.actualSize(QSize(w, h))


class EnMAPBoxMimeData(QMimeData):
    def __init__(self):
        super(EnMAPBoxMimeData, self).__init__()
        self.mData = None

    def setEnMAPBoxData(self, data):
        self.mData = data

    def enmapBoxData(self):
        return self.mData

    def hasEnMAPBoxData(self):
        return self.mData != None


if __name__ == '__main__':
    from enmapboxtestdata import enmap

    for b in ['B', 'G', 'R', 'NIR', 'SWIR']:
        print(bandClosestToWavelength(enmap, b))
