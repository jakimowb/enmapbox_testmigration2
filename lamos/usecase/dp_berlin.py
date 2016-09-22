from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import CompositingApplier, StatisticsApplier
from lamos.operators.stack import StackApplier
from lamos.operators.importer import LucasImportApplier
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
import hub.file
from hub.timing import tic, toc
from hub.datetime import Date
from emb.processing.estimators import Classifiers


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatXMGRS'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS_ENVI'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\productsMGRS'
    folder6 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucasMGRS'
    folder7 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\stackMGRS'
    folder8 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\rfcMGRS'

    filename1 = r'\\141.20.140.91\SAN_Projects\Geomultisens\data\testdata\reference_data\eu27_lucas_2012_subset1.shp'
    filename2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucas_lc4.pkl'
    filename3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucas_lc4.json'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['192023','193023','194023','192024','193024','194024']
    mgrsFootprints = ['33UUU', '33UVU', '33UUT', '33UVT']

    i=3
    mgrsFootprints = mgrsFootprints[i:i+1]

    start = Date(2014, 1, 1)
    end = Date(2016, 6, 30)

    composer = LandsatXComposer(start=start, end=end)
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=50)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=50)


    tsBuilder = TimeseriesBuilder(start=start, end=None)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints)

    #MGRSArchive(folder4).saveAsENVI(folder4b, compress=False, filter=mgrsFootprints, processes=50)

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5, of='ENVI',
                                footprints=mgrsFootprints, inextension='.img')
    bufferYears = 0

    # 2.5 year composite
    #applier.appendDateParameters(date1=start, date2=end, bufferYears=bufferYears)

    # 12 month composites
    #applier.appendDateParameters(date1=Date(2014,  1,  1), date2=Date(2014, 12, 31), bufferYears=bufferYears)
    #applier.appendDateParameters(date1=Date(2015,  1,  1), date2=Date(2015, 12, 31), bufferYears=bufferYears)

    # 6 month composites
    #applier.appendDateParameters(date1=Date(2014,  4,  1), date2=Date(2014,  9, 30), bufferYears=bufferYears)
    #applier.appendDateParameters(date1=Date(2014, 10,  1), date2=Date(2015,  3, 31), bufferYears=bufferYears)
    #applier.appendDateParameters(date1=Date(2015,  4,  1), date2=Date(2015,  9, 30), bufferYears=bufferYears)
    #applier.appendDateParameters(date1=Date(2015, 10,  1), date2=Date(2016,  3, 31), bufferYears=bufferYears)

    # 3 month composites
    applier.appendDateParameters(date1=Date(2014,  3,  1), date2=Date(2014,  5, 31), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2014,  6,  1), date2=Date(2014,  8, 31), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2014,  9,  1), date2=Date(2014, 11, 30), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2014, 12,  1), date2=Date(2015,  2, 28), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2015,  3,  1), date2=Date(2015,  5, 31), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2015,  6,  1), date2=Date(2015,  8, 31), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2015,  9,  1), date2=Date(2015, 11, 30), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2015, 12,  1), date2=Date(2016,  2, 29), bufferYears=bufferYears)
    applier.appendDateParameters(date1=Date(2016,  3,  1), date2=Date(2016,  5, 31), bufferYears=bufferYears)

    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    #applier.controls.setNumThreads(10)
    applier.apply()

    return

    # import LUCAS data
    importer = LucasImportApplier(inshapefile=filename1, outfolder=folder6, footprints=mgrsFootprints, buffer=300)
    #importer.apply()

    # build feature stack
    stacker = StackApplier(outfolder=folder7, outproduct='stack', outimage='stack', footprints=mgrsFootprints)
    for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr']:
        stacker.appendFeatures(infolder=folder5, inproduct='statistics', inimage=key+'_2014-01-01_to_2016-06-30_1y', inextension='.img', inbands=None)
#    stacker.apply()

    sampleReader = SampleReadApplier(featureFolder=folder7, featureProduct='stack', featureImage='stack', featureExtension='.vrt',
                                     labelFolder=folder6, labelProduct='lucas', labelImage='lucas_lc4', labelExtension='.img',
                                     footprints=mgrsFootprints)
    if 0:
        sample = sampleReader.apply()
        hub.file.savePickle(var=sample, file=filename2)
    else:
        sample = hub.file.restorePickle(file=filename2)

    rfc = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100, class_weight='balanced', n_jobs=10)
    rfc._fit(sample)
    exportSampleAsJSON(sample=sample, rfc=rfc, outfile=filename3)

    predictor = ClassifierPredictApplier(featureFolder=folder7, featureProduct='stack', featureImage='stack', featureExtension='.vrt',
                                         labelFolder=folder8, labelProduct='rfc', labelImage='rfc_lc4', labelExtension='.img',
                                         classifier=rfc, footprints=mgrsFootprints)
    #predictor.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
