from hub.datetime import Date
from hub.timing import tic, toc
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ndvi import NDVIApplier
from lamos.operators.tc import TCApplier
from lamos.operators.compositing import StatisticsApplier
from lamos.processing.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive

def test(i=None):

    MGRSFootprint.shpRoot = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\04_Landsat'
    folder2 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar2_landsatX'
    folder3 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar2_landsatXMGRS'
    folder3b = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar2_landsatXMGRS_GTiff'
    folder4 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar2_landsatTimeseriesMGRS'
    folder5 = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar2_products'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = None #['169032','170032','171034','171035','172034','172035','173034','178034','177034','176034','173035']
    mgrsFootprints = ['35TMF','36TWL','38TMK','37SEB','36SYG','36SWH','35SNC'] # ['36SVG','37SEB','37SEA','37SFA','37SFB','38TMK','38SMK']


    if i is not None:
        mgrsFootprints = mgrsFootprints[i:i+1]
        assert len(mgrsFootprints) > 0

    composer = LandsatXComposer()
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=50)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=50)

    #MGRSArchive(folder3).saveAsGTiff(outfolder=folder3b, compress='LZW', filter=mgrsFootprints, processes=100)


    start = Date(2015, 1, 1)
    end = Date(2015, 12, 31)
    tsBuilder = TimeseriesBuilder(start=start, end=end)
    #tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints, processes=50)

    applier = StatisticsApplier(infolder=folder4, outfolder=folder5,
                                footprints=mgrsFootprints, inextension='.vrt', of='ENVI',
                                percentiles=[5, 25, 50, 75, 95], variables=['tcb','tcg','tcw','ndvi'], mean=True, stddev=True)

    bufferYears = 0
    applier.appendDateParameters(date1=start, date2=end, bufferYears=bufferYears)
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    #applier.apply()

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
    test(11)
    toc()
