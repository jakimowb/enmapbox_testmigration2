import unittest.case
from typing import Union

import numpy as np

from enmapboxprocessing.typing import Array2d, Array3d


class TestCase(unittest.case.TestCase):

    def assertArrayEqual(self, array1: Union[Array2d, Array3d], array2: Union[Array2d, Array3d]):
        array1 = np.array(array1)
        array2 = np.array(array2)
        self.assertTrue(np.all(array1==array2))
