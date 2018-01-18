from unittest import TestCase
import numpy as np
import tempfile
from os.path import join
from hubdc.tiling import UTMTilingScheme
from hubdc.model import *
from hubdc.testdata import BrandenburgDistricts

class TestUTMTilingScheme(TestCase):
    def test_mgrsGrids(self):
        outdir = join(tempfile.gettempdir(), 'hubdc_test_tiling')

        roi = SpatialGeometry.fromVector(filename=BrandenburgDistricts.shp)

        for zone in [32, 33]:
            for band in ['u']:
                mgrs1mil = '{}{}'.format(str(zone).zfill(2), band.upper())
                for (iy, ix), grid in UTMTilingScheme.mgrsGrids(zone=zone,
                                                                band=band,
                                                                resolution=Resolution(x=300, y=300),
                                                                anchor=Point(x=5, y=5),
                                                                roi=roi).items():
                    assert isinstance(grid, Grid)
                    array = np.zeros(grid.shape())
                    createRasterFromArray(grid=grid, array=array,
                                          filename=join(outdir, '{}_Y{}_X{}.tif'.format(mgrs1mil, iy, ix)),
                                          driver='GTiff',
                                          options=['compress=lzw'])
