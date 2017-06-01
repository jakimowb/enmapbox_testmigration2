from unittest import TestCase


class TestNdvi(TestCase):
    def test_ndvi(self):
        from enmapbox.testdata.HymapBerlinB import HymapBerlinB_image
        from .algorithms import ndvi
        from tempfile import tempdir
        from os.path import join
        ndvi(infile=HymapBerlinB_image,
             outfile=join(tempdir(), 'ndvi.img'))
