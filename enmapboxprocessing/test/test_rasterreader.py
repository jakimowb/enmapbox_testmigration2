import numpy as np
from qgis._core import QgsRasterRange, QgsRasterLayer

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.testcase import TestCase
from enmapboxtestdata import enmap


class TestRasterReader(TestCase):

    def setUp(self):
        self.reader = RasterReader(enmap)
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
        lead = self.reader.array(boundingBox=self.provider.extent(), width=4, height=2)
        gold = self.array
        self.assertArrayEqual(lead, gold)

    def test_readAllData_withBoundingBox_atNativeResolution(self):
        lead = self.reader.array(boundingBox=self.provider.extent())
        gold = self.array
        self.assertArrayEqual(lead, gold)

    def test_readAllData_withBoundingBox_atOversampledResolution(self):
        lead = self.reader.array(boundingBox=self.provider.extent(), width=8, height=4)
        lead = np.array(lead)[:, ::2, ::2]
        gold = self.array
        self.assertArrayEqual(lead, gold)

    def test_readEveryPixel_oneByOne(self):
        for xOffset in range(3):
            for yOffset in range(2):
                lead = self.reader.arrayFromPixelOffsetAndSize(xOffset, yOffset, width=1, height=1)
                gold = self.array[:, yOffset:yOffset + 1, xOffset:xOffset + 1]
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


class TestRasterMaskReader(TestCase):

    def setUp(self):
        self.array = np.array([[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]])
        self.provider = Driver(filename='c:/vsimem/test.bsq').createFromArray(self.array).provider
        self.reader = RasterReader(self.provider)

    def test_without_noData(self):
        gold = np.full_like(self.array, True, dtype=np.bool)
        lead = self.reader.maskArray(self.array)
        self.assertArrayEqual(lead, gold)

    def test_withSource_noData(self):
        self.provider.setNoDataValue(bandNo=1, noDataValue=0)
        gold = np.full_like(self.array, True, dtype=np.bool)
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
        gold = np.full_like(self.array, True, dtype=np.bool)
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
        gold = np.full_like(self.array, True, dtype=np.bool)
        gold[0, 0, 0:5] = False
        lead = self.reader.maskArray(self.array)
        self.assertArrayEqual(lead, gold)
