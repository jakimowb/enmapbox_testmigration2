import numpy as np
from qgis._core import QgsRasterRange

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.testcase import TestCase
from enmapbox.exampledata import enmap


class TestRasterReader(TestCase):

    def setUp(self):
        self.reader = RasterReader(enmap)
        self.provider = self.reader.provider
        self.array = self.reader.gdalDataset.ReadAsArray()

    def test_readFirstPixel(self):
        lead = self.reader.arrayFromPixelOffsetAndSize(xOffset=0, yOffset=0, width=1, height=1)
        gold = self.array[:, 0:1, 0:1]
        self.assertArrayEqual(lead, gold)

    def test_readLastPixel(self):
        lead = self.reader.arrayFromPixelOffsetAndSize(xOffset=3, yOffset=1, width=1, height=1)
        gold = self.array[:, 1:2, 3:4]
        self.assertArrayEqual(lead, gold)

    def test_readAllData(self):
        lead = self.reader.array()
        gold = self.array
        self.assertArrayEqual(lead, gold)

    def test_readAllData_withBoundingBox_andSize(self):
        array = np.array(self.reader.array(boundingBox=self.provider.extent(), width=22, height=40))
        self.assertEqual((177, 40, 22), array.shape)

    def test_readAllData_withBoundingBox_atNativeResolution(self):
        lead = self.reader.array(boundingBox=self.provider.extent())
        gold = self.array
        self.assertArrayEqual(lead, gold)

    def test_readAllData_withBoundingBox_atOversampledResolution(self):
        array = np.array(self.reader.array(boundingBox=self.provider.extent(), width=22, height=40))
        self.assertEqual((177, 40, 22), array.shape)

    def test_readEveryPixel_oneByOne(self):
        for xOffset in range(3):
            for yOffset in range(2):
                lead = self.reader.arrayFromPixelOffsetAndSize(xOffset, yOffset, width=1, height=1)
                gold = self.array[:, yOffset:yOffset + 1, xOffset:xOffset + 1]
                self.assertArrayEqual(lead, gold)

    def test_readWithOverlap(self):
        lead = self.reader.array(10, 10, self.reader.width() - 20, self.reader.height() - 20, overlap=10)
        gold = self.array
        self.assertArrayEqual(lead, gold)


class TestRasterMetadataReader(TestCase):
    def setUp(self):
        self.reader = RasterReader(enmap)

    def test_metadata_thatExists(self):
        gold = 'Micrometers'
        self.assertEqual(gold, self.reader.metadataItem('wavelength_units', 'ENVI'))
        self.assertEqual(gold, self.reader.metadataItem('wavelength units', 'ENVI'))
        self.assertEqual(gold, self.reader.metadataItem('wavelength_units'.upper(), 'ENVI'.lower()))
        self.assertEqual(gold, self.reader.metadataItem('wavelength units'.upper(), 'ENVI'.lower()))
        self.assertIsNone(self.reader.metadataItem('abc', 'XYZ'))

    def test_bandwise_metadata(self):
        self.assertEqual(self.reader.Micrometers, self.reader.wavelengthUnits(1))
        self.assertEqual(460.0, self.reader.wavelength(1))
        self.assertEqual(460.0, self.reader.wavelength(1, self.reader.Nanometers))
        self.assertEqual(0.460, self.reader.wavelength(1, self.reader.Micrometers))
        self.assertEqual(5.8, self.reader.fwhm(1))
        self.assertEqual(5.8, self.reader.fwhm(1, self.reader.Nanometers))
        self.assertEqual(0.0058, self.reader.fwhm(1, self.reader.Micrometers))


class TestRasterMaskReader(TestCase):

    def setUp(self):
        self.array = np.array([[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]])
        filename = 'c:/vsimem/test.bsq'
        Driver(filename).createFromArray(self.array)
        self.reader = RasterReader(filename)
        self.provider = self.reader.provider

    def test_without_noData(self):
        gold = np.full_like(self.array, True, dtype=bool)
        lead = self.reader.maskArray(self.array)
        self.assertArrayEqual(lead, gold)

    def test_withSource_noData(self):
        self.provider.setNoDataValue(bandNo=1, noDataValue=0)
        gold = np.full_like(self.array, True, dtype=bool)
        gold[0, 0, 0] = False
        lead = self.reader.maskArray(self.array)
        self.assertArrayEqual(lead, gold)

    def test_withUser_noData(self):
        self.provider.setUserNoDataValue(bandNo=1, noData=[
            QgsRasterRange(0, 0),  # add 0
            QgsRasterRange(1, 2, QgsRasterRange.IncludeMin),  # add 1
            QgsRasterRange(1, 2, QgsRasterRange.IncludeMax),  # add 2
            QgsRasterRange(2, 4, QgsRasterRange.Exclusive),  # add 3
        ])
        gold = np.full_like(self.array, True, dtype=bool)
        gold[0, 0, 0:4] = False
        lead = self.reader.maskArray(self.array)
        self.assertArrayEqual(lead, gold)

    def test_withSourceAndUser_noData(self):
        self.provider.setNoDataValue(bandNo=1, noDataValue=4)  # add 4
        self.provider.setUserNoDataValue(bandNo=1, noData=[
            QgsRasterRange(0, 0),  # add 0
            QgsRasterRange(1, 2, QgsRasterRange.IncludeMin),  # add 1
            QgsRasterRange(1, 2, QgsRasterRange.IncludeMax),  # add 2
            QgsRasterRange(2, 4, QgsRasterRange.Exclusive),  # add 3
        ])
        gold = np.full_like(self.array, True, dtype=bool)
        gold[0, 0, 0:5] = False
        lead = self.reader.maskArray(self.array)
        self.assertArrayEqual(lead, gold)
