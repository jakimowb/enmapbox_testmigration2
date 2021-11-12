from enmapbox.exampledata import enmap
from enmapboxprocessing.algorithm.awesomespectralindexalgorithm import AwesomeSpectralIndexAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestAwesomeSpectralIndexAlgorithm(TestCase):

    def test_ndvi(self):
        alg = AwesomeSpectralIndexAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_INDEX: 'NDVI',
            alg.P_OUTPUT_VRT: self.filename('ndvi.vrt'),
        }
        result = self.runalg(alg, parameters)
        print(RasterReader(result[alg.P_OUTPUT_VRT]).array()[0].max())

    def test_evi(self):
        alg = AwesomeSpectralIndexAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_INDEX: 'EVI',
            alg.P_SCALE: 1e4,
            alg.P_OUTPUT_VRT: self.filename('evi.vrt'),
        }
        self.runalg(alg, parameters)

