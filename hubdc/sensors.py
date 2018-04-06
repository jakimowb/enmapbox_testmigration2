import os
from os.path import join, exists, dirname, basename
import operator
from datetime import datetime as Datetime, timedelta as Timedelta
import yaml
import dask.array as da
import pandas as pd
import numpy as np
from hubdc.core import *
from hubdc.daskmodel import DaskRaster, openDaskRaster


class LandsatCfmask(object):
    _dict = {'CLEAR': 0, 'water': 1, 'shadow_shadow': 2, 'snow': 3, 'cloud': 4, 'fill': 255}
    items = _dict.items
    keys = _dict.keys
    values = _dict.values
    clear, water, cloudShadow, snow, cloud, fill = values()


class LandsatPixelQADaskRaster(DaskRaster):
    '''
    Provides methods for interrogating the Level-2 pixel QA values.
    Inspired by https://github.com/USGS-EROS/espa-l2qa-tools/blob/master/pixel_qa/pixel_qa.py.
    '''

    FILL = 0  # 1
    CLEAR = 1  # 2
    WATER = 2  # 4
    CLOUD_SHADOW = 3  # 8
    SNOW = 4  # 16
    CLOUD = 5  # 32
    CLOUD_CONF1 = 6  # 64
    CLOUD_CONF2 = 7  # 128
    CIRRUS_CONF1 = 8  # 256
    CIRRUS_CONF2 = 9  # 512
    TERRAIN_OCCL = 10  # 1024

    SINGLE_BIT = 0x01  # 00000001
    DOUBLE_BIT = 0x03  # 00000011

    LOW_CONF = 1  # low confidence (01)
    MODERATE_CONF = 2  # moderate confidence (10)
    HIGH_CONF = 3  # high confidence (11)

    def fill(self):
        '''Determines if pixel QA is fill.'''
        return DaskRaster(self >> self.FILL & self.SINGLE_BIT, grid=self.grid())

    def clear(self):
        '''Determines if pixel QA is clear.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.CLEAR & self.SINGLE_BIT, grid=self.grid())

    def water(self):
        '''Determines if pixel QA water.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.WATER & self.SINGLE_BIT, grid=self.grid())

    def cloudShadow(self):
        '''Determines if pixel QA is cloud shadow.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.CLOUD_SHADOW & self.SINGLE_BIT, grid=self.grid())

    def snow(self):
        '''Determines if pixel QA is snow.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.SNOW & self.SINGLE_BIT, grid=self.grid())

    def pixel_qa_is_cloud(self):
        '''Determines if pixel QA is cloud.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.CLOUD & self.SINGLE_BIT, grid=self.grid())

    def cloudConfidence(self):
        '''Returns the cloud confidence value (0-3) for the pixel QA.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.CLOUD_CONF1 & self.DOUBLE_BIT, grid=self.grid())

    def cirrusConfidence(self):
        '''Returns the cirrus confidence value (0-3) for the pixel QA.
         pixel value. These are valid for L8 only.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.CIRRUS_CONF1 & self.DOUBLE_BIT, grid=self.grid())

    def terrainOccluded(self):
        '''Determines if pixel QA is terrain occluded.'''
        assert isinstance(self, DaskRaster)
        return DaskRaster(self >> self.TERRAIN_OCCL & self.SINGLE_BIT, grid=self.grid())

    def cfmask(self):
        '''Returns cfmask from pixel QA.'''
        assert isinstance(self, DaskRaster)
        cfmask = da.full_like(self, fill_value=LandsatCfmask.fill, dtype=np.uint8)
        cfmask[self.clear()] = LandsatCfmask.clear
        cfmask[self.water()] = LandsatCfmask.water
        cfmask[self.snow()] = LandsatCfmask.snow
        cfmask[self.cloudShadow()] = LandsatCfmask.cloudShadow
        return DaskRaster(cfmask, grid=self.grid())


class LandsatDB(object):
    def __init__(self, dataFrame):
        assert isinstance(dataFrame, pd.DataFrame)
        assert 'MTL' in dataFrame
        self._df = dataFrame

    def toHTML(self, filename):
        assert filename.endswith('.html')
        if not exists(dirname(filename)):
            os.makedirs(dirname(filename))
        self._df.to_html(open(filename, 'w'))

    def toPickle(self, filename):
        assert filename.endswith('.pkl')
        if not exists(dirname(filename)):
            os.makedirs(dirname(filename))
        self._df.to_pickle(path=filename)

    @staticmethod
    def fromPickle(filename):
        assert filename.endswith('.pkl')
        df = pd.read_pickle(path=filename)
        return LandsatDB(dataFrame=df)

    @staticmethod
    def fromFolders(folders):
        '''Create database from all Landsat scenes located relativ to one of the source directories.
        Lamdsat scenes are found by searches for *_MTL.txt files.

        :param folders: source directories
        :type folders: list
        :return: data frame with information from MTL files
        :rtype: hubdc.sensors.LandsatDB
        '''
        assert isinstance(folders, list)

        # find all mtl files
        mtlFilenames = list()
        for folder in folders:
            for root, _, filenames in os.walk(folder):
                for f in filenames:
                    if f.endswith('MTL.txt'):
                        mtlFilenames.append(join(root, f))

        # create a data frame for all sources
        dfs = list()
        for filename in mtlFilenames:
            meta = dict()
            meta['MTL'] = filename
            index = [basename(filename.replace('_MTL.txt', ''))]
            with open(filename) as file:
                lines = file.readlines()
            for line in lines:
                line = line.strip()
                drop = False
                for s in ['GROUP', 'END_GROUP', 'QUANTIZE', 'FILE_NAME', 'RADIANCE', 'THERMAL', 'GRID_CELL', 'ORIGIN',
                          'FILE_DATE', 'METADATA_FILE_NAME', 'ORIENTATION', 'OUTPUT_FORMAT', 'REFLECTIVE_']:
                    if line.startswith(s):
                        drop = True
                        break
                if drop: continue
                if line == 'END': break
                split = line.split(' = ')
                if len(split) != 2:
                    assert 0
                key, value = split
                if not key in meta:
                    meta[key] = list()

                if key in ['WRS_PATH', 'WRS_ROW']:
                    castedValue = int(value)  # handle integers with leading zeros (e.g. '023' to 23)
                else:
                    castedValue = yaml.load(value)

                meta[key] = pd.Series([castedValue], index=index)

            dfs.append(pd.DataFrame(meta))

        dataFrame = pd.concat(dfs, axis=0, join='inner')
        return LandsatDB(dataFrame=dataFrame)

    def mtlFilenames(self):
        return list(self._df['MTL'].values)

    def filterSpatialExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        extent = spatialExtent.reproject(targetProjection=Projection.WGS84())

        intersects = list()
        for sceneId, scene in self._df.iterrows():
            intersects.append(extent.intersects(other=Extent(xmin=scene['CORNER_UL_LON_PRODUCT'],
                                                             xmax=scene['CORNER_LR_LON_PRODUCT'],
                                                             ymin=scene['CORNER_LR_LAT_PRODUCT'],
                                                             ymax=scene['CORNER_UL_LAT_PRODUCT'])))

        db = LandsatDB(self._df[pd.Series(data=intersects, index=self._df.index)])
        return db

    # todo try out df.query("X == 1 and Y in ['A','B','C']")

    def filterAttributes(self, *args, **kwargs):
        db = self
        for name, values in kwargs.items():
            if not isinstance(values, (list, tuple)):
                values = [values]

            def ufunc(df):
                results = [self._df[name] == value for value in values]
                result = results[0]
                for res in results:
                    result = result | res
                return result

            db = db.filterFunction(ufunc=ufunc)

        for expression in args:
            ufunc = lambda df: eval('df.{}'.format(expression))
            db = db.filterFunction(ufunc=ufunc)
        return db

    def filterFunction(self, ufunc):
        df = self._df[ufunc(self._df)]
        return LandsatDB(dataFrame=df)

    def extent(self):
        return SpatialExtent(xmin=self._df.CORNER_UL_LON_PRODUCT.min(),
                             xmax=self._df.CORNER_LR_LON_PRODUCT.max(),
                             ymin=self._df.CORNER_LR_LAT_PRODUCT.min(),
                             ymax=self._df.CORNER_UL_LAT_PRODUCT.max(),
                             projection=Projection.WGS84())

    def grid(self, resolution=None):
        if resolution is None:
            resolution = Resolution(x=0.01, y=0.01)
        return Grid(extent=self.extent(), resolution=resolution, projection=Projection.WGS84())

    def timeseries(self, grid=None, xchunk=None, ychunk=None, extensions=['.img', '.tif']):
        if grid is None:
            grid = self.grid()
        return LandsatTimeseries(mtlFilenames=self.mtlFilenames(), grid=grid, xchunk=xchunk, ychunk=ychunk,
                                 extensions=extensions)


class LandsatScene(object):
    def __init__(self, mtlFilename, grid=None, xchunk=None, ychunk=None, extensions=('.img', '.tif')):
        self._filename = mtlFilename[:-7]
        self._folder = dirname(self._filename)
        self._sceneId = basename(self._folder)
        self._grid = grid
        self._xchunk = xchunk
        self._ychunk = ychunk
        self._extensions = extensions
        self._sensor, self._path, self._row, self._date = self._sceneInfos()

    def _findFile(self, name):
        for extension in self._extensions:
            filename = self._filename + name + extension
            if exists(filename):
                return filename
        raise KeyError(
            'file for given extensions {} not found: {}'.format(repr(self._extensions), self._filename + name))

    def _sceneInfos(self):
        if len(self._sceneId) == 21:
            sensor, path, row = self._sceneId[0:3], self._sceneId[3:6], self._sceneId[6:9]
            year, doy = int(self._sceneId[9:13]), int(self._sceneId[13:16])
            date = Datetime(year=year, month=1, day=1) + Timedelta(days=doy - 1)
        elif len(self._sceneId) == 39:
            sensor, path, row = self._sceneId[0:4], self._sceneId[4:7], self._sceneId[7:10]
            sensor = sensor.replace('0', '')
            year, month, day = int(self._sceneId[10:14]), int(self._sceneId[14:16]), int(self._sceneId[16:18])
            date = Datetime(year=year, month=month, day=day)
        else:
            assert 0

        return sensor, path, row, date

    def date(self):
        return self._date

    def raster(self, name, **kwargs):
        filename = self._findFile(name=name)
        raster = openDaskRaster(filename=filename, grid=self._grid,
                                xchunk=self._xchunk, ychunk=self._ychunk,
                                name=os.path.basename(filename)[:-4], **kwargs)
        return raster

    def sr_band(self, i, **kwargs):
        return self.raster(name='sr_band' + str(i), **kwargs)

    def aerosol(self, **kwargs):
        if self._sensor == 'LC8':
            return self.sr_band(1, **kwargs)
        else:
            raise KeyError('{} has no aerosol band'.format(self._sensor))

    def blue(self, **kwargs):
        i = 2 if self._sensor == 'LC8' else 1
        return self.sr_band(i, **kwargs)

    def green(self, **kwargs):
        i = 3 if self._sensor == 'LC8' else 2
        return self.sr_band(i, **kwargs)

    def red(self, **kwargs):
        i = 4 if self._sensor == 'LC8' else 3
        return self.sr_band(i, **kwargs)

    def nir(self, **kwargs):
        i = 5 if self._sensor == 'LC8' else 4
        return self.sr_band(i, **kwargs)

    def swir1(self, **kwargs):
        i = 6 if self._sensor == 'LC8' else 5
        return self.sr_band(i, **kwargs)

    def swir2(self, **kwargs):
        return self.sr_band(7, **kwargs)

    def cfmask(self, **kwargs):
        return self.raster(name='cfmask', **kwargs)


class LandsatTimeseries(object):
    def __init__(self, mtlFilenames, grid, xchunk, ychunk, extensions=('.img', '.tif')):
        assert isinstance(grid, Grid)
        self._scenesByDate = dict()
        self._grid = grid
        for mtlFilename in mtlFilenames:
            scene = LandsatScene(mtlFilename=mtlFilename, grid=grid, xchunk=xchunk, ychunk=ychunk,
                                 extensions=extensions)
            if scene.date() not in self._scenesByDate:
                self._scenesByDate[scene.date()] = list()
            self._scenesByDate[scene.date()].append(scene)

    def grid(self):
        return self._grid

    def stack(self, name, dtype=None, **kwargs):

        def mosaic(arrays, name):
            if name in ['cfmask']:
                agg = da.min
            else:
                agg = da.max
            # todo better use noData for mosaicking!
            result = agg(da.stack(arrays), axis=0)
            return result

        dates = sorted(self._scenesByDate)
        stack = list()
        if hasattr(LandsatScene, name):
            LandsatSceneProduct = getattr(LandsatScene, name)
            getRaster = lambda scene: LandsatSceneProduct(scene, **kwargs)
        else:
            getRaster = lambda scene: LandsatScene.raster(scene, name, **kwargs)

        for date in sorted(self._scenesByDate):
            scenes = self._scenesByDate[date]
            #rasters = [LandsatSceneProduct(scene, **kwargs) for scene in scenes]
            rasters = [getRaster(scene) for scene in scenes]

            stack.append(mosaic(arrays=rasters, name=name))

        stack = da.stack([band[0] for band in stack])
        if dtype is not None:
            stack = stack.astype(dtype=dtype)
        return DaskRaster(daskArray=stack,
                          grid=self.grid(), noDataValue=rasters[0].noDataValue(),
                          metadataDict={'': {'dates': dates}})
