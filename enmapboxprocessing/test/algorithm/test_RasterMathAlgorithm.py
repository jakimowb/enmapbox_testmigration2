import numpy as np

from enmapboxprocessing.algorithm.rastermathalgorithm import RasterMathAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, hires

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRasterMathAlgorithm(TestCase):

    def test_copy_raster(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_CODE: 'A',
            alg.P_R1: 'c:/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = np.array(RasterReader(enmap).array())
        lead = np.array(RasterReader(result[alg.P_R1]).array())
        self.assertEqual(gold.dtype, lead.dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))


    def test_add_raster(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_B: enmap,
            alg.P_CODE: 'A + B',
            alg.P_R1: 'c:/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = np.array(RasterReader(enmap).array()) * 2
        lead = np.array(RasterReader(result[alg.P_R1]).array())
        self.assertEqual(gold.dtype, lead.dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))

    def test_add_bands(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_A_BAND: 1,
            alg.P_B: hires,
            alg.P_B_BAND: 1,
            alg.P_CODE: 'A + B',
            alg.P_R1: 'c:/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        lead = np.array(RasterReader(result[alg.P_R1]).array())
        self.assertEqual(32355913, np.sum(lead))

    def test_inputs_lists(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_INPUTS: [enmap, enmap],
            alg.P_R1: 'c:/vsimem/sum.tif',
            alg.P_R2: 'c:/vsimem/mask.tif',
            alg.P_CODE: 'R1 = np.average(INPUTS, axis=0)\n'
                        'R2 = np.all(INPUT_MASKS, axis=0)\n'
                        'feedback.pushInfo(str(INPUTS_[0].noDataValue()))'
        }
        self.runalg(alg, parameters)

    def test_add_bands_and_manually_mask(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_A_BAND: 1,
            alg.P_B: hires,
            alg.P_B_BAND: 1,
            alg.P_CODE: 'R1 = A + B\n'
                        'R1[~AM] = -99\n'
                        'R1[~BM] = -99\n'
                        'R1_.setNoDataValue(-99)\n'
                        'R1_.setBandName("my band", bandNo=1)\n'
                        'R1_.setMetadataItem("my key", 42, "MY DOMAIN")\n',
            alg.P_R1: 'c:/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        raster = RasterReader(result[alg.P_R1])
        self.assertEqual(-99, raster.noDataValue())
        self.assertEqual('my band', raster.bandName(1))
        self.assertEqual('42', raster.metadataItem('my key', 'MY DOMAIN'))
        self.assertEqual(10797202, np.sum(RasterReader(result[alg.P_R1]).array()))

    def test_with_overlap(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: hires,
            alg.P_CODE: 'from scipy.ndimage import gaussian_filter\n'
                        'R1 = gaussian_filter(A, sigma=3)\n',
            alg.P_R1: 'c:/vsimem/raster.tif',
            alg.P_OVERLAP: 15
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(631432553, np.sum(RasterReader(result[alg.P_R1]).array()))

    def test_stats(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_CODE: 'hist, bin_edges = np.histogram(A, bins=10, range=(0, 10000))\n'
                        'for a, b, n in zip(bin_edges[:-1], bin_edges[1:], hist):\n'
                        "   feedback.pushInfo(f'[{a}, {b}]: {n}')\n",
            alg.P_MONOLITHIC: True
        }
        self.runalg(alg, parameters)

    def test_add_raster_and_mask(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_B: enmap,
            alg.P_CODE: 'A + B',
            alg.P_R1: 'c:/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = np.array(RasterReader(enmap).array()) * 2
        lead = np.array(RasterReader(result[alg.P_R1]).array())
        self.assertEqual(gold.dtype, lead.dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))

    def test_copy_band(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_A: enmap,
            alg.P_EXPRESSION: 'np.add(A@1, A@2)',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array(bandList=[1, 2])
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(gold[0].dtype, lead[0].dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))

    def test_build_stack(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap, enmap, enmap],
            alg.P_EXPRESSION: 'list(A) + list(B) + list(C)',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = 3 * RasterReader(enmap).bandCount()
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).bandCount()
        self.assertEqual(gold, lead)

    def test_multiline(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap],
            alg.P_EXPRESSION: 'nir = np.float32(A@64)\n'
                              'red = np.float32(A@38)\n'
                              'ndvi = (nir - red) / (nir + red)\n'
                              'ndvi',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(35297, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array())))

