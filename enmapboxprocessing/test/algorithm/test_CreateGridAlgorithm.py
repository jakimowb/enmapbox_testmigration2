import subprocess
import webbrowser

import processing
from qgis._core import QgsRasterLayer, QgsProcessingContext, QgsCoordinateReferenceSystem

from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestCreateGridAlgorithm(TestCase):

    def test_pythonCommand(self):
        raster = QgsRasterLayer(enmap)
        alg = CreateGridAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CRS: raster.crs(),
            alg.P_EXTENT: raster.extent(),
            alg.P_UNIT: alg.PixelUnits,
            alg.P_WIDTH: raster.width(),
            alg.P_HEIGHT: raster.height(),
            alg.P_OUTPUT_RASTER: c + '/vsimem/grid.tif'
        }
        processing, QgsCoordinateReferenceSystem
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_RASTER] + '.log')

    def test_pixelUnits(self):
        raster = QgsRasterLayer(enmap)
        alg = CreateGridAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CRS: raster.crs(),
            alg.P_EXTENT: raster.extent(),
            alg.P_UNIT: alg.PixelUnits,
            alg.P_WIDTH: raster.width(),
            alg.P_HEIGHT: raster.height(),
            alg.P_OUTPUT_RASTER: c + '/vsimem/gridPixelUnits.tif'
        }
        result = self.runalg(alg, parameters)
        grid = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])
        for gold, lead in [
            (raster.crs(), grid.crs()), (raster.extent(), grid.extent()), (raster.width(), grid.width()),
            (raster.height(), grid.height())
        ]:
            self.assertEqual(gold, lead)

    def test_georeferencedUnits(self):
        raster = QgsRasterLayer(enmap)
        alg = CreateGridAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CRS: raster.crs(),
            alg.P_EXTENT: raster.extent(),
            alg.P_UNIT: alg.GeoreferencedUnits,
            alg.P_WIDTH: raster.rasterUnitsPerPixelX(),
            alg.P_HEIGHT: raster.rasterUnitsPerPixelY(),
            alg.P_OUTPUT_RASTER: c + '/vsimem/gridGeoreferencedUnits.tif'
        }
        result = self.runalg(alg, parameters)
        grid = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])
        for gold, lead in [
            (raster.crs(), grid.crs()), (raster.extent(), grid.extent()), (raster.width(), grid.width()),
            (raster.height(), grid.height())
        ]:
            self.assertEqual(gold, lead)
