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
import os, re, tempfile, pickle
import pyqtgraph as pg
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from osgeo import gdal
from enmapbox.gui.utils import loadUi, gdalDataset, SpatialPoint


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

class SpectralProfile(QObject):

    @staticmethod
    def deserialize(input):
        profiledata = pickle.loads(input)
        profile = SpectralProfile()
        for k in profile.__dict__.keys():
            if k in profiledata.keys():
                profile.__dict__[k] = profiledata[k]
            else:
                print('Can not make use of restored key {}'.format(k))
        for k in profiledata.keys():
            if k not in profile.__dict__.keys():
                profile.__dict__[k] = profiledata[k]
        return profile

    @staticmethod
    def fromRasterSource(source, position):
        from enmapbox.gui.utils import geo2px, px2geo
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


        profile = SpectralProfile()
        profile.setValues(values)
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

    def setMetadata(self, metaData):
        assert isinstance(metaData, dict)
        self.mMetadata.update(metaData)

    def yValues(self):
        return self.mValues[:]

    def yUnit(self):
        return self.mValueUnit

    def xValues(self):
        return self.mValuePositions[:]

    def xUnit(self):
        return self.mValueUnit


    def plot(self):
        """
        Plots this profile to an new PyQtGraph window
        :return:
        """
        import pyqtgraph as pg
        pg.plot(self.xValues(), self.yValues(), title=self.name())
        pg.QAPP.exec_()

    def __eq__(self, other):
        return isinstance(other, SpectralProfile) \
            and self.mValues == other.mValues \
            and self.mValuePositions == other.mValuePositions \
            and self.mValueUnit == other.mValueUnit \
            and self.mValuePositionUnit == other.mValuePositionUnit

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.mValues)

    def serialize(self):
        import pickle
        profiledata = self.__dict__
        return pickle.dumps(profiledata)





class SpectralLibraryReader(object):
    """
    Abstract Class of an SpectralLibraryReader.
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

class EnviSpectralLibraryReader(SpectralLibraryReader):

    @staticmethod
    def canRead(pathESL):
        """
        Checks if a file can be read as SpectraLibrary
        :param pathESL: path to ENVI Spectral Library (ESL)
        :return: True, if pathESL can be read as Spectral Library.
        """

        if not os.path.isfile(pathESL):
            return False
        hdr = EnviSpectralLibraryReader.readENVIHeader(pathESL, typeConversion=False)
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

        ds = EnviSpectralLibraryReader.esl2vrt(pathESL, tmpVrt)
        md = EnviSpectralLibraryReader.readENVIHeader(pathESL, typeConversion=True)
        data = ds.ReadAsArray()

        nSpectra, nbands = data.shape
        valueUnit = ''
        valuePositionUnit = md.get('wavelength units')
        valuePositions = md.get('wavelength')
        if valuePositions is None:
            valuePositions = [range(1, nbands+1)]
            valuePositionUnit = 'Band'

        spectraNames = md.get('spectra names', ['Spectrum {}'.format(i+1) for i in range(nSpectra)])
        profiles = []
        for i, name in enumerate(spectraNames):
            p = SpectralProfile()
            p.setValues(data[i,:],
                        valueUnit=valueUnit,
                        valuePositions=valuePositions,
                        valuePositionUnit=valuePositionUnit)
            p.setName(name)
            profiles.append(p)


        SLIB = SpectralLibrary()
        SLIB.addProfiles(profiles)
        return SLIB

    @staticmethod
    def esl2vrt(pathESL, pathVrt=None):
        """
        Creates a GDAL Virtual Raster (VRT) that allows to read an ENVI Spectral Library file
        :param pathESL: path ENVI Spectral Library file (binary part)
        :param pathVrt: (optional) path of created GDAL VRT.
        :return: GDAL VRT
        """

        hdr = EnviSpectralLibraryReader.readENVIHeader(pathESL, typeConversion=False)
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
            for k in to_int: md[k] = toType(int, md[k])
            for k in to_float: md[k] = toType(float, md[k])


        return md

class SpectralLibrary(QObject):

    @staticmethod
    def readFrom(uri):
        """
        Reads a Spectral Library from the source specified in "uri" (path, url, ...)
        :param uri: path or uri of the source from which to read SpectralProfiles and return them in a SpectralLibrary
        :return: SpectralLibrary
        """
        for cls in SpectralLibraryReader.__subclasses__():
            if cls.canRead(uri):
                return cls.readFrom(uri)
        return None

    def __init__(self, parent=None):
        super(SpectralLibrary, self).__init__(parent)

        self.mProfiles = []
        self.mName = ''


    sigNameChanged = pyqtSignal(str)

    def setName(self, name):
        if name != self.mName:
            self.mName = name
            self.sigNameChanged.emit(name)

    def name(self):
        return self.mName


    sigProfilesAdded = pyqtSignal(list)

    def addProfiles(self, profiles):
        to_add = self.extractProfileList(profiles)
        to_add = [p for p in to_add if p not in self.mProfiles]
        if len(to_add) > 0:
            self.mProfiles.extend(to_add)
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

    def __len__(self):
        return len(self.mProfiles)

    def __iter__(self):
        return iter(self.mProfiles)

    def __getitem__(self, slice):
        return self.mProfiles[slice]

    def __delitem__(self, slice):
        profiles = self[slice]
        self.removeProfiles(profiles)
