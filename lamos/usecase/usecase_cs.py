import os, sys, datetime
import lamos.cubebuilder.tiling
import lamos.cubebuilder.rasterdb
from hub.timing import tic, toc

if __name__ == '__main__':

    ### TILING ###
    # location of input landsat scenes
    sensorfolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    # location for storing mgrs tiles of landsat scenes
    tilesfolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseCS\tiles'
    # shapefile defining the MGRS/WRS2 Tiling Scheme
    tilingshapefile = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    if 0: # do the tiling?
        # do the tiling for choosen footprints (all scenes inside a footprint will be processed)
        tic('tile Landsat Scenes')
        for footprint in [191026,192026,193026]:
            lamos.cubebuilder.tiling.tileFootprint(footprint, sensorfolder, tilesfolder, tilingshapefile,
                                                   timerange=[datetime.date(2011, 1, 1), datetime.date(2013, 12, 31)])
            lamos.cubebuilder.tiling.tileFootprint(footprint, sensorfolder, tilesfolder, tilingshapefile,
                                                   timerange=[datetime.date(1986, 1, 1), datetime.date(1988, 12, 31)])
        toc()

    #sys.exit()

    ### CUBE BUILDING ###
    # location for rasterDB (stores metadata and knows about the connection between original scenes and tiles)
    cubesfolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseCS\cubes'
    dbfile = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseCS\rasterdb.pickle'
    rasterDB = lamos.cubebuilder.rasterdb.RasterDB()
    # create new or load existing RasterDB. if already existing
    if 0: # load existing RasterDB?
        tic('load rasterDB')
        rasterDB.load(dbfile)
    else:
        tic('create rasterDB')

        # set spatial subset by MGRS tiles (perhaps better to support subsetting by a shapefile(?))
        # - find all existing MGRS tiles in the tiles folder
        mgrstiles = list()
        for utmzone in os.listdir(tilesfolder):
            for mgrstile in os.listdir(os.path.join(tilesfolder, utmzone)):
                mgrstiles.append(mgrstile)
        mgrstiles = ['33UUQ','33UVQ','33UUP','33UVP']
        # - apply subset
        rasterDB.setSpatialSubset(mgrstiles)

        # parse metafiles and convert to homogenized metadata (as defined by Daniel Scheffer)
        rasterDB.parseMetadata(scenesfolder=sensorfolder,
                               tilesfolder=tilesfolder)

        # save rasterDB for later use
        rasterDB.save(dbfile)
    toc()

#    sys.exit()

    # spectral bands subset of virtual sensor (as defined by Dirk Pflugmacher)
    # NOTE: mapping of Landsat Sensors bands to virtual sensor bands is hard coded inside gms.rasterdb module
    # In this example only Landsat 8 will support 'aerosol' observations, resulting in a layer-stack with less bands, compared to the other layer-stack
    rasterDB.setSpectralSubset((1,2,3,4,8,10,11)) #  => 'aerosol', 'blue', 'green', 'red', 'nir', 'swir-1', 'swir-2'

    # filter scenes by homogenized metainfo (as defined by Daniel Scheffer)
    # - This example filter function includes all scenes with acquisition year >= 1970
    def filterFunction(meta):
        return True
    rasterDB.setFilterFunction(filterFunction)

    # query cube
    rasterDB.queryCube()

    # create cube (write VRT or ENVI stacks)
    tic('writing tile cubes')
    rasterDB.createCube(cubesfolder, ENVI=True)
    toc()
