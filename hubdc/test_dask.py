from dask import delayed
from hubdc.testdata import LT51940232010189KIS01
from hubdc.model import *
import numpy as np


class Landsat(object):

    def __init__(self):
        self.bands = dict()
        self.bands['cfmask'] = delayed(openRaster)(LT51940232010189KIS01.cfmask)
        self.bands['red'] = delayed(openRaster)(LT51940232010189KIS01.red)
        self.bands['nir'] = delayed(openRaster)(LT51940232010189KIS01.nir)

    def nd(self, k1, k2, grid):
        b1 = self.bands[k1].array(grid=grid)
        b2 = self.bands[k2].array(grid=grid)
        return np.float32(b1-b2)/(b1+b2)

landsat = Landsat()

grid = openRaster(LT51940232010189KIS01.cfmask).grid()

bands = dict()
bands['cfmask'] = delayed(openRaster)(LT51940232010189KIS01.cfmask)
bands['red'] = delayed(openRaster)(LT51940232010189KIS01.red)
bands['nir'] = delayed(openRaster)(LT51940232010189KIS01.nir)

result = delayed(landsat.nd)('nir', 'red', grid)
print(result.compute())
