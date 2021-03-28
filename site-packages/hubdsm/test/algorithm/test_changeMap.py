from unittest import TestCase

import numpy as np

from hubdsm.algorithm.changemap import changeMap
from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.raster import Raster


class TestChangeMap(TestCase):

    def test(self):
        filename = 'c:/vsimem/changemap.bsq'
        categories = [
            Category(id=0, name='Unclassified', color=Color()),
            Category(id=1, name='Class 1', color=Color()),
            Category(id=2, name='Class 2', color=Color())
        ]
        raster1 = Raster.createFromArray(array=np.array([[[0, 1, 1], [2, 1, 10]]])).setNoDataValue(0)
        raster2 = Raster.createFromArray(array=np.array([[[10, 1, 1], [1, 1, 0]]])).setNoDataValue(0)
        band1 = raster1.band(number=1)
        band2 = raster2.band(number=1)

        gdalRaster = changeMap(band1=band1, band2=band2, filename=filename)
        self.assertListEqual(list([1, 2, 2, 3, 2, 1]), list(gdalRaster.readAsArray().flatten()))
        self.assertListEqual([(c.id, c.name) for c in gdalRaster.categories], [(1, '0->0'), (2, '1->1'), (3, '2->1')])

        filename = 'c:/vsimem/changemap2.bsq'
        gdalRaster = changeMap(
            band1=band1, band2=band2, categories1=categories, categories2=categories, filename=filename
        )

        self.assertListEqual(
            [(c.id, c.name) for c in gdalRaster.categories],
            [(1, 'Unclassified->Unclassified'), (2, 'Class 1->Class 1'), (3, 'Class 2->Class 1')]
        )
