from collections import OrderedDict
from typing import  Dict

import numpy as np

from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.core.band import Band


def uniqueBandValueCounts(band: Band, po=ProcessingOptions()) -> Dict[int, int]:
    '''Return unique band value counts.'''

    t0 = po.callbackStart(uniqueBandValueCounts.__name__)

    grid = band.gdalBand.grid
    subgrids = list(grid.subgrids(shape=po.getShape(default=grid.shape)))
    counts = dict()
    i = 1
    n = len(subgrids)
    for subgrid in subgrids:
        po.callbackProgress(i, n)
        i += 1
        sample = band.readAsSample(grid=subgrid)
        for value, count in zip(*np.unique(sample.values, return_counts=True)):
            counts[value] = counts.get(value, 0) + count
    counts = OrderedDict(sorted(counts.items(), key=lambda item: item[0]))
    po.callbackFinish(uniqueBandValueCounts.__name__, t0=t0)
    return counts
