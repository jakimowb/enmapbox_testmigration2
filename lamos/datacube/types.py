from __future__ import division, print_function
from os import listdir
from os.path import join, basename, dirname, exists
from shutil import copy
from collections import OrderedDict
import ogr


from rios.pixelgrid import PixelGridDefn, pixelGridFromFile
from hub.datetime import Date

from hub.file import saveJSON, restoreJSON
from hub.gdal.util import stack_images, gdalwarp
from hub.gdal.api import GDALMeta
import hub.rs.virtual
import hub.envi
import rios.applier
import numpy

from enmapbox.processing.applier import ApplierHelper
from hub.timing import tic, toc
from multiprocessing.pool import ThreadPool
import subprocess

def findFilename(filenameWithoutExtension, extensions, mustExist=True):
    for extention in extensions:
        if exists(filenameWithoutExtension+extention):
            return filenameWithoutExtension+extention

    if mustExist:
        raise Exception('file not found: '+filenameWithoutExtension)
    else:
        return None

class LandsatScene():

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

    def __init__(self, folder):
        self.folder = folder
        self.dirname = dirname(folder)
        self.sceneId = basename(folder)
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

    def stack(self, dirname):

        folder = join(dirname, self.sceneId)
        # sr stack
        outfile = stack_images(outfile=join(folder, self.sceneId+'_sr.vrt'), infiles=self.sr_filenames)
        meta = GDALMeta(outfile)
        meta.setBandNames(self.SR_BANDNAMES)
        meta.setNoDataValue(self.SR_NODATAVALUE)
        meta.setAcquisitionDate(Date.fromLandsatSceneID(self.sceneId))
        meta.setMetadataItem('sceneid', self.sceneId)
        meta.setMetadataItem('wavelength', [int((u+l)/2) for u, l in zip(self.SR_WAVELENGTH_UPPER, self.SR_WAVELENGTH_LOWER)])
        meta.setMetadataItem('wavelength units', 'nanometers')
        meta.writeMeta()

        # toa stack
        outfile = stack_images(outfile=join(folder, self.sceneId + '_toa.vrt'), infiles=self.toa_filenames)
        meta = GDALMeta(outfile)
        meta.setBandNames(self.TOA_BANDNAMES)
        meta.setNoDataValue(self.TOA_NODATAVALUE)
        meta.setAcquisitionDate(Date.fromLandsatSceneID(self.sceneId))
        meta.setMetadataItem('sceneid', self.sceneId)
        meta.setMetadataItem('wavelength', [int((u + l) / 2) for u, l in zip(self.TOA_WAVELENGTH_UPPER, self.TOA_WAVELENGTH_LOWER)])
        meta.setMetadataItem('wavelength units', 'nanometers')
        meta.writeMeta()

        # qa stack
        outfile = stack_images(outfile=join(folder, self.sceneId + '_qa.vrt'), infiles=self.qa_filenames)
        meta = GDALMeta(outfile)
        meta.setBandNames(self.QA_BANDNAMES)
        meta.setAcquisitionDate(Date.fromLandsatSceneID(self.sceneId))
        meta.setMetadataItem('sceneid', self.sceneId)
        meta.writeMeta()

        # meta files
        copy(self.mtl_filename, folder)
        copy(self.espa_filename, folder)

        return LandsatSceneStacked(folder)

class LT4Scene(LandsatScene):

    SR_BANDNAMES = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
    SR_BASENAMES = ['sr_band' + str(i) for i in [1, 2, 3, 4, 5, 7]]
    SR_WAVELENGTH_LOWER = [450, 520, 630, 760, 1550, 2080]
    SR_WAVELENGTH_UPPER = [520, 600, 690, 900, 1750, 2350]
    SR_NODATAVALUE = -9999
    TOA_BANDNAMES = ['tir1']
    TOA_BASENAMES = ['toa_band6']
    TOA_WAVELENGTH_LOWER = [10400]
    TOA_WAVELENGTH_UPPER = [12500]
    TOA_NODATAVALUE = -9999
    QA_BASENAMES  = ['cfmask', 'cfmask_conf', 'sr_adjacent_cloud_qa', 'sr_atmos_opacity', 'sr_cloud_qa',
                     'sr_cloud_shadow_qa', 'sr_ddv_qa', 'sr_fill_qa', 'sr_land_water_qa', 'sr_snow_qa', 'toa_band6_qa']
    QA_BANDNAMES = QA_BASENAMES

class LT5Scene(LT4Scene):

    QA_BASENAMES = LT4Scene.QA_BASENAMES + ['toa_qa']
    QA_BANDNAMES = QA_BASENAMES

class LE7Scene(LandsatScene):

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

class LC8Scene(LandsatScene):

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

class LandsatSceneStacked():

    EXTENSIONS = ['.tif','.img','.vrt']

    def __init__(self, folder):
        self.folder = folder
        self.dirname = dirname(folder)
        self.sceneId = basename(folder)
        self.sr_filename = findFilename(join(self.folder, self.sceneId + '_sr'), self.EXTENSIONS)
        self.toa_filename = findFilename(join(self.folder, self.sceneId + '_toa'), self.EXTENSIONS)
        self.qa_filename = findFilename(join(self.folder, self.sceneId + '_qa'), self.EXTENSIONS)
        self.mtl_filename = join(self.folder, self.sceneId + '_MTL.txt')
        self.espa_filename = join(self.folder, self.sceneId + '.xml')

    def subset(self, dirname, pixelGrid):

        assert isinstance(pixelGrid, PixelGridDefn)
        folder = join(dirname, self.sceneId)

        options  = '-overwrite -of VRT -ot Int16 -r near'
        options += ' -te '+ str(pixelGrid.xMin) + ' ' + str(pixelGrid.yMin) + ' ' + str(pixelGrid.xMax) + ' ' + str(pixelGrid.yMax)
        options += ' -tr '+ str(pixelGrid.xRes) + ' ' + str(pixelGrid.yRes)
        options += ' -t_srs '+pixelGrid.projection
        infile = self.sr_filename
        outfile = join(folder, basename(infile))[:-4]+'.vrt'
        gdalwarp(outfile=outfile, infile=infile, options=options, verbose=True)
        GDALMeta(outfile).copyMetadata(GDALMeta(infile)).writeMeta()


def landsatScene(folder):

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
    for key, type in [('LC8', LC8Scene), ('LE7', LE7Scene), ('LT5', LT5Scene), ('LT4', LT4Scene)]:
        if sceneId.startswith(key):
            scene = type(folder)
            assert isinstance(scene, LandsatScene)
            return scene

    raise Exception('unknown landsat product')

def createMGRSFootprintLookup(shapedir, outfile):

        lookup = OrderedDict()
        for basename in listdir(shapedir):
            shapefile = join(shapedir, basename, basename+'.shp')
            print(shapefile)
            dataSource = ogr.Open(shapefile)
            layer = dataSource.GetLayer(0)
            for feature in layer:
                try:
                    info = {key : int(round(value)) for key, value in zip(['xMin', 'yMin', 'xMax', 'yMax'], feature.geometry().GetEnvelope())}
                    info['name'] = feature.GetField('MGRS')
                    info['folders'] = [info['name'][:3], info['name'][3:]]
                    info['srs'] = 'EPSG:326'+info['name'][0:2]
                    lookup[info['name']] = info
                except ValueError:
                    print('-> shapefile is invalid!')
                    break
        saveJSON(file=outfile, var=lookup)

class Footprint():

    FOOTPRINT_LOOKUP = OrderedDict()

    @staticmethod
    def loadLookup(self, filename):
        self.LOOKUP = restoreJSON(filename)

    def __init__(self, name, ul, lr):

        self.utm = name[0:2]

def test_scene_stacking():

    wrs2FootprintName = '194024'

    pixelGrid = pixelGridFromFile(r'C:\Work\data\gms\landsatXMGRS\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.vrt')
    for sceneId in ['LC81940242015235LGN00', 'LE71940242015275NSG00', 'LT51940242010189KIS01', 'LT41940241990126XXX03']:
        scene = landsatScene(folder=join(r'C:\Work\data\gms\landsat\194\024', sceneId))
        scene = scene.stack(dirname=r'C:\Work\data\gms\_landsatWRS2\194\024')
        scene.subset(dirname=r'C:\Work\data\gms\_landsatMGRS\194\024', pixelGrid=pixelGrid)

def test_mgrs_footprint():

    MGRSFootprint.createMGRSFootprintLookup(shapedir=r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files',
                                            outfile=r'C:\Work\data\gms\gis\_mgrsLookup\mgrsFootprintLookup.json')

if __name__ == '__main__':

    tic()
    #test_scene_stacking()
    test_mgrs_footprint()
    toc()
