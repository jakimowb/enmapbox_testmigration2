import numpy as np

from enmapboxprocessing.algorithm.classificationperformancealgorithm import aa_stratified
from enmapboxprocessing.test.algorithm.testcase import TestCase

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class Test_aa_stratified(TestCase):

    def test(self):
        map =       ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'C', 'C', 'B', 'B', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
        reference = ['A', 'A', 'A', 'A', 'A', 'C', 'B', 'A', 'B', 'C', 'A', 'B', 'B', 'B', 'B', 'B', 'A', 'A', 'B', 'B', 'C', 'C', 'C', 'C', 'C', 'D', 'D', 'B', 'B', 'A', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'C', 'C', 'B']
        stratum =   ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '3', '3', '3', '3', '3', '3', '3', '3', '3', '3', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4']
        h = ['1', '2', '3', '4']
        N_h = [40000, 30000, 20000, 10000]

        stats = aa_stratified(stratum, reference, map, h, N_h)

        cm = [[9.2,  1.6, 1.6, 0.0],
              [4.8, 10.8, 3.2, 0.0],
              [0.0, 0.8, 2.4, 1.6],
              [0.0, 0.4, 0.8, 2.8]]


        cmp = [[0.23, 0.04, 0.04, 0.00],
               [0.12, 0.27, 0.08, 0.00],
               [0.00, 0.02, 0.06, 0.04],
               [0.00, 0.01, 0.02, 0.07]]

        # class-wise accuracies
        #         ua         ua_se      pa         pa_se      f1         f1_se
        cwa = [[0.7419355, 0.1645627, 0.6571429, 0.1477318, 0.6969697, 0.11034620],
                 [0.5744681, 0.1248023, 0.7941176, 0.1165671, 0.6666667, 0.09354009],
                 [0.5000000, 0.2151657, 0.3000000, 0.1504438, 0.3750000, 0.13219833],
                 [0.7000000, 0.1527525, 0.6363636, 0.1623242, 0.6666667, 0.11284328]]
        cwa = np.array(cwa).T

        #           oa          oa_se
        accuracy = [0.63000000, 0.08465617]

        #        class proportion proportion_se
        area = [[0.35,            0.08225975],
                [0.34,            0.07586538],
                [0.20,            0.06429101],
                [0.11,            0.03073181]]
        area = np.array(area).T

        self.assertTrue(np.allclose(cmp, stats['confusion_matrix_proportions']))
        self.assertTrue(np.allclose(cm, stats['confusion_matrix_counts']))
        self.assertAlmostEqual(accuracy[0], stats['overall_accuracy'])
        self.assertAlmostEqual(accuracy[1], stats['overall_accuracy_se'])
        self.assertTrue(np.allclose(area[0], stats['area_proportion']))
        self.assertTrue(np.allclose(area[1], stats['area_proportion_se']))
        self.assertTrue(np.allclose(cwa[0], stats['users_accuracy']))
        self.assertTrue(np.allclose(cwa[1], stats['users_accuracy_se']))
        self.assertTrue(np.allclose(cwa[2], stats['producers_accuracy']))
        self.assertTrue(np.allclose(cwa[3], stats['producers_accuracy_se']))
        self.assertTrue(np.allclose(cwa[4], stats['f1']))
        self.assertTrue(np.allclose(cwa[5], stats['f1_se']))
