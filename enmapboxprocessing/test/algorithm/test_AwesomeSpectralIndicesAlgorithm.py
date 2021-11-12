from enmapbox.exampledata import enmap
from enmapboxprocessing.algorithm.awesomespectralindexalgorithm import AwesomeSpectralIndicesAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestAwesomeSpectralIndexAlgorithm(TestCase):

    def test_single(self):
        alg = AwesomeSpectralIndicesAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_INDICES: 'NDVI',
            alg.P_OUTPUT_VRT: self.filename('ndvi.vrt'),
        }
        result = self.runalg(alg, parameters)
        print(RasterReader(result[alg.P_OUTPUT_VRT]).array()[0].max())

    def test_evi(self):
        alg = AwesomeSpectralIndicesAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_INDEX: 'EVI',
            alg.P_SCALE: 1e4,
            alg.P_OUTPUT_VRT: self.filename('evi.vrt'),
        }
        self.runalg(alg, parameters)

