from osgeo import gdal, osr, ogr
from multiprocessing.pool import ThreadPool
from applier import (Applier, ApplierControls, ApplierOperator, ApplierInputRaster, ApplierOutputRaster,
                     ApplierInputRasterGroup, ApplierOutputRasterGroup, ApplierInputRasterArchive, PixelGrid)

tilingSchemeShp = r'C:\Work\data\applier_ts\tiling_scheme.shp'

class TSApplierTilingScheme(object):

    @classmethod
    def fromShapefile(cls, filename, regionOfInterest):
        applierTilingScheme = TSApplierTilingScheme()
        ds = ogr.Open(filename)
        layer = ds.GetLayer()
        layerProjection = layer.GetSpatialRef() #.Clone()

        # set spatial filter
        transform = osr.CoordinateTransformation(regionOfInterest.projection, layerProjection)
        roiGeometry = regionOfInterest.geometry.Clone()
        roiGeometry.Transform(transform)
        layer.SetSpatialFilter(roiGeometry)

        for feature in layer:
            gridProjection = osr.SpatialReference()
            gridProjection.ImportFromEPSG(int(feature.GetField('epsg')))
            tileGeometry = feature.GetGeometryRef().Clone()
            tile = TSApplierTile(name=feature.GetField('name'),
                               tileGeometry=tileGeometry,
                               tileProjection=layerProjection,
                               gridProjection=gridProjection)
            tile = tile.intersectWithRegionOfInterest(regionOfInterest=regionOfInterest)
            applierTilingScheme.addTile(tile=tile)
        return applierTilingScheme

    def __init__(self):
        self.tiles = list()

    def __iter__(self):
        for tile in self.tiles:
            assert isinstance(tile, TSApplierTile)
            yield tile

    def addTile(self, tile):
        assert isinstance(tile, TSApplierTile)
        self.tiles.append(tile)

class TSApplierTile(object):

    def __init__(self, name, tileGeometry, tileProjection, gridProjection):
        assert isinstance(tileGeometry, ogr.Geometry)
        assert isinstance(tileProjection, osr.SpatialReference)
        assert isinstance(gridProjection, osr.SpatialReference)
        self.name = name
        self.tileGeometry = tileGeometry
        self.tileProjection = tileProjection
        self.gridProjection = gridProjection

    def intersectWithRegionOfInterest(self, regionOfInterest):
        assert isinstance(regionOfInterest, TSApplierRegionOfInterest)
        transform = osr.CoordinateTransformation(regionOfInterest.projection, self.tileProjection)
        roiGeometry = regionOfInterest.geometry.Clone()
        roiGeometry.Transform(transform)
        tileGeometry = self.tileGeometry.Intersection(roiGeometry)
        return TSApplierTile(self.name, tileGeometry=tileGeometry, tileProjection=self.tileProjection, gridProjection=self.gridProjection)

    def makePixelGrid(self, gridResolution, gridAnchor, gridBuffer):
        # transform tile into target projection
        transform = osr.CoordinateTransformation(self.tileProjection, self.gridProjection)
        tileGeometry = self.tileGeometry.Clone()
        tileGeometry.Transform(transform)

        bb = tileGeometry.GetEnvelope()
        xrange, yrange = bb[:2], bb[2:]
        grid = PixelGrid(projection=str(self.gridProjection),
                                 xMin=min(xrange), xMax=max(xrange),
                                 yMin=min(yrange), yMax=max(yrange),
                                 xRes=gridResolution, yRes=gridResolution)
        grid = grid.pixelBuffer(buffer=gridBuffer)
        grid = grid.anchor(xAnchor=gridAnchor[0], yAnchor=gridAnchor[1])
        return grid

class TSApplierRegionOfInterest(object):

    @classmethod
    def fromShapefile(cls, filename):
        ds = ogr.Open(filename)
        layer = ds.GetLayer()
        projection = layer.GetSpatialRef()
        geometry = ogr.Geometry(ogr.wkbMultiPolygon)
        for feature in layer:
            geometry.AddGeometry(feature.GetGeometryRef())
        geometry = geometry.UnionCascaded()
        return TSApplierRegionOfInterest(geometry=geometry, projection=projection)

    def __init__(self, geometry, projection):
        assert isinstance(geometry, ogr.Geometry)
        assert isinstance(projection, osr.SpatialReference)
        self.geometry = geometry
        self.projection = projection

class TSApplierOutputRaster(ApplierOutputRaster):

    def __init__(self, filename):
        ApplierOutputRaster.__init__(self, filename=filename)
        self.tilename = ''

    @property
    def filename(self):
        return self._filename.format(tilename=self.tilename)

class TSApplier(object):

    def __init__(self, tilingScheme):
        assert isinstance(tilingScheme, TSApplierTilingScheme)

        self.tilingScheme = tilingScheme
        self.inputRaster = ApplierInputRasterGroup()
        self._inputRasterArchive = dict()
        self.outputRaster = ApplierOutputRasterGroup()
        self.controls = TSApplierControls()

    def setInputRasterArchive(self, key, value):
        self._inputRasterArchive[key] = value

    def apply(self, operator, *ufuncArgs, **ufuncKwargs):

        print('start TilingScheme Applier')

        if self.controls.nworkerAcross > 0:
            pool = ThreadPool(processes=self.controls.nworkerAcross)

        def applyTile(args):
            i, tile = args
            import copy
            self_controls = copy.deepcopy(self.controls)
            self__inputRasterArchive = self._inputRasterArchive
            self_outputRaster = copy.deepcopy(self.outputRaster)

            tileApplier = Applier(controls=self_controls)
            pixelGrid = tile.makePixelGrid(gridResolution=30, gridAnchor=(15,15), gridBuffer=1)
            tileApplier.controls.setReferenceGrid(grid=pixelGrid)
            for k, v in self__inputRasterArchive.items():
                group = v.getIntersectionByPixelGrid(grid=pixelGrid)
                tileApplier.inputRaster.setGroup(key=k, value=group)
            tileApplier.outputRaster = self_outputRaster
            for outputRaster in tileApplier.outputRaster.getFlatRasters():
                outputRaster.tilename = tile.name
            return tileApplier.apply(operator=operator,
                                     description='Tile {i}/{n} ({name})'.format(i=i+1, n=len(self.tilingScheme.tiles), name=tile.name),
                                     overwrite=True, *ufuncArgs, **ufuncKwargs)

        argss = [(i, tile) for i, tile in enumerate(self.tilingScheme)]
        if self.controls.nworkerAcross is None:
            tileResults = list()
            for args in argss:
                tileResults.append(applyTile(args=args))
        else:
            pool.map_async(func=applyTile, iterable=argss)

            pool.close()
            pool.join()

        self.controls.progressBar.setLabelText('done TilingScheme Applier')

class TSApplierControls(ApplierControls):

    def setNumThreads(self, nworkerAcrossTiles=None, nworkerWithinTiles=None):
        if nworkerAcrossTiles is not None and nworkerWithinTiles is None:
            nworkerWithinTiles = 1
        ApplierControls.setNumThreads(self, nworker=nworkerWithinTiles)
        self.nworkerAcross = nworkerAcrossTiles
