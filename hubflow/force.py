from hubflow.core import *

class ForceDB(FlowObject):
    def __init__(self, folder, spatialFilter=None):
        self._folder = folder
        self._spatialFilter = spatialFilter

    def __getstate__(self):
        return {'folder': self.folder(), 'spatialFilter': self.spatialFilter()}

    def folder(self):
        return self._folder

    def spatialFilter(self):
        assert isinstance(self._spatialFilter, SpatialFilter)
        return self._spatialFilter

    def levelNames(self):
        return [name for name in os.listdir(join(self.folder())) if name.startswith('level')]

    def levels(self, filters=None):
        for levelName in self.levelNames():
            yield self.level(levelName=levelName, filters=filters)

    def level2(self, filters=None):
        return ForceL2(db=self, filters=filters)

    def level(self, levelName, filters=None):
        return ForceLevel(db=self, levelName=levelName, filters=filters)

    def extractAsArray(self, locations, sources):
        assert isinstance(locations, Vector)
        result = OrderedDict()
        result2 = OrderedDict()

        for tileName in self.spatialFilter().tileNames():
            result[tileName] = OrderedDict()
            result2[tileName] = OrderedDict()

        for tileName in self.spatialFilter().tileNames():
            maps = list()
            for source in sources:
                assert isinstance(source, ForceLevel)
                maps.extend(source.tile(name=tileName).collection().rasters())

            maps.append(locations)
            arrays = MapCollection(maps=maps).extractAsArray(masks=[locations])

            for array, raster in zip(arrays[:-1], maps[:-1]):
                assert isinstance(raster, Raster)
                result[tileName][raster.filename()] = array
            result2[tileName][locations.filename()] = arrays[-1]

        return result, result2

    def extractClassificationSample(self, filename, locations, sources):
        assert isinstance(locations, VectorClassification)
        featureArrays, labelArrays = self.extractAsArray(locations=locations, sources=sources)
        features = list()
        labels = list()
        for tileName in featureArrays:
            stack = list()
            for name, array in featureArrays[tileName].items():
                stack.append(array)
            stack = np.concatenate(stack, axis=0)
            features.append(stack)
            labels.append(labelArrays[tileName][locations.filename()])
        features = np.concatenate(features, axis=1)
        labels = np.concatenate(labels, axis=1)
        head, ext = splitext(filename)
        raster = Raster.fromArray(array=np.atleast_3d(features),
                                  filename=join(head, '.raster.bsq'))
        classification = Classification.fromArray(array=np.atleast_3d(labels), classDefinition=locations.classDefinition(),
                                                  filename=join(head, '.classification.bsq'))
        sample = ClassificationSample(raster=raster, classification=classification)
        sample.pickle(filename=filename)
        return sample

    def predict(self, basename, levelName, estimator, sources):
        assert isinstance(estimator, Estimator)

        for tileName in self.spatialFilter().tileNames():
            rasters = list()
            for source in sources:
                assert isinstance(source, ForceLevel)
                rasters.extend(source.tile(name=tileName).collection().rasters())

            rasterStack = RasterStack(rasters=rasters)
            filename = join(self.folder(), levelName, tileName, basename)
            estimator._predict(filename, rasterStack, mask=None)

class ForceLevel(FlowObject):

    def __init__(self, db, levelName, filters=None):
        assert isinstance(db, ForceDB)
        assert isinstance(filters, (type(None), list))

        self._db = db
        self._levelName = levelName
        self._filters = filters
        self._tiles = None # is cached later
        self._tileType = ForceTile


    def __getstate__(self):
        return {'db': self.db(),
                'levelName': self.levelName()}

    def db(self):
        return self._db

    def levelName(self):
        return self._levelName

    def filters(self, forceList=False):
        if self._filters is None and forceList:
            return list()
        return self._filters

    def folder(self):
        return join(self.db().folder(), self.levelName())

    def tiles(self):

        if self._tiles is None: # chache tiles
            self._tiles = list()
            for name in os.listdir(join(self.db().folder(), self.levelName())):
                self._tiles.append(self._makeTile(name))

        for tile in self._tiles:
            assert isinstance(tile, ForceTile)
            yield tile

    def _makeTile(self, name):
        return self._tileType(forceDB=self.db(), levelName=self.levelName(), name=name, filters=self.filters())

    def tile(self, name):

        for tile in self.tiles():
            if tile.name() == name:
                return tile
        raise Exception('tile not found: {}/{}'.format(self.level(), name))


class ForceL2(ForceLevel):

    def __init__(self, db, levelName=None, filters=None):
        ForceLevel.__init__(self, db=db, levelName='level2', filters=filters)
        self._tileType = ForceL2Tile

    def __getstate__(self):
        return {'forceDB': self.db()}

    def mean(self, basename, levelName, dateRangeFilter, sensorFilter):
        for tileName in self.db().spatialFilter().tileNames():
            tile = self.tile(name=tileName)
            assert isinstance(tile, ForceL2Tile)
            tile.mean(filename=join(self.db().folder(), levelName, tile.name(), basename),
                      dateRangeFilter=dateRangeFilter, sensorFilter=sensorFilter)

    def std(self, basename, levelName, dateRangeFilter, sensorFilter):
        for tileName in self.db().spatialFilter().tileNames():
            tile = self.tile(name=tileName)
            assert isinstance(tile, ForceL2Tile)
            tile.std(filename=join(self.db().folder(), levelName, tile.name(), basename),
                     dateRangeFilter=dateRangeFilter, sensorFilter=sensorFilter)


class ForceTile(FlowObject):
    def __init__(self, forceDB, levelName, name, filters=None):
        assert isinstance(forceDB, ForceDB)
        self._forceDB = forceDB
        self._levelName = levelName
        self._name = name
        self._filters = filters
        self._collectionType = ForceCollection

    def __getstate__(self):
        return {'forceDB': self.forceDB(),
                'levelName': self.levelName(),
                'name': self.name()}

    def forceDB(self):
        return self._forceDB

    def levelName(self):
        return self._levelName

    def name(self):
        return self._name

    def filters(self, forceList=False):
        if self._filters is None and forceList:
            return list()
        return self._filters

    def folder(self):
        return join(self.forceDB().folder(), self.levelName(), self.name())

    def collection(self, filters=None):
        if filters is None:
            filters = list()
        return self._collectionType(tile=self, filters=self.filters(forceList=True) + filters)

    def grid(self, filters=None):
        collection = self.collection(filters=filters)
        for raster in collection.rasters():
            return raster.grid()
        raise Exception('no raster in collection: {}'.format(collection))


class ForceL2Tile(ForceTile):

    def __init__(self, forceDB, name, levelName=None, filters=None):
        ForceTile.__init__(self, forceDB=forceDB, levelName='level2', name=name, filters=filters)
        self._collectionType = ForceL2Collection

    def __getstate__(self):
        return {'forceDB': self.forceDB(),
                'name': self.name()}

    def mean(self, filename, dateRangeFilter=None, sensorFilter=None):

        filters = self.filters(forceList=True)

        if dateRangeFilter is not None:
            filters.append(dateRangeFilter)
        if sensorFilter is not None:
            filters.append(sensorFilter)
        boaCollection = self.collection(filters=filters + [ProductFilter(products=['BOA'])])
        cldCollection = self.collection(filters=filters + [ProductFilter(products=['CLD'])])

        boas = list()
        for boaRaster, cldRaster in zip(boaCollection.rasters(), cldCollection.rasters()):
            boa = np.float32(boaRaster.readAsArray())
            cld = cldRaster.readAsArray()
            boa[:, cld[0] < 1] = np.nan
            boas.append(boa)
        assert len(boas) > 0, 'empty tile: {}'.format(self.name())
        array = np.nanmean(boas, axis=0)
        noDataValue = boaRaster.noDataValue()
        array[np.isnan(array)] = noDataValue
        raster = Raster.fromArray(array=array, filename=filename, grid=boaRaster.grid())
        raster.dataset().setNoDataValue(value=noDataValue)
        return raster

    def std(self, filename, dateRangeFilter=None, sensorFilter=None):

        filters = self.filters(forceList=True)

        if dateRangeFilter is not None:
            filters.append(dateRangeFilter)
        if sensorFilter is not None:
            filters.append(sensorFilter)
        boaCollection = self.collection(filters=filters + [ProductFilter(products=['BOA'])])
        cldCollection = self.collection(filters=filters + [ProductFilter(products=['CLD'])])

        boas = list()
        for boaRaster, cldRaster in zip(boaCollection.rasters(), cldCollection.rasters()):
            boa = np.float32(boaRaster.readAsArray())
            cld = cldRaster.readAsArray()
            boa[:, cld[0] < 1] = np.nan
            boas.append(boa)
        assert len(boas) > 0, 'empty tile: {}'.format(self.name())
        array = np.nanstd(boas, axis=0)
        noDataValue = np.finfo(dtype=np.float32).min
        array[np.isnan(array)] = noDataValue
        raster = Raster.fromArray(array=array, filename=filename, grid=boaRaster.grid())
        raster.dataset().setNoDataValue(value=noDataValue)
        return raster


class ForceCollection(FlowObject):

    def __init__(self, tile, filters):
        assert isinstance(tile, ForceTile)
        for filter in filters:
            assert isinstance(filter, Filter), repr(filter)

        self._tile = tile
        self._filters = filters

    def __getstate__(self):
        return {'tile': self.tile(),
                'filters': list(self.filters())}

    def tile(self):
        return self._tile

    def filters(self):
        for filter in self._filters:
            assert isinstance(filter, Filter)
            yield filter

    def rasters(self):
        for name in os.listdir(join(self.tile().folder())):
            raster = Raster(join(self.tile().folder(), name))

            if splitext(raster.filename())[1] in ['.hdr', '.xml']:
                continue

            valid = True
            for filter in self.filters():
                if not filter.evaluate(raster=raster):
                    valid = False
                    break


            if not valid:
                continue

            yield raster


class ForceL2Collection(ForceCollection):
    pass



class Filter(FlowObject):

    def evaluate(self, raster):
        assert isinstance(raster, Raster)
        return True


class DateRangeFilter(Filter):

    def __init__(self, start, end):
        self._start = start
        self._end = end

    def __getstate__(self):
        return {'start': self.start(),
                'end': self.end()}

    def start(self):
        return self._start

    def end(self):
        return self._end

    def evaluate(self, raster):
        assert isinstance(raster, Raster)
        date, level, sensor, product = splitext(basename(raster.filename()))[0].split('_')
        return date >= self.start() and date <= self.end()


class ProductFilter(Filter):
    def __init__(self, products):
        self._products = products

    def __getstate__(self):
        return {'products': self.products()}

    def products(self):
        return self._products

    def evaluate(self, raster):
        assert isinstance(raster, Raster)
        date, level, sensor, product = splitext(basename(raster.filename()))[0].split('_')
        return product in self.products()


class SensorFilter(Filter):
    def __init__(self, sensors):
        self._sensors = sensors

    def __getstate__(self):
        return {'sensors': self.sensors()}

    def sensors(self):
        return self._sensors

    def evaluate(self, raster):
        assert isinstance(raster, Raster)
        date, level, sensor, product = splitext(basename(raster.filename()))[0].split('_')
        return sensor in self.sensors()


class SpatialFilter(FlowObject):

    def __init__(self, tileNames):
        self._tileNames = tileNames

    def __getstate__(self):
        return {'tileNames': self._tileNames}

    def tileNames(self):
        return self._tileNames

    def evaluate(self, tileName):
        return tileName in self.tileNames()


class FileFilter(Filter):

    def __init__(self, basenames=None, extensions=None):
        self._basenames = basenames
        self._extensions = extensions

    def __getstate__(self):
        return {'basenames': self._basenames, 'extensions': self._extensions}

    def evaluate(self, raster):
        assert isinstance(raster, Raster)
        valid = True
        if self._basenames is not None:
            valid &= splitext(basename(raster.filename()))[0] in self._basenames
        if self._extensions is not None:
            valid &= splitext(raster.filename())[1] in self._extensions
        return valid
