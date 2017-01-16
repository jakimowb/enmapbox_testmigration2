import hub.file
from enmapbox.processing.estimators import Classifiers
from hub.datetime import Date
from hub.timing import tic, toc
from lamos.operators.compositing import StatisticsApplier
from lamos.operators.importer import LucasImportApplier
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
from lamos.operators.stack import StackApplier
from lamos.operators.importer import LucasImportApplier
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
from lamos.processing.types import MGRSFootprint, MGRSTilingScheme, MGRSArchive, WRS2Footprint
import hub.file
from hub.timing import tic, toc
from hub.datetime import Date
from enmapbox.processing.estimators import Classifiers
from os.path import join


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    root = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms'
    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = join(root, 'landsatX_2012')
    folder3 = join(root, 'landsatXMGRS_2012')
    folder3b = join(root, 'landsatXMGRS_2012_GTiff')

    folder4 = join(root, 'landsatTimeseriesMGRS_2012')
    folder5 = join(root, 'productsMGRS_2012')
    folder6 = join(root, 'lucasMGRS_2012_withWater')
    folder7 = join(root, 'stackMGRS_2012')
    folder8 = join(root, 'rfcMGRS_2012')

    #filename1 = r'\\141.20.140.91\SAN_Projects\Geomultisens\data\testdata\reference_data\eu27_lucas_2012_subset1.shp'
    filename1 = r'\\141.20.140.91\SAN_Projects\Geomultisens\workspace\gms_landcover\bbrdb\rfcMGRS_20161028\reference_data\eu27_lucas_2012_subset1_bbsite_plus200water.shp'
    filename2 = join(root, 'lucas_lc4.pkl')
    filename3 = join(root, 'lucas_lc4.json')

    #WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['192023','193023','194023','192024','193024','194024']
    mgrsFootprints = ['33UUU', '33UVU', '33UUT', '33UVT']

    #i=3
    #mgrsFootprints = mgrsFootprints[i:i+1]

    start = Date(2011, 1, 1)
    end = Date(2013, 12, 31)

    composer = LandsatXComposer(start=start, end=end)
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=50)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=50)
    #MGRSArchive(folder3).saveAsGTiff(folder3b, filter=mgrsFootprints, processes=50)

    tsBuilder = TimeseriesBuilder(start=start, end=None)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints)


    applier = StatisticsApplier(infolder=folder4, outfolder=folder5, of='ENVI',
                                footprints=mgrsFootprints, inextension='.tif')
    applier.appendDateParameters(date1=start, date2=end, bufferYears=0)
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    #applier.controls.setNumThreads(10)
    #applier.apply()

    # import LUCAS data
    importer = LucasImportApplier(inshapefile=filename1, outfolder=folder6, footprints=mgrsFootprints, buffer=300)
    #importer.apply()

    # build feature stack
    stacker = StackApplier(outfolder=folder7, outproduct='stack', outimage='stack', footprints=mgrsFootprints)
    for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr']:
        stacker.appendFeatures(infolder=folder5, inproduct='statistics', inimage=key+'_2011-01-01_to_2013-12-31_1y', inextension='.img', inbands=None)
    #stacker.apply()

    sampleReader = SampleReadApplier(featureFolder=folder7, featureProduct='stack', featureImage='stack', featureExtension='.vrt',
                                     labelFolder=folder6, labelProduct='lucas', labelImage='lucas_lc4', labelExtension='.img',
                                     footprints=mgrsFootprints)
    if 0:
        sample = sampleReader.apply()
        hub.file.savePickle(var=sample, filename=filename2)
    else:
        sample = hub.file.restorePickle(filename=filename2)

    rfc = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100, class_weight='balanced', n_jobs=100)
    rfc.fitSample(sample)
    exportSampleAsJSON(sample=sample, rfc=rfc, outfile=filename3)

    predictor = ClassifierPredictApplier(featureFolder=folder7, featureProduct='stack', featureImage='stack', featureExtension='.vrt',
                                         labelFolder=folder8, labelProduct='rfc', labelImage='rfc_lc4', labelExtension='.img',
                                         classifier=rfc, footprints=mgrsFootprints)
    predictor.apply()


if __name__ == '__main__':

    tic()
    #test()
    toc()

    import gdal
    from os import chdir

    chdir(r'H:\EuropeanDataCube\sentinel2\Processing\L2A_TOI\S2A_USER_PRD_MSIL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE')
    ds = gdal.Open(r'SENTINEL2_L2A:S2A_USER_MTD_SAFL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.xml:20m:EPSG_32633')
    for i in range(ds.RasterCount):
        print(ds.GetRasterBand(i+1).GetDescription())

    ds = gdal.Open(r'S2A_USER_MTD_SAFL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.xml')
    print(ds.GetSubDatasets())