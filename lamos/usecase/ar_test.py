from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ndvi import NDVIApplier
from lamos.operators.mean import MeanApplier
from lamos.operators.compositing import CompositingApplier
from hub.timing import tic, toc
from hub.datetime import Date

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'C:\Work\data\gms\landsat'
    folder2 = r'C:\Work\data\gms\landsatX'
    folder3 = r'C:\Work\data\gms\landsatXMGRS'
    folder4 = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    folder5 = r'C:\Work\data\gms\productsMGRS'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['193024','194024']
    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

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

    applier = MeanApplier(infolder=folder4, outfolder=folder5, inextension='.img', footprints=mgrsFootprints, compressed=False)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()

    years = [2000]#, 2001]
    months = [2]#, 5, 8, 11]
    days = [15]
    bufferDays = 190
    bufferYears = 30

    folder5 = r'C:\Work\data\gms\comp'
#    mgrsFootprints = ['32UQC']

    applier = CompositingApplier(infolder=folder4, outfolder=folder5, compressed=False,
                                 years=years, months=months, days=days,
                                 bufferDays=bufferDays, bufferYears=bufferYears,
                                 footprints=mgrsFootprints, inextension='.img')
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()

if __name__ == '__main__':

    tic()
    test()
    toc()
