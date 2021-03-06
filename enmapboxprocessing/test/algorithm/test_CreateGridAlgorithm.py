from qgis._core import QgsRasterLayer, QgsProcessingContext, QgsCoordinateReferenceSystem

import processing
from enmapbox.exampledata import enmap
from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestCreateGridAlgorithm(TestCase):

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
            alg.P_OUTPUT_GRID: self.filename('gridPixelUnits.tif')
        }
        result = self.runalg(alg, parameters)
        grid = QgsRasterLayer(result[alg.P_OUTPUT_GRID])
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
            alg.P_OUTPUT_GRID: self.filename('gridGeoreferencedUnits.tif')
        }
        result = self.runalg(alg, parameters)
        grid = QgsRasterLayer(result[alg.P_OUTPUT_GRID])
        for gold, lead in [
            (raster.crs(), grid.crs()), (raster.extent(), grid.extent()), (raster.width(), grid.width()),
            (raster.height(), grid.height())
        ]:
            self.assertEqual(gold, lead)
