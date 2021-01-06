from qgis._core import QgsRasterLayer


from enmapboxtestdata import enmap
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.processing.creategrid import CreateGrid
from hubdsm.test.processing.testcase import TestCase


class TestCreateGrid(TestCase):

    def test(self):
        filename = 'c:/vsimem/grid.vrt'

        layer = QgsRasterLayer(enmap)


        alg = CreateGrid()
        io = {
            alg.P_CRS: layer.crs(),
            alg.P_EXTENT: layer.extent(),
            alg.P_RESOLUTION: 30,
            alg.P_OUTPUT_GRID: filename
        }
        self.runalg(alg=alg, io=io)
        raster1 = GdalRaster.open(filename)
        raster2 = GdalRaster.open(enmap)
        assert raster1.grid.equal(raster2.grid)
