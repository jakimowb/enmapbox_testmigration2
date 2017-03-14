from unittest import TestCase
from .CubeWriter import CubeWriter
from .Cube import Cube
from osgeo import gdal
from tempfile import gettempdir
from os.path import join

from hubdc.util.pixelgrid import pixelGridFromFile
from enmapbox.testdata.HymapBerlinA import HymapBerlinA_image, HymapBerlinA_train

class TestCubeWriter(TestCase):

    def test_addDatasetAndWrite(self):

        cube = Cube(pixelGridDefn=pixelGridFromFile(HymapBerlinA_image))
        for filename in [HymapBerlinA_image, HymapBerlinA_train]:
            cube.addDataset(dataset=gdal.Open(filename))

        cubeWriter = CubeWriter('ENVI')
        for dataset, bname in zip(cube, ['image.bsq', 'train.bsq']):
            filename = join(gettempdir(), 'TestCubeWriter', bname)
            cubeWriter.addDataset(filename=filename, dataset=dataset)
        cubeWriter.write()
