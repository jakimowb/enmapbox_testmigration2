from os.path import join, dirname
from osgeo import osr, ogr
from hubdc.core import Grid

def getMGRSShapefile():
    return join(dirname(__file__), 'gis', 'mgrs', 'mgrs.shp')

def getMGRSPixelGridsByNames(names, res, anchor, buffer=0):

    # get features from shapefile
    ds = ogr.Open(getMGRSShapefile())
    layer = ds.GetLayer()
    features = dict()
    for feature in layer:
        name = feature.GetField('GRID1MIL')+feature.GetField('GRID100K')
        if name in names:
            features[name] = feature

    # reproject to UTM landsat grid
    sourceSRS = layer.GetSpatialRef()
    for name in names:
        feature = features[name]
        utm = name[0:2]
        targetSRS = osr.SpatialReference()
        targetSRS.ImportFromEPSG(int('326'+utm))
        transform = osr.CoordinateTransformation(sourceSRS, targetSRS)
        geom = feature.GetGeometryRef()
        geom.Transform(transform)
        bb = geom.GetEnvelope()
        xrange, yrange = bb[:2], bb[2:]
        grid = Grid(projection=str(targetSRS),
                    xMin=min(xrange), xMax=max(xrange),
                    yMin=min(yrange), yMax=max(yrange),
                    xRes=res, yRes=res)
        grid = grid.buffer(buffer=buffer)
        grid = grid.anchor(x=anchor[0], y=anchor[1])
        yield name, grid

def getMGRSPixelGridsByShape(shape, res, anchor, pixelBuffer=0, trim=True):

    assert isinstance(shape, ogr.Geometry)

    ds = ogr.Open(getMGRSShapefile())
    layer = ds.GetLayer()
#    targetSRS = layer.GetSpatialRef()
    layer.SetSpatialFilter(shape)

    for feature in layer:
        name = feature.GetField('GRID1MIL')+feature.GetField('GRID100K')

        # reproject to UTM landsat grid
        sourceSRS = layer.GetSpatialRef()
        utm = name[0:2]
        targetSRS = osr.SpatialReference()
        targetSRS.ImportFromEPSG(int('326'+utm))
        transform = osr.CoordinateTransformation(sourceSRS, targetSRS)
        geom = feature.GetGeometryRef()
        if trim:
            geom = geom.Intersection(shape)

        geom.Transform(transform)
        bb = geom.GetEnvelope()
        xrange, yrange = bb[:2], bb[2:]
        grid = Grid(projection=str(targetSRS),
                    xMin=min(xrange), xMax=max(xrange),
                    yMin=min(yrange), yMax=max(yrange),
                    xRes=res, yRes=res)
        grid = grid.pixelBuffer(buffer=pixelBuffer)
        grid = grid.anchor(x=anchor[0], y=anchor[1])

        yield name, grid

def getWRS2Shapefile():
    return join(dirname(__file__), 'gis', 'wrs2', 'wrs2.shp')

def getWRS2NamesInsidePixelGrid(grid):
    assert isinstance(grid, Grid)

    ds = ogr.Open(getWRS2Shapefile())
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

def getWRS2FootprintsGeometry(footprints):

    ds = ogr.Open(getWRS2Shapefile())
    layer = ds.GetLayer()

    geometry = ogr.Geometry(ogr.wkbMultiPolygon)
    for feature in layer:
        if str(feature.GetField('PR')).zfill(6) in footprints:
            geometry.AddGeometry(feature.GetGeometryRef())

    return geometry.UnionCascaded()
