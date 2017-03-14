from unittest import TestCase
from .Cube import Cube

from rios.pixelgrid import PixelGridDefn, pixelGridFromFile
from osgeo import gdal
import numpy
import enmapbox.testdata.HymapBerlinA as fnA
import enmapbox.testdata.HymapBerlinB as fnB


class TestCube(TestCase):

    def test_addDatasets(self):

        cube = Cube(pixelGridFromFile(fnA.HymapBerlinA_image))
        cube.addDataset(gdal.Open(fnA.HymapBerlinA_image))
        cube.addDataset(gdal.Open(fnA.HymapBerlinA_image))

    def test_getDataArrayBy__getitem__(self):
        cube = Cube(pixelGridFromFile(fnA.HymapBerlinA_image))
        cube.addDataset(gdal.Open(fnA.HymapBerlinA_image), key='myImage')
        self.assertIsInstance(cube['myImage'], numpy.ndarray)

    def test_setDataArrayBy__setitem__(self):
        cube = Cube(pixelGridFromFile(fnA.HymapBerlinA_image))
        cube.addDataset(gdal.Open(fnA.HymapBerlinA_image), key='myImage')
        cube['myImage2'] = cube['myImage']
        self.assertIsInstance(cube['myImage2'], numpy.ndarray)

    def test_getDatasetBy__call__(self):
        cube = Cube(pixelGridFromFile(fnA.HymapBerlinA_image))
        cube.addDataset(gdal.Open(fnA.HymapBerlinA_image), key='myImage')
        self.assertIsInstance(cube('myImage'), gdal.Dataset)


    def test_geoTransformMismatch(self):
        cube = Cube(pixelGridFromFile(fnA.HymapBerlinA_image))
        cube.addDataset(gdal.Open(fnA.HymapBerlinA_image))
        with self.assertRaises(AssertionError):
            cube.addDataset(gdal.Open(fnB.HymapBerlinB_image))
