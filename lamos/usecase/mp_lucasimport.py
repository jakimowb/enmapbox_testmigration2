from __future__ import print_function
from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import CompositingApplier, StatisticsApplier
from lamos.operators.stack import StackApplier
from lamos.operators.importer import LucasImportApplier
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
import hub.file
from hub.timing import tic, toc
from hub.datetime import Date
from enmapbox.processing.estimators import Classifiers


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'


    folder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucasMGRS'
    filename = r'\\141.20.140.91\SAN_Projects\Geomultisens\data\testdata\reference_data\eu27_lucas_2012_subset1.shp'

    mgrsNames = ['33UUU', '33UVU', '33UUT', '33UVT']
    for mgrsName in mgrsNames:
        mgrs = MGRSFootprint.fromShp(mgrsName)
        print(mgrs.name)
        print('UL:', mgrs.getUL(), 'LR:', mgrs.getUL())
        print('BoundingBox with 300m Buffer auf USGS Landsat PixelGrid gesnapped:', mgrs.getBoundingBox(300, snap='landsat'))
        print()


    return
    # import LUCAS data
    importer = LucasImportApplier(inshapefile=filename, outfolder=folder, footprints=mgrsFootprints, buffer=300)
    importer.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
