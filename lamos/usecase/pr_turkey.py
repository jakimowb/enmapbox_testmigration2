from hub.datetime import Date
from hub.timing import tic, toc
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ndvi import NDVIApplier
from lamos.operators.tc import TCApplier
from lamos.processing.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\04_Landsat'
    folder2 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatX'
    folder3 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatXMGRS'
    folder4 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatTimeseriesMGRS'
    folder5 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_products'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['169032','170032','171034','171035','172034','172035','173034','178034','177034','176034','173035']
    mgrsFootprints = ['36SVG','37SEB','37SEA','37SFA','37SFB','38TMK','38SMK']

    composer = LandsatXComposer()
    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    tsBuilder = TimeseriesBuilder(start=Date(2014, 1, 1), end=None)
    tsBuilder.build(infolder=folder3, outfolder=folder4, envi=True, compressed=False, footprints=mgrsFootprints)

    applier = NDVIApplier(infolder=folder4, outfolder=folder5, inextension='.img', footprints=mgrsFootprints, compressed=False)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()

    applier = TCApplier(infolder=folder4, outfolder=folder5, inextension='.img', footprints=mgrsFootprints, compressed=False)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()



if __name__ == '__main__':

    tic()
    test()
    toc()
