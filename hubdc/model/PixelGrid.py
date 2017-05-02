from osgeo import osr
from rios.pixelgrid import PixelGridDefn, pixelGridFromFile


class PixelGrid(PixelGridDefn):

    @staticmethod
    def fromPixelGrid(pixelGrid):
        assert isinstance(pixelGrid, PixelGridDefn)
        nrows, ncols = pixelGrid.getDimensions()
        return PixelGrid(geotransform=pixelGrid.makeGeoTransform(),
                         nrows=nrows, ncols=ncols,
                         projection=pixelGrid.projection)

    @staticmethod
    def fromDataset(dataset):
        return PixelGrid(geotransform=dataset.gdalDataset.GetGeoTransform(),
                         nrows=dataset.gdalDataset.RasterYSize, ncols=dataset.gdalDataset.RasterXSize,
                         projection=dataset.gdalDataset.GetProjection())

    @classmethod
    def fromFile(clf, filename):
        return clf.fromPixelGrid(pixelGridFromFile(filename))

    def __init__(self, geotransform=None, nrows=None, ncols=None, projection=None,
            xMin=None, xMax=None, yMin=None, yMax=None, xRes=None, yRes=None):

        def getProjectionWKT(projection):
            if projection.startswith('EPSG:'):
                epsg = int(projection[-4:])
                projection = osr.SpatialReference()
                projection.ImportFromEPSG(epsg)
                return projection.ExportToWkt()
            return projection

        def trimBoundsToResolutionMultipleAndCastGeoTransformToFloat(pixelGrid):
            geotransform = tuple(float(v) for v in pixelGrid.makeGeoTransform())
            nrows, ncols = pixelGrid.getDimensions()
            PixelGridDefn.__init__(self, geotransform=geotransform, nrows=nrows, ncols=ncols, projection=projection)

        projection = getProjectionWKT(projection)
        trimBoundsToResolutionMultipleAndCastGeoTransformToFloat(pixelGrid=PixelGridDefn(geotransform=geotransform, nrows=nrows, ncols=ncols,
                                                                                         projection=projection, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax,
                                                                                         xRes=xRes, yRes=yRes))

    def equalUL(self, other):
        return (self.xMin == other.xMin and
                self.yMax == other.yMax)

    def equalDimensions(self, other):
        return self.getDimensions() == other.getDimensions()

    def equal(self, other):
        return (self.equalProjection(other=other) and
                self.equalUL(other=other) and
                self.equalPixSize(other=other) and
                self.equalDimensions(other=other))

    def intersection(self, other):
        return PixelGrid.fromPixelGrid(PixelGridDefn.intersection(self, other))

    def reproject(self, targetGrid):
        return PixelGrid.fromPixelGrid(PixelGridDefn.reproject(self, targetGrid))

    def buffer(self, buffer, north=True, west=True, south=True, east=True):
        buffered = self.copy()
        if west: buffered.xMin -= buffer
        if east: buffered.xMax += buffer
        if south: buffered.yMin -= buffer
        if north: buffered.yMax += buffer
        return PixelGrid.fromPixelGrid(buffered)

    def anchor(self, xAnchor, yAnchor):
        anchored = self.copy()

        xMinOff = (anchored.xMin - xAnchor) % anchored.xRes
        yMinOff = (anchored.yMin - yAnchor) % anchored.yRes
        xMaxOff = (anchored.xMax - xAnchor) % anchored.xRes
        yMaxOff = (anchored.yMax - yAnchor) % anchored.yRes

        # round snapping offset
        if xMinOff > anchored.xRes / 2.: xMinOff -= anchored.xRes
        if yMinOff > anchored.yRes / 2.: yMinOff -= anchored.yRes
        if xMaxOff > anchored.xRes / 2.: xMaxOff -= anchored.xRes
        if yMaxOff > anchored.yRes / 2.: yMaxOff -= anchored.yRes

        anchored.xMin -= xMinOff
        anchored.yMin -= yMinOff
        anchored.xMax -= xMaxOff
        anchored.yMax -= yMaxOff

        return anchored


    def copy(self):
        return self.fromPixelGrid(self)

    def subsetPixelWindow(self, xoff, yoff, width, height):
        xMin = self.xMin + xoff*self.xRes
        xMax = xMin + width*self.xRes
        yMax = self.yMax - yoff*self.yRes
        yMin = yMax - height*self.yRes
        pixelGrid = PixelGrid(projection=self.projection, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax, xRes=self.xRes, yRes=self.yRes)
        return pixelGrid

    def iterSubgrids(self, windowxsize, windowysize):
        ysize, xsize = self.getDimensions()
        yoff = 0
        while yoff < ysize:
            xoff = 0
            while xoff < xsize:
                pixelGridTile = self.subsetPixelWindow(xoff=xoff, yoff=yoff, width=windowxsize, height=windowysize)
                pixelGridTile = pixelGridTile.intersection(self) # ensures that tiles at the left and lower edges are trimmed
                yield pixelGridTile
                xoff += windowxsize
            yoff += windowysize

    def subgrids(self, windowxsize, windowysize):
        return list(self.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize))