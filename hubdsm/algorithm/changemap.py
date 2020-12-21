from typing import List

import numpy as np

from hubdsm.core.band import Band
from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.gdalraster import GdalRaster


def changeMap(
        band1: Band, band2: Band, categories1: List[Category] = None, categories2: List[Category] = None, filename=None
) -> GdalRaster:
    '''Return change map.'''

    grid = band1.gdalBand.grid
    mask = band1.readAsMaskArray()
    np.logical_and(mask, band2.readAsMaskArray(grid=grid), out=mask)

    array = band1.readAsArray().astype(np.uint64) * mask
    np.multiply(array, np.uint64(1e10), out=array)
    np.add(array, band2.readAsArray(grid=grid).astype(np.uint64) * mask, out=array)

    uniques, array = np.unique(array, return_index=False, return_inverse=True, return_counts=False)
    array = np.reshape(array, grid.shape.withZ(1)) + 1

    vmax = array.max()
    if vmax <= np.uint8(-1):
        array = array.astype(np.uint8)
    elif vmax <= np.uint16(-1):
        array = array.astype(np.uint16)
    elif vmax <= np.uint32(-1):
        array = array.astype(np.uint32)

    if categories1 is None:
        labels1 = {str(v): str(int(v // 1e10)) for v in uniques}
    else:
        labels1 = {str(c.id): c.name for c in categories1}

    if categories2 is None:
        labels2 = {str(v): str(int(v - (v // 1e10) * 1e10)) for v in uniques}
    else:
        labels2 = {str(c.id): c.name for c in categories2}

    def labelFromUnique(unique: int):
        id1 = int(unique // 1e10)
        id2 = int(unique - id1 * 1e10)
        return labels1.get(str(id1), str(id1)) + '->' + labels2.get(str(id2), str(id2))

    categories = [Category(id=i + 1, name=labelFromUnique(unique), color=Color.fromRandom()) for i, unique in
                  enumerate(uniques)]

    gdalRaster = GdalRaster.createFromArray(array=array, grid=grid, filename=filename)
    gdalRaster.setCategories(categories=categories)
    return gdalRaster
