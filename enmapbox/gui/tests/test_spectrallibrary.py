# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.sandbox import initQgisEnvironment
from enmapbox.gui.utils import *
QGIS_APP = initQgisEnvironment()

from enmapbox.gui.spectrallibraries import SpectralProfile, SpectralLibrary, EnviSpectralLibraryIO
from enmapbox.testdata.UrbanGradient import Speclib, EnMAP
class testclassData(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):
        pass

    def test_spectralProfile(self):

        p = SpectralProfile()
        self.assertFalse(p.isValid())

        p  = SpectralProfile.fromRasterSource(EnMAP, QPoint(20,40))
        self.assertIsInstance(p, SpectralProfile)
        self.assertTrue(p.pxCoordinate() == QPoint(20,40))
        self.assertIsInstance(p.geoCoordinate(), SpatialPoint)

        s = p.serialize()
        self.assertIsInstance(s, str)
        p1 = SpectralProfile.deserialize(s)
        self.assertIsInstance(p1, SpectralProfile)

        p2 = SpectralProfile.deserialize(unicode(s))
        self.assertIsInstance(p2, SpectralProfile)
        self.assertEqual(p1,p2)

    def test_ENVISpectralLibraryReader(self):
        self.assertTrue(EnviSpectralLibraryIO.canRead(Speclib))
        tmpDir = tempfile.mkdtemp(prefix='testSpecLibs')
        pathTestVRT = os.path.join(tmpDir, 'esl.vrt')

        dsVRT = EnviSpectralLibraryIO.esl2vrt(Speclib, pathVrt=pathTestVRT)
        self.assertIsInstance(dsVRT, gdal.Dataset)
        self.assertEqual(dsVRT.RasterCount, 1)
        self.assertEqual(dsVRT.RasterXSize, 244)
        self.assertEqual(dsVRT.RasterYSize, 75)
        self.assertEqual(dsVRT.GetRasterBand(1).DataType, gdal.GDT_Float32)

        #todo: test ESLs with bip and pil interleave?
        hdr = EnviSpectralLibraryIO.readENVIHeader(Speclib, typeConversion=True)

        for key, value in {
                'samples':244,
                'lines':75,
                'bands':1,
                'header offset':0,
                'file type':'ENVI Spectral Library',
                'data type':4,
                'interleave':'bsq',
                'sensor type':'Unknown',
                'byte order':0,
                'wavelength units':'Micrometers',
                'reflectance scale factor':1.000000}.items():
            self.assertEqual(hdr.get(key), value)

    def test_spectralLibrary(self):

        sl = SpectralLibrary.readFrom(Speclib)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl), 75)

        p0 = sl[0]
        self.assertIsInstance(p0, SpectralProfile)
        self.assertTrue(p0 in sl)

        p1 = SpectralProfile()
        p1.setValues([1,3,4], valuePositions=[1,2,3])
        self.assertTrue(p1 not in sl)

        self.assertEqual(p1, pickle.loads(pickle.dumps(p1)))

if __name__ == "__main__":

    unittest.main()



