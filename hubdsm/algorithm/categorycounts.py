from collections import OrderedDict
from typing import  Dict

import numpy as np

from hubdsm.core.raster import Raster
from hubdsm.error import GridMismatchError, BandCountMismatchError


def categoryCounts(raster: Raster, n: int = None) -> Dict[int, int]:
    '''Return counts for categories 1, 2, ..., n.  If n is None, n is derived from the maximum value in the raster.'''

    rasterBands = raster.bands

    if n is None:
        n = 0
        for rasterBand in rasterBands:
            array = rasterBand.readAsArray(grid=raster.grid)
            n = max(n, np.nanmax(array))

    counts = OrderedDict()
    for array, maskArray in zip(raster.iterArrays(), raster.iterMaskArrays()):
        data = array[maskArray]
        hist, bin_edges = np.histogram(data, bins=n, range=[1, n + 1, ])
        for i, count in enumerate(hist, 1):
            counts[i] = counts.get(i, 0) + count
    return counts
