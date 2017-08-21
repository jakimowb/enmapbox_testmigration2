# -*- coding: utf-8 -*-

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
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from __future__ import absolute_import
import os, re, tempfile, pickle, copy
from collections import OrderedDict
from qgis.core import *
from qgis.gui import *
import pyqtgraph as pg
from pyqtgraph import functions as fn
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from osgeo import gdal, gdal_array
from enmapbox.gui.utils import loadUI, gdalDataset, SpatialPoint, PanelWidgetBase
from enmapbox.gui.utils import geo2px, px2geo, SpatialExtent, SpatialPoint
from enmapbox.gui.utils import MimeDataHelper



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

def value2str(value, sep=' '):
    if isinstance(value, list):
        value = sep.join([str(v) for v in value])
    elif isinstance(value, np.array):
        value = value2str(value.astype(list), sep=sep)
    else:
        value = str(value)
    return value

class SpectralLibraryTableView(QTableView):

    def __init__(self, parent=None):
        super(SpectralLibraryTableView, self).__init__(parent)

    def contextMenuEvent(self, event):

        menu = QMenu(self)

        m = menu.addMenu('Copy...')
        a = m.addAction("Cell Values")
        a.triggered.connect(lambda :self.onCopy2Clipboard('CELLVALUES', separator=';'))
        a = m.addAction("Spectral Values")
        a.triggered.connect(lambda: self.onCopy2Clipboard('YVALUES', separator=';'))
        a = m.addAction("Spectral Values + Metadata")
        a.triggered.connect(lambda: self.onCopy2Clipboard('ALL', separator=';'))

        a = m.addAction("Spectral Values (Excel)")
        a.triggered.connect(lambda: self.onCopy2Clipboard('YVALUES', separator='\t'))
        a = m.addAction("Spectral Values + Metadata (Excel)")
        a.triggered.connect(lambda: self.onCopy2Clipboard('ALL', separator='\t'))

        a = menu.addAction('Save to file')
        a.triggered.connect(self.onSaveToFile)

        a = menu.addAction('Set color')
        a.triggered.connect(self.onSetColor)

        m.addSeparator()

        a = menu.addAction('Check')
        a.triggered.connect(lambda : self.setCheckState(Qt.Checked))
        a = menu.addAction('Uncheck')
        a.triggered.connect(lambda: self.setCheckState(Qt.Unchecked))

        menu.addSeparator()
        a = menu.addAction('Remove')
        a.triggered.connect(lambda : self.model().removeProfiles(self.selectedSpectra()))
        menu.popup(QCursor.pos())

    def onCopy2Clipboard(self, key, separator='\t'):
        assert key in ['CELLVALUES', 'ALL', 'YVALUES']
        txt = None
        if key == 'CELLVALUES':
            lines = []
            line = []
            row = None
            for idx in self.selectionModel().selectedIndexes():
                if row is None:
                    row = idx.row()
                elif row != idx.row():
                    lines.append(line)
                    line = []
                line.append(self.model().data(idx, role=Qt.DisplayRole))
            lines.append(line)
            lines = [value2str(l, sep=separator) for l in lines]
            QApplication.clipboard().setText('\n'.join(lines))
        else:
            sl = SpectralLibrary(profiles=self.selectedSpectra())
            txt = None
            if key == 'ALL':
                lines = CSVSpectralLibraryIO.asTextLines(sl, separator=separator)
                txt = '\n'.join(lines)
            elif key == 'YVALUES':
                lines = []
                for p in sl:
                    assert isinstance(p, SpectralProfile)
                    lines.append(separator.join([str(v) for v in p.yValues()]))
                txt = '\n'.join(lines)
            if txt:
                QApplication.clipboard().setText(txt)

    def onSaveToFile(self, *args):
        sl = SpectralLibrary(profiles=self.selectedSpectra())
        sl.exportProfiles()




    def selectedSpectra(self):
        rows = self.selectedRowsIndexes()
        m = self.model()
        return [m.idx2profile(m.createIndex(r, 0)) for r in rows]

    def onSetColor(self):
        c = QColorDialog.getColor()
        if isinstance(c, QColor):
            model = self.model()
            for idx in self.selectedRowsIndexes():
                model.setData(model.createIndex(idx, 1), c, Qt.BackgroundRole)

    def setCheckState(self, checkState):
        model = self.model()

        for idx in self.selectedRowsIndexes():
            model.setData(model.createIndex(idx, 0), checkState, Qt.CheckStateRole)

        selectionModel = self.selectionModel()
        assert isinstance(selectionModel, QItemSelectionModel)
        selectionModel.clearSelection()

    def selectedRowsIndexes(self):
        selectionModel = self.selectionModel()
        assert isinstance(selectionModel, QItemSelectionModel)
        return sorted(list(set([i.row() for i in self.selectionModel().selectedIndexes()])))


class SpectralProfileMapTool(QgsMapToolEmitPoint):

    sigProfileRequest = pyqtSignal(SpatialPoint, QgsMapCanvas)

    def __init__(self, canvas, showCrosshair=True):
        self.mShowCrosshair = showCrosshair
        self.mCanvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.mCanvas)
        self.marker = QgsVertexMarker(self.mCanvas)
        self.rubberband = QgsRubberBand(self.mCanvas, QGis.Polygon)

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
            geom.addPart([QgsPoint(ext.upperLeftPt().x(),cen.y()), QgsPoint(ext.lowerRightPt().x(), cen.y())],
                          QGis.Line)
            geom.addPart([QgsPoint(cen.x(), ext.upperLeftPt().y()), QgsPoint(cen.x(), ext.lowerRightPt().y())],
                          QGis.Line)
            self.rubberband.addGeometry(geom, None)
            self.rubberband.show()
            #remove crosshair after 0.1 sec
            QTimer.singleShot(100, self.hideRubberband)

        self.sigProfileRequest.emit(SpatialPoint(crs, geoPoint), self.mCanvas)

    def hideRubberband(self):
        self.rubberband.reset()



class SpectralProfilePlotDataItem(pg.PlotDataItem):

    def __init__(self, spectralProfle):
        assert isinstance(spectralProfle, SpectralProfile)
        super(SpectralProfilePlotDataItem, self).__init__(spectralProfle.xValues(), spectralProfle.yValues())
        self.mProfile = spectralProfle

    def setClickable(self, b, width=None):
        assert isinstance(b, bool)
        self.curve.setClickable(b, width=width)

    def setColor(self, color):
        if not isinstance(color, QColor):

            color = QColor(color)
        self.setPen(color)

    def pen(self):

        return fn.mkPen(self.opts['pen'])

    def color(self):
        return self.pen().color()

    def setLineWidth(self, width):
        pen = pg.mkPen(self.opts['pen'])
        assert isinstance(pen, QPen)
        pen.setWidth(width)
        self.setPen(pen)



class SpectralProfile(QObject):

    @staticmethod
    def fromRasterSource(source, position):

        from osgeo import gdal_array

        ds = gdalDataset(source)
        crs = QgsCoordinateReferenceSystem(ds.GetProjection())
        gt = ds.GetGeoTransform()

        if isinstance(position, QPoint):
            px = position
        elif isinstance(position, SpatialPoint):
            px = geo2px(position.toCrs(crs), gt)
        elif isinstance(position, QgsPoint):
            px = geo2px(position, ds.GetGeoTransform())
        else:
            raise Exception('Unsupported type of argument "position" {}'.format(str(position)))
        #check out-of-raster
        if px.x() < 0 or px.y() < 0: return None
        if px.x() > ds.RasterXSize - 1 or px.y() > ds.RasterYSize - 1: return None


        values = ds.ReadAsArray(px.x(), px.y(), 1, 1)

        values = values.flatten()
        for b in range(ds.RasterCount):
            band = ds.GetRasterBand(b+1)
            nodata = band.GetNoDataValue()
            if nodata and values[b] == nodata:
                return None

        wl = ds.GetMetadataItem('wavelength','ENVI')
        wlu = ds.GetMetadataItem('wavelength_units','ENVI')
        if wl is not None and len(wl) > 0:
            wl = re.sub(r'[ {}]','', wl).split(',')
            wl = [float(w) for w in wl]

        profile = SpectralProfile()
        profile.setValues(values, valuePositions=wl, valuePositionUnit=wlu)
        profile.setCoordinates(px=px, spatialPoint=SpatialPoint(crs,px2geo(px, gt)))
        profile.setSource(ds.GetFileList()[0])
        return profile

    def __init__(self, parent=None):
        super(SpectralProfile, self).__init__(parent)
        self.mName = ''
        self.mValues = []
        self.mValueUnit = None
        self.mValuePositions = []
        self.mValuePositionUnit = None
        self.mMetadata = dict()
        self.mSource = None
        self.mPxCoordinate = None
        self.mGeoCoordinate = None

    sigNameChanged = pyqtSignal(str)
    def setName(self, name):
        assert isinstance(name, str)
        if name != self.mName:
            self.mName = name
            self.sigNameChanged.emit(name)

    def name(self):
        return self.mName

    def setSource(self, uri):
        assert isinstance(uri, str)
        self.mSource = uri

    def source(self):
        return self.mSource

    def setCoordinates(self, px=None, spatialPoint=None):
        if isinstance(px, QPoint):
            self.mPxCoordinate = px
        if isinstance(spatialPoint, SpatialPoint):
            self.mGeoCoordinate = spatialPoint

    def pxCoordinate(self):
        return self.mPxCoordinate

    def geoCoordinate(self):
        return self.mGeoCoordinate

    def isValid(self):
        return len(self.mValues) > 0 and self.mValueUnit is not None

    def setValues(self, values, valueUnit=None,
                  valuePositions=None, valuePositionUnit=None):
        n = len(values)
        self.mValues = values[:]

        if valuePositions is None:
            valuePositions = list(range(n))
            valuePositionUnit = 'Index'
        self.setValuePositions(valuePositions, unit=valuePositionUnit)

    def setValuePositions(self, positions, unit=None):
        assert len(positions) == len(self.mValues)
        self.mValuePositions = positions[:]
        self.mValuePositionUnit = unit

    def updateMetadata(self, metaData):
        assert isinstance(metaData, dict)
        self.mMetadata.update(metaData)

    def setMetadata(self, key, value):
        assert isinstance(key, str)
        self.mMetadata[key] = value

    def metadata(self, key, default=None):
        return self.mMetadata.get(key, default=default)


    def yValues(self):
        return self.mValues[:]

    def yUnit(self):
        return self.mValueUnit

    def xValues(self):
        return self.mValuePositions[:]

    def xUnit(self):
        return self.mValuePositionUnit

    def valueIndexes(self):
        return np.arange(len(self.yValues()))

    def clone(self):
        return copy.copy(self)

    def plot(self):
        """
        Plots this profile to an new PyQtGraph window
        :return:
        """
        import pyqtgraph as pg

        pi = SpectralProfilePlotDataItem(self)
        pi.setClickable(True)
        pw = pg.plot( title=self.name())
        pw.getPlotItem().addItem(pi)

        pi.setColor('green')
        pg.QAPP.exec_()


    def __reduce_ex__(self, protocol):

        return self.__class__, (), self.__getstate__()

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __copy__(self):
        return copy.deepcopy(self)

    def isEqual(self, other):
        if not isinstance(other, SpectralProfile):
            return False
        if len(self.mValues) != len(other.mValues):
            return False
        return all(a == b for a, b in zip(self.mValues, other.mValues)) \
               and self.mValuePositions == other.mValuePositions \
               and self.mValueUnit == other.mValueUnit \
               and self.mValuePositionUnit == other.mValuePositionUnit \
               and self.mGeoCoordinate == other.mGeoCoordinate \
               and self.mPxCoordinate == other.mPxCoordinate

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

class SpectralLibraryWriter(object):

    @staticmethod
    def writeSpeclib(speclib):
        assert isinstance(speclib, SpectralLibrary)



class SpectralLibraryIO(object):
    """
    Abstract Class to define I/O operations for spectral libraries
    Overwrite the canRead and read From routines.
    """
    @staticmethod
    def canRead(path):
        """
        Returns true if it can reath the source definded by path
        :param path: source uri
        :return: True, if source is readibly
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
        """Writes the SpectralLibrary speclib to path, returns a list of written files"""
        assert isinstance(speclib, SpectralLibrary)
        return None


class CSVSpectralLibraryIO(SpectralLibraryIO):

    @staticmethod
    def write(speclib, path, separator='\t'):

        assert isinstance(speclib, SpectralLibrary)
        lines = ['Spectral Library {}'.format(speclib.name())]

        lines.extend(
            CSVSpectralLibraryIO.asTextLines(speclib, separator=separator)
        )

        file = open(path, 'w')
        for line in lines:
            file.write(line+'\n')
        file.flush()
        file.close()

    @staticmethod
    def asTextLines(speclib, separator='\t'):
        lines = []
        grouping = speclib.groupBySpectralProperties()
        for profiles in grouping.values():
            wlU = profiles[0].xUnit()
            wavelength = profiles[0].xValues()

            columns = ['n', 'name', 'geo', 'px', 'src']
            if wlU in [None, 'Index']:
                columns.extend(['b{}'.format(i + 1) for i in range(len(wavelength))])
            else:
                for i, wl in enumerate(wavelength):
                    columns.append('b{}_{}'.format(i + 1, wl))
            lines.append(value2str(columns, sep=separator))

            for i, p in enumerate(profiles):
                line = [i + 1, p.name(), p.geoCoordinate(), p.pxCoordinate(), p.source()]
                line.extend(p.yValues())
                lines.append(value2str(line, sep=separator))
            lines.append('')
        return lines


class EnviSpectralLibraryIO(SpectralLibraryIO):

    @staticmethod
    def canRead(pathESL):
        """
        Checks if a file can be read as SpectraLibrary
        :param pathESL: path to ENVI Spectral Library (ESL)
        :return: True, if pathESL can be read as Spectral Library.
        """

        if not os.path.isfile(pathESL):
            return False
        hdr = EnviSpectralLibraryIO.readENVIHeader(pathESL, typeConversion=False)
        if hdr is None or hdr['file type'] != 'ENVI Spectral Library':
            return False
        return True

    @staticmethod
    def readFrom(pathESL, tmpVrt=None):
        """
        Reads an ENVI Spectral Library (ESL).
        :param pathESL: path ENVI Spectral Library
        :param tmpVrt: (optional) path of GDAL VRt that is used to read the ESL
        :return: SpectalLibrary
        """

        ds = EnviSpectralLibraryIO.esl2vrt(pathESL, tmpVrt)
        md = EnviSpectralLibraryIO.readENVIHeader(pathESL, typeConversion=True)
        data = ds.ReadAsArray()

        nSpectra, nbands = data.shape
        valueUnit = ''
        valuePositionUnit = md.get('wavelength units')
        valuePositions = md.get('wavelength')
        if valuePositions is None:
            valuePositions = list(range(1, nbands+1))
            valuePositionUnit = 'Band'

        spectraNames = md.get('spectra names', ['Spectrum {}'.format(i+1) for i in range(nSpectra)])
        profiles = []
        for i, name in enumerate(spectraNames):
            p = SpectralProfile()
            p.setValues(data[i,:],
                        valueUnit=valueUnit,
                        valuePositions=valuePositions,
                        valuePositionUnit=valuePositionUnit)
            p.setName(name.strip())
            p.setSource(pathESL)
            profiles.append(p)


        SLIB = SpectralLibrary()
        SLIB.addProfiles(profiles)
        return SLIB

    @staticmethod
    def write(speclib, path, ext='sli'):
        dn = os.path.dirname(path)
        bn = os.path.basename(path)

        writtenFiles = []

        if bn.lower().endswith(ext.lower()):
            bn = os.path.splitext(bn)[0]

        if not os.path.isdir(dn):
            os.makedirs(dn)

        def value2hdrString(values):
            s = None
            maxwidth = 75
            if isinstance(values, list):
                lines = ['{']
                values = [str(v) for v in values]
                line = ' '
                l = len(values)
                for i, v in enumerate(values):
                    line += v
                    if i < l-1: line += ', '
                    if len(line) > maxwidth:
                        lines.append(line)
                        line = ' '
                line += '}'
                lines.append(line)
                s = '\n'.join(lines)

            else:
                s = str(values)
            return s


        for iGrp, grp in enumerate(speclib.groupBySpectralProperties().values()):

            wl = grp[0].xValues()
            wlu = grp[0].xUnit()


            # stack profiles
            pData = [np.asarray(p.yValues()) for p in grp]
            pData = np.vstack(pData)
            pNames = [p.name() for p in grp]

            if iGrp == 0:
                pathDst = os.path.join(dn, '{}.{}'.format(bn, ext))
            else:
                pathDst = os.path.join(dn, '{}.{}.{}'.format(bn, iGrp, ext))

            ds = gdal_array.SaveArray(pData, pathDst, format='ENVI')
            assert isinstance(ds, gdal.Dataset)
            ds.SetDescription(speclib.name())
            ds.SetMetadataItem('band names', 'Spectral Library', 'ENVI')
            ds.SetMetadataItem('spectra names',value2hdrString(pNames),'ENVI')
            ds.SetMetadataItem('wavelength', value2hdrString(wl), 'ENVI')
            ds.SetMetadataItem('wavelength units', wlu, 'ENVI')
            # todo: add more metadata

            pathHdr = ds.GetFileList()[1]
            ds = None

            # last step: change ENVI Hdr
            hdr = open(pathHdr).readlines()
            for iLine in range(len(hdr)):
                if re.search('file type =', hdr[iLine]):
                    hdr[iLine] = 'file type = ENVI Spectral Library\n'
                    break
            file = open(pathHdr, 'w')
            file.writelines(hdr)
            file.flush()
            file.close()
            writtenFiles.append(pathDst)

        return writtenFiles


    @staticmethod
    def esl2vrt(pathESL, pathVrt=None):
        """
        Creates a GDAL Virtual Raster (VRT) that allows to read an ENVI Spectral Library file
        :param pathESL: path ENVI Spectral Library file (binary part)
        :param pathVrt: (optional) path of created GDAL VRT.
        :return: GDAL VRT
        """

        hdr = EnviSpectralLibraryIO.readENVIHeader(pathESL, typeConversion=False)
        assert hdr is not None and hdr['file type'] == 'ENVI Spectral Library'

        eType = LUT_IDL2GDAL[int(hdr['data type'])]
        xSize = int(hdr['samples'])
        ySize = int(hdr['lines'])
        bands = int(hdr['bands'])
        byteOrder = 'MSB' if hdr['byte order'] == 0 else 'LSB'

        if pathVrt is None:
            pathVrt = tempfile.mktemp(prefix='tmpESLVrt', suffix='.esl.vrt')

        from enmapbox.gui.virtualrasters import describeRawFile
        ds = describeRawFile(pathESL, pathVrt, xSize, ySize, bands=bands, eType=eType, byteOrder=byteOrder)
        for key, value in hdr.items():
            if isinstance(value, list):
                value = ','.join(str(v) for v in value)
            ds.SetMetadataItem(key, str(value), 'ENVI')
        ds.FlushCache()
        return ds

    @staticmethod
    def readENVIHeader(pathESL, typeConversion=False):
        """
        Reads an ENVI Header File (*.hdr) and returns its values in a dictionary
        :param pathESL: path to ENVI Header
        :param typeConversion: Set on True to convert header keys with numeric
        values into numeric data types (int / float)
        :return: dict
        """
        if not os.path.isfile(pathESL):
            return None

        paths = [os.path.splitext(pathESL)[0] + '.hdr', pathESL + '.hdr']
        pathHdr = None
        for p in paths:
            if os.path.exists(p):
                pathHdr = p

        if pathHdr is None:
            return None

        hdr = open(pathHdr).readlines()
        i = 0
        while i < len(hdr):
            if '{' in hdr[i]:
                while not '}' in hdr[i]:
                    hdr[i] = hdr[i] + hdr.pop(i + 1)
            i += 1

        hdr = [''.join(re.split('\n[ ]*', line)).strip() for line in hdr]
        # keep lines with <tag>=<value> structure only
        hdr = [line for line in hdr if re.search('^[^=]+=', line)]

        # restructure into dictionary of type
        # md[key] = single value or
        # md[key] = [list-of-values]
        md = dict()
        for line in hdr:
            tmp = line.split('=')
            key, value = tmp[0].strip(), '='.join(tmp[1:]).strip()
            if value.startswith('{') and value.endswith('}'):
                value = value.strip('{}').split(',')
            md[key] = value

        # check required metadata tegs
        for k in ['byte order', 'data type', 'header offset', 'lines', 'samples', 'bands']:
            if not k in md.keys():
                return None

        #todo: transform known strings into int/floats?
        def toType(t, arg):
            if isinstance(arg, list):
                return [toType(t, a) for a  in arg]
            else:
                return t(arg)

        if typeConversion:
            to_int = ['bands','lines','samples','data type','header offset','byte order']
            to_float = ['fwhm','wavelength', 'reflectance scale factor']
            for k in to_int:
                if k in md.keys():
                    md[k] = toType(int, md[k])
            for k in to_float:
                if k in md.keys():
                    md[k] = toType(float, md[k])


        return md

class SpectralLibraryPanel(QDockWidget, loadUI('speclibviewpanel.ui')):

    def __init__(self, parent=None):
        """Constructor."""
        super(SpectralLibraryPanel, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


class SpectralLibrary(QObject):
    @staticmethod
    def readFromSourceDialog(parent=None):
        """
        Opens a FileOpen dialog to select
        :param parent:
        :return:
        """
        from enmapbox.gui.utils import settings, DIR_TESTDATA
        SETTINGS = settings()
        lastDataSourceDir = SETTINGS.value('_lastSpecLibSourceDir', None)

        if lastDataSourceDir is None:
            lastDataSourceDir = DIR_TESTDATA

        if not os.path.exists(lastDataSourceDir):
            lastDataSourceDir = None

        uris = QFileDialog.getOpenFileNames(parent, "Open spectral library", lastDataSourceDir)
        if len(uris) > 0:
            SETTINGS.setValue('_lastSpecLibSourceDir', os.path.dirname(uris[-1]))

        uris = [u for u in uris if os.path.isfile(u)]
        speclib = SpectralLibrary()
        for u in uris:
            sl = SpectralLibrary.readFrom(str(u))
            speclib.addSpeclib(sl)
        return speclib

    @staticmethod
    def readFrom(uri):
        """
        Reads a Spectral Library from the source specified in "uri" (path, url, ...)
        :param uri: path or uri of the source from which to read SpectralProfiles and return them in a SpectralLibrary
        :return: SpectralLibrary
        """
        for cls in SpectralLibraryIO.__subclasses__():
            if cls.canRead(uri):
                return cls.readFrom(uri)
        return None



    def __init__(self, parent=None, profiles=None):
        super(SpectralLibrary, self).__init__(parent)

        self.mProfiles = []
        self.mName = ''
        if profiles is not None:
            self.mProfiles.extend(profiles[:])


    sigNameChanged = pyqtSignal(str)

    def setName(self, name):
        if name != self.mName:
            self.mName = name
            self.sigNameChanged.emit(name)

    def name(self):
        return self.mName

    def addSpeclib(self, speclib):
        assert isinstance(speclib, SpectralLibrary)
        self.addProfiles([p for p in speclib])

    sigProfilesAdded = pyqtSignal(list)

    def addProfile(self, profile):
        self.addProfiles([profile])

    def addProfiles(self, profiles, index=None):
        to_add = self.extractProfileList(profiles)
        to_add = [p for p in to_add if p not in self.mProfiles]
        if len(to_add) > 0:
            if index is None:
                index = len(self.mProfiles)
            self.mProfiles[index:index] = to_add
            self.sigProfilesAdded.emit(to_add)
        return to_add

    def extractProfileList(self, profiles):
        if isinstance(profiles, SpectralProfile):
            profiles = [profiles]
        if isinstance(profiles, list):
            profiles = [p for p in profiles if isinstance(p, SpectralProfile)]
        elif isinstance(profiles, SpectralLibrary):
            profiles = profiles.mProfiles[:]
        else:
            raise Exception('Unknown type {}'.format(type(profiles)))
        return profiles


    def groupBySpectralProperties(self):
        """
        Groups the SpectralProfiles by:
            wavelength (xValues), wavelengthUnit (xUnit) and yUnit
        :return: {(xValues, wlU, yUnit):[list-of-profiles]}
        """

        d = dict()
        for p in self.mProfiles:
            #assert isinstance(p, SpectralProfile)
            id = (str(p.xValues()), str(p.xUnit()), str(p.yUnit()))
            if id not in d.keys():
                d[id] = list()
            d[id].append(p)
        return d

    def asTextLines(self, separator='\t'):
        return CSVSpectralLibraryIO.asTextLines(self, separator=separator)

    def exportProfiles(self, path=None):

        if path is None:
            filters = 'ENVI Spectral Library (*.esl *.sli);;CSV Table (*.csv)'
            path = QFileDialog.getSaveFileName(parent=None, caption="Save Spectral Library", filter=filters)


        if len(path) > 0:
            ext = os.path.splitext(path)[-1].lower()
            if ext in ['.sli','.esl']:
                EnviSpectralLibraryIO.write(self, path)

            if ext in ['.csv']:
                CSVSpectralLibraryIO.write(self, path, separator='\t')

            s = ""

    sigProfilesRemoved = pyqtSignal(list)
    def removeProfiles(self, profiles):
        """
        Removes profiles from this ProfileSet
        :param profiles: Profile or [list-of-profiles] to be removed
        :return: [list-of-remove profiles] (only profiles that existed in this set before)
        """
        to_remove = self.extractProfileList(profiles)
        to_remove = [p for p in to_remove if p in self.mProfiles]
        if len(to_remove) > 0:
            for p in to_remove:
                self.mProfiles.remove(p)
            self.sigProfilesRemoved.emit(to_remove)
        return to_remove

    def yRange(self):
        minY = min([min(p.yValues()) for p in self.mProfiles])
        maxY = max([max(p.yValues()) for p in self.mProfiles])
        return  minY, maxY

    def plot(self):
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

    def index(self, obj):
        return self.mProfiles.index(obj)

    def __reduce_ex__(self, protocol):
        return self.__class__, (), self.__getstate__()

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)


    def __len__(self):
        return len(self.mProfiles)

    def __iter__(self):
        return iter(self.mProfiles)

    def __getitem__(self, slice):
        return self.mProfiles[slice]

    def __delitem__(self, slice):
        profiles = self[slice]
        self.removeProfiles(profiles)

    def __eq__(self, other):
        if not isinstance(other, SpectralLibrary):
            return False

        if len(self) != len(other):
            return False

        for p1, p2 in zip(self.__iter__(), other.__iter__()):
            if p1 != p2:
                return False
        return True


class SpectralLibraryTableViewModel(QAbstractTableModel):

    sigPlotStyleChanged = pyqtSignal(SpectralProfile)

    class ProfileWrapper(object):
        def __init__(self, profile):
            assert isinstance(profile, SpectralProfile)
            self.profile = profile
            self.style = QColor('white')
            self.checkState = Qt.Unchecked

    def __init__(self, spectralLibrary, parent=None):
        super(SpectralLibraryTableViewModel, self).__init__(parent)

        self.cIndex = '#'
        self.cStyle = 'Style'
        self.cName = 'Name'
        self.cPxX = 'px x'
        self.cPxY = 'px y'
        self.cCRS = 'CRS'
        self.cGeoX = 'x'
        self.cGeoY = 'y'
        self.cSrc = 'Source'

        self.columnNames = [self.cIndex, self.cStyle, self.cName, \
                            self.cPxX, self.cPxY, self.cGeoX, self.cGeoY, self.cCRS,
                            self.cSrc]

        assert isinstance(spectralLibrary, SpectralLibrary)
        self.mSpecLib = spectralLibrary
        self.mSpecLib.sigProfilesRemoved.connect(self.onProfilesRemoved)
        self.mSpecLib.sigProfilesAdded.connect(self.onProfilesAdded)


        self.mProfileWrappers = OrderedDict()
        self.onProfilesAdded([p for p in self.mSpecLib])

    def removeProfiles(self, profiles):
        self.mSpecLib.removeProfiles(profiles)

    def onProfilesAdded(self, profiles):
        for p in profiles:
            self.mProfileWrappers[p] = SpectralLibraryTableViewModel.ProfileWrapper(p)
        self.layoutChanged.emit()

    def onProfilesRemoved(self, profiles):
        self.layoutChanged.emit()
        for p in profiles:
            self.mProfileWrappers.pop(p)

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columnNames[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None

    def sort(self, col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        columnName = self.columnNames[col]
        rev = order == Qt.DescendingOrder
        sortedProfiles = None
        profiles = self.mProfileWrappers.keys()
        if columnName == self.cName:
            sortedProfiles = sorted(profiles, key= lambda p: p.name(), reverse=rev)
        elif columnName == self.cSrc:
            sortedProfiles = sorted(profiles, key=lambda p: p.source(), reverse=rev)
        elif columnName == self.cIndex:
            sortedProfiles = sorted(profiles, key=lambda p: self.mSpecLib.index(p), reverse=rev)

        if sortedProfiles is not None:
            tmp = OrderedDict([(p, self.mProfileWrappers[p]) for p in sortedProfiles])
            self.mProfileWrappers.clear()
            self.mProfileWrappers.update(tmp)
            self.layoutChanged.emit()

    def rowCount(self, parentIdx=None, *args, **kwargs):
        return len(self.mSpecLib)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.columnNames)

    def profile2idx(self, profile):
        assert isinstance(profile, SpectralProfile)
        #return self.createIndex(self.mSpecLib.index(profile), 0)
        #pw = self.mProfileWrappers[profile]
        return self.createIndex(self.mProfileWrappers.keys().index(profile), 0)



    def idx2profileWrapper(self, index):
        assert isinstance(index, QModelIndex)
        if not index.isValid():
            return None
        return self.mProfileWrappers.values()[index.row()]

        """
        p = self.idx2profile(index)
        assert isinstance(p, SpectralProfile)
        pw = self.mProfileWrappers[p]
        assert isinstance(pw, SpectralLibraryTableViewModel.ProfileWrapper)
        return pw
        """

    def indices2profiles(self, indices):
        profiles = []
        for idx in indices:
            p = self.mProfileWrappers.keys()[idx.row()]
            if p not in profiles:
                profiles.append(p)
        return profiles


    def idx2profile(self, index):
        pw = self.idx2profileWrapper(index)
        if isinstance(pw, SpectralLibraryTableViewModel.ProfileWrapper):
            return  pw.profile
        else:
            return None

    def data(self, index, role=Qt.DisplayRole):
        if role is None or not index.isValid():
            return None

        columnName = self.columnNames[index.column()]
        profileWrapper = self.idx2profileWrapper(index)
        profile = profileWrapper.profile
        px = profile.pxCoordinate()
        geo = profile.geoCoordinate()
        value = None
        if role == Qt.DisplayRole:
            if columnName == self.cIndex:
                value = self.mSpecLib.index(profile)+1
            elif columnName == self.cName:
                value = profile.name()
            elif columnName == self.cSrc:
                value = profile.source()

            if px is not None:
                if columnName == self.cPxX:
                    value = profile.pxCoordinate().x()
                elif columnName == self.cPxY:
                    value = profile.pxCoordinate().y()

            if geo is not None:
                if columnName == self.cGeoX:
                    value = '{:0.10f}'.format(profile.geoCoordinate().x())
                elif columnName == self.cGeoY:
                    value = '{:0.10f}'.format(profile.geoCoordinate().y())
                elif columnName == self.cCRS:
                    value = profile.geoCoordinate().crs().authid()


        if role == Qt.BackgroundRole:
            if columnName == self.cStyle:
                return self.mProfileWrappers[profile].style

        if role == Qt.EditRole:
            if columnName == self.cName:
                value = profile.name()

        if role == Qt.UserRole:
            value = profile
        if role == Qt.CheckStateRole:
            if columnName == self.cIndex:
                value = profileWrapper.checkState
        return value



    def setData(self, index, value, role=None):
        if role is None or not index.isValid():
            return False
        assert isinstance(index, QModelIndex)
        cName = self.columnNames[index.column()]
        profileWrapper = self.idx2profileWrapper(index)
        profile = profileWrapper.profile

        if role  == Qt.EditRole:
            if cName == self.cName:
                profile.setName(str(value))
                return True

        if role == Qt.CheckStateRole:
            if cName == self.cIndex:
                profileWrapper.checkState = value
                return True
        if role == Qt.BackgroundRole:
            if cName == self.cStyle:
                profileWrapper.style = value
                return True

        return False

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction

    def dropMimeData(self, data, action, row, column, parent):
        profile = self.idx2profile(parent)
        s = ""

    def mimeData(self, indexes):

        if len(indexes) == 0:
            return None

        profiles = self.indices2profiles(indexes)
        speclib = SpectralLibrary(profiles=profiles)
        mimeData = QMimeData()
        import pickle
        d = pickle.dumps(speclib)
        mimeData.setData(MimeDataHelper.MDF_SPECTRALLIBRARY, d)

        #as text
        mimeData.setText('\n'.join(speclib.asTextLines()))

        return mimeData

    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []

        types.append(MimeDataHelper.MDF_DATASOURCETREEMODELDATA)
        types.append(MimeDataHelper.MDF_LAYERTREEMODELDATA)
        types.append(MimeDataHelper.MDF_URILIST)
        return types

    def flags(self, index):
        if index.isValid():
            columnName = self.columnNames[index.column()]
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            if columnName in [self.cName]:  # allow check state
                flags = flags | Qt.ItemIsEditable | Qt.ItemIsUserCheckable
            if columnName == self.cIndex:
                flags = flags | Qt.ItemIsUserCheckable
            return flags
        return None

    def insertRows(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
        pass

    def removeRows(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
        pass


class UnitComboBoxItemModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(UnitComboBoxItemModel, self).__init__(parent)
        self.mUnits = []

    def addUnit(self, unit):
        if unit is not None and unit not in self.mUnits:
            self.mUnits.append(unit)
            self.reset()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.mUnits)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def getUnitFromIndex(self, index):
        if index.isValid():
            return self.mUnits[index.row()]
        return None

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


class SpectraLibraryViewPanel(QDockWidget, loadUI('speclibviewpanel.ui')):
    def __init__(self, parent=None):
        super(SpectraLibraryViewPanel, self).__init__(parent)
        self.setupUi(self)
        self.mModel = None

        self.mColorCurrentSpectra = QColor('green')
        self.mColorSelectedSpectra = QColor('yellow')

        self.m_plot_max = 50
        self.mPlotXUnitModel = UnitComboBoxItemModel(self)
        self.mPlotXUnitModel.addUnit('Index')

        self.cbXUnit.setModel(self.mPlotXUnitModel)
        self.cbXUnit.currentIndexChanged.connect(lambda: self.setPlotXUnit(self.cbXUnit.currentText()))
        self.cbXUnit.setCurrentIndex(0)
        self.mSelectionModel = None

        self.mCurrentSpectra = []
        self.tableViewSpeclib.verticalHeader().setMovable(True)
        self.tableViewSpeclib.verticalHeader().setDragEnabled(True)
        self.tableViewSpeclib.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)
        self.tableViewSpeclib.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)


        self.mSpeclib = SpectralLibrary()
        self.mSpeclib.sigProfilesAdded.connect(self.onProfilesAdded)
        self.mSpeclib.sigProfilesRemoved.connect(self.onProfilesRemoved)
        self.mPlotDataItems = dict()

        self.mModel = SpectralLibraryTableViewModel(self.mSpeclib)
        self.tableViewSpeclib.setModel(self.mModel)
        self.mSelectionModel = QItemSelectionModel(self.mModel)
        self.mSelectionModel.selectionChanged.connect(self.onSelectionChanged)
        #self.mSelectionModel.currentChanged.connect(self.onCurrentSelectionChanged)
        self.tableViewSpeclib.setSelectionModel(self.mSelectionModel)

        self.plotWidget.setAntialiasing(True)

        self.btnLoadFromFile.clicked.connect(lambda : self.addSpeclib(SpectralLibrary.readFromSourceDialog(self)))
        self.btnExportSpeclib.clicked.connect(self.onExportSpectra)
        self.btnAddCurrentToSpeclib.clicked.connect(self.addCurrentSpectraToSpeclib)




        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapbox = EnMAPBox.instance()
        if enmapbox:
            enmapbox.sigCurrentSpectraChanged.connect(self.setCurrentSpectra)
            self.btnLoadfromMap.setEnabled(True)
            self.btnLoadfromMap.clicked.connect(lambda : EnMAPBox.instance().activateMapTool('SPECTRUMREQUEST'))
        else:
            self.btnLoadfromMap.setEnabled(False)

    def setPlotXUnit(self, unit):
        unit = str(unit)

        pi = self.getPlotItem()
        if unit == 'Index':
            for pdi in pi.dataItems:

                assert isinstance(pdi, SpectralProfilePlotDataItem)
                p = pdi.mProfile
                pdi.setData(y=pdi.yData, x= p.valueIndexes())
                pdi.setVisible(True)
        else:
            #hide items that can not be presented in unit "unit"
            for pdi in pi.dataItems[:]:
                p = pdi.mProfile
                if pdi.mProfile.xUnit() != unit:
                    pdi.setVisible(False)
                else:
                    pdi.setData(y=pdi.yData, x=pdi.mProfile.xValues())
                    pdi.setVisible(True)
        pi.replot()
    def getPlotItem(self):
        pi = self.plotWidget.getPlotItem()
        assert isinstance(pi, pg.PlotItem)
        return pi

    def onExportSpectra(self, *args):
        self.mSpeclib.exportProfiles()


    def onProfilesAdded(self, profiles):
        # todo: remove some PDIs from plot if there are too many
        pi = self.getPlotItem()
        if True:
            to_remove = max(0, len(pi.listDataItems()) - self.m_plot_max)
            if to_remove > 0:
                for pdi in pi.listDataItems()[0:to_remove]:
                    pi.removeItem(pdi)

        for p in profiles:
            self.mPlotXUnitModel.addUnit(p.xUnit())
            pi.addItem(self.createPDI(p))

    def addSpectralPlotItem(self, pdi):
        assert isinstance(pdi, SpectralProfilePlotDataItem)
        pi = self.getPlotItem()

        pi.addItem(pdi)

    def onProfilesRemoved(self, profiles):
        pi = self.getPlotItem()
        for p in profiles:
            self.removePDI(p)

    def addSpeclib(self, speclib):
        if isinstance(speclib, SpectralLibrary):
            self.mSpeclib.addProfiles([copy.copy(p) for p in speclib])


    def addCurrentSpectraToSpeclib(self, *args):
        self.mSpeclib.addProfiles([p.clone() for p in self.mCurrentSpectra])

    sigCurrentSpectraChanged = pyqtSignal(list)
    def setCurrentSpectra(self, listOfSpectra):
        plotItem =  self.getPlotItem()
        #remove old items
        for p in self.mCurrentSpectra:
            if p not in self.mSpeclib:
                self.removePDI(p)

        self.mCurrentSpectra = listOfSpectra[:]
        if self.cbAddCurrentSpectraToSpeclib.isChecked():
            self.addCurrentSpectraToSpeclib()

        for p in self.mCurrentSpectra:
            self.mPlotXUnitModel.addUnit(p.xUnit())
            plotItem.addItem(self.createPDI(p, QColor('green')))

        self.sigCurrentSpectraChanged.emit(self.mCurrentSpectra)

    def createPDI(self, profile, color=None):
        if color is None:
            color = QColor('white')
        if not isinstance(color, QColor):
            color = QColor(color)
        assert isinstance(profile, SpectralProfile)
        if profile not in self.mPlotDataItems.keys():

            pdi = SpectralProfilePlotDataItem(profile)
            pdi.setClickable(True)
            pdi.setPen(fn.mkPen(color, width=1))

            pdi.sigClicked.connect(self.onProfileClicked)
            self.mPlotDataItems[profile] = pdi
            pdi = self.mPlotDataItems[profile]
        return pdi

    def removePDI(self, profile):
        """
        Removes the SpectraProfilePlotDataItem realted to SpectraProfile 'profile'
        :param profile:
        :return:
        """
        assert isinstance(profile, SpectralProfile)
        if profile in self.mPlotDataItems.keys():
            pdi = self.mPlotDataItems.pop(profile)
            self.getPlotItem().removeItem(pdi)
            return pdi
        else:
            return None

    def onProfileClicked(self, pdi):
        m = self.mModel
        idx = m.profile2idx(pdi.mProfile)


        currentSelection = self.mSelectionModel.selection()

        profileSelection = QItemSelection(m.createIndex(idx.row(), 0), \
                                   m.createIndex(idx.row(), m.columnCount()-1))

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            profileSelection.merge(currentSelection, QItemSelectionModel.Select)
        self.mSelectionModel.select(profileSelection, QItemSelectionModel.ClearAndSelect)



    def currentSpectra(self):
        return self.mCurrentSpectra[:]





    def onSelectionChanged(self, selected, deselected):
        if not isinstance(self.mModel, SpectralLibraryTableViewModel):
            return None

        assert isinstance(selected, QItemSelection)
        assert isinstance(deselected, QItemSelection)

        for selectionRange in deselected:
            for idx in selectionRange.indexes():
                p = self.mModel.idx2profile(idx)
                pdi = self.mPlotDataItems[p]
                assert isinstance(pdi, SpectralProfilePlotDataItem)
                pdi.setPen(fn.mkPen(self.mModel.mProfileWrappers[p].style))
                pdi.setShadowPen(None)


        to_front = []
        for selectionRange in selected:
            for idx in selectionRange.indexes():
                p = self.mModel.idx2profile(idx)
                pdi = self.mPlotDataItems[p]
                assert isinstance(pdi, SpectralProfilePlotDataItem)
                pdi.setPen(fn.mkPen(QColor('red'), width = 2))
                pdi.setShadowPen(fn.mkPen(QColor('black'), width=4))
                to_front.append(pdi)

        pi = self.getPlotItem()
        l = len(pi.dataItems)
        for pdi in to_front:
            pdi.setZValue(l)



if __name__ == "__main__":
    import enmapboxtestdata
    from enmapboxtestdata import speclib

    from enmapbox.gui.utils import SpatialPoint, SpatialExtent, initQgisApplication
    qapp = initQgisApplication()

    mySpec = SpectralProfile()
    mySpec.setValues([0.2, 0.3, 0.5, 0.7])

    #mySpec.plot()

    sl0 = SpectralLibrary(profiles=[mySpec])

    sl1 = SpectralLibrary.readFrom(speclib)
    #d = pickle.dumps(sl1)

    #sl1.addProfiles([mySpec])
    if False:
        tmpDir = r'/Users/benjamin.jakimow/Documents/Temp/enmapbox'
        pathDst = os.path.join(tmpDir, 'test2.csv')
        sl1.exportProfiles(pathDst)
        s = 2
    if False:
        tmpDir = r'/Users/benjamin.jakimow/Documents/Temp/enmapbox'
        pathDst = os.path.join(tmpDir, 'test.sli')

        EnviSpectralLibraryIO.write(sl1, pathDst)
        sl2 = SpectralLibrary.readFrom(pathDst)

    w  = SpectraLibraryViewPanel()
    w.show()
    w.addSpeclib(sl1)

    qapp.exec_()

