from os.path import join, dirname
from osgeo import osr, ogr
from hubdc.model.PixelGrid import PixelGrid

def getMGRSPixelGridsByNames(names, res, anchor, buffer=0):

    # get features from shapefile
    shp = join(dirname(__file__), 'mgrs.shp')
    ds = ogr.Open(shp)
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
        grid = PixelGrid(projection=str(targetSRS),
                         xMin=min(xrange), xMax=max(xrange),
                         yMin=min(yrange), yMax=max(yrange),
                         xRes=res, yRes=res)
        grid = grid.buffer(buffer=buffer)
        grid = grid.anchor(xAnchor=anchor[0], yAnchor=anchor[1])
        yield name, grid

def getMGRSPixelGridsByShape(shape, res, anchor, pixelBuffer=0, trim=True):

    assert isinstance(shape, ogr.Geometry)

    shp = join(dirname(__file__), 'mgrs.shp')
    ds = ogr.Open(shp)
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
        grid = PixelGrid(projection=str(targetSRS),
                         xMin=min(xrange), xMax=max(xrange),
                         yMin=min(yrange), yMax=max(yrange),
                         xRes=res, yRes=res)
        grid = grid.pixelBuffer(buffer=pixelBuffer)
        grid = grid.anchor(xAnchor=anchor[0], yAnchor=anchor[1])

        yield name, grid
