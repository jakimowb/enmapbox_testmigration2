from enmapboxprocessing.algorithm._experimental_customcolor import ExperimentalCustomColor

from enmapboxprocessing.test.algorithm.testcase import TestCase

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class Test_ExperimentalCustomColor(TestCase):

    def test(self):
        alg = ExperimentalCustomColor()
        alg.initAlgorithm()
        parameters = {alg.P_COLOR: '#FF0000'}
        self.runalg(alg, parameters)
