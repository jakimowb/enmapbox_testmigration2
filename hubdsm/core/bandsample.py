from dataclasses import dataclass

import numpy as np


@dataclass
class BandSample(object):
    xLocations: np.ndarray
    yLocations: np.ndarray
    values: np.ndarray

    def __post_init__(self):
        assert isinstance(self.xLocations, np.ndarray)
        assert isinstance(self.yLocations, np.ndarray)
        assert isinstance(self.values, np.ndarray)
        assert self.xLocations.shape == self.yLocations.shape == self.values.shape == (self.n, )
        assert self.xLocations.ndim == self.yLocations.ndim == self.values.ndim == 1

    @property
    def n(self):
        return len(self.values)