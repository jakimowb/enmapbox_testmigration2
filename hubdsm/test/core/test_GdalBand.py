from unittest.case import TestCase

import numpy as np
from osgeo import gdal, ogr

from enmapboxtestdata import enmap, landcover_polygons
from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.error import ProjectionMismatchError
from hubdsm.core.extent import Extent
from hubdsm.core.gdalband import GdalBand
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.gdalrasterdriver import MEM_DRIVER, ENVI_DRIVER
from hubdsm.core.ogrlayer import OgrLayer
from hubdsm.core.pixellocation import PixelLocation
from hubdsm.core.projection import Projection
from hubdsm.core.resolution import Resolution
from hubdsm.core.shape import GridShape
from hubdsm.core.size import Size


class TestGdalBand(TestCase):

    def test(self):
        gdalBand = GdalBand.open(enmap, number=1)
        self.assertEqual(gdalBand.index, 0)
        self.assertEqual(gdalBand.raster.filename, enmap)
        self.assertEqual(gdalBand.gdalDataType, gdal.GDT_Int16)
        self.assertTrue(
            gdalBand.grid.equal(
                other=Grid(
                    extent=Extent(ul=Location(x=380952.37, y=5820372.35), size=Size(x=6600.0, y=12000.0)),
                    resolution=Resolution(x=30.0, y=30.0),
                    projection=Projection(
                        wkt='PROJCS["UTM_Zone_33N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1],AXIS["Easting",EAST],AXIS["Northing",NORTH]]')
                )
            )
        )

    def test_flushCache(self):
        gdalBand = GdalBand.open(MEM_DRIVER.createFromArray(array=np.array([[[1]], [[0]]])), number=1)
        gdalBand.flushCache()

    def test_readAsArray(self):
        gdalBand = GdalBand.open(MEM_DRIVER.createFromArray(array=np.array([[[1]], [[0]]])), number=1)
        self.assertTrue(np.all(np.equal(gdalBand.readAsArray(), [[1]])))
        self.assertTrue(np.all(np.equal(gdalBand.readAsArray(), gdalBand.readAsArray(grid=gdalBand.grid))))
        try:
            grid = GdalRaster.open(enmap).grid
            gdalBand.readAsArray(grid=grid)
        except ProjectionMismatchError:
            pass

    def test_writeArray(self):
        gdalBand = GdalBand.open(MEM_DRIVER.createFromArray(array=np.array([[[-1, -1]]])), number=1)

        gdalBand.fill(0)
        self.assertTrue(np.all(np.equal(gdalBand.readAsArray(), [[0, 0]])))

        gdalBand.writeArray(np.array([[1, 1]]))
        self.assertTrue(np.all(np.equal(gdalBand.readAsArray(), [[1, 1]])))

        grid = gdalBand.grid.subgrid(offset=PixelLocation(x=1, y=0), shape=GridShape(x=1, y=1))
        gdalBand.writeArray(np.array([[2]]), grid=grid)
        self.assertTrue(np.all(np.equal(gdalBand.readAsArray(), [[1, 2]])))

    def test_metadata(self):
        gdalBand = MEM_DRIVER.createFromArray(array=np.array([[[1]]])).band(1)
        gdalBand.setMetadataDict(metadataDict={'A': {'a': 1}, 'B': {'b': None}})
        self.assertDictEqual(gdalBand.metadataDict, {'A': {'a': '1'}})
        self.assertIsNone(gdalBand.metadataItem(key='b', domain='B'))

    def test_noDataValue(self):
        gdalBand = MEM_DRIVER.createFromArray(array=np.array([[[1]]])).band(1)
        gdalBand.setNoDataValue(None)
        self.assertIsNone(gdalBand.noDataValue)
        gdalBand.setNoDataValue(0)
        self.assertEqual(gdalBand.noDataValue, 0)

    def test_description(self):
        gdalBand = MEM_DRIVER.createFromArray(array=np.array([[[1]]])).band(1)
        gdalBand.setDescription('B1')
        self.assertEqual(gdalBand.description, 'B1')

    def test_categories(self):
        gdalBand = MEM_DRIVER.createFromArray(array=np.array([[[1]]], dtype=np.uint8)).band(1)
        self.assertTrue(len(gdalBand.categories) == 0)
        categories = [Category(id=0, name='Unclassified', color=Color()),
                      Category(id=1, name='a', color=Color(red=255)),
                      Category(id=3, name='b', color=Color(blue=255))]
        gdalBand.setCategories(categories=categories)
        self.assertListEqual(gdalBand.categories, categories)

    def test_rasterizeAndPolygonize(self):
        assert 0
        grid = GdalRaster.open(enmap).grid
        ogrLayer = OgrLayer.open(landcover_polygons)
        gdalBand = ENVI_DRIVER.createFromArray(
            array=np.zeros(shape=grid.shape.withZ(1), dtype=np.uint8),
            grid=grid,
            filename=r'c:\_test\ids.bsq').band(number=1)
        gdalBand.rasterize(ogrLayer=ogrLayer, burnAttribute='level_3_id')
        print(np.unique(gdalBand.readAsArray(), return_counts=True))
