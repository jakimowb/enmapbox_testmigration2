from unittest import TestCase

from hubdsm.algorithm.importenmapl1b import importEnmapL1B


class TestImportEnmapL1B(TestCase):

    def test(self):
        importEnmapL1B(filenameMetadataXml=r'C:\Users\janzandr\Downloads\ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z__rows100-199\ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z-METADATA.XML')
