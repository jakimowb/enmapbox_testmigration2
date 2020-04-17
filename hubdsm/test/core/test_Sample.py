from collections import OrderedDict
from unittest.case import TestCase

import numpy as np

from hubdsm.core.color import Color
from hubdsm.core.sample import Sample


class TestSample(TestCase):

    def test(self):
        arrayDict = OrderedDict(
            # a=np.array(['a1', 'a2', 'a3456789']),
            b=np.array([1, 2, 3], dtype=np.uint8),
            c=np.array([True, False, True], dtype=np.bool),
            d=np.array([1.1, 2.2, 3.3], dtype=np.float32)
        )
        sample = Sample.fromArrays(arrays=arrayDict, xLocations=[1, 2, 3], yLocations=[0, 0, 0])
