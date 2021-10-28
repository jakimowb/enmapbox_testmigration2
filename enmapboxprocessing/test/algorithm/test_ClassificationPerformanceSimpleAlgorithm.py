from math import isnan

from qgis._core import QgsProcessingException

from enmapbox.exampledata import landcover_polygons, enmap
from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import landcover_map_l3

writeToDisk = True


class TestClassificationPerformanceSimpleAlgorithm(TestCase):

    def test(self):
        alg = ClassificationPerformanceSimpleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: landcover_map_l3,
            alg.P_REFERENCE: landcover_polygons,
            alg.P_OPEN_REPORT: False,
            alg.P_OUTPUT_REPORT: self.filename('report.html'),
        }
        self.runalg(alg, parameters)

    def test_perfectMap(self):
        alg = ClassificationPerformanceSimpleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: landcover_map_l3,
            alg.P_REFERENCE: landcover_map_l3,
            alg.P_OPEN_REPORT: False,
            alg.P_OUTPUT_REPORT: self.filename('report_perfectMap.html'),
        }
        result = self.runalg(alg, parameters)
        stats = Utils.jsonLoad(result[alg.P_OUTPUT_REPORT] + '.json')
        for v in stats['producers_accuracy_se'] + stats['users_accuracy_se']:
            self.assertFalse(isnan(v))  # previously we had NaN values, so better check this

    def test_error_messages(self):
        alg = ClassificationPerformanceSimpleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: enmap,
            alg.P_REFERENCE: landcover_map_l3,
            alg.P_OPEN_REPORT: False,
            alg.P_OUTPUT_REPORT: self.filename('report.html'),
        }
        try:
            self.runalg(alg, parameters)
        except QgsProcessingException as error:
            self.assertEqual(
                str(error),
                'Unable to execute algorithm\nInvalid classification, requires paletted/unique values renderer (Predicted classification layer)'
            )
        parameters = {
            alg.P_CLASSIFICATION: landcover_map_l3,
            alg.P_REFERENCE: enmap,
            alg.P_OPEN_REPORT: False,
            alg.P_OUTPUT_REPORT: self.filename('report2.html'),
        }
        try:
            self.runalg(alg, parameters)
        except QgsProcessingException as error:
            self.assertEqual(
                str(error),
                'Unable to execute algorithm\nInvalid classification, requires paletted/unique values renderer (Observed categorized layer)'
            )
