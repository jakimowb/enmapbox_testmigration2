from __future__ import division
from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ndvi import NDVIApplier
from hub.timing import tic, toc
from hub.datetime import Date


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatXMGRS'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\ndviTimeseriesMGRS'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['192023','193023','194023','192024','193024','194024']
    mgrsFootprints = ['33UUU', '33UVU', '33UUT', '33UVT']

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


if __name__ == '__main__':

    tic()
    test()
    toc()
