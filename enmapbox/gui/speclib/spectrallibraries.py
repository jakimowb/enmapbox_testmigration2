# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    spectrallibraries.py

    Spectral Profiles and Libraries for a GUI context.
    ---------------------
    Date                 : Juli 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This file is part of the EnMAP-Box.                                   *
*                                                                         *
*   The EnMAP-Box is free software; you can redistribute it and/or modify *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   The EnMAP-Box is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with the EnMAP-Box. If not, see <http://www.gnu.org/licenses/>. *
*                                                                         *
***************************************************************************
"""

#see http://python-future.org/str_literals.html for str issue discussion
import os, pathlib, re, tempfile, pickle, copy, shutil, locale, uuid, io, json

import weakref
from collections import OrderedDict
from qgis.core import *
from qgis.gui import *
from qgis.utils import qgsfunction
from qgis.PyQt.QtCore import NULL
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import QgsField, QgsFields, QgsFeature, QgsMapLayer, QgsVectorLayer, QgsConditionalStyle
from qgis.gui import QgsMapCanvas, QgsDockWidget
from pyqtgraph.widgets.PlotWidget import PlotWidget
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
from pyqtgraph.graphicsItems.PlotItem import PlotItem
import pyqtgraph.functions as fn
import numpy as np
from osgeo import gdal, gdal_array, ogr
import collections
from enmapbox.gui.utils import *

from vrtbuilder.virtualrasters import describeRawFile
from enmapbox.gui.widgets.models import *
from enmapbox.gui.plotstyling import PlotStyle, PlotStyleDialog, MARKERSYMBOLS2QGIS_SYMBOLS, createSetPlotStyleAction
import enmapbox.gui.mimedata as mimedata

MODULE_IMPORT_PATH = 'enmapbox.gui.speclib.spectrallibraries'

MIMEDATA_SPECLIB = 'application/hub-spectrallibrary'
MIMEDATA_SPECLIB_LINK = 'application/hub-spectrallibrary-link'
MIMEDATA_XQT_WINDOWS_CSV = 'application/x-qt-windows-mime;value="Csv"'
MIMEDATA_TEXT = 'text/plain'

COLOR_SELECTED_SPECTRA = QColor('green')
COLOR_SELECTED_SPECTRA = QColor('yellow')

DEBUG = True
def log(msg:str):
    if DEBUG:
        QgsMessageLog.logMessage(msg, 'spectrallibraries.py')

def containsSpeclib(mimeData:QMimeData)->bool:
    for f in [MIMEDATA_SPECLIB, MIMEDATA_SPECLIB_LINK]:
        if f in mimeData.formats():
            return True

    return False

FILTERS = 'ENVI Spectral Library + CSV (*.esl *.sli);;CSV Table (*.csv);;ESRI Shapefile (*.shp)'

PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
CURRENT_SPECTRUM_STYLE = PlotStyle()
CURRENT_SPECTRUM_STYLE.markerSymbol = None
CURRENT_SPECTRUM_STYLE.linePen.setStyle(Qt.SolidLine)
CURRENT_SPECTRUM_STYLE.linePen.setColor(Qt.green)


DEFAULT_SPECTRUM_STYLE = PlotStyle()
DEFAULT_SPECTRUM_STYLE.markerSymbol = None
DEFAULT_SPECTRUM_STYLE.linePen.setStyle(Qt.SolidLine)
DEFAULT_SPECTRUM_STYLE.linePen.setColor(Qt.white)

EMPTY_VALUES = [None, NULL, QVariant(), '']
EMPTY_PROFILE_VALUES = {'x':None, 'y':None, 'xUnit':None, 'yUnit':None}

VALUE_FIELD = 'values'
STYLE_FIELD = 'style'
NAME_FIELD = 'name'
FID_FIELD = 'fid'

VSI_DIR = '/vsimem/speclibs/'
gdal.Mkdir(VSI_DIR, 0)


loadSpeclibUI = lambda name: loadUIFormClass(os.path.join(os.path.dirname(__file__), name))


def vsiSpeclibs()->list:
    """
    Returns the URIs pointing on VSIMEM in memory speclibs
    :return: [list-of-str]
    """
    visSpeclibs = []
    for bn in gdal.ReadDir(VSI_DIR):
        if bn == '':
            continue
        p = pathlib.PurePosixPath(VSI_DIR) / bn
        p = p.as_posix()
        stats = gdal.VSIStatL(p)
        if isinstance(stats, gdal.StatBuf) and not stats.IsDirectory():
            visSpeclibs.append(p)

    return visSpeclibs

#CURRENT_SPECTRUM_STYLE.linePen
#pdi.setPen(fn.mkPen(QColor('green'), width=3))
def gdalDataset(pathOrDataset, eAccess=gdal.GA_ReadOnly):
    """

    :param pathOrDataset: path or gdal.Dataset
    :return: gdal.Dataset
    """

    if isinstance(pathOrDataset, QgsRasterLayer):
        return gdalDataset(pathOrDataset.source())

    if not isinstance(pathOrDataset, gdal.Dataset):
        pathOrDataset = gdal.Open(pathOrDataset, eAccess)

    assert isinstance(pathOrDataset, gdal.Dataset)

    return pathOrDataset

def runRemoveFeatureActionRoutine(layerID, id:int):
    """
    Is applied to a set of layer features to change the plotStyle JSON string stored in styleField
    :param layerID: QgsVectorLayer or vector id str
    :param styleField: str, name of string field in layer.fields() to store the PlotStyle
    :param id: feature id of feature for which the QgsAction was called
    """

    layer = findMapLayer(layerID)

    if isinstance(layer, QgsVectorLayer):
        if layer.selectedFeatureCount():
            ids = layer.selectedFeatureIds()
        else:
            ids = [id]
        if len(ids) == 0:
            return
        b = layer.isEditable()
        layer.startEditing()
        layer.deleteFeatures(ids)
        layer.commitChanges()

        if b:
            layer.startEditing()
    else:
        print('unable to find layer "{}"'.format(layerID))

def createRemoveFeatureAction():
    """
    Creates a QgsAction to remove selected QgsFeatures from a QgsVectorLayer
    :return: QgsAction
    """

    iconPath = ':/images/themes/default/mActionDeleteSelected.svg'
    pythonCode = """
from {modulePath} import runRemoveFeatureActionRoutine
layerId = '[% @layer_id %]'
#layerId = [% "layer" %]
runRemoveFeatureActionRoutine(layerId, [% $id %])
""".format(modulePath=MODULE_IMPORT_PATH)

    return QgsAction(QgsAction.GenericPython, 'Remove Spectrum', pythonCode, iconPath, True,
                       notificationMessage='msgRemoveSpectra',
                       actionScopes={'Feature'})

def findTypeFromString(value:str):
    """
    Returns a fitting basic python data type of a string value, i.e.
    :param value: string
    :return: type out of [str, int or float]
    """
    for t in (int, float, str):
        try:
            _ = t(value)
        except ValueError:
            continue
        return t

    #every values can be converted into a string
    return str



def toType(t, arg, empty2None=True):
    """
    Converts lists or single values into type t.

    Examples:
        toType(int, '42') == 42,
        toType(float, ['23.42', '123.4']) == [23.42, 123.4]

    :param t: type
    :param arg: value to convert
    :param empty2None: returns None in case arg is an emptry value (None, '', NoneType, ...)
    :return: arg as type t (or None)
    """
    if isinstance(arg, list):
        return [toType(t, a) for a in arg]
    else:

        if empty2None and arg in EMPTY_VALUES:
            return None
        else:
            return t(arg)


def encodeProfileValueDict(d:dict)->str:
    """
    Converts a SpectralProfile value dictionary into a JSON string.
    :param d: dict
    :return: str
    """
    if not isinstance(d, dict):
        return None
    d2 = {}
    for k in EMPTY_PROFILE_VALUES.keys():
        v  = d.get(k)
        if v is not None:
            d2[k] = v
    return json.dumps(d2, sort_keys=True, separators=(',', ':'))

def decodeProfileValueDict(jsonDump:str):
    """
    Converts a json string into a SpectralProfile value dictionary
    :param jsonDump: str
    :return: dict
    """
    d = EMPTY_PROFILE_VALUES.copy()
    if isinstance(jsonDump, str):
        d2 = json.loads(jsonDump)
        d.update(d2)
    return d


def qgsFieldAttributes2List(attributes)->list:
    """Returns a list of attibutes with None instead of NULL or QVariatn("""
    r = QVariant(None)
    return [None if v == r else v for v in attributes]


def qgsFields2str(qgsFields:QgsFields)->str:
    """Converts the QgsFields definition into a pickalbe string"""
    infos = []
    for field in qgsFields:
        assert isinstance(field, QgsField)
        info = [field.name(), field.type(), field.typeName(), field.length(), field.precision(), field.comment(), field.subType()]
        infos.append(info)
    return json.dumps(infos)

def str2QgsFields(fieldString:str)->QgsFields:
    """Converts the string from qgsFields2str into a QgsFields collection"""
    fields = QgsFields()

    infos = json.loads(fieldString)
    assert isinstance(infos, list)
    for info in infos:
        field = QgsField(*info)
        fields.append(field)
    return fields




#Lookup table for ENVI IDL DataTypes to GDAL Data Types
LUT_IDL2GDAL = {1:gdal.GDT_Byte,
                12:gdal.GDT_UInt16,
                2:gdal.GDT_Int16,
                13:gdal.GDT_UInt32,
                3:gdal.GDT_Int32,
                4:gdal.GDT_Float32,
                5:gdal.GDT_Float64,
                #:gdal.GDT_CInt16,
                #8:gdal.GDT_CInt32,
                6:gdal.GDT_CFloat32,
                9:gdal.GDT_CFloat64}

def ogrStandardFields()->list:
    """Returns the minimum set of field a Spectral Library has to contain"""
    fields = [
        ogr.FieldDefn(FID_FIELD, ogr.OFTInteger),
        ogr.FieldDefn(NAME_FIELD, ogr.OFTString),
        #ogr.FieldDefn('x_unit', ogr.OFTString),
        #ogr.FieldDefn('y_unit', ogr.OFTString),
        ogr.FieldDefn('source', ogr.OFTString),
        ogr.FieldDefn(VALUE_FIELD, ogr.OFTString),
        ogr.FieldDefn(STYLE_FIELD, ogr.OFTString),
        ]
    return fields

def createStandardFields():

    fields = QgsFields()
    for f in ogrStandardFields():
        assert isinstance(f, ogr.FieldDefn)
        name = f.GetName()
        ogrType = f.GetType()

        if ogrType == ogr.OFTString:
            a,b = QVariant.String, 'varchar'
        elif ogrType in [ogr.OFTInteger, ogr.OFTInteger64]:
            a,b = QVariant.Int, 'int'
        elif ogrType in [ogr.OFTReal]:
            a,b = QVariant.Double, 'double'
        else:
            raise NotImplementedError()

        fields.append(QgsField(name, a, b))

    return fields


def value2str(value, sep:str=' ')->str:
    """
    Converst a value into a string
    :param value:
    :param sep: str separator for listed values
    :return:
    """
    if isinstance(value, list):
        value = sep.join([value2str(v, sep=sep) for v in value])
    elif isinstance(value, np.ndarray):
        value = value2str(value.astype(list), sep=sep)
    elif value in EMPTY_VALUES:
        value = ''
    else:
        value = str(value)
    return value


class AbstractSpectralLibraryIO(object):
    """
    Abstract class interface to define I/O operations for spectral libraries
    Overwrite the canRead and read From routines.
    """
    @staticmethod
    def canRead(path):
        """
        Returns true if it can read the source defined by path
        :param path: source uri
        :return: True, if source is readable.
        """
        return False

    @staticmethod
    def readFrom(path):
        """
        Returns the SpectralLibrary read from "path"
        :param path: source of SpectralLibrary
        :return: SpectralLibrary
        """
        return None

    @staticmethod
    def write(speclib, path):
        """Writes the SpectralLibrary to path and returns a list of written files that can be used to open the spectral library with readFrom"""
        assert isinstance(speclib, SpectralLibrary)
        return []

    @staticmethod
    def score(uri:str)->int:
        """
        Returns a score value for the give uri. E.g. 0 for unlikely/unknown, 20 for yes, probalby thats the file format the reader can read.

        :param uri: str
        :return: int
        """
        return 0


class SpectralLibrary(QgsVectorLayer):
    _instances = []
    @staticmethod
    def readFromMimeData(mimeData:QMimeData):
        if MIMEDATA_SPECLIB_LINK in mimeData.formats():
            #extract from link
            id = pickle.loads(mimeData.data(MIMEDATA_SPECLIB_LINK))
            for sl in SpectralLibrary.instances():
                assert isinstance(sl, SpectralLibrary)
                if sl.id() == id:
                    return sl
            pass
        elif MIMEDATA_SPECLIB in mimeData.formats():
            #unpickle
            return SpectralLibrary.readFromPickleDump(mimeData.data(MIMEDATA_SPECLIB))
        elif MIMEDATA_TEXT in mimeData.formats():

            return CSVSpectralLibraryIO.fromString(mimeData.text())

        return None

    @staticmethod
    def readFromPickleDump(data):
        return pickle.loads(data)

    @staticmethod
    def readFromSourceDialog(parent=None):
        """
        Opens a FileOpen dialog to select
        :param parent:
        :return:
        """

        SETTINGS = settings()
        lastDataSourceDir = SETTINGS.value('_lastSpecLibSourceDir', '')

        if not QFileInfo(lastDataSourceDir).isDir():
            lastDataSourceDir = None

        uris = QFileDialog.getOpenFileNames(parent, "Open spectral library", lastDataSourceDir, filter=FILTERS + ';;All files (*.*)', )
        if isinstance(uris, tuple):
            uris = uris[0]

        if len(uris) > 0:
            SETTINGS.setValue('_lastSpecLibSourceDir', os.path.dirname(uris[-1]))

        uris = [u for u in uris if QFileInfo(u).isFile()]
        speclib = SpectralLibrary()
        for u in uris:
            sl = SpectralLibrary.readFrom(str(u))
            if isinstance(sl, SpectralLibrary):
                speclib.addSpeclib(sl)
        return speclib


    @staticmethod
    def readFromRasterPositions(pathRaster, positions):
        #todo: handle vector file input & geometries
        if not isinstance(positions, list):
            positions = [positions]
        profiles = []
        source = gdal.Open(pathRaster)
        i = 0
        for position in positions:
            profile = SpectralProfile.fromRasterSource(source, position)
            if isinstance(profile, SpectralProfile):
                profile.setName('Spectrum {}'.format(i))
                profiles.append(profile)
                i += 1

        sl = SpectralLibrary()
        sl.startEditing()
        sl.addProfiles(profiles)
        assert sl.commitChanges()
        return sl

    @staticmethod
    def readFrom(uri):
        """
        Reads a Spectral Library from the source specified in "uri" (path, url, ...)
        :param uri: path or uri of the source from which to read SpectralProfiles and return them in a SpectralLibrary
        :return: SpectralLibrary
        """
        readers = AbstractSpectralLibraryIO.__subclasses__()
        #readers = [r for r in readers if not r is ClipboardIO] + [ClipboardIO]
        for cls in sorted(readers, key=lambda r:r.score(uri)):
            if cls.canRead(uri):
                return cls.readFrom(uri)
        return None



    sigNameChanged = pyqtSignal(str)

    __refs__ = []
    @classmethod
    def instances(cls)->list:
        #clean refs
        SpectralLibrary.__refs__ = [r for r in SpectralLibrary.__refs__ if r() is not None]
        for r in SpectralLibrary.__refs__:
            if r is not None:
                yield r()

    def __init__(self, name='SpectralLibrary', fields:QgsFields=None, uri=None):


        #crs = SpectralProfile.crs
        #uri = 'Point?crs={}'.format(crs.authid())
        lyrOptions = QgsVectorLayer.LayerOptions(loadDefaultStyle=False, readExtentFromXml=False)
        #super(SpectralLibrary, self).__init__(uri, name, 'memory', lyrOptions)

        if uri is None:
            #create a new, empty backend
            existing_vsi_files = vsiSpeclibs()
            assert isinstance(existing_vsi_files, list)
            i = 0
            uri = pathlib.PurePosixPath(VSI_DIR) / '{}.gpkg'.format(name)
            while uri.as_posix() in existing_vsi_files:
                i += 1
                uri = pathlib.PurePosixPath(VSI_DIR) /'{}{:03}.gpkg'.format(name, i)
            uri = uri.as_posix()
            drv = ogr.GetDriverByName('GPKG')
            assert isinstance(drv, ogr.Driver)
            co = ['VERSION=AUTO']
            dsSrc = drv.CreateDataSource(uri, options=co)
            assert isinstance(dsSrc, ogr.DataSource)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            co = ['GEOMETRY_NAME=geom',
                  'GEOMETRY_NULLABLE=YES',
                  'FID=fid'
                  ]
            lyr =dsSrc.CreateLayer(name, srs = srs, geom_type=ogr.wkbPoint, options=co)
            assert isinstance(lyr, ogr.Layer)
            ldefn = lyr.GetLayerDefn()
            assert isinstance(ldefn, ogr.FeatureDefn)
            for f in ogrStandardFields():
                lyr.CreateField(f)
            dsSrc.FlushCache()
        #consistency check
        uri2 = '{}|{}'.format(dsSrc.GetName(), lyr.GetName())
        assert QgsVectorLayer(uri2).isValid()
        super(SpectralLibrary, self).__init__(uri2, name, 'ogr', lyrOptions)
        self.__refs__.append(weakref.ref(self))

        self.initTableConfig()

    def initTableConfig(self):
        """
        Initializes the QgsAttributeTableConfig
        """

        mgr = self.actions()
        assert isinstance(mgr, QgsActionManager)
        actionSetStyle = createSetPlotStyleAction(self.fields().at(self.fields().lookupField(STYLE_FIELD)))
        assert isinstance(actionSetStyle, QgsAction)
        mgr.addAction(actionSetStyle)

        actionRemoveSpectrum = createRemoveFeatureAction()
        assert isinstance(actionRemoveSpectrum, QgsAction)
        mgr.addAction(actionRemoveSpectrum)

        columns = self.attributeTableConfig().columns()
        columns = [columns[-1]] + columns[:-1]
        conf = QgsAttributeTableConfig()
        conf.setColumns(columns)
        conf.setActionWidgetVisible(True)
        conf.setActionWidgetStyle(QgsAttributeTableConfig.ButtonList)
        self.setAttributeTableConfig(conf)

        self.setEditorWidgetSetup(self.fields().lookupField('style'), QgsEditorWidgetSetup('PlotSettings', {}))
        self.setEditorWidgetSetup(self.fields().lookupField('values'), QgsEditorWidgetSetup('SpectralProfile', {}))

        #

    def __del__(self):

        uri = self.source()

        vsiUris = vsiSpeclibs()
        if uri in vsiUris:
            others = [sl for sl in SpectralLibrary.instances() if sl != self and sl.source() == uri]
            if len(others) == 0:
                #unlink VSIMem data space
                gdal.Unlink(self.source())
                pass

    def mimeData(self, formats:list=None)->QMimeData:
        """
        Wraps this Speclib into a QMimeData object
        :return: QMimeData
        """
        if isinstance(formats, str):
            formats = [formats]
        elif formats is None:
            formats = [MIMEDATA_SPECLIB_LINK]

        mimeData = QMimeData()

        for format in formats:
            assert format in [MIMEDATA_SPECLIB_LINK, MIMEDATA_SPECLIB, MIMEDATA_TEXT]
            if format == MIMEDATA_SPECLIB_LINK:
                mimeData.setData(MIMEDATA_SPECLIB_LINK, pickle.dumps(self.id()))
            elif format == MIMEDATA_SPECLIB:
                mimeData.setData(MIMEDATA_SPECLIB, pickle.dumps(self))
            elif format == MIMEDATA_TEXT:
                txt = CSVSpectralLibraryIO.asString(self)
                mimeData.setText(txt)

        return mimeData

    def optionalFields(self)->list:
        """
        Returns the list of optional fields that are not part of the standard field set.
        :return: [list-of-QgsFields]
        """
        standardFields = createStandardFields()
        return [f for f in self.fields() if f not in standardFields]

    def optionalFieldNames(self)->list:
        """
        Returns the names of additions fields / attributes
        :return: [list-of-str]
        """
        requiredFields = [f.name for f  in ogrStandardFields()]
        return [n for n in self.fields().names() if n not in requiredFields]

    """
    def initConditionalStyles(self):
        styles = self.conditionalStyles()
        assert isinstance(styles, QgsConditionalLayerStyles)

        for fieldName in self.fieldNames():
            red = QgsConditionalStyle("@value is NULL")
            red.setTextColor(QColor('red'))
            styles.setFieldStyles(fieldName, [red])

        red = QgsConditionalStyle('﻿"__serialized__xvalues" is NULL OR "__serialized__yvalues is NULL" ')
        red.setBackgroundColor(QColor('red'))
        styles.setRowStyles([red])
    """

    def addMissingFields(self, fields:QgsFields):
        """Adds missing fields"""
        missingFields = []
        for field in fields:
            assert isinstance(field, QgsField)
            i = self.fields().lookupField(field.name())
            if i == -1:
                missingFields.append(field)

        for f in missingFields:
            self.addAttribute(f)
            s = ""

        s = ""
        #if len(missingFields) > 0:
        #    self.dataProvider().addAttributes(missingFields)


    def addSpeclib(self, speclib, addMissingFields=True):
        assert isinstance(speclib, SpectralLibrary)
        if addMissingFields:
            self.addMissingFields(speclib.fields())
        self.addProfiles([p for p in speclib])

    def addProfiles(self, profiles, addMissingFields:bool=None):

        if addMissingFields is None:
            addMissingFields = isinstance(profiles, SpectralLibrary)

        if isinstance(profiles, SpectralProfile):
            profiles = [profiles]
        elif isinstance(profiles, SpectralLibrary):
            profiles = profiles.profiles()

        assert isinstance(profiles, list)
        if len(profiles) == 0:
            return

        for i, p in enumerate(profiles):
            assert isinstance(p, SpectralProfile)

        fields = self.fields()

        fid = 0
        assert self.isEditable(), 'SpectralLibrary not editable. call startEditing() first'

        if addMissingFields:
            self.addMissingFields(profiles[0].fields())

        fields = self.fields()

        def createCopy(srcFeature:QgsFeature)->QgsFeature:


            srcFields = srcFeature.fields()
            dstFields = self.fields()
            p2 = QgsFeature(dstFields)
            for field in dstFields:
                a = srcFields.lookupField(field.name())
                if a >= 0:
                    p2.setAttribute(dstFields.lookupField(field.name()), srcFeature.attribute(a))

            p2.setAttribute(FID_FIELD, None)
            return p2
        profiles = [createCopy(p) for p in profiles]
        self.addFeatures(profiles)

    def speclibFromFeatureIDs(self, fids):
        if isinstance(fids, int):
            fids = [fids]
        assert isinstance(fids, list)

        profiles = list(self.profiles(fids))

        speclib = SpectralLibrary()
        speclib.startEditing()
        speclib.addMissingFields(self.fields())
        speclib.addProfiles(profiles)
        speclib.commitChanges()
        return speclib

    def removeProfiles(self, profiles):
        """
        Removes profiles from this ProfileSet
        :param profiles: Profile or [list-of-profiles] to be removed
        :return: [list-of-remove profiles] (only profiles that existed in this set before)
        """
        if not isinstance(profiles, list):
            profiles = [profiles]

        for p in profiles:
            assert isinstance(p, SpectralProfile)

        fids = [p.id() for p in profiles]
        if len(fids) == 0:
            return

        b = self.isEditable()
        self.startEditing()
        self.deleteFeatures(fids)
        self.commitChanges()
        #saveEdits(self, leaveEditable=True)


    def features(self, fids=None)->QgsFeatureIterator:
        """
        Returns the QgsFeatures stored in this QgsVectorLayer
        :param fids: optional, [int-list-of-feature-ids] to return
        :return: QgsFeatureIterator
        """
        featureRequest = QgsFeatureRequest()
        if fids is not None:
            if isinstance(fids, int):
                fids = [fids]
            if not isinstance(fids, list):
                fids = list(fids)
            for fid in fids:
                assert isinstance(fid, int)
            featureRequest.setFilterFids(fids)
        # features = [f for f in self.features() if f.id() in fids]
        return self.getFeatures(featureRequest)


    def profiles(self, fids=None):
        """
        Like features(fids=None), but converts each returned QgsFeature into a SpectralProfile
        :param fids: optional, [int-list-of-feature-ids] to return
        :return: generator of [List-of-SpectralProfiles]
        """
        for f in self.features(fids=fids):
            yield SpectralProfile.fromSpecLibFeature(f)




    def groupBySpectralProperties(self, excludeEmptyProfiles=True):
        """
        Returns SpectralProfiles grouped by:
            xValues, xUnit and yUnit, e.g. wavelength, wavelength unit ('nm') and y unit ('reflectance')

        :return: {(xValues, wlU, yUnit):[list-of-profiles]}
        """

        results = dict()
        for p in self.profiles():
            assert isinstance(p, SpectralProfile)
            d = p.values()
            if excludeEmptyProfiles and d['y'] is None:
                continue
            key = (tuple(d['x']), d['xUnit'], d['yUnit'])
            if key not in results.keys():
                results[key] = []
            results[key].append(p)
        return results


    def asTextLines(self, separator='\t'):
        return CSVSpectralLibraryIO.asString(self, dialect=separator)

    def asPickleDump(self):
        return pickle.dumps(self)

    def exportProfiles(self, path=None, parent=None):

        if path is None:

            path, filter = QFileDialog.getSaveFileName(parent=parent, caption="Save Spectral Library", filter=FILTERS)

        if len(path) > 0:
            ext = os.path.splitext(path)[-1].lower()
            if ext in ['.sli','.esl']:
                return EnviSpectralLibraryIO.write(self, path)

            if ext in ['.csv']:
                return CSVSpectralLibraryIO.write(self, path)


        return []


    def yRange(self):
        profiles = self.profiles()
        minY = min([min(p.yValues()) for p in profiles])
        maxY = max([max(p.yValues()) for p in profiles])
        return minY, maxY

    def __repr__(self):
        return str(self.__class__) + '"{}" {} feature(s)'.format(self.name(), self.dataProvider().featureCount())

    def plot(self):
        """Create a plot widget and shows all SpectralProfile in this SpectralLibrary."""
        import pyqtgraph as pg
        pg.mkQApp()

        win = pg.GraphicsWindow(title="Spectral Library")
        win.resize(1000, 600)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        # Create a plot with some random data
        p1 = win.addPlot(title="Spectral Library {}".format(self.name()), pen=0.5)
        yMin, yMax = self.yRange()
        p1.setYRange(yMin, yMax)

        # Add three infinite lines with labels
        for p in self:
            pi = pg.PlotDataItem(p.xValues(), p.yValues())
            p1.addItem(pi)

        pg.QAPP.exec_()

    def fieldNames(self):
        """
        Retunrs the field names. Shortcut from self.fields().names()
        :return: [list-of-str]
        """
        return self.fields().names()

    def __reduce_ex__(self, protocol):
        return self.__class__, (), self.__getstate__()

    def __getstate__(self):
        """
        Pickles a SpectralLibrary
        :return: pickle dump
        """

        fields = qgsFields2str(self.fields())
        data = []
        for feature in self.features():
            data.append((feature.geometry().asWkt(),
                         qgsFieldAttributes2List(feature.attributes())
                        ))


        dump = pickle.dumps((self.name(),fields, data))
        return dump
        #return self.__dict__.copy()

    def __setstate__(self, state):
        """
        Restores a pickled SpectralLibrary
        :param state:
        :return:
        """
        name, fields, data = pickle.loads(state)
        self.setName(name)
        fieldNames = self.fieldNames()
        dataFields = str2QgsFields(fields)
        fieldsToAdd = [f for f in dataFields if f.name() not in fieldNames]
        self.startEditing()
        if len(fieldsToAdd) > 0:

            for field in fieldsToAdd:
                assert isinstance(field, QgsField)
                self.fields().append(field)
            self.commitChanges()
            self.startEditing()

        fieldNames = self.fieldNames()
        order = [fieldNames.index(f.name()) for f in dataFields]
        reoder = list(range(len(dataFields))) != order

        features = []
        nextFID = self.allFeatureIds()
        nextFID = max(nextFID) if len(nextFID) else 0

        for i, datum in enumerate(data):
            nextFID += 1
            wkt, attributes = datum
            feature = QgsFeature(self.fields(), nextFID)
            if reoder:
                attributes = [attributes[i] for i in order]
            feature.setAttributes(attributes)
            feature.setAttribute(FID_FIELD, nextFID)
            feature.setGeometry(QgsGeometry.fromWkt(wkt))
            features.append(feature)
        self.addFeatures(features)
        self.commitChanges()


    def __len__(self):
        cnt = self.featureCount()
        #can be -1 if the number of features is unknown
        return max(cnt, 0)

    def __iter__(self):
        r = QgsFeatureRequest()
        for f in self.getFeatures(r):
            yield SpectralProfile.fromSpecLibFeature(f)

    def __getitem__(self, slice):
        fids = sorted(self.allFeatureIds())[slice]

        if isinstance(fids, list):
            return sorted(self.profiles(fids=fids), key=lambda p:p.id())
        else:
            return SpectralProfile.fromSpecLibFeature(self.getFeature(fids))

    def __delitem__(self, slice):
        profiles = self[slice]
        self.removeProfiles(profiles)

    def __eq__(self, other):
        if not isinstance(other, SpectralLibrary):
            return False

        if len(self) != len(other):
            return False

        for p1, p2 in zip(self.__iter__(), other.__iter__()):
            if not p1 == p2:
                return False
        return True



class AddAttributeDialog(QDialog):
    """
    A dialog to set up a new QgsField.
    """
    def __init__(self, layer, parent=None):
        assert isinstance(layer, QgsVectorLayer)
        super(AddAttributeDialog, self).__init__(parent)

        assert isinstance(layer, QgsVectorLayer)
        self.mLayer = layer

        self.setWindowTitle('Add Field')
        l = QGridLayout()

        self.tbName = QLineEdit('Name')
        self.tbName.setPlaceholderText('Name')
        self.tbName.textChanged.connect(self.validate)

        l.addWidget(QLabel('Name'), 0,0)
        l.addWidget(self.tbName, 0, 1)

        self.tbComment = QLineEdit()
        self.tbComment.setPlaceholderText('Comment')
        l.addWidget(QLabel('Comment'), 1, 0)
        l.addWidget(self.tbComment, 1, 1)

        self.cbType = QComboBox()
        self.typeModel = OptionListModel()

        for ntype in self.mLayer.dataProvider().nativeTypes():
            assert isinstance(ntype, QgsVectorDataProvider.NativeType)
            o = Option(ntype,name=ntype.mTypeName, tooltip=ntype.mTypeDesc)
            self.typeModel.addOption(o)
        self.cbType.setModel(self.typeModel)
        self.cbType.currentIndexChanged.connect(self.onTypeChanged)
        l.addWidget(QLabel('Type'), 2, 0)
        l.addWidget(self.cbType, 2, 1)

        self.sbLength = QSpinBox()
        self.sbLength.setRange(0, 99)
        self.sbLength.valueChanged.connect(lambda : self.setPrecisionMinMax())
        self.lengthLabel = QLabel('Length')
        l.addWidget(self.lengthLabel, 3, 0)
        l.addWidget(self.sbLength, 3, 1)

        self.sbPrecision = QSpinBox()
        self.sbPrecision.setRange(0, 99)
        self.precisionLabel = QLabel('Precision')
        l.addWidget(self.precisionLabel, 4, 0)
        l.addWidget(self.sbPrecision, 4, 1)

        self.tbValidationInfo = QLabel()
        self.tbValidationInfo.setStyleSheet("QLabel { color : red}")
        l.addWidget(self.tbValidationInfo, 5, 0, 1, 2)


        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        l.addWidget(self.buttons, 6, 1)
        self.setLayout(l)

        self.mLayer = layer

        self.onTypeChanged()

    def accept(self):

        msg = self.validate()

        if len(msg) > 0:
            QMessageBox.warning(self, "Add Field", msg)
        else:
            super(AddAttributeDialog, self).accept()

    def field(self):
        """
        Returns the new QgsField
        :return:
        """
        ntype = self.currentNativeType()
        return QgsField(name=self.tbName.text(),
                        type=QVariant(ntype.mType).type(),
                        typeName=ntype.mTypeName,
                        len=self.sbLength.value(),
                        prec=self.sbPrecision.value(),
                        comment=self.tbComment.text())




    def currentNativeType(self):
        return self.cbType.currentData().value()

    def onTypeChanged(self, *args):
        ntype = self.currentNativeType()
        vMin , vMax = ntype.mMinLen, ntype.mMaxLen
        assert isinstance(ntype, QgsVectorDataProvider.NativeType)

        isVisible = vMin < vMax
        self.sbLength.setVisible(isVisible)
        self.lengthLabel.setVisible(isVisible)
        self.setSpinBoxMinMax(self.sbLength, vMin , vMax)
        self.setPrecisionMinMax()

    def setPrecisionMinMax(self):
        ntype = self.currentNativeType()
        vMin, vMax = ntype.mMinPrec, ntype.mMaxPrec
        isVisible = vMin < vMax
        self.sbPrecision.setVisible(isVisible)
        self.precisionLabel.setVisible(isVisible)

        vMax = max(ntype.mMinPrec, min(ntype.mMaxPrec, self.sbLength.value()))
        self.setSpinBoxMinMax(self.sbPrecision, vMin, vMax)

    def setSpinBoxMinMax(self, sb, vMin, vMax):
        assert isinstance(sb, QSpinBox)
        value = sb.value()
        sb.setRange(vMin, vMax)

        if value > vMax:
            sb.setValue(vMax)
        elif value < vMin:
            sb.setValue(vMin)


    def validate(self):

        msg = []
        name = self.tbName.text()
        if name in self.mLayer.fields().names():
            msg.append('Field name "{}" already exists.'.format(name))
        elif name == '':
            msg.append('Missing field name')
        elif name == 'shape':
            msg.append('Field name "{}" already reserved.'.format(name))

        msg = '\n'.join(msg)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(len(msg) == 0)

        self.tbValidationInfo.setText(msg)

        return msg




class SpectralLibraryTableFilterModel(QgsAttributeTableFilterModel):

    def __init__(self, sourceModel, parent=None):

        dummyCanvas = QgsMapCanvas()
        dummyCanvas.setDestinationCrs(SpectralProfile.crs)
        dummyCanvas.setExtent(QgsRectangle(-180,-90,180,90))

        super(SpectralLibraryTableFilterModel, self).__init__(dummyCanvas, sourceModel, parent=parent)

        self.mDummyCanvas = dummyCanvas

        #self.setSelectedOnTop(True)

"""
class SpectralProfileMapTool(QgsMapToolEmitPoint):

    sigProfileRequest = pyqtSignal(SpatialPoint, QgsMapCanvas)

    def __init__(self, canvas, showCrosshair=True):
        self.mShowCrosshair = showCrosshair
        self.mCanvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.mCanvas)
        self.marker = QgsVertexMarker(self.mCanvas)
        self.rubberband = QgsRubberBand(self.mCanvas, QgsWkbTypes.PolygonGeometry)

        color = QColor('red')

        self.rubberband.setLineStyle(Qt.SolidLine)
        self.rubberband.setColor(color)
        self.rubberband.setWidth(2)

        self.marker.setColor(color)
        self.marker.setPenWidth(3)
        self.marker.setIconSize(5)
        self.marker.setIconType(QgsVertexMarker.ICON_CROSS)  # or ICON_CROSS, ICON_X

    def canvasPressEvent(self, e):
        geoPoint = self.toMapCoordinates(e.pos())
        self.marker.setCenter(geoPoint)
        #self.marker.show()

    def setStyle(self, color=None, brushStyle=None, fillColor=None, lineStyle=None):
        if color:
            self.rubberband.setColor(color)
        if brushStyle:
            self.rubberband.setBrushStyle(brushStyle)
        if fillColor:
            self.rubberband.setFillColor(fillColor)
        if lineStyle:
            self.rubberband.setLineStyle(lineStyle)

    def canvasReleaseEvent(self, e):

        pixelPoint = e.pixelPoint()

        crs = self.mCanvas.mapSettings().destinationCrs()
        self.marker.hide()
        geoPoint = self.toMapCoordinates(pixelPoint)
        if self.mShowCrosshair:
            #show a temporary crosshair
            ext = SpatialExtent.fromMapCanvas(self.mCanvas)
            cen = geoPoint
            geom = QgsGeometry()
            geom.addPart([QgsPointXY(ext.upperLeftPt().x(),cen.y()), QgsPointXY(ext.lowerRightPt().x(), cen.y())],
                          Qgis.Line)
            geom.addPart([QgsPointXY(cen.x(), ext.upperLeftPt().y()), QgsPointXY(cen.x(), ext.lowerRightPt().y())],
                          Qgis.Line)
            self.rubberband.addGeometry(geom, None)
            self.rubberband.show()
            #remove crosshair after 0.1 sec
            QTimer.singleShot(100, self.hideRubberband)

        self.sigProfileRequest.emit(SpatialPoint(crs, geoPoint), self.mCanvas)

    def hideRubberband(self):
        self.rubberband.reset()

"""

class SpectralProfilePlotDataItem(PlotDataItem):

    def __init__(self, spectralProfile):
        assert isinstance(spectralProfile, SpectralProfile)
        super(SpectralProfilePlotDataItem, self).__init__()
        self.mProfile = spectralProfile

        self.setData(x=spectralProfile.xValues(), y=spectralProfile.yValues())
        self.setStyle(self.mProfile.style())
    def setClickable(self, b, width=None):
        assert isinstance(b, bool)
        self.curve.setClickable(b, width=width)


    def setStyle(self, style):
        assert isinstance(style, PlotStyle)
        self.setVisible(style.isVisible())

        self.setSymbol(style.markerSymbol)
        self.setSymbolBrush(style.markerBrush)
        self.setSymbolSize(style.markerSize)
        self.setSymbolPen(style.markerPen)
        self.setPen(style.linePen)


    def setColor(self, color):
        if not isinstance(color, QColor):
            color = QColor(color)
        self.setPen(color)

    def pen(self):
        return fn.mkPen(self.opts['pen'])

    def color(self):
        return self.pen().color()

    def setLineWidth(self, width):
        from pyqtgraph.functions import mkPen
        pen = mkPen(self.opts['pen'])
        assert isinstance(pen, QPen)
        pen.setWidth(width)
        self.setPen(pen)


class SpectralProfile(QgsFeature):

    crs = QgsCoordinateReferenceSystem('EPSG:4326')

    @staticmethod
    def fromMapCanvas(mapCanvas, position)->list:
        """
        Returns a list of Spectral Profiles the raster layers in QgsMapCanvas mapCanvas.
        :param mapCanvas:
        :param position:
        """
        assert isinstance(mapCanvas, QgsMapCanvas)
        layers = [l for l in mapCanvas.layers() if isinstance(l, QgsRasterLayer)]
        sources = [l.source() for l in layers]
        return SpectralProfile.fromRasterSources(sources, position)

    @staticmethod
    def fromRasterSources(sources, position)->list:
        """
        Returns a list of Spectral Profiles
        :param sources: list-of-raster-sources, e.g. file paths, gdal.Datasets, QgsRasterLayers
        :param position:
        :return:
        """
        profiles = [SpectralProfile.fromRasterSource(s, position) for s in sources]
        return [p for p in profiles if isinstance(p, SpectralProfile)]

    @staticmethod
    def fromRasterSource(source, position):
        """
        Returns the Spectral Profiles from source at position `position`
        :param source: path or gdal.Dataset
        :param position:
        :return: SpectralProfile
        """

        ds = gdalDataset(source)

        files = ds.GetFileList()
        if len(files) > 0:
            baseName = os.path.basename(files[0])
        else:
            baseName = 'Spectrum'
        crs = QgsCoordinateReferenceSystem(ds.GetProjection())
        gt = ds.GetGeoTransform()

        if isinstance(position, QPoint):
            px = position
        elif isinstance(position, SpatialPoint):
            px = geo2px(position.toCrs(crs), gt)
        elif isinstance(position, QgsPointXY):
            px = geo2px(position, ds.GetGeoTransform())
        else:
            raise Exception('Unsupported type of argument "position" {}'.format('{}'.format(position)))
        #check out-of-raster
        if px.x() < 0 or px.y() < 0: return None
        if px.x() > ds.RasterXSize - 1 or px.y() > ds.RasterYSize - 1: return None


        x = ds.ReadAsArray(px.x(), px.y(), 1, 1)

        x = x.flatten()
        for b in range(ds.RasterCount):
            band = ds.GetRasterBand(b+1)
            nodata = band.GetNoDataValue()
            if nodata and x[b] == nodata:
                return None

        wl = ds.GetMetadataItem(str('wavelength'), str('ENVI'))
        wlu = ds.GetMetadataItem(str('wavelength_units'), str('ENVI'))
        if wl is not None and len(wl) > 0:
            wl = re.sub(r'[ {}]','', wl).split(',')
            wl = [float(w) for w in wl]

        profile = SpectralProfile()
        profile.setName('{} x{} y{}'.format(baseName, px.x(), px.y()))


        profile.setValues(x=x, y=wl, xUnit=wlu)

        profile.setCoordinates(SpatialPoint(crs, px2geo(px, gt)))
        profile.setSource('{}'.format(ds.GetFileList()[0]))
        return profile




    @staticmethod
    def fromSpecLibFeature(feature):
        assert isinstance(feature, QgsFeature)
        sp = SpectralProfile(fields=feature.fields())
        sp.setId(feature.id())
        sp.setAttributes(feature.attributes())
        sp.setGeometry(feature.geometry())
        return sp


    def __init__(self, parent=None, fields=None, values:dict=None):


        if fields is None:
            fields = createStandardFields()
        assert isinstance(fields, QgsFields)
        #QgsFeature.__init__(self, fields)
        #QObject.__init__(self)
        super(SpectralProfile, self).__init__(fields)
        #QObject.__init__(self)
        #fields = self.fields()

        assert isinstance(fields, QgsFields)
        self.mValueCache = None
        self.setStyle(DEFAULT_SPECTRUM_STYLE)
        if isinstance(values, dict):
            self.setValues(**values)



    def fieldNames(self):
        return self.fields().names()

    def setName(self, name:str):
        if name != self.name():
            self.setAttribute('name', name)
            #self.sigNameChanged.emit(name)

    def name(self):
        return self.metadata('name')

    def setSource(self, uri: str):
        self.setAttribute('source', uri)

    def source(self):
        return self.metadata('source')

    def setCoordinates(self, pt):
        if isinstance(pt, SpatialPoint):
            sp = pt.toCrs(SpectralProfile.crs)
            self.setGeometry(QgsGeometry.fromPointXY(sp))
        elif isinstance(pt, QgsPointXY):
            self.setGeometry(QgsGeometry.fromPointXY(pt))


    def geoCoordinate(self):
        return self.geometry()


    def style(self)->PlotStyle:
        """
        Returns this features's PlotStyle
        :return: PlotStyle
        """
        styleJson = self.metadata(STYLE_FIELD)
        try:
            style = PlotStyle.fromJSON(styleJson)
        except Exception as ex:
            style = DEFAULT_SPECTRUM_STYLE
        return style


    def setStyle(self, style:PlotStyle):
        """
        Sets a Spectral Profiles's plot style
        :param style: PLotStyle
        """
        if isinstance(style, PlotStyle):
            self.setMetadata(STYLE_FIELD, style.json())
        else:
            self.setMetadata(STYLE_FIELD, None)

    def updateMetadata(self, metaData):
        if isinstance(metaData, dict):
            for key, value in metaData.items():
                self.setMetadata(key, value)

    def removeField(self, name):
        fields = self.fields()
        values = self.attributes()
        i = self.fieldNameIndex(name)
        if i >= 0:
            fields.remove(i)
            values.pop(i)
            self.setFields(fields)
            self.setAttributes(values)

    def setMetadata(self, key: str, value, addMissingFields=False):
        """

        :param key: Name of metadata field
        :param value: value to add. Need to be of type None, str, int or float.
        :param addMissingFields: Set on True to add missing fields (in case value is not None)
        :return:
        """
        i = self.fieldNameIndex(key)

        if i < 0:
            if value is not None and addMissingFields:

                fields = self.fields()
                values = self.attributes()
                fields.append(createQgsField(key, value))
                values.append(value)
                self.setFields(fields)
                self.setAttributes(values)

            return False
        else:
            return self.setAttribute(key, value)

    def metadata(self, key: str, default=None):
        """
        Returns a field value or None, if not existent
        :param key: str, field name
        :param default: default value to be returned
        :return: value
        """
        assert isinstance(key, str)
        i = self.fieldNameIndex(key)
        if i < 0:
            return None

        v = self.attribute(i)
        if v == QVariant(None):
            v = None
        return default if v is None else v

    def values(self)->dict:
        """
        Returns a dictionary with 'x', 'y', 'xUnit' and 'yUnit' values.
        :return: {'x':list,'y':list,'xUnit':str,'yUnit':str}
        """
        if self.mValueCache is None:

            jsonStr = self.attribute(self.fields().indexFromName(VALUE_FIELD))
            d = decodeProfileValueDict(jsonStr)
            self.mValueCache = d
        return self.mValueCache

    def setValues(self, x=None, y=None, xUnit=None, yUnit=None):

        d = self.values().copy()

        if isinstance(x, np.ndarray):
            x = x.tolist()

        if isinstance(y, np.ndarray):
            y = y.tolist()

        if x is not None:
            d['x'] = x
        if y is not None:
            d['y'] = y
        if xUnit is not None:
            assert isinstance(xUnit, str)
            d['xUnit'] = xUnit
        if yUnit is not None:
            assert isinstance(yUnit, str)
            d['yUnit'] = yUnit

        if d['x'] is not None:
            assert d['y'] != None
            assert len(d['y']) == len(d['x'])

        #todo: clean empty values to keep json string short


        self.setAttribute(VALUE_FIELD, encodeProfileValueDict(d))
        self.mValueCache = d


    def xValues(self)->list:
        """
        Returns the x Values / wavelength information.
        If wavelength information is not undefined it will return a list of band indices [0, ..., n-1]
        :return: [list-of-numbers]
        """
        values = self.values()
        xValues = values['x']
        if xValues is None and values['y'] is not None:
            return list(range(len(values['y'])))
        return None


    def yValues(self)->list:
        """
        Returns the x Values / DN / spectral profile values
        :return: [list-of-numbers]
        """
        return self.values()['y']

    def setXUnit(self, unit : str):
        d = self.values()
        d['xUnit'] = unit
        self.setValues(**d)

    def xUnit(self)->str:
        """
        Returns the semantic unit of x values, e.g. a wavelength unit like 'nm' or 'um'
        :return: str
        """
        return self.values()['xUnit']

    def setYUnit(self, unit:str=None):
        """
        :param unit:
        :return:
        """
        d = self.values()
        d['yUnit'] = unit
        self.setValues(**d)

    def yUnit(self)->str:
        """
        Returns the semantic unit of y values, e.g. 'reflectances'"
        :return: str
        """

        return self.values()['yUnit']

    def copyFieldSubset(self, fields):

        sp = SpectralProfile(fields=fields)

        fieldsInCommon = [field for field in sp.fields() if field in self.fields()]

        sp.setGeometry(self.geometry())
        sp.setId(self.id())

        for field in fieldsInCommon:
            assert isinstance(field, QgsField)
            i = sp.fieldNameIndex(field.name())
            sp.setAttribute(i, self.attribute(field.name()))
        return sp

    def clone(self):
        """
        Create a clone of this SpectralProfile
        :return: SpectralProfile
        """
        return self.__copy__()

    def plot(self):
        """
        Plots this profile to an new PyQtGraph window
        :return:
        """
        import pyqtgraph as pg

        pi = SpectralProfilePlotDataItem(self)
        pi.setClickable(True)
        pw = pg.plot( title=self.name())
        pw.plotItem().addItem(pi)

        pi.setColor('green')
        pg.QAPP.exec_()


    def __reduce_ex__(self, protocol):

        return self.__class__, (), self.__getstate__()

    def __getstate__(self):

        if self.mValueCache is None:
            self.values()
        wkt = self.geometry().asWkt()
        state = (qgsFields2str(self.fields()), qgsFieldAttributes2List(self.attributes()), wkt)
        dump = pickle.dumps(state)
        return dump

    def __setstate__(self, state):
        state = pickle.loads(state)
        fields, attributes, wkt = state
        fields = str2QgsFields(fields)
        self.setFields(fields)
        self.setGeometry(QgsGeometry.fromWkt(wkt))
        self.setAttributes(attributes)


    def __copy__(self):
        sp = SpectralProfile(fields=self.fields())
        sp.setId(self.id())
        sp.setAttributes(self.attributes())
        sp.setGeometry(QgsGeometry.fromWkt(self.geometry().asWkt()))
        if isinstance(self.mValueCache, dict):
            sp.values()
        return sp

    def __eq__(self, other):
        if not isinstance(other, SpectralProfile):
            return False
        if not np.array_equal(self.fieldNames(), other.fieldNames()):
            return False

        names1 = self.fieldNames()
        names2 = other.fieldNames()
        for i1, n in enumerate(self.fieldNames()):
            if n == FID_FIELD:
                continue
            i2 = names2.index(n)
            if self.attribute(i1) != other.attribute(i2):
                return False

        return True

    def __hash__(self):

        return hash(id(self))

    def setId(self, id):
        self.setAttribute(FID_FIELD, id)
        if id is not None:
            super(SpectralProfile, self).setId(id)

    """
    def __eq__(self, other):
        if not isinstance(other, SpectralProfile):
            return False
        if len(self.mValues) != len(other.mValues):
            return False
        return all(a == b for a,b in zip(self.mValues, other.mValues)) \
            and self.mValuePositions == other.mValuePositions \
            and self.mValueUnit == other.mValueUnit \
            and self.mValuePositionUnit == other.mValuePositionUnit \
            and self.mGeoCoordinate == other.mGeoCoordinate \
            and self.mPxCoordinate == other.mPxCoordinate

    def __ne__(self, other):
        return not self.__eq__(other)
    """
    def __len__(self):
        return len(self.mValues)







class SpectralProfileValueTableModel(QAbstractTableModel):
    """
    A TableModel to show and edit spectral values of a SpectralProfile
    """
    def __init__(self, parent=None):
        super(SpectralProfileValueTableModel, self).__init__(parent)
        self.cYValue = 'Value'
        self.cXValue = None
        self.mColumnNames = [self.cYValue, self.cXValue]
        self.mColumnDataTypes = [None, None]
        self.mColumnDataUnits = [None, None]
        self.mYType = None
        self.mValues = EMPTY_PROFILE_VALUES.copy()

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value, role: int=Qt.EditRole):

        v = False
        if orientation == Qt.Horizontal and role == Qt.EditRole:
            if section == 0:
                self.cYValue = value
                v = True
            elif section == 1:
                self.cXValue = value
                v = True
        if v == True:
            self.headerDataChanged.emit(orientation, section, section)

        return v

    def columnNames(self)->list:
        return [self.cYValue, self.cXValue]

    def setProfileData(self, values):
        """
        :param values:
        :return:
        """
        if isinstance(values, SpectralProfile):
            values = values.values()
        assert isinstance(values, dict)

        for k in EMPTY_PROFILE_VALUES.keys():
            assert k in values.keys()

        self.beginResetModel()
        for i, k in enumerate(['y','x']):
            if values[k] and len(values[k]) > 0:
                self.mColumnDataTypes[i] = type(values[k][0])
            else:
                self.mColumnDataTypes[i] = None
        self.mValues.update(values)
        self.endResetModel()

    def values(self)->dict:
        """
        Returns the value dictionary of a SpectralProfile
        :return: dict
        """
        return self.mValues

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        if self.mValues['x'] is None:
            return 0
        else:
            return len(self.mValues['x'])

    def columnCount(self, parent=QModelIndex()):
        return len(self.columnNames())

    def data(self, index, role=Qt.DisplayRole):
        if role is None or not index.isValid():
            return None

        c = index.column()
        i = index.row()

        if role in [Qt.DisplayRole, Qt.EditRole]:
            if c == 0:
                return self.mValues['y'][i]
            elif c == 1:
                return self.mValues['x'][i]
        if role == Qt.UserRole:
            return self.mValues

        return None

    def setData(self, index, value, role=None):
        if role is None or not index.isValid():
            return None

        c = index.column()
        i = index.row()

        if role == Qt.EditRole:
            #cast to correct data type
            dt = self.mColumnDataTypes[c]
            if dt in [int, float]:
                value = dt(value)

            if c == 0:
                self.mValues['y'][i] = value
                return True
            elif c == 1:
                self.mValues['x'][i] = value
                return True
        return False

    def setColumnValueUnit(self, index, valueUnit:str):
        if isinstance(index, QModelIndex):
            index = index.column()
        assert isinstance(index, int)
        assert index < self.columnCount(None)
        assert valueUnit is None or isinstance(valueUnit, (None, str))

        seö

    def setColumnDataType(self, index, dataType):
        if isinstance(index, QModelIndex):
            index = index.column()
        assert isinstance(index, int)
        assert index < self.columnCount(None)
        assert dataType in [None, int, float]
        self.beginResetModel()
        self.mColumnDataTypes[index] = dataType
        self.endResetModel()

    def flags(self, index):
        if index.isValid():
            c = index.column()
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

            if c == 0:
                flags = flags | Qt.ItemIsEditable
            elif c == 1 and self.mValues['xUnit']:
                flags = flags | Qt.ItemIsEditable
            return flags
            # return item.qt_flags(index.column())
        return None

    def headerData(self, col, orientation, role):
        if Qt is None:
            return None
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columnNames()[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None

class SpectralProfileEditorWidget(QWidget, loadSpeclibUI('spectralprofileeditorwidget.ui')):

    sigProfileValuesChanged = pyqtSignal(dict)
    def __init__(self, parent=None):
        super(SpectralProfileEditorWidget, self).__init__(parent)
        self.setupUi(self)

        self.mDefault = None
        self.mModel = SpectralProfileValueTableModel(parent=self)
        self.mModel.dataChanged.connect(lambda :self.sigProfileValuesChanged.emit(self.profileValues()))
        self.tableView.setModel(self.mModel)
        self.cbXUnit.currentTextChanged.connect(lambda text: self.mModel.setHeaderData(1, Qt.Horizontal, 'X [{}]'.format(text), Qt.EditRole))
        self.cbYUnit.currentTextChanged.connect(lambda text: self.mModel.setHeaderData(0, Qt.Horizontal, 'Y [{}]'.format(text), Qt.EditRole))

        self.actionReset.triggered.connect(self.resetProfileValues)
        self.btnReset.setDefaultAction(self.actionReset)
        self.setProfileValues(EMPTY_PROFILE_VALUES.copy())


    def setProfileValues(self, values):

        if isinstance(values, SpectralProfile):
            values = values.values()

        assert isinstance(values, dict)
        import copy
        self.mDefault = copy.deepcopy(values)

        def cbSetOrSelect(cb:QComboBox, text):
            idx = -1
            for i in range(cb.count()):
                v = cb.itemText(i)
                if v == text:
                    idx = i
                    break
            if idx >= 0:
                cb.setCurrentIndex(idx)
            else:
                cb.insertItem(0, text)

        cbSetOrSelect(self.cbXUnit, values['xUnit'])
        cbSetOrSelect(self.cbYUnit, values['yUnit'])
        self.mModel.setProfileData(values)

        #todo: select units in comboboxes

    def resetProfileValues(self):
        self.setProfileValues(self.mDefault)

    def profileValues(self)->dict:
        """
        Returns the value dictionary of a SpectralProfile
        :return: dict
        """
        return self.mModel.values()


def deleteSelected(layer):

    assert isinstance(layer, QgsVectorLayer)
    b = layer.isEditable()

    layer.startEditing()
    layer.deleteSelectedFeatures()
    layer.commitChanges()

    #saveEdits(layer, leaveEditable=b)


class SpectralLibraryPanel(QgsDockWidget):
    sigLoadFromMapRequest = None
    def __init__(self, parent=None):
        super(SpectralLibraryPanel, self).__init__(parent)
        self.setObjectName('spectralLibraryPanel')
        self.setWindowTitle('Spectral Library')
        self.SLW = SpectralLibraryWidget(self)
        self.setWidget(self.SLW)


    def speclib(self)->SpectralLibrary:
        return self.SLW.speclib()

    def setCurrentSpectra(self, listOfSpectra):
        self.SLW.setCurrentSpectra(listOfSpectra)

    def setAddCurrentSpectraToSpeclibMode(self, b: bool):
        self.SLW.setAddCurrentSpectraToSpeclibMode(b)


class UnitComboBoxItemModel(OptionListModel):
    def __init__(self, parent=None):
        super(UnitComboBoxItemModel, self).__init__(parent)

    def addUnit(self, unit):

        o = Option(unit, unit)
        self.addOption(o)


    def getUnitFromIndex(self, index):
        o = self.idx2option(index)
        assert isinstance(o, Option)
        return o.mValue

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if (index.row() >= len(self.mUnits)) or (index.row() < 0):
            return None
        unit = self.getUnitFromIndex(index)
        value = None
        if role == Qt.DisplayRole:
            value = '{}'.format(unit)
        return value




class SpectralLibraryPlotWidget(PlotWidget):

    def __init__(self, parent=None):
        super(SpectralLibraryPlotWidget, self).__init__(parent)
        self.mModel = None
        self.mPlotItems = dict()
        self.setAntialiasing(True)
        self.setAcceptDrops(True)


    def setModel(self, model):
        assert isinstance(model, SpectralLibraryTableModel)
        self.mModel = model
        speclib = self.speclib()
        assert isinstance(speclib, SpectralLibrary)
        speclib.committedFeaturesAdded.connect(self.onProfilesAdded)
        speclib.committedFeaturesRemoved.connect(self.onProfilesRemoved)
        speclib.committedAttributeValuesChanges.connect(self.onProfileDataChanged)

        self.onProfilesAdded(speclib.id(), speclib[:])

        #self.mModel.rowsAboutToBeRemoved.connect(self.onRowsAboutToBeRemoved)
        #self.mModel.rowsInserted.connect(self.onRowsInserted)
        #self.mModel.dataChanged.connect(self.onDataChanged)
        #if self.mModel.rowCount() > 0:
        #    self.onRowsInserted(self.mModel.index(0,0), 0, self.mModel.rowCount())



    def speclib(self):
        if not isinstance(self.mModel, SpectralLibraryTableModel):
            return None
        return self.mModel.speclib()

    def onProfileDataChanged(self, layerID, changeMap):


        fieldNames = self.speclib().fieldNames()
        iStyle = fieldNames.index(HIDDEN_ATTRIBUTE_PREFIX+'style')

        fids = list(changeMap.keys())
        for fid in fids:
            if iStyle in changeMap[fid].keys():
                #update the local plot style
                style = changeMap[fid].get(iStyle)

                style = pickle.loads(style)

                pdi = self.mPlotItems.get(fid)
                if isinstance(pdi, SpectralProfilePlotDataItem):
                    pdi.setStyle(style)


    def onProfilesAdded(self, layerID, features):

        if len(features) == 0:
            return

        speclib = self.speclib()
        assert isinstance(speclib, SpectralLibrary)

        fids = [f.id() for f in features]
        #remove if existent
        self.onProfilesRemoved(layerID, fids)

        pdis = []
        for feature in features:
            profile = SpectralProfile.fromSpecLibFeature(feature)
            assert isinstance(profile, SpectralProfile)
            pdi = SpectralProfilePlotDataItem(profile)
            self.mPlotItems[pdi.mProfile.id()] = pdi
            pdis.append(pdi)

        for pdi in pdis:
            self.plotItem.addItem(pdi)


    def onProfilesRemoved(self, layerID, fids):

        if len(fids) == 0:
            return
        fids = [fid for fid in fids if fid in list(self.mPlotItems.keys())]
        pdis = [self.mPlotItems.pop(fid) for fid in fids]
        pdis = [pdi for pdi in pdis if isinstance(pdi, SpectralProfilePlotDataItem)]
        for pdi in pdis:
            self.removeItem(pdi)

    def onDataChanged(self, topLeft, bottomRight, roles):

        if topLeft.column() == 0:
            for row in range(topLeft.row(), bottomRight.row()+1):
                fid = self.mModel.rowToId(row)
                idx = self.mModel.idToIndex(fid)
                profile = self.mModel.spectralProfile(idx)

                pdi = self.mPlotItems.get(fid)
                if isinstance(pdi, SpectralProfilePlotDataItem):
                    if len(roles) == 0 or Qt.DecorationRole in roles or Qt.CheckStateRole in roles:
                        pdi.setStyle(profile.style())


    def onRowsAboutToBeRemoved(self, index, first, last):

        fids = [self.mModel.rowToId(i) for i in range(first, last+1)]
        fids = [fid for fid in fids if fid in list(self.mPlotItems.keys())]
        pdis = [self.mPlotItems.pop(fid) for fid in fids]
        pdis = [pdi for pdi in pdis if isinstance(pdi, SpectralProfilePlotDataItem)]
        for pdi in pdis:
            self.removeItem(pdi)

    def onRowsInserted(self, index, first, last):

        for i in range(first, last+1):
            fid = self.mModel.rowToId(i)
            if fid < 0:
                continue

            idx = self.mModel.index(i,0)
            p = self.mModel.spectralProfile(idx)
            assert fid == p.id()

            pdi = SpectralProfilePlotDataItem(p)
            self.mPlotItems[fid] = pdi
            self.addItem(pdi)

    def dragEnterEvent(self, event):
        assert isinstance(event, QDragEnterEvent)
        if containsSpeclib(event.mimeData()):
            event.accept()

    def dragMoveEvent(self, event):
        assert isinstance(event, QDragMoveEvent)
        if containsSpeclib(event.mimeData()):
            event.accept()

    def dropEvent(self, event):
        assert isinstance(event, QDropEvent)
        mimeData = event.mimeData()

        speclib = SpectralLibrary.readFromMimeData(mimeData)
        if isinstance(speclib, SpectralLibrary):
            self.speclib().addSpeclib(speclib)
            event.accept()



class SpectralLibraryWidget(QFrame, loadSpeclibUI('spectrallibrarywidget.ui')):
    sigLoadFromMapRequest = pyqtSignal()

    def __init__(self, parent=None, speclib:SpectralLibrary=None):
        super(SpectralLibraryWidget, self).__init__(parent)
        self.setupUi(self)

        self.mColorCurrentSpectra = COLOR_SELECTED_SPECTRA
        self.mColorSelectedSpectra = COLOR_SELECTED_SPECTRA

        self.m_plot_max = 500
        self.mPlotXUnitModel = UnitComboBoxItemModel()
        self.mPlotXUnitModel.addUnit('Index')

        self.mPlotXUnitModel = OptionListModel()
        self.mPlotXUnitModel.addOption(Option('Index'))

        self.cbXUnit.setModel(self.mPlotXUnitModel)
        self.cbXUnit.currentIndexChanged.connect(lambda: self.setPlotXUnit(self.cbXUnit.currentText()))
        self.cbXUnit.setCurrentIndex(0)
        self.mSelectionModel = None

        self.mCurrentSpectra = []

        if not isinstance(speclib, SpectralLibrary):
            speclib = SpectralLibrary()
        assert isinstance(speclib, SpectralLibrary)
        self.mSpeclib = speclib
        fields = self.mSpeclib.fields()
        self.mSpeclib.setEditorWidgetSetup(fields.lookupField('style'), QgsEditorWidgetSetup('PlotSettings',{}))
        self.mSpeclib.setEditorWidgetSetup(fields.lookupField('values'), QgsEditorWidgetSetup('SpectralProfile', {}))
        self.mSpeclib.startEditing()
        self.mSpeclib.editingStarted.connect(self.onEditingToggled)
        self.mSpeclib.editingStopped.connect(self.onEditingToggled)
        self.mCanvas = QgsMapCanvas()

        assert isinstance(self.mDualView, QgsDualView)
        self.mDualView.init(self.mSpeclib, self.mCanvas)#, context=self.mAttributeEditorContext)
        self.mDualView.setView(QgsDualView.AttributeTable)
        self.mDualView.setAttributeTableConfig(self.mSpeclib.attributeTableConfig())

        self.mOverPlotDataItems = dict() #stores plotDataItems


        pi = self.plotItem()
        pi.setAcceptDrops(True)

        pi.dropEvent = self.dropEvent


        self.initActions()

        self.mMapInteraction = False
        self.setMapInteraction(False)

    def initActions(self):


        self.actionSelectProfilesFromMap.triggered.connect(self.sigLoadFromMapRequest.emit)
        self.actionSaveCurrentProfiles.triggered.connect(self.addCurrentSpectraToSpeclib)
        self.actionAddCurrentProfilesAutomatically.toggled.connect(self.actionSaveCurrentProfiles.setDisabled)

        #self.actionSaveCurrentProfiles.event = onEvent

        self.actionImportSpeclib.triggered.connect(lambda :self.importSpeclib())
        self.actionSaveSpeclib.triggered.connect(lambda :self.speclib().exportProfiles(parent=self))

        self.actionReload.triggered.connect(lambda : self.speclib().dataProvider().forceReload())
        self.actionToggleEditing.toggled.connect(self.onToggleEditing)
        self.actionSaveEdits.triggered.connect(self.onSaveEdits)
        self.actionDeleteSelected.triggered.connect(lambda : deleteSelected(self.speclib()))
        self.actionCutSelectedRows.setVisible(False) #todo
        self.actionCopySelectedRows.setVisible(False) #todo
        self.actionPasteFeatures.setVisible(False)

        self.actionSelectAll.triggered.connect(lambda :
                                               self.speclib().selectAll()
                                               )

        self.actionInvertSelection.triggered.connect(lambda :
                                                     self.speclib().invertSelection()
                                                     )
        self.actionRemoveSelection.triggered.connect(lambda :
                                                     self.speclib().removeSelection()
                                                     )


        self.actionAddAttribute.triggered.connect(self.onAddAttribute)
        self.actionRemoveAttribute.triggered.connect(self.onRemoveAttribute)


        #to hide
        self.actionPanMapToSelectedRows.setVisible(False)
        self.actionZoomMapToSelectedRows.setVisible(False)

        self.actionFormView.triggered.connect(lambda : self.mDualView.setView(QgsDualView.AttributeEditor))
        self.actionTableView.triggered.connect(lambda : self.mDualView.setView(QgsDualView.AttributeTable))
        self.btnFormView.setDefaultAction(self.actionFormView)
        self.btnTableView.setDefaultAction(self.actionTableView)

        self.onEditingToggled()


    def importSpeclib(self, path=None):
        slib = None
        if path is None:
            slib = SpectralLibrary.readFromSourceDialog(self)
        else:
            slib = SpectralLibrary.readFrom(path)

        if isinstance(slib, SpectralLibrary):
            self.speclib().addSpeclib(slib)


    def speclib(self):
        return self.mSpeclib

    def onSaveEdits(self, *args):

        if self.mSpeclib.isModified():

            b = self.mSpeclib.isEditable()
            self.mSpeclib.commitChanges()
            if b:
                self.mSpeclib.startEditing()

    def onToggleEditing(self, b:bool):

        if b == False:

            if self.mSpeclib.isModified():
                result = QMessageBox.question(self, 'Leaving edit mode', 'Save changes?', buttons=QMessageBox.No | QMessageBox.Yes, defaultButton=QMessageBox.Yes)
                if result == QMessageBox.Yes:
                    self.mSpeclib.commitChanges()
                    s = ""
                else:
                    self.mSpeclib.rollBack()
                    s = ""

            else:
                self.mSpeclib.commitChanges()
                s = ""
        else:
            self.mSpeclib.startEditing()




    def onEditingToggled(self, *args):
        speclib = self.speclib()

        hasSelectedFeatures = speclib.selectedFeatureCount() > 0
        isEditable = speclib.isEditable()
        self.actionToggleEditing.blockSignals(True)
        self.actionToggleEditing.setChecked(isEditable)
        self.actionSaveEdits.setEnabled(isEditable)
        self.actionReload.setEnabled(not isEditable)
        self.actionToggleEditing.blockSignals(False)


        self.actionAddAttribute.setEnabled(isEditable)
        self.actionDeleteSelected.setEnabled(isEditable and hasSelectedFeatures)
        self.actionPasteFeatures.setEnabled(isEditable)
        self.actionToggleEditing.setEnabled(not speclib.readOnly())

        self.actionRemoveAttribute.setEnabled(isEditable and len(speclib.optionalFieldNames()) > 0)

    def onAddAttribute(self):
        """
        Slot to add an optional QgsField / attribute
        """

        if self.mSpeclib.isEditable():
            d = AddAttributeDialog(self.mSpeclib)
            d.exec_()
            if d.result() == QDialog.Accepted:
                field = d.field()
                self.mSpeclib.addAttribute(field)
        else:
            log('call SpectralLibrary().startEditing before adding attributes')

    def onRemoveAttribute(self):
        """
        Slot to remove none-mandatory fields / attributes
        """

        if self.mSpeclib.isEditable():
            fieldNames = self.mSpeclib.optionalFieldNames()
            if len(fieldNames) > 0:
                fieldName, accepted = QInputDialog.getItem(self, 'Remove Field', 'Select', fieldNames, editable=False)
                if accepted:
                    i = self.mSpeclib.fields().indexFromName(fieldName)
                    if i >= 0:
                        b = self.mSpeclib.isEditable()
                        self.mSpeclib.startEditing()
                        self.mSpeclib.deleteAttribute(i)
                        self.mSpeclib.commitChanges()
        else:
            log('call SpectralLibrary().startEditing before removing attributes')

    def setMapInteraction(self, b : bool):

        if b == False:
            self.setCurrentSpectra([])
        self.mMapInteraction = b
        self.actionSelectProfilesFromMap.setVisible(b)
        self.actionSaveCurrentProfiles.setVisible(b)
        self.actionAddCurrentProfilesAutomatically.setVisible(b)
        self.actionPanMapToSelectedRows.setVisible(b)
        self.actionZoomMapToSelectedRows.setVisible(b)


    def mapInteraction(self):
        return self.mMapInteraction


    def onAttributesChanged(self):
        self.btnRemoveAttribute.setEnabled(len(self.mSpeclib.metadataAttributes()) > 0)

    def addAttribute(self, name):
        name = str(name)
        if len(name) > 0 and name not in self.mSpeclib.metadataAttributes():
            self.mModel.addAttribute(name)

    def setPlotXUnit(self, unit):
        unit = str(unit)

        pi = self.plotItem()
        if unit == 'Index':
            for pdi in pi.dataItems:

                assert isinstance(pdi, SpectralProfilePlotDataItem)
                p = pdi.mProfile
                assert isinstance(p, SpectralProfile)
                pdi.setData(y=pdi.yData, x= p.xValues())
                pdi.setVisible(True)
        else:
            #hide items that can not be presented in unit "unit"
            for pdi in pi.dataItems[:]:
                p = pdi.mProfile
                assert isinstance(p, SpectralProfile)
                if p.xUnit() != unit:
                    pdi.setVisible(False)
                else:
                    pdi.setData(y=p.yValues(), x=p.xValues())
                    pdi.setVisible(True)
        pi.replot()

    def plotItem(self):
        pi = self.plotWidget.getPlotItem()

        assert isinstance(pi, PlotItem)
        return pi

    def onExportSpectra(self, *args):
        self.mSpeclib.exportProfiles()



    def addSpeclib(self, speclib):
        if isinstance(speclib, SpectralLibrary):
            self.speclib().addSpeclib(speclib)

    def setAddCurrentSpectraToSpeclibMode(self, b:bool):
        self.actionAddCurrentProfilesAutomatically.setChecked(b)

    def addCurrentSpectraToSpeclib(self, *args):
        self.speclib().addProfiles(self.mCurrentSpectra)
        self.setCurrentSpectra([])

    sigCurrentSpectraChanged = pyqtSignal(list)
    def setCurrentSpectra(self, listOfSpectra:list):
        if listOfSpectra is None:
            listOfSpectra = []


        for i in range(len(listOfSpectra)):
            if type(listOfSpectra[i]) == QgsFeature:
                listOfSpectra[i] = SpectralProfile.fromSpecLibFeature(listOfSpectra[i])


        for p in listOfSpectra:
            assert isinstance(p, SpectralProfile)

        plotItem = self.plotItem()

        #remove old items
        for key in list(self.mOverPlotDataItems.keys()):
            if isinstance(key, SpectralProfile):
                pdi = self.mOverPlotDataItems[key]
                self.mOverPlotDataItems.pop(key)
                self.plotItem().removeItem(pdi)

        self.mCurrentSpectra.clear()
        self.mCurrentSpectra.extend(listOfSpectra)
        if self.actionAddCurrentProfilesAutomatically.isChecked() and len(self.mCurrentSpectra) > 0:
            self.addCurrentSpectraToSpeclib()
            #this will change the speclib and add each new profile automatically to the plot
        else:
            for p in self.mCurrentSpectra:
                assert isinstance(p, SpectralProfile)
                self.mPlotXUnitModel.addOption(Option(p.xUnit()))
                pdi = SpectralProfilePlotDataItem(p)
                pdi.setStyle(CURRENT_SPECTRUM_STYLE)

                plotItem.addItem(pdi)
                pdi.setZValue(len(plotItem.dataItems))
                self.mOverPlotDataItems[p] = pdi
        self.sigCurrentSpectraChanged.emit(self.mCurrentSpectra)



    def onProfileClicked(self, pdi):
        m = self.mModel

        idx = m.profile2idx(pdi.mProfile)
        if idx is None:
            return

        currentSelection = self.mSelectionModel.selection()

        profileSelection = QItemSelection(m.createIndex(idx.row(), 0), \
                                          m.createIndex(idx.row(), m.columnCount()-1))

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            profileSelection.merge(currentSelection, QItemSelectionModel.Toggle)

        self.mSelectionModel.select(profileSelection, QItemSelectionModel.ClearAndSelect)



    def currentSpectra(self):
        return self.mCurrentSpectra[:]




class SpectralLibraryFeatureSelectionManager(QgsIFeatureSelectionManager):


    def __init__(self, layer, parent=None):
        s =""
        super(SpectralLibraryFeatureSelectionManager, self).__init__(parent)
        assert isinstance(layer, QgsVectorLayer)
        self.mLayer = layer
        self.mLayer.selectionChanged.connect(self.selectionChanged)

    def layer(self):
        return self.mLayer

    def deselect(self, ids):

        if len(ids) > 0:
            selected = [id for id in self.selectedFeatureIds() if id not in ids]
            self.mLayer.deselect(ids)

            self.selectionChanged.emit(selected, ids, True)

    def select(self, ids:list):
        self.mLayer.select(ids)

    def selectAll(self):

        self.mLayer.selectAll()


    def selectFeatures(self, selection, command):

        super(SpectralLibraryFeatureSelectionManager, self).selectF
        s = ""
    def selectedFeatureCount(self)->int:
        return self.mLayer.selectedFeatureCount()

    def selectedFeatureIds(self)->list:
        return self.mLayer.selectedFeatureIds()

    def setSelectedFeatures(self, ids):
        self.mLayer.selectByIds(ids)



class SpectralProfileEditorWidgetWrapper(QgsEditorWidgetWrapper):

    def __init__(self, vl:QgsVectorLayer, fieldIdx:int, editor:QWidget, parent:QWidget):
        super(SpectralProfileEditorWidgetWrapper, self).__init__(vl, fieldIdx, editor, parent)
        self.mEditorWidget = None
        self.mLabel = None


    def createWidget(self, parent: QWidget):
        #log('createWidget')
        w = None
        if not self.isInTable(parent):
            w = SpectralProfileEditorWidget(parent=parent)
        else:
            #w = PlotStyleButton(parent)
            w = QLabel(parent)
        return w

    def initWidget(self, editor:QWidget):
        #log(' initWidget')
        if isinstance(editor, SpectralProfileEditorWidget):
            self.mEditorWidget = editor
            self.mEditorWidget.sigProfileValuesChanged.connect(self.onValueChanged)

        if isinstance(editor, QLabel):
            self.mLabel = editor
            self.mLabel.setEnabled(False)
            self.mLabel.setToolTip('Use Form View to edit values')


    def onValueChanged(self, *args):
        self.valueChanged.emit(self.value())
        s = ""

    def valid(self, *args, **kwargs)->bool:
        return isinstance(self.mEditorWidget, SpectralProfileEditorWidget) or isinstance(self.mLabel, QLineEdit)

    def value(self, *args, **kwargs):
        value = None
        if isinstance(self.mEditorWidget, SpectralProfileEditorWidget):
            v = self.mEditorWidget.profileValues()
            value = encodeProfileValueDict(v)

        return value


    def setEnabled(self, enabled:bool):

        if self.mEditorWidget:
            self.mEditorWidget.setEnabled(enabled)


    def setValue(self, value):
        if isinstance(self.mEditorWidget, SpectralProfileEditorWidget):
            self.mEditorWidget.setProfileValues(decodeProfileValueDict(value))
        if isinstance(self.mLabel, QLineEdit):
            self.mLabel.setText(value2str(value))




class SpectralProfileEditorConfigWidget(QgsEditorConfigWidget):

    def __init__(self, vl:QgsVectorLayer, fieldIdx:int, parent:QWidget):

        super(SpectralProfileEditorConfigWidget, self).__init__(vl, fieldIdx, parent)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel('Shows a widget to specify values of a SpectralProfile'))
        self.mConfig = {}

    def config(self, *args, **kwargs)->dict:
        log(' config()')
        config = {}

        return config

    def setConfig(self, *args, **kwargs):
        log(' setConfig()')
        self.mConfig = {}



class SpectralProfileEditorWidgetFactory(QgsEditorWidgetFactory):

    def __init__(self, name:str):

        super(SpectralProfileEditorWidgetFactory, self).__init__(name)


    def configWidget(self, vl:QgsVectorLayer, fieldIdx:int, parent=QWidget)->QgsEditorConfigWidget:

        w = SpectralProfileEditorConfigWidget(vl, fieldIdx, parent)

        return w

    def create(self, vl:QgsVectorLayer, fieldIdx:int, editor:QWidget, parent:QWidget)->SpectralProfileEditorWidgetWrapper:
        w = SpectralProfileEditorWidgetWrapper(vl, fieldIdx, editor, parent)
        return w
        pass

    def writeConfig(self, config, configElement, doc, layer, fieldIdx):

        s  = ""

    def readConfig(self, configElement, layer, fieldIdx):

        d = {}
        return d

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
        if field.type() == QVariant.String and field.name() == VALUE_FIELD:
            return 20
        elif field.type() == QVariant.String:
            return 5
        else:
            return 0 #no support

