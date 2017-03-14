from unittest import TestCase
from .CubeReader import CubeReader

import enmapbox.testdata.HymapBerlinA as fn
from rios.pixelgrid import PixelGridDefn, pixelGridFromFile

class TestCubeReader(TestCase):


    def test_initCubeReaderWithTestImagePixelGrid(self):

        cr = CubeReader(pixelGridFromFile(fn.HymapBerlinA_image))

    def test_addImages(self):

        cr = CubeReader(pixelGridFromFile(fn.HymapBerlinA_image))
        cr.addImage(fn.HymapBerlinA_image)
        cr.addImage(fn.HymapBerlinA_train, 'train')

        self.assertListEqual([fn.HymapBerlinA_image, fn.HymapBerlinA_train], cr.filenames)
        self.assertListEqual([None, 'train'], cr.keys)

    def test_read(self):

        cr = CubeReader(pixelGridFromFile(fn.HymapBerlinA_image))
        cr.addImage(fn.HymapBerlinA_image)
        cr.addImage(fn.HymapBerlinA_train, 'train')
        cube = cr.read()