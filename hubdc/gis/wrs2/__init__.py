from os.path import join, dirname
from osgeo import osr, ogr
from hubdc.model.PixelGrid import PixelGrid

def getWRS2NamesInsidePixelGrid(grid):
    assert isinstance(grid, PixelGrid)

    # open WRS2 shapefile layer
    shp = join(dirname(__file__), 'wrs2.shp')
    ds = ogr.Open(shp)
    layer = ds.GetLayer()

    # set up transformation
    targetSRS = layer.GetSpatialRef()
    gridSRS = osr.SpatialReference(str(grid.projection))
    transform = osr.CoordinateTransformation(gridSRS, targetSRS)

    # create grid extent and transform into shapefile SRS
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(grid.xMin, grid.yMax)
    ring.AddPoint(grid.xMin, grid.yMin)
    ring.AddPoint(grid.xMax, grid.yMin)
    ring.AddPoint(grid.xMax, grid.yMax)
    ring.AddPoint(grid.xMin, grid.yMax)
    geom = ogr.Geometry(ogr.wkbPolygon)
    geom.AddGeometry(ring)
    geom.Transform(transform)

    # set spatial filter
    layer.SetSpatialFilter(geom)

    return [str(feature.GetField('PR')).zfill(6) for feature in layer]
