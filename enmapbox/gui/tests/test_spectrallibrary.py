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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.gui.sandbox import initQgisEnvironment
from enmapbox.gui.utils import *
QGIS_APP = initQgisEnvironment()
import unicodedata
from enmapbox.gui.spectrallibraries import SpectralProfile, SpectralLibrary, EnviSpectralLibraryIO
from enmapboxtestdata import speclib, enmap


def u2s(s):
    if isinstance(s, unicode):
        #s = s.encode(s, 'utf-8')
        #s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
        s = unicodedata.normalize('NFKD', s).encode('utf-8', 'ignore')
    return str(s)


class testclassData(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):
        pass

    def test_spectralProfile(self):

        p = SpectralProfile()
        self.assertFalse(p.isValid())

        p  = SpectralProfile.fromRasterSource(enmap, QPoint(20,40))
        self.assertIsInstance(p, SpectralProfile)
        self.assertTrue(p.pxCoordinate() == QPoint(20,40))
        self.assertIsInstance(p.geoCoordinate(), SpatialPoint)

        dump = pickle.dumps(p)
        p2 = pickle.loads(dump)
        self.assertTrue(p.isEqual(p2))

    def test_SpectralLibraryWriter(self):

        spec1 = SpectralProfile()
        spec1.setValues([0.2, 0.3, 0.5, 0.7])
        umlaute = ['ü','Ü',u'ö',u'Ö']
        for u in umlaute:
            spec1.setMetadata(u,u)

        sl = SpectralLibrary()
        sl.addProfile(spec1)

        tmpDir = tempfile.mkdtemp(prefix='testSpecLibs')
        paths = ['sl1-str.sli',
                u'sl2-unicode.sli',
                 'sl3-str-umlaut.sli',
                u'sl4-unicode-umlaut.sli',
]
        for p in paths:
            path = os.path.join(tmpDir, p)
            sl.exportProfiles(path)
            sl2 = SpectralLibrary.readFrom(path)
            self.assertIsInstance(sl2, SpectralLibrary)
            self.assertEqual(len(sl), len(sl2))
            profile = sl2[0]
            self.assertIsInstance(profile, SpectralProfile)
            for u in umlaute:
                u = u2s(u)

                v = profile.metadata(u)
                self.assertEqual(v, u, msg='Failed to load key "{}"'.format(u))

    def test_ENVISpectralLibraryReader(self):
        self.assertTrue(EnviSpectralLibraryIO.canRead(speclib))
        tmpDir = tempfile.mkdtemp(prefix='testSpecLibs')
        pathTestVRT = os.path.join(tmpDir, 'esl.vrt')
        sl = EnviSpectralLibraryIO.readFrom(speclib)
        s0 = sl[0]
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertIsInstance(s0, SpectralProfile)

        nSpectra = len(sl)
        nBands = len(s0)

        dsVRT = EnviSpectralLibraryIO.esl2vrt(speclib, pathVrt=pathTestVRT)
        self.assertIsInstance(dsVRT, gdal.Dataset)
        self.assertEqual(dsVRT.RasterCount, 1)
        self.assertEqual(dsVRT.RasterXSize, nBands)
        self.assertEqual(dsVRT.RasterYSize, nSpectra)
        #self.assertEqual(dsVRT.GetRasterBand(1).DataType, gdal.GDT_Float32)

        #todo: test ESLs with bip and pil interleave?
        hdr = EnviSpectralLibraryIO.readENVIHeader(speclib, typeConversion=True)

        for key, value in {
                'samples':nBands,
                'lines':nSpectra,
                'bands':1,
                'header offset':0,
                'file type':'ENVI Spectral Library',
               # 'data type':4,
                'interleave':'bsq',
                'sensor type':'Unknown',
                'byte order':0,
                'wavelength units':'Micrometers'}.items():
            self.assertEqual(hdr.get(key), value)

    def test_spectralLibrary(self):

        sl = SpectralLibrary.readFrom(speclib)
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



