from unittest import TestCase


class TestNdviWithGDAL(TestCase):
    def test_ndviWithGDAL(self):
        from enmapbox.testdata.HymapBerlinB import HymapBerlinB_image
        from .ndviWithGDAL import ndviWithGDAL
        from tempfile import tempdir
        from os.path import join
        ndviWithGDAL(infile=HymapBerlinB_image,
                     outfile=join(tempdir(), 'ndviWithGDAL.img'))
