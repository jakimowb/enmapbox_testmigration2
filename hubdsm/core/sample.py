from typing import Dict

from dataclasses import dataclass

import numpy as np


@dataclass
class Sample(object):
    values: np.ndarray
    xLocations: np.ndarray
    yLocations: np.ndarray


    def __post_init__(self):
        assert isinstance(self.xLocations, np.ndarray)
        assert isinstance(self.yLocations, np.ndarray)
        assert isinstance(self.values, np.ndarray)
        assert self.xLocations.ndim == self.yLocations.ndim == 1
        assert self.values.ndim == 2
        assert self.xLocations.shape[0] == self.yLocations.shape[0] == self.nsamples

    @staticmethod
    def fromArrays(arrays: Dict[str, np.ndarray], xLocations: np.ndarray, yLocations: np.ndarray) -> 'Sample':
        dtype = np.dtype(
            dict(
                names=tuple(arrays.keys()),
                formats=tuple(array.dtype for array in arrays.values())
            )
        )
        values = np.array(list(arrays.values()), dtype=dtype)
        return Sample

    @property
    def nsamples(self):
        return self.values.shape[0]

    @property
    def nfeatures(self):
        return self.values.shape[1]
