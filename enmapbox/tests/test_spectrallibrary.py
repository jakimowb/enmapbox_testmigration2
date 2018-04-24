# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from enmapbox.gui.utils import *
from enmapbox.gui.spectrallibraries import *
from enmapboxtestdata import speclib, enmap
QGIS_APP = initQgisApplication()



class TestSpecLibs(unittest.TestCase):

    def setUp(self):

        self.SP = None
        self.SPECLIB = None

    def tearDown(self):
        pass

    def test_speclibSerialization(self):
        sl = SpectralLibrary.readFrom(speclib)

        self.assertIsInstance(sl, SpectralLibrary)
        ba = sl.asPickleDump()
        self.assertIsInstance(ba, bytes)
        sl2 = SpectralLibrary.readFromPickleDump(ba)
        self.assertIsInstance(sl2, SpectralLibrary)
        self.assertEqual(sl, sl2)




    def test_spectralProfile(self):

        spec1 = SpectralProfile()
        spec1.setValues([0,4,3,2,1],['-'], [450,500,750, 1000, 1500], 'nm')
        #self.assertTrue(spec1.isValid())

        values = [('key','value'),('key', 100),('Üä','ÜmlÄute')]
        for md in values:
            k, v = md
            spec1.setMetadata(k,v)
            v2 = spec1.metadata(k)
            self.assertEqual(v,v2)

        self.SP = spec1

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
                v = profile.metadata(u)
                self.assertEqual(v, u, msg='Failed to load key "{}"'.format(u))


    def test_speclibTableViewModel(self):

        from enmapboxtestdata import speclib
        sl = SpectralLibrary.readFrom(speclib)
        self.assertIsInstance(sl, SpectralLibrary)

        m = SpectralLibraryTableViewModel(speclib=sl)
        m.insertProfiles(sl[:])
        m.insertProfiles(sl)


        l = len(sl)
        self.assertEqual(l, m.rowCount())
        p0 = sl[0]
        p1 = sl[-1]

        self.assertIsInstance(p0, SpectralProfile)
        self.assertIsInstance(p1, SpectralProfile)

        idx0 = m.profile2idx(p0)
        self.assertIsInstance(idx0, QModelIndex)
        self.assertEqual(m.idx2profile(idx0), p0)
        self.assertTrue(idx0.row() == 0)

        mw = m.idx2profileWrapper(idx0)
        self.assertIsInstance(mw, SpectralLibraryTableViewModel.ProfileWrapper)
        self.assertEqual(mw.profile, p0)
        self.assertEqual(m.idx2profileWrapper(idx0), mw)



        idx1 = m.profile2idx(p1)
        self.assertIsInstance(idx1, QModelIndex)
        self.assertTrue(idx1.row() == m.rowCount()-1)
        self.assertEqual(m.idx2profile(idx1), p1)

        mw = m.idx2profileWrapper(idx1)
        self.assertIsInstance(mw, SpectralLibraryTableViewModel.ProfileWrapper)
        self.assertEqual(mw.profile, p1)
        self.assertEqual(m.idx2profileWrapper(idx1), mw)


        profiles = m.indices2profiles([idx0, idx1])
        self.assertTrue(len(profiles) == 2)
        self.assertTrue(p0 in profiles)
        self.assertTrue(p1 in profiles)
        

        sl.removeProfiles(p1)

        self.assertEqual(m.rowCount(), l-1)
        self.assertEqual(len(sl), l-1)
        self.assertTrue(p1 not in sl)
        self.assertEqual(m.profile2idx(p1), None)


        tv =  SpectralLibraryTableView()
        m = SpectralLibraryTableViewModel()
        tv.setModel(m)
        import enmapbox.gui.mimedata as mimedata
        md = QMimeData()
        sl = SpectralLibrary.readFrom(speclib)
        md.setData(mimedata.MDF_SPECTRALLIBRARY, sl.asPickleDump())
        e = QDropEvent(QPointF(0, 0), Qt.MoveAction, md, Qt.LeftButton, Qt.NoModifier)
        tv.dropEvent(e)

        self.assertEqual(sl, m.mSpecLib)
        self.assertTrue(id(sl) != id(m.mSpecLib))




def test_speclibWidget(self):
        p = SpectralLibraryWidget()
        p.addSpeclib(self.SPECLIB)
        p.show()






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
    spec1 = SpectralProfile()
    spec1.setValues([0, 4, 3, 2, 1], ['-'], [450, 500, 750, 1000, 1500], 'nm')

    spec2 = SpectralProfile()
    spec2.setValues([3, 2, 1, 0, 1], ['-'], [450, 500, 750, 1000, 1500], 'nm')

    sl = SpectralLibrary()
    sl.addProfiles([spec1, spec2])
    self.assertEqual(len(sl), 2)
    self.assertEqual(sl[0], spec1)

    tempDir = tempfile.gettempdir()
    pathESL = tempfile.mktemp(prefix='speclib.', suffix='.esl')
    pathCSV = tempfile.mktemp(prefix='speclib.', suffix='.csv')
    try:
        sl.exportProfiles(pathESL)
    except Exception as ex:
        self.fail('Unable to write ESL. {}'.format(ex))

    try:
        sl2 = SpectralLibrary.readFrom(pathESL)
    except Exception as ex:
        self.fail('Unable to read ESL. {}'.format(ex))

    try:
        sl.exportProfiles(pathCSV)
    except Exception as ex:
        self.fail('Unable to write CSV. {}'.format(ex))

    try:
        sl2 = SpectralLibrary.readFrom(pathCSV)
    except Exception as ex:
        self.fail('Unable to read CSV. {}'.format(ex))

    self.SPECLIB = sl


if __name__ == "__main__":

    unittest.main()
    QGIS_APP.exec_()


