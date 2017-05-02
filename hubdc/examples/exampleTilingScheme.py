from hubdc import PixelGrid, Applier, ApplierOperator, ApplierOutput
from osgeo import ogr, osr

def getMGRSPixelGrids(names, res, anchor, buffer=0):

    # get features from shapefile
    shp = r'C:\Work\data\gms\gis\MGRS_100km\mgrs_100km.shp'
    ds = ogr.Open(shp)
    layer = ds.GetLayer()
    features = dict()
    for feature in layer:
        name = feature.GetField('GRID1MIL')+feature.GetField('GRID100K')
        if name in names:
            features[name] = feature

    # reproject to UTM landsat grid
    sourceSRS = layer.GetSpatialRef()
    grids = dict()
    for name, feature in features.items():
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
        grids[name] = grid
    return grids


LANDSAT_ANCHOR = (15, 15)
SENTINEL_ANCHOR = (0, 0)

def script():

    for name, grid in getMGRSPixelGrids(names=['32UPC', '32UQC', '33UTT', '33UUT'], res=30, anchor=LANDSAT_ANCHOR, buffer=300).items():

        print('Apply '+name)
        applier = Applier(grid=grid, ufuncClass=RandomImage, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
        applier['out'] = ApplierOutput(r'c:\output\random{name}.img'.format(name=name), format='ENVI')
        applier.run()

class RandomImage(ApplierOperator):

    def ufunc(self):
        import numpy
        ysize, xsize = self.grid.getDimensions()
        randomImage = numpy.random.random_integers(low=0, high=255, size=(1, ysize, xsize))
        self.setData('out', array=randomImage, dtype=numpy.uint8)

if __name__ == '__main__':
    script()

