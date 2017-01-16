from __future__ import division, print_function
from os import listdir, chdir
from os.path import join, basename, dirname, exists, getctime
from shutil import copy
from collections import OrderedDict
import ogr, osr, gdal

from enmapbox.processing.types import PixelGrid, PixelGridDefn, pixelGridFromFile
from hub.datetime import Date, DateRange

from hub.file import saveJSON, restoreJSON
from hub.gdal.util import stack_images, stack_bands, gdalwarp, gdal_translate
from hub.gdal.api import GDALMeta
from hub.file import filesearch
import hub.rs.virtual
import hub.envi
import rios.applier
import numpy

from enmapbox.processing.applier import ApplierHelper
from hub.timing import tic, toc
from multiprocessing.pool import ThreadPool
import subprocess

LANDSAT_ANCHOR = (15,15)
SENTINEL_ANCHOR = (0,0)

def createMGRSFootprintUTMLookup(shapedir, outfile):

    lookup = OrderedDict()
    for basename in listdir(shapedir):
        shapefile = join(shapedir, basename, basename+'.shp')
        print(shapefile)
        dataSource = ogr.Open(shapefile)
        layer = dataSource.GetLayer(0)
        for feature in layer:
            try:
                geom = feature.geometry()
                env = geom.GetEnvelope()
                info = {key : int(round(value)) for key, value in zip(['xMin', 'yMin', 'xMax', 'yMax'], (env[0], env[2], env[1], env[3]))}
                info['name'] = feature.GetField('MGRS')
                info['folders'] = [info['name'][:3], info['name'][3:]]
                info['epsg'] = '326'+info['name'][0:2]
                lookup[info['name']] = info
            except ValueError:
                print('-> shapefile is invalid!')
                break
    saveJSON(file=outfile, var=lookup)

def createMGRSFootprintLEALookup(shapefile, outfile):

    lookup = OrderedDict()
    print(shapefile)
    dataSource = ogr.Open(shapefile)
    layer = dataSource.GetLayer(0)
    for feature in layer:
        geom = feature.geometry()
        env = geom.GetEnvelope()
        info = {key: int(round(value)) for key, value in
                zip(['xMin', 'yMin', 'xMax', 'yMax'], (env[0], env[2], env[1], env[3]))}
        info['name'] = feature.GetField('GRID1MIL')+feature.GetField('GRID100K')
        info['folders'] = [info['name'][:3], info['name'][3:]]
        info['epsg'] = '3035'
        lookup[info['name']] = info
    saveJSON(file=outfile, var=lookup)

def createMGRSFootprintWRS2FilterLookup(shapefile, outfile):

    lookup = OrderedDict()
    print(shapefile)
    dataSource = ogr.Open(shapefile)
    layer = dataSource.GetLayer(0)

    for feature in layer:
        wrs2 = str(int(feature.GetField('WRSPR')))
        mgrs = feature.GetField('GRID1MIL') + feature.GetField('GRID100K')
        if not wrs2 in lookup: lookup[wrs2] = list()
        lookup[wrs2].append(mgrs)

    saveJSON(file=outfile, var=lookup)

def findFilename(filenameWithoutExtension, extensions, mustExist=True):
    for extention in extensions:
        if exists(filenameWithoutExtension+extention):
            return filenameWithoutExtension+extention

    if mustExist:
        raise Exception('file not found: '+filenameWithoutExtension)
    else:
        return None

class LandsatSceneNative():

    EXTENSIONS = ['.tif','.img']
    SR_BANDNAMES = None
    SR_BASENAMES = None
    SR_WAVELENGTH_LOWER = None
    SR_WAVELENGTH_UPPER = None
    SR_NODATAVALUE = None
    TOA_BANDNAMES = None
    TOA_BASENAMES = None
    TOA_WAVELENGTH_LOWER = None
    TOA_WAVELENGTH_UPPER = None
    TOA_NODATAVALUE = None
    QA_BASENAMES  = None
    QA_BANDNAMES = None
    SENSOR = None

    def __init__(self, folder):
        self.folder = folder
        #self.dirname = dirname(folder)
        self.sceneId = basename(folder)
        self.wrs2FootprintName = self.sceneId[3:9]
        self.mtl_filename = join(self.folder, self.sceneId + '_MTL.txt')
        self.espa_filename = join(self.folder, self.sceneId + '.xml')

        self.sr_filenames = list()
        for sr_basename in self.SR_BASENAMES:
            self.sr_filenames.append(findFilename(join(self.folder, self.sceneId + '_' + sr_basename), self.EXTENSIONS))

        self.toa_filenames = list()
        for toa_basename in self.TOA_BASENAMES:
            self.toa_filenames.append(findFilename(join(self.folder, self.sceneId + '_' + toa_basename), self.EXTENSIONS))

        self.qa_filenames = list()
        for qa_basename in self.QA_BASENAMES:
            self.qa_filenames.append(findFilename(join(self.folder, self.sceneId + '_' + qa_basename), self.EXTENSIONS))

    def asLandsatScene(self, dirname):

        print(self.sceneId+' as LandsatScene')
        folder = join(dirname, self.sceneId)

        with open(self.mtl_filename) as f:
            for line in f:
                if line.strip().startswith('FILE_DATE'):
                    processingTime = line.split('=')[1].strip()
                    break

        # sr stack
        outfile = join(folder, self.sceneId+'_sr.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=self.sr_filenames)
            meta = GDALMeta(outfile)
            meta.setBandNames(self.SR_BANDNAMES)
            meta.setNoDataValue(self.SR_NODATAVALUE)
            meta.setAcquisitionDate(Date.fromLandsatSceneID(self.sceneId))
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', self.SENSOR)
            meta.setMetadataItem('wavelength', [int((u+l)/2) for u, l in zip(self.SR_WAVELENGTH_UPPER, self.SR_WAVELENGTH_LOWER)])
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.setMetadataItem('processing time', processingTime)
            meta.writeMeta()

        # toabt stack
        outfile = join(folder, self.sceneId + '_toabt.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=self.toa_filenames)
            meta = GDALMeta(outfile)
            meta.setBandNames(self.TOA_BANDNAMES)
            meta.setNoDataValue(self.TOA_NODATAVALUE)
            meta.setAcquisitionDate(Date.fromLandsatSceneID(self.sceneId))
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', self.SENSOR)
            meta.setMetadataItem('wavelength', [int((u + l) / 2) for u, l in zip(self.TOA_WAVELENGTH_UPPER, self.TOA_WAVELENGTH_LOWER)])
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.setMetadataItem('processing time', processingTime)
            meta.writeMeta()

        # qa stack
        outfile = join(folder, self.sceneId + '_qa.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=self.qa_filenames)
            meta = GDALMeta(outfile)
            meta.setBandNames(self.QA_BANDNAMES)
            meta.setAcquisitionDate(Date.fromLandsatSceneID(self.sceneId))
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('processing time', processingTime)
            meta.writeMeta()

        # meta files
        copy(self.mtl_filename, folder)
        copy(self.espa_filename, folder)

        return LandsatScene(folder)

    def importIntoDataCube(self, dirname, footprints, resolution, buffer, anchor, tmpsuffix='_tmp'):

        assert isinstance(footprints, MGRSFootprintCollection)
        assert isinstance(resolution, int)
        assert isinstance(buffer, int)

        tmpdirname = join(dirname + tmpsuffix)
        landsatScene = self.asLandsatScene(dirname=join(tmpdirname, '1_landsatWRS2_stacked', self.wrs2FootprintName[3], self.wrs2FootprintName[3:]))
        for footprint in landsatScene.getOverlappingMGRSFootprints():
            if footprint in footprints:
                landsatTile = landsatScene.cutMGRSFootprint(dirname=join(tmpdirname, '2_landsatMGRS_cutted', *footprint.subfolders),
                                              footprint=footprint, buffer=buffer)
                spectralTile = landsatTile.resample(dirname=join(dirname, *footprint.subfolders), resolution=resolution, buffer=buffer, anchor=anchor)


class LT4SceneNative(LandsatSceneNative):

    SR_BANDNAMES = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    SR_BASENAMES = ['sr_band' + str(i) for i in [1, 2, 3, 4, 5, 7]]
    SR_WAVELENGTH_LOWER = [450, 520, 630, 760, 1550, 2080]
    SR_WAVELENGTH_UPPER = [520, 600, 690, 900, 1750, 2350]
    SR_NODATAVALUE = -9999
    TOA_BANDNAMES = ['tir']
    TOA_BASENAMES = ['toa_band6']
    TOA_WAVELENGTH_LOWER = [10400]
    TOA_WAVELENGTH_UPPER = [12500]
    TOA_NODATAVALUE = -9999
    QA_BASENAMES  = ['cfmask', 'cfmask_conf', 'sr_adjacent_cloud_qa', 'sr_atmos_opacity', 'sr_cloud_qa',
                     'sr_cloud_shadow_qa', 'sr_ddv_qa', 'sr_fill_qa', 'sr_land_water_qa', 'sr_snow_qa', 'toa_band6_qa']
    QA_BANDNAMES = QA_BASENAMES
    SENSOR = 'TM'

class LT5SceneNative(LT4SceneNative):

    QA_BASENAMES = LT4SceneNative.QA_BASENAMES + ['toa_qa']
    QA_BANDNAMES = QA_BASENAMES

class LE7SceneNative(LandsatSceneNative):

    SR_BANDNAMES = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    SR_BASENAMES = ['sr_band' + str(i) for i in [1, 2, 3, 4, 5, 7]]
    SR_WAVELENGTH_LOWER = [450, 520, 630, 770, 1550, 2090]
    SR_WAVELENGTH_UPPER = [520, 600, 690, 900, 1750, 2350]
    SR_NODATAVALUE = -9999
    TOA_BANDNAMES = ['tir1']
    TOA_BASENAMES = ['toa_band6']
    TOA_WAVELENGTH_LOWER = [10400]
    TOA_WAVELENGTH_UPPER = [12500]
    TOA_NODATAVALUE = -9999
    QA_BASENAMES  = ['cfmask', 'cfmask_conf', 'sr_adjacent_cloud_qa', 'sr_atmos_opacity', 'sr_cloud_qa',
                     'sr_cloud_shadow_qa', 'sr_ddv_qa', 'sr_fill_qa', 'sr_land_water_qa', 'sr_snow_qa', 'toa_band6_qa', 'toa_qa']
    QA_BANDNAMES = QA_BASENAMES
    SENSOR = 'ETM'

class LC8SceneNative(LandsatSceneNative):

    SR_BANDNAMES = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    SR_BASENAMES = ['sr_band' + str(i) for i in [1, 2, 3, 4, 5, 6, 7]]
    SR_WAVELENGTH_LOWER = [430, 450, 530, 640, 850, 1570, 2110]
    SR_WAVELENGTH_UPPER = [450, 510, 590, 670, 880, 1600, 2290]
    SR_NODATAVALUE = -9999
    TOA_BANDNAMES = ['tir1', 'tir2']
    TOA_BASENAMES = ['toa_band10', 'toa_band11']
    TOA_WAVELENGTH_LOWER = [10600, 11500]
    TOA_WAVELENGTH_UPPER = [11190, 12510]
    TOA_NODATAVALUE = -9999
    QA_BASENAMES  = ['cfmask', 'cfmask_conf']
    SENSOR = 'OLI_TIRS'

def landsatSceneNative(folder):

    # factory for landsat scenes
    # LXSPPPRRRYYYYDDDGSIVV
    # L = Landsat
    # X = Sensor
    # S = Satellite
    # PPP = WRS path
    # RRR = WRS row
    # YYYY = Year
    # DDD = Julian day of year
    # GSI = Ground station identifier
    # VV = Archive version number

    sceneId = basename(folder)
    for key, landsatType in [('LC8', LC8SceneNative), ('LE7', LE7SceneNative), ('LT5', LT5SceneNative), ('LT4', LT4SceneNative)]:
        if sceneId.startswith(key):
            scene = landsatType(folder)
            assert isinstance(scene, LandsatSceneNative)
            return scene

    raise Exception('unknown landsat product')

class LandsatScene():

    MGRS_BY_WRS2_LOOKUP = None
    EXTENSIONS = ['.tif','.img','.vrt']

    @staticmethod
    def loadLookup(filename):
        LandsatScene.MGRS_BY_WRS2_LOOKUP = restoreJSON(filename)

    def __init__(self, folder):
        self.folder = folder
        self.dirname = dirname(folder)
        self.sceneId = basename(folder)
        self.wrs2FootprintName = self.sceneId[3:9]
        self.sr_filename = findFilename(join(self.folder, self.sceneId + '_sr'), self.EXTENSIONS)
        self.toabt_filename = findFilename(join(self.folder, self.sceneId + '_toabt'), self.EXTENSIONS)
        self.qa_filename = findFilename(join(self.folder, self.sceneId + '_qa'), self.EXTENSIONS)
        self.mtl_filename = join(self.folder, self.sceneId + '_MTL.txt')
        self.espa_filename = join(self.folder, self.sceneId + '.xml')

    def getOverlappingMGRSFootprints(self):

        mgrsFootprintNames = LandsatScene.MGRS_BY_WRS2_LOOKUP[self.wrs2FootprintName]
        return MGRSFootprintCollection(names=mgrsFootprintNames)

    def cutMGRSFootprint(self, dirname, footprint, buffer):

        assert isinstance(footprint, MGRSFootprint)
        print(self.sceneId+' cut '+footprint.name)
        pixelGrid = footprint.getPixelGridLandsat30m(buffer=buffer)
        folder = join(dirname, self.sceneId)

        if not exists(folder):
            options  = '-overwrite -of VRT -ot Int16 -r near'
            options += ' -te '+ str(pixelGrid.xMin) + ' ' + str(pixelGrid.yMin) + ' ' + str(pixelGrid.xMax) + ' ' + str(pixelGrid.yMax)
            options += ' -tr '+ str(pixelGrid.xRes) + ' ' + str(pixelGrid.yRes)
            options += ' -t_srs '+pixelGrid.projection
            for infile in [self.sr_filename, self.toabt_filename, self.qa_filename]:
                outfile = join(folder, basename(infile))[:-4]+'.vrt'
                gdalwarp(outfile=outfile, infile=infile, options=options, verbose=True)
                GDALMeta(outfile).copyMetadata(GDALMeta(infile)).writeMeta()

            copy(self.mtl_filename, folder)
            copy(self.espa_filename, folder)

        return LandsatTile(folder=folder, footprint=footprint)

class SpectralTileMultiResolution():

    def __init__(self, folder, footprint, resolutions):

        self.folder = folder
        self.sceneId = basename(folder)
        self.footprint = footprint
        self.resolutions = resolutions
        self.spectralTiles = {resolution:SpectralTile(folder=folder, footprint=footprint, resolution=resolution) for resolution in resolutions}

    def resample(self, dirname, resolution, buffer, anchor, ot='Int16', r_sr='average', r_qa='near', bufferTwoSided=False):

        for spectralTile in self.spectralTiles.values():
            assert isinstance(spectralTile, SpectralTile)
            spectralTile.resample(dirname=dirname, resolution=resolution, buffer=buffer, anchor=anchor,
                                  ot=ot, r_sr=r_sr, r_qa=r_qa, overwriteFolder=True, overwriteFiles=False, bufferTwoSided=bufferTwoSided)

        return SpectralTileMultiResolution(folder=join(dirname, self.sceneId), footprint=self.footprint, resolutions=self.resolutions)

    def stack(self, dirname, sr_bandnames, qa_bandnames):
        print(self.sceneId+'('+self.footprint.name+') stack multi-resolutions')
        folder = join(dirname, self.sceneId)

        # sr stack
        infiles = list()
        inbands = list()
        outfile = join(folder, self.sceneId+'_sr.vrt')
        if not exists(outfile):
            wavelength = list()
            for resolution, bandname in sr_bandnames:
                spectralTile = self.spectralTiles[resolution]
                infiles.append(spectralTile.sr_filename)
                bandindex = spectralTile.getSRBandByName(bandname)
                bandnumber = bandindex+1
                inbands.append(bandnumber)
                meta = spectralTile.getSRMeta()
                acquisitionDate = meta.getAcquisitionDate()
                processingDate =  meta.getMetadataItem('processing time')
                sensor = meta.getMetadataItem('sensor')
                wavelength.append(meta.getMetadataItem('wavelength')[bandindex])

            options = ''
            stack_bands(outfile, infiles=infiles, inbands=inbands, options=options)

            meta = GDALMeta(outfile)
            meta.setBandNames([bandname for resolution, bandname in sr_bandnames])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('processing time', processingDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', sensor)
            meta.setMetadataItem('wavelength', wavelength)
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.writeMeta()

        # qa stack
        infiles = list()
        inbands = list()
        outfile = join(folder, self.sceneId + '_qa.vrt')
        if not exists(outfile):
            for resolution, bandname in qa_bandnames:
                spectralTile = self.spectralTiles[resolution]
                infiles.append(spectralTile.qa_filename)
                bandnumber = spectralTile.getQABandByName(bandname)+1
                inbands.append(bandnumber)
            options = ''
            stack_bands(outfile, infiles=infiles, inbands=inbands, options=options)
            meta = GDALMeta(outfile)
            meta.setBandNames([bandname for resolution, bandname in qa_bandnames])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.writeMeta()

        return SpectralTile(folder=folder, footprint=self.footprint)

class SpectralTile():

    EXTENSIONS = ['.tif', '.vrt']

    def __init__(self, folder, footprint, resolution=None):
        assert isinstance(footprint, MGRSFootprint)
        self.footprint = footprint
        self.folder = folder
        self.resolution = resolution
        self.dirname = dirname(folder)
        self.sceneId = basename(folder)
        resolution_ = str(resolution)+'m' if resolution is not None else ''
        self.sr_filename = findFilename(join(self.folder, self.sceneId + '_sr'+resolution_), self.EXTENSIONS)
        self.qa_filename = findFilename(join(self.folder, self.sceneId + '_qa'+resolution_), self.EXTENSIONS)
        self.sr_meta = None
        self.qa_meta = None

    def getSRMeta(self):

        if self.sr_meta is None: self.sr_meta = GDALMeta(self.sr_filename)
        return self.sr_meta

    def getQAMeta(self):

        if self.qa_meta is None: self.qa_meta = GDALMeta(self.qa_filename)
        return self.qa_meta

    def getSRBandByName(self, bandname):
        bandnames = self.getSRMeta().getMetadataItem('band names')
        bandindex = bandnames.index(bandname)
        return bandindex

    def getQABandByName(self, bandname):
        bandnames = self.getQAMeta().getMetadataItem('band names')
        bandindex = bandnames.index(bandname)
        return bandindex

    def resample(self, dirname, resolution, buffer, anchor, ot, r_sr, r_qa, overwriteFolder=False, overwriteFiles=False, bufferTwoSided=False):

        print(self.sceneId+'('+self.footprint.name+') resample to resolution='+str(resolution)+', anchor='+str(anchor))
        folder = join(dirname, self.sceneId)
        pixelGrid = self.footprint.getPixelGrid(resolution=resolution, buffer=buffer, north=not bufferTwoSided, west=not bufferTwoSided, anchor=anchor)

        if overwriteFolder or not exists(folder):
            for infile, r in zip([self.sr_filename, self.qa_filename], [r_sr,r_qa]):
                outfile = join(folder, basename(infile))[:-4]+'.vrt'
                if overwriteFiles or not exists(outfile):
                    options  = '-of VRT -ot '+ot+' -r '+r
                    options += ' -projwin '+ str(pixelGrid.xMin) + ' ' + str(max(pixelGrid.yMin,pixelGrid.yMax)) + ' ' + str(pixelGrid.xMax) + ' ' + str(min(pixelGrid.yMin,pixelGrid.yMax))
                    options += ' -tr '+ str(pixelGrid.xRes) + ' ' + str(pixelGrid.yRes)
                    gdal_translate(outfile=outfile, infile=infile, options=options, verbose=True)
                    GDALMeta(outfile).copyMetadata(GDALMeta(infile)).writeMeta()

        return SpectralTile(folder=folder, footprint=self.footprint, resolution=self.resolution)

    def saveAsGTiff(self, dirname=None, compress='LZW', interleave='BAND', predictor='2',
                    tiled='YES', blockxsize=256, blockysize=256):

        print(self.sceneId+'('+self.footprint.name+') save as GTiff')

        if dirname is None: dirname = self.dirname
        folder = join(dirname, self.sceneId)

        options = '-co "TILED='+tiled+'" -co "BLOCKXSIZE='+str(blockxsize)+'" -co "BLOCKYSIZE='+str(blockysize)+'" -co "PROFILE=GeoTIFF" '
        options += '-co "COMPRESS=' + compress + '" -co "PREDICTOR=' + predictor + '" -co "INTERLEAVE=' + interleave + '" '

        for infile in [self.sr_filename, self.qa_filename]:
            outfile = join(folder, basename(infile))[:-4]+'.tif'
            if not exists(outfile):
                hub.gdal.util.gdal_translate(outfile=outfile, infile=infile, options=options)
                inmeta = GDALMeta(infile)
                outmeta = GDALMeta(outfile)
                outmeta.copyMetadata(inmeta).writeMeta()

class LandsatTile(SpectralTile):

    def __init__(self, folder, footprint):
        SpectralTile.__init__(folder=folder, footprint=footprint)
        self.wrs2FootprintName = self.sceneId[3:9]
        self.toabt_filename = findFilename(join(self.folder, self.sceneId + '_toabt'), self.EXTENSIONS)
        self.mtl_filename = join(self.folder, self.sceneId + '_MTL.txt')
        self.espa_filename = join(self.folder, self.sceneId + '.xml')

class SentinelSceneNative():

    SENSOR = 'MSI'

    def __init__(self, l1c_folder, l2a_folder):
        self.l1c_folder = l1c_folder
        self.folder = l2a_folder
        self.sceneId = basename(self.folder)
        self.filenames = filesearch(self.folder, '*.jp2')

    def repairSRS(self):

        # grab all pixel grids from L1C files
        pixelGridByFootprintAndResolution = dict()
        for resolution, pattern in zip([10,20,60], ['*B02.jp2','*B05.jp2','*B01.jp2']):
            filenames = filesearch(self.l1c_folder, pattern)
            for f in filenames:
                footprintName = f[-13:-8]
                pixelGridByFootprintAndResolution[footprintName, resolution] = PixelGrid(pixelGridFromFile(f))

        # set srs for all L2A files
        # - need to use additional vrt files, because the srs of the JP2 files can not be modified
        for fn in self.filenames:
            outfile = fn.replace('.jp2', '.vrt')
            if exists(outfile):
                continue
            bn = basename(fn)
            if bn.startswith('S2A_OPER_PVI_L1C'):
                continue
            elif bn.startswith('S2A_USER_MSI'):
                footprintName = fn[-17:-12]
            else:
                footprintName = fn[-13:-8]
            resolution = int(fn[-7:-5])

            pixelGrid = pixelGridByFootprintAndResolution[footprintName, resolution]

            options = '-of VRT'
            if not exists(basename(outfile)):
                # there seams to be a problem with the length of the  S2 filenames
                # exists() return False even when the VRTs already exist
                # when deleting the VRTs, all is ok

                #gdal_translate(outfile=outfile, infile=fn, options=options)
                gdal_translate(outfile=basename(outfile), infile=basename(fn), options=options)

                ds = gdal.Open(outfile, gdal.GA_Update)
                ds.SetProjection(pixelGrid.projection)
                ds.SetGeoTransform(pixelGrid.makeGeoTransform())
                ds = None

    def getOverlappingMGRSFootprints(self):
        
        for filename in self.filenames:
            if basename(filename).startswith('S2A_OPER_PVI_L1C'):
                yield MGRSFootprint(name=filename[-9:-4])

    def yieldTiles(self):
        for footprint in self.getOverlappingMGRSFootprints():
            yield SentinelTileNative(folder=self.folder, footprint=footprint)

    def importIntoDataCube(self, dirname, footprints, resolution, buffer, anchor, resampling='average', tmpsuffix='_tmp',
                           bufferTwoSided=False, saveAsGTiff=False):

        assert isinstance(footprints, MGRSFootprintCollection)
        assert isinstance(resolution, int)
        assert isinstance(buffer, int)

        tmpdirname = join(dirname+tmpsuffix)
        for sceneTileNative in self.yieldTiles():
            footprint = sceneTileNative.footprint
            if footprint in footprints:
                sentinelTile = sceneTileNative.asSentinelTileMultiResolution(dirname=join(tmpdirname, '1_sentinelNative_stacked', *footprint.subfolders),
                                                        l1c_folder=self.l1c_folder)

                sentinelTile = sentinelTile.cutMGRSFootprint(join(tmpdirname, '2_sentinelMGRS_multires', *footprint.subfolders),
                                               footprint=footprint, buffer=buffer, bufferTwoSided=bufferTwoSided)

                spectralTileMultiResolution = sentinelTile.asSpectralTileMultiResolution()
                spectralTileMultiResolution = spectralTileMultiResolution.resample(dirname=join(tmpdirname, '3_sentinelMGRS_resampled_'+str(resolution)+'m', *footprint.subfolders),
                                                                                   resolution=resolution, buffer=buffer, anchor=anchor,
                                                                                   r_sr=resampling, bufferTwoSided=bufferTwoSided)

                sr_bandnames = [(10, 'blue'), (10, 'green'), (10, 'red'),
                                (20, 'rededge1'), (20, 'rededge2'), (20, 'rededge3'),
                                (10, 'nir'),
                                (20, 'swir1'), (20, 'swir2')]
                qa_bandnames = [(10, 'AOT'), (10, 'WVP'),
                                (20, 'CLD'), (20, 'SCL'), (20, 'SNW')]

                spectralTile = spectralTileMultiResolution.stack(dirname=join(dirname, *footprint.subfolders), sr_bandnames=sr_bandnames, qa_bandnames=qa_bandnames)

                if saveAsGTiff:
                    spectralTile.saveAsGTiff()

class SentinelTileNative():

    SENSOR = SentinelSceneNative.SENSOR

    def __init__(self, folder, footprint):
        assert isinstance(footprint, MGRSFootprint)
        self.folder = folder
        self.sceneId = basename(folder)
        self.filenames = filesearch(self.folder, '*'+footprint.name+'*.jp2')
        self.footprint = footprint

    def asSentinelTileMultiResolution(self, dirname, l1c_folder):
        print(self.sceneId+'('+self.footprint.name+') stack JP2 files')
        folder = join(dirname, self.sceneId)
        acquisitionDate = Date.fromText(self.sceneId[47:55])
        processingDate = Date.fromText(self.sceneId[25:33])

        def selectFilename(startswith='', endswith='', extension='.vrt'):
            for filename in self.filenames:
                filename = filename.replace('.jp2','')
                if basename(filename).startswith(startswith) and filename.endswith(endswith):
                    return filename+extension
            raise Exception('file not found')


        options = '-srcnodata 0 -vrtnodata 0'

        # sr 10m stack
        infiles = [selectFilename(endswith=b+'_10m') for b in ['B02','B03','B04','B08']]
        outfile = join(folder, self.sceneId + '_sr10m.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=infiles, options=options)
            meta = GDALMeta(outfile)
            #meta.setNoDataValue(noDataValue)
            meta.setBandNames(['blue', 'green', 'red', 'nir'])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('processing time', processingDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', self.SENSOR)
            meta.setMetadataItem('wavelength', [490, 560, 665, 842])
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.writeMeta()

        # sr 20m stack
        infiles = [selectFilename(endswith=b+'_20m') for b in ['B05','B06','B07','B8A','B11','B12']]
        outfile = join(folder, self.sceneId + '_sr20m.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=infiles, options=options)
            meta = GDALMeta(outfile)
            #meta.setNoDataValue(noDataValue)
            meta.setBandNames(['rededge1','rededge2','rededge3','nir1','swir1', 'swir2'])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', self.SENSOR)
            meta.setMetadataItem('wavelength', [705, 740, 783, 865, 1610, 2190])
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.writeMeta()

        # sr 60m stack
        infiles = [selectFilename(endswith=b+'_60m') for b in ['B01','B09']]
        outfile = join(folder, self.sceneId + '_sr60m.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=infiles, options=options)
            meta = GDALMeta(outfile)
            #meta.setNoDataValue(noDataValue)
            meta.setBandNames(['aerosol','water-vapor'])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', self.SENSOR)
            meta.setMetadataItem('wavelength', [443, 945])
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.writeMeta()

        # toa 60m stack (this is only a single file)
        infiles = [filesearch(l1c_folder, 'S2A_OPER_MSI_L1C*'+self.footprint.name+'_B10.jp2')[0]]
        outfile = join(folder, self.sceneId + '_toa60m.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=infiles, options=options)
            meta = GDALMeta(outfile)
            #meta.setNoDataValue(noDataValue)
            meta.setBandNames(['cirrus'])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.setMetadataItem('sensor', self.SENSOR)
            meta.setMetadataItem('wavelength', [1375])
            meta.setMetadataItem('wavelength units', 'nanometers')
            meta.writeMeta()

        # qa 10m stack
        infiles = [selectFilename(startswith='S2A_USER_'+b+'_L2A') for b in ['AOT','WVP']]
        outfile = join(folder, self.sceneId + '_qa10m.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=infiles, options=options)
            meta = GDALMeta(outfile)
            #meta.setNoDataValue(noDataValue)
            meta.setBandNames(['AOT', 'WVP'])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.writeMeta()

        # qa 20m stack
        infiles = [selectFilename(startswith='S2A_USER_'+b+'_L2A') for b in ['CLD','SCL','SNW']]
        outfile = join(folder, self.sceneId + '_qa20m.vrt')
        if not exists(outfile):
            stack_images(outfile=outfile, infiles=infiles, options=options)
            meta = GDALMeta(outfile)
            #meta.setNoDataValue(noDataValue)
            meta.setBandNames(['CLD','SCL','SNW'])
            meta.setAcquisitionDate(acquisitionDate)
            meta.setMetadataItem('sceneid', self.sceneId)
            meta.writeMeta()

        return SentinelTileMultiResolution(folder, footprint=self.footprint)

class SentinelTileMultiResolution():

    EXTENSIONS = ['.tif', '.vrt']

    def __init__(self, folder, footprint):
        assert isinstance(footprint, MGRSFootprint)
        self.folder = folder
        self.footprint = footprint
        self.sceneId = basename(folder)
        self.sr10m_filename = findFilename(join(self.folder, self.sceneId + '_sr10m'), self.EXTENSIONS)
        self.sr20m_filename = findFilename(join(self.folder, self.sceneId + '_sr20m'), self.EXTENSIONS)
        self.sr60m_filename = findFilename(join(self.folder, self.sceneId + '_sr60m'), self.EXTENSIONS)
        self.toa60m_filename = findFilename(join(self.folder, self.sceneId + '_toa60m'), self.EXTENSIONS)
        self.qa10m_filename = findFilename(join(self.folder, self.sceneId + '_qa10m'), self.EXTENSIONS)
        self.qa20m_filename = findFilename(join(self.folder, self.sceneId + '_qa20m'), self.EXTENSIONS)

    def cutMGRSFootprint(self, dirname, footprint, buffer, bufferTwoSided=False):

        assert isinstance(footprint, MGRSFootprint)

        folder = join(dirname, self.sceneId)
        pixelGrid10 = footprint.getPixelGrid(resolution=10, buffer=buffer, anchor=SENTINEL_ANCHOR, north=not bufferTwoSided, west=not bufferTwoSided)
        pixelGrid20 = footprint.getPixelGrid(resolution=20, buffer=buffer, anchor=SENTINEL_ANCHOR, north=not bufferTwoSided, west=not bufferTwoSided)
        pixelGrid60 = footprint.getPixelGrid(resolution=60, buffer=buffer, anchor=SENTINEL_ANCHOR, north=not bufferTwoSided, west=not bufferTwoSided)


        options_default = '-overwrite -of VRT -ot Int16 -r near'

        # 10m files
        options = options_default
        options += ' -te '+str(pixelGrid10.xMin)+' '+str(pixelGrid10.yMin)+' '+str(pixelGrid10.xMax)+' ' + str(pixelGrid10.yMax)
        options += ' -tr '+str(pixelGrid10.xRes)+' '+str(pixelGrid10.yRes)
        options += ' -t_srs '+pixelGrid10.projection
        for infile in [self.sr10m_filename, self.qa10m_filename]:
            outfile = join(folder, basename(infile))[:-4] + '.vrt'
            if not exists(outfile):
                gdalwarp(outfile=outfile, infile=infile, options=options, verbose=True)
                GDALMeta(outfile).copyMetadata(GDALMeta(infile)).writeMeta()

        # 20m files
        options = options_default
        options += ' -te '+str(pixelGrid20.xMin)+' '+str(pixelGrid20.yMin)+' '+str(pixelGrid20.xMax)+' ' + str(pixelGrid20.yMax)
        options += ' -tr '+str(pixelGrid20.xRes)+' '+str(pixelGrid20.yRes)
        options += ' -t_srs '+pixelGrid20.projection
        for infile in [self.sr20m_filename, self.qa20m_filename]:
            outfile = join(folder, basename(infile))[:-4] + '.vrt'
            if not exists(outfile):
                gdalwarp(outfile=outfile, infile=infile, options=options, verbose=True)
                GDALMeta(outfile).copyMetadata(GDALMeta(infile)).writeMeta()

        # 60m files
        options = options_default
        options += ' -te '+str(pixelGrid60.xMin)+' '+str(pixelGrid60.yMin)+' '+str(pixelGrid60.xMax)+' ' + str(pixelGrid60.yMax)
        options += ' -tr '+str(pixelGrid60.xRes)+' '+str(pixelGrid60.yRes)
        options += ' -t_srs '+pixelGrid60.projection
        for infile in [self.sr60m_filename, self.toa60m_filename]:
            outfile = join(folder, basename(infile))[:-4] + '.vrt'
            if not exists(outfile):
                gdalwarp(outfile=outfile, infile=infile, options=options, verbose=True)
                GDALMeta(outfile).copyMetadata(GDALMeta(infile)).writeMeta()

        return SentinelTileMultiResolution(folder, footprint=footprint)

    def asSpectralTileMultiResolution(self, resolutions=[10, 20]):
        return SpectralTileMultiResolution(folder=self.folder, footprint=self.footprint, resolutions=resolutions)

class SentinelTile(SpectralTile):

    def __init__(self, folder, footprint):
        SpectralTile.__init__(folder=folder, footprint=footprint)

class Image():

    def __init__(self, filename):
        self.filename = filename

    def cutMGRSFootprintAndResample(self, dirname, productname, footprint, buffer, resolution, anchor, ot=None, r=None,
                         north=True, west=True, south=True, east=True):

        assert isinstance(footprint, MGRSFootprint)
        print(basename(self.filename)+' cut '+footprint.name+' and resample')
        pixelGrid = footprint.getPixelGrid(resolution=resolution, buffer=buffer, anchor=anchor,
                                           north=north, west=west, south=south, east=east)
        folder = join(dirname, productname)

        outfile = join(folder, basename(self.filename))[:-4]+'.vrt'
        if not exists(outfile):
            options  = '-overwrite -of VRT'
            if ot is not None: options += ' -ot '+ot
            if r is not None: options += ' -r '+r
            options += ' -te '+ str(pixelGrid.xMin) + ' ' + str(pixelGrid.yMin) + ' ' + str(pixelGrid.xMax) + ' ' + str(pixelGrid.yMax)
            options += ' -tr '+ str(pixelGrid.xRes) + ' ' + str(pixelGrid.yRes)
            options += ' -t_srs '+pixelGrid.projection
            gdalwarp(outfile=outfile, infile=self.filename, options=options, verbose=True)
            GDALMeta(outfile).copyMetadata(GDALMeta(self.filename)).writeMeta()

        return Tile(folder=folder, footprint=footprint, imagename=basename(outfile)[:-4])


    def importIntoDataCube(self, dirname, productname, footprints, resolution, buffer, anchor):

        assert isinstance(footprints, MGRSFootprintCollection)
        assert isinstance(resolution, int)
        assert isinstance(buffer, int)

        for footprint in footprints:
            tile = self.cutMGRSFootprintAndResample(dirname=join(dirname, *footprint.subfolders),
                                                    productname=productname,
                                                    footprint=footprint, buffer=buffer, resolution=resolution, anchor=anchor)

class Tile():

    EXTENSIONS = ['.tif', '.vrt']

    def __init__(self, folder, footprint, imagename):

        assert isinstance(footprint, MGRSFootprint)
        self.footprint = footprint
        self.folder = folder
        self.dirname = dirname(folder)
        self.productname = basename(folder)
        self.imagename = imagename
        self.filename = findFilename(join(self.folder, imagename), self.EXTENSIONS)

    def saveAsGTiff(self, dirname=None, compress='LZW', interleave='BAND', predictor='2',
                    tiled='YES', blockxsize=256, blockysize=256):

        print(join(self.productname, self.imagename)+'('+self.footprint.name+') save as GTiff')

        if dirname is None: dirname = self.dirname
        folder = join(dirname, self.productname)

        options = '-co "TILED='+tiled+'" -co "BLOCKXSIZE='+str(blockxsize)+'" -co "BLOCKYSIZE='+str(blockysize)+'" -co "PROFILE=GeoTIFF" '
        options += '-co "COMPRESS=' + compress + '" -co "PREDICTOR=' + predictor + '" -co "INTERLEAVE=' + interleave + '" '

        outfile = join(folder, basename(self.filename))[:-4]+'.tif'
        if not exists(outfile):
            hub.gdal.util.gdal_translate(outfile=outfile, infile=self.filename, options=options)
            inmeta = GDALMeta(self.filename)
            outmeta = GDALMeta(outfile)
            outmeta.copyMetadata(inmeta).writeMeta()

class MGRSFootprint():

    LOOKUP = None
    @staticmethod
    def loadLookup(filename):
        MGRSFootprint.LOOKUP = restoreJSON(filename)


    def __init__(self, name):
        self.name = name
        self.subfolders = (name[:3], name[3:])

    def getPixelGrid(self, resolution, buffer, anchor, north=True, west=True, south=True, east=True):
        info = MGRSFootprint.LOOKUP[self.name]
        projection = osr.SpatialReference()
        projection.ImportFromEPSG(int(info['epsg']))
        projection = projection.ExportToWkt()
        pixelGridDefn = PixelGridDefn(self, projection=projection,
                                      xMin=float(info['xMin']), xMax=float(info['xMax']), yMin=float(info['yMin']), yMax=float(info['yMax']),
                                      xRes=float(resolution), yRes=float(resolution))
        pixelGrid = PixelGrid(pixelGridDefn)
        pixelGrid = pixelGrid.buffer(buffer=buffer, north=north, west=west, south=south, east=east)
        pixelGrid = pixelGrid.anchor(xAnchor=anchor[0], yAnchor=anchor[1])
        return pixelGrid

class MGRSFootprintCollection():

    def __init__(self, names=[]):

        self.footprints = list()
        for name in names:
           self.footprints.append(MGRSFootprint(name=name))

    def __iter__(self):
        for footprint in self.footprints:
            assert isinstance(footprint, MGRSFootprint)
            yield footprint

    def __contains__(self, footprint):
        assert isinstance(footprint, MGRSFootprint)
        for ifootprint in self.footprints:
            if ifootprint.name == footprint.name:
                return True
        return False

def test_landsat_spatial_homogenization():

    roi = MGRSFootprintCollection(['33UVU'])
    sceneNative = LandsatSceneNative(folder=r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00')

    sceneNative.importIntoDataCube(dirname=r'C:\Work\data\gms\_landsatMGRS_30m', footprints=roi,
                                   resolution=30, buffer=300, anchor=LANDSAT_ANCHOR)

def test_image_spatial_homogenization():

    roi = MGRSFootprintCollection(['33UUT','33UUU','33UVT','33UVU'])
    image = Image(filename=r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img')
    image.importIntoDataCube(dirname=r'C:\Work\data\gms\_imageMGRS_30m', footprints=roi,
                             productname='band1-of-landsat',
                             resolution=30, buffer=300, anchor=LANDSAT_ANCHOR)


def test_sentinel_spatial_homogenization():

    #roi = MGRSFootprintCollection(['33UVU'])
    roi = MGRSFootprintCollection(['33UUT','33UUU','33UVT','33UVU'])
    sceneNative = SentinelSceneNative(l1c_folder=r'C:\Work\data\gms\sentinel\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE',
                                      l2a_folder=r'C:\Work\data\gms\sentinel\S2A_USER_PRD_MSIL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE')
    #sceneNative.repairSRS()
    sceneNative.importIntoDataCube(dirname=r'C:\Work\data\gms\_sentinelMGRS_30m3', footprints=roi,
                                   resolution=30, buffer=300, anchor=LANDSAT_ANCHOR, bufferTwoSided=True,
                                   saveAsGTiff=True)



def test_sentinel():
    import gdal
    from os import chdir

    #xmlfile = 'S2A_USER_MTD_SAFL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.xml'
    #ds = gdal.Open(xmlfile)
    #sds = ds.GetSubDatasets()

    if 0:
        chdir(r'C:\Work\data\gms\sentinel\S2A_USER_PRD_MSIL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE')
        ds = gdal.Open(
            r'SENTINEL2_L2A:S2A_USER_MTD_SAFL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.xml:60m:EPSG_32633')
        for i in range(ds.RasterCount):
            print(ds.GetRasterBand(i + 1).GetDescription())

    if 1:
        chdir(r'C:\Work\data\gms\sentinel\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE')
        ds = gdal.Open(
            r'SENTINEL2_L1C:S2A_OPER_MTD_SAFL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.xml:60m:EPSG_32633')

        for i in range(ds.RasterCount):
            print(ds.GetRasterBand(i + 1).GetDescription())

def test_createMGRSFootprintLookup():
    createMGRSFootprintUTMLookup(shapedir=r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files',
                                 outfile=r'C:\Work\data\gms\gis\_lookup\mgrsFootprintUTMLookup.json')
    createMGRSFootprintLEALookup(shapefile=r'C:\Work\data\gms\gis\MGRS_100km\mgrs_100km_lea.shp',
                                 outfile=r'C:\Work\data\gms\gis\_lookup\mgrsFootprintLEALookup.json')
    #createMGRSFootprintWRS2FilterLookup(shapefile=r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp',
    #                                    outfile=r'C:\Work\data\gms\gis\_lookup\mgrsByWrs2Lookup.json')

def test_landsat_archive_spatial_homogenization():

    roi = MGRSFootprintCollection(['33UVU'])
    sceneNative = LandsatSceneNative(folder=r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00')

    sceneNative.importIntoDataCube(dirname=r'C:\Work\data\gms\_landsatMGRS_30m', footprints=roi,
                                   resolution=30, buffer=300, anchor=LANDSAT_ANCHOR)

if __name__ == '__main__':

    #test_createMGRSFootprintLookup()
    LandsatScene.loadLookup(r'C:\Work\data\gms\gis\_lookup\mgrsByWrs2Lookup.json')
    MGRSFootprint.loadLookup(r'C:\Work\data\gms\gis\_lookup\mgrsFootprintUTMLookup.json')

    tic()
    #test_landsat_spatial_homogenization()
    #test_sentinel_spatial_homogenization()
    test_image_spatial_homogenization()

    #test_sentinel()
    toc()
