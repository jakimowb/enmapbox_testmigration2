import hub.gdal.util, hub.file, hub.rs.virtual, hub.gdal.api
from hub.timing import tic, toc
import os, copy, numpy, yaml

# also see http://landsat.usgs.gov/band_designations_landsat_satellites.php
bandinfoBySensor = dict()
bandinfoBySensor['OLI_TIRS'] = {
    'band number'        : range(1,12),
    'vrt band number'    : [ 1,         2,      3,       4,     8,     10,       11,       15,    14,       12,      13],
    'band name'          : ['aerosol', 'blue', 'green', 'red', 'nir', 'swir-1', 'swir-2', 'pan', 'cirrus', 'tir-1', 'tir-2'],
    'wavelength lower'   : [ 430,       450,    530,     640,   850,   1570,     2110,     500,   1360,     10600,   11500],
    'wavelength upper'   : [ 450,       510,    590,     670,   880,   1600,     2290,     680,   1380,     11190,   12510],
    'spatial resolution' : [ 30,        30,     30,      30,    30,    30,       30,       15,    30,       100,     100]}
bandinfoBySensor['OLI_TIRS']['filename toa reflectance'] = ['toa_band'+str(i) for i in bandinfoBySensor['OLI_TIRS']['band number']]
bandinfoBySensor['OLI_TIRS']['filename surface reflectance'] = ['sr_band'+str(i) for i in bandinfoBySensor['OLI_TIRS']['band number']]
bandinfoBySensor['OLI_TIRS']['filename DN'] = ['B'+str(i) for i in bandinfoBySensor['OLI_TIRS']['band number']]
bandinfoBySensor['OLI_TIRS']['filename cfmask'] = 'cfmask'


bandinfoBySensor['ETM'] = {
    'band number'        : range(1,9),
    'vrt band number'    : [ 2,      3,          4,          8,          10,         12,          11,         15],
    'band name'          : ['blue', 'green',    'red',      'nir',      'swir-1',   'tir',       'swir-2',   'pan'],
    'wavelength lower'   : [ 450,    520,        630,        770,        1550,       10400,       2090,      520],
    'wavelength upper'   : [ 520,    600,        690,        900,        1750,       12500,       2350,      900],
    'spatial resolution' : [ 30,     30,         30,         30,         30,         60,          30,         15]}
bandinfoBySensor['ETM']['filename toa reflectance'] = ['toa_band'+str(i) for i in bandinfoBySensor['ETM']['band number']]
bandinfoBySensor['ETM']['filename surface reflectance'] = ['sr_band'+str(i) for i in bandinfoBySensor['ETM']['band number']]
bandinfoBySensor['ETM']['filename DN'] = ['B'+str(i) for i in bandinfoBySensor['ETM']['band number']]
bandinfoBySensor['ETM']['filename cfmask'] = 'cfmask'

bandinfoBySensor['TM'] = {
    'band number'          : range(1,8),
    'vrt band number'      : [ 2,      3,       4,     8,     10,       12,    11],
    'band name'            : ['blue', 'green', 'red', 'nir', 'swir-1', 'tir', 'swir-2'],
    'wavelength lower'     : [ 450,    520,     630,   760,   1550,     10400, 2080],
    'wavelength upper'     : [ 520,    600,     690,   900,   1750,     12500, 2350],
    'spatial resolution'   : [ 30,     30,      30,    30,    30,       120,   30]}
bandinfoBySensor['TM']['filename toa reflectance'] = ['toa_band'+str(i) for i in bandinfoBySensor['TM']['band number']]
bandinfoBySensor['TM']['filename surface reflectance'] = ['sr_band'+str(i) for i in bandinfoBySensor['TM']['band number']]
bandinfoBySensor['TM']['filename DN'] = ['B'+str(i) for i in bandinfoBySensor['TM']['band number']]
bandinfoBySensor['TM']['filename cfmask'] = 'cfmask'

bandinfoBySensor['vrt'] = {
    'band number'          : [ 1,         2,      3,       4,     5,          6,          7,          8,     9,      10,      11,      12,     13,     14,       15,    16],
    'band name'            : ['aerosol', 'blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'nir2', 'swir1', 'swir2', 'tir1', 'tir2', 'cirrus', 'pan', 'water-vapor']}

class RasterDB:

    def __init__(self):
        pass

    def parseMetadata(self, scenesfolder, tilesfolder):
        self.scenesfolder = scenesfolder
        self.tilesfolder =  tilesfolder
        self.scenesByTile = dict()
        self.metaByScene = dict()
        for tilename in self.mgrstiles:

            # get scene ids
            #vrtfiles = hub.file.filesearch(os.path.join(self.tilesfolder, tilename[0:2], tilename), '*.vrt')
            #sceneIDs = {os.path.basename(file)[0:21] for file in vrtfiles}
            sceneIDs = os.listdir(os.path.join(self.tilesfolder, tilename[0:2], tilename))
            self.scenesByTile[tilename] = sceneIDs

            # parse scene MTL files
            for sceneID in sceneIDs:
                mtlfile = os.path.join(self.scenesfolder, sceneID[3:6], sceneID[6:9], sceneID, sceneID)+'_MTL.txt'
                espafile = os.path.join(self.scenesfolder, sceneID[3:6], sceneID[6:9], sceneID, sceneID)+'.xml'

                # only parse metafiles if not already done
                if not self.metaByScene.has_key(sceneID):
                    print('parse '+sceneID)
                    print(mtlfile)
                    print(espafile)
                    meta = hub.rs.virtual.parseLandsatMeta(mtlfile, espafile)
                    self.metaByScene[sceneID] = meta

    def setSpatialSubset(self, mgrstiles):
        # todo calculate intersection between ROI and available data
        # hard coded test case
        self.mgrstiles = mgrstiles #  ['32UPD','32UQD','33UTU','33UUU']

    def setSpectralSubset(self, spectralSubset):
        self.spectralSubset = spectralSubset

    def setFilterFunction(self, filterFunction):
        self.filterFunction = filterFunction

    def queryCube(self):
        self.cube = dict()
        for mgrstile in self.mgrstiles:
            self.cube[mgrstile] = {band:dict() for band in self.spectralSubset}
            self.cube[mgrstile]['cfmask'] = dict()
            print(mgrstile)
            for sceneID in self.scenesByTile[mgrstile]:
                if self.filterFunction(self.metaByScene.get(sceneID)):
                    print(sceneID)
                    bandinfo = bandinfoBySensor[self.metaByScene[sceneID]['Sensor']]

                    # reflectance bands
                    vrtBandNumbers = bandinfo['vrt band number']
                    for band in self.spectralSubset:
                        try:
                            filename = bandinfo['filename surface reflectance'][vrtBandNumbers.index(band)]
                            fullfilename = os.path.join(self.tilesfolder, mgrstile[0:2], mgrstile, sceneID, sceneID+'_'+filename+'_'+mgrstile+'.vrt')
                            self.cube[mgrstile][band][sceneID] = fullfilename
                        except ValueError:
                            pass

                    # cloud mask
                    filename = bandinfo['filename cfmask']
                    fullfilename = os.path.join(self.tilesfolder, mgrstile[0:2], mgrstile, sceneID, sceneID+'_'+filename+'_'+mgrstile+'.vrt')
                    self.cube[mgrstile]['cfmask'][sceneID] = fullfilename
                    #print(filename)

    def save(self, dbfile): hub.file.savePickle(self.__dict__, dbfile)

    def load(self, dbfile): self.__dict__ = hub.file.restorePickle(dbfile)

    def createCube(self, vrtfolder, ENVI=False):
        print('Create VRT files')
        for mgrstile in self.cube:
            print(mgrstile)
            allSceneIDs = set()
            for vrtband in self.cube[mgrstile]:
                # get filenames and sort by acquisition date
                sceneIDs = self.cube[mgrstile][vrtband].keys()
                allSceneIDs.update(sceneIDs)
                filenames = self.cube[mgrstile][vrtband].values()
                dates = [str(self.metaByScene[sceneID]['AcqDate']) for sceneID in sceneIDs]
                sorted = numpy.argsort(dates)
                dates =numpy.array(dates)[sorted]
                filenames =numpy.array(filenames)[sorted]
                sceneIDs =numpy.array(sceneIDs)[sorted]

                outfileVRT = os.path.join(vrtfolder, mgrstile[0:2], mgrstile, 'band'+str(vrtband)+'.vrt')
                outfileENVI = outfileVRT.replace('.vrt', '.img')
                hub.file.mkfiledir(outfileVRT)
                vrtExist = os.path.exists(outfileVRT)
                enviExist = os.path.exists(outfileENVI)

                if not vrtExist:
                    hub.gdal.util.stack(outfileVRT, filenames)

                # prepare metadata
                if not vrtExist or (ENVI and not enviExist):

                    outMeta = hub.gdal.api.GDALMeta(outfileVRT)
                    outMeta.setNoDataValue(outMeta.rb[0].getNoDataValue())

                    #outMeta.setMetadataItem('acquisition_time', dates, mapToBands=True)
                    #outMeta.setMetadataItem('scene_id', sceneIDs, mapToBands=True)
                    outMeta.setBandNames(list(filenames))
                    #gdalMeta.setMetadataItem('MTLFile', [mtlfile], mapToBands=True)
                    #gdalMeta.setMetadataItem('ESPAFile', [espafile], mapToBands=True)
                    meta = dict()
                    for sceneID in sceneIDs:
                        for key in ['AcqDate', 'AcqTime', 'ProcLCode', 'Satellite', 'SceneID', 'Sensor', 'SunAzimuth', 'SunElevation', 'geometric accuracy']:
                            if not meta.has_key(key): meta[key] = list()
                            meta[key].append(self.metaByScene[sceneID][key])

                    for key in meta.keys():
                        outMeta.setMetadataItem(key, meta[key], mapToBands=True)

                if not vrtExist:
                    outMeta.writeMeta(outfileVRT)

                if ENVI and not os.path.exists(outfileENVI):
                    hub.gdal.util.gdal_translate(outfileENVI, outfileVRT, '-of ENVI')
                    outMeta.writeMeta(outfileENVI)

    def getTileFolders(self, rootfolder):
        return [os.path.join(rootfolder, mgrstile) for mgrstile in self.mgrstiles]

if __name__ == '__main__':

    # create or load RasterDB
    dbfile = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\tiles\rasterdb.pickle'
    rasterDB = RasterDB()

    if 1:
        tic('create rasterDB')

        # spatial subset by shapefile
        rasterDB.setSpatialSubset(r'c:\'rio.shp')

        # parse metafile (this may take a while)
        rasterDB.parseMetadata(scenesfolder=r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat',
                               tilesfolder= r'\\141.20.140.91\NAS_Work\EuropeanDataCube\tiles')

        # save rasterDB for later use
        rasterDB.save(dbfile)
    else:
        tic('load rasterDB')
        rasterDB.load(dbfile)
    toc()

    # spectral bands subset of virtual sensor (as defined by Dirk Pflugmacher)
    rasterDB.setSpectralSubset((2,3,4,8,10,11)) #  => 'blue', 'green', 'red', 'nir', 'swir-1', 'swir-2'

    # filter scenes by homogenized metainfo (as defined by Daniel Scheffer)
    filterFunction = lambda meta: yaml.load(meta['AcqDate']).year == 2013
    rasterDB.setFilterFunction(filterFunction)

    # query cube
    rasterDB.queryCube()

    # create cube (write VRT or ENVI stacks)
    cubefolder = r'H:\EuropeanDataCube\testQuery'
    rasterDB.createCube(cubefolder)

    from enmap.apps.imageml import imageSVC