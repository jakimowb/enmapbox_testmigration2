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
import os
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from osgeo import gdal
from enmapbox.gui.utils import loadUi, gdalDataset, SpatialPoint


class SpectralProfile(QObject):

    @staticmethod
    def deserialize(input):

        return None

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

        self.mValues = []
        self.mValueUnit = None
        self.mValuePositions = []
        self.mValuePositionUnit = None
        self.mMetadata = dict()
        self.mSource = None
        self.mPxCoordinate = None
        self.mGeoCoordinate = None

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

    def __eq__(self, other):
        return isinstance(other, SpectralProfile) \
            and self.mValues == other.mValue \
            and self.mValuePositions == other.mValuePositions \
            and self.mValueUnit == other.mValueUnit \
            and self.mValuePositionUnit == other.mValuePositionUnit


    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.mValues)


    def serialize(self):

        s = ""


class ProfileSet(QObject):
    def __init__(self, parent=None):
        super(ProfileSet, self).__init__(parent)

        self.mProfiles = []

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
        elif isinstance(profiles, ProfileSet):
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