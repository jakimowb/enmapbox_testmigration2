from hub.timing import tic, toc
import lamos._old_cubebuilder.tiling

if __name__ == '__main__':

    ### TILING ###
    # location of input landsat scenes
    sensorfolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    # location for storing mgrs tiles of landsat scenes
    tilesfolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseDirk\tiles'
    # shapefile defining the MGRS/WRS2 Tiling Scheme
    tilingshapefile = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    # do the tiling for choosen footprints (all scenes inside a footprint will be processed)
    tic('tile Landsat Scenes')
    for footprint in [193024,194024]:
        lamos._old_cubebuilder.tiling.tileFootprint(footprint, sensorfolder, tilesfolder, tilingshapefile)
    toc()
