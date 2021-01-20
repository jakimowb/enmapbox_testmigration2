import unittest.case
from typing import Union

import numpy as np

from enmapboxprocessing.typing import Array2d, Array3d


class TestCase(unittest.case.TestCase):

    def assertArrayEqual(self, array1: Union[Array2d, Array3d], array2: Union[Array2d, Array3d]):
        self.assertListEqual(list(np.array(array1).flatten()), list(np.array(array2).flatten()))
