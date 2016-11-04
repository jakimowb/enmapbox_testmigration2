from lamos.processing.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import StatisticsApplier
from hub.timing import tic, toc
from hub.datetime import Date
from lamos.operators.stack import StackApplier
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
import hub.file
from enmapbox.processing.estimators import Classifiers
from os.path import join

def test(i=None):

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    bufferYears = 1
    syears = str(bufferYears*2+1)+'years'

    root = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\new'
    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = join(root, 'landsatX')
    folder3 = join(root, 'landsatXMGRS')
    folder4 = join(root, 'landsatTimeseriesMGRS')
    folder4b = join(root, 'landsatTimeseriesMGRS_GTiff')
    folder5 = join(root, 'statisticsMGRS_'+syears)
    folder6 = join(root, 'referenceMGRS')
    folder7 = join(root, 'stackMGRS_'+syears)
    folder8 = join(root, 'rfcMGRS_'+syears)
    folder9 = join(root, 'samples_'+syears)

    #filename1 = r'\\141.20.140.91\NAS_Projects\Baltrak\Andrey\SHP\2007.shp'

    wrs2Footprints = ['160024','161023','161024']
    mgrsFootprints = ['41ULS', '41ULT', '41ULU', '41UMS', '41UMT', '41UMU', '41UMV', '41UNS', '41UNT', '41UNU', '41UNV',
                      '41UPS', '41UPT', '41UPU', '41UPV']

    # for sampling only
    mgrsFootprints = mgrsFootprints[:-1]

    WRS2Footprint.createUtmLookup(infolder=folder1, filter=wrs2Footprints)

    start = Date(1985, 1, 1)
    end = Date(2015, 12, 31)

    if i is not None:
        mgrsFootprints = mgrsFootprints[i:i+1]

    for inextension in ['.tif','.img']:
        composer = LandsatXComposer(inextension=inextension)
        #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=20)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=50)

    tsBuilder = TimeseriesBuilder(start=start, end=end)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints, processes=1)

    #MGRSArchive(folder4).saveAsGTiff(outfolder=folder4b, filter=mgrsFootprints, processes=1)
    #MGRSArchive(folder4).saveAsENVI(outfolder=folder4b, filter=mgrsFootprints, processes=10)

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5, of='GTiff',
                                footprints=mgrsFootprints, inextension='.img',
                                percentiles=[0, 5, 25, 50, 75, 95, 100],
                                variables=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr', 'msavi2'],
                                )
    for year in range(start.year, end.year+1):
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    #applier.apply()

    # build feature stacks for all years
    for year in range(start.year, end.year+1):

        stacker = StackApplier(outfolder=folder7, outproduct='stack', outimage=str(year)+'_stack', footprints=mgrsFootprints)
        for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr', 'msavi2']:
            stacker.appendFeatures(infolder=folder5, inproduct='statistics', inimage=key+'_'+str(year)+'-01-01_to_'+str(year)+'-12-31_'+str(bufferYears*2+1)+'y', inextension='.tif', inbands=None)
        #stacker.apply()


    for year in range(start.year, end.year + 1):
        print('draw sample', str(year))
        featureImage = str(year) + '_stack'
        labelImage = '2007_class'

        filenameRFC = join(folder9, str(year) + '.rfc')
        if 1:
            # - draw sample and train RFC
            sampleReader = SampleReadApplier(featureFolder=folder7, featureProduct='stack', featureImage=featureImage,
                                             featureExtension='.vrt',
                                             labelFolder=folder6, labelProduct='reference', labelImage=labelImage,
                                             labelExtension='.img',
                                             footprints=mgrsFootprints)
            sample = sampleReader.apply()
            hub.file.savePickle(var=sample, filename=join(folder9, str(year) + '.pkl'))
            rfc = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100, class_weight='balanced', n_jobs=20)
            rfc.pickle(filename=filenameRFC)
            rfc.fitSample(sample)
            filename = join(folder9, str(year) + '.json')
            exportSampleAsJSON(sample=sample, rfc=rfc, outfile=filename)
        else:
            rfc = hub.file.restorePickle(filename=filenameRFC)

        continue
        predictor = ClassifierPredictApplier(featureFolder=folder7, featureProduct='stack', featureImage=str(year)+'_stack', featureExtension='.vrt',
                                             outFolder=folder8, outProduct='rfc', outClassification=str(year)+'_rfc', outProbability=str(year)+'_rfprob', outExtension='.img',
                                             classifier=rfc, footprints=mgrsFootprints)
        predictor.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()


'''
import subprocess
for i in range(14):
    subprocess.call(['python', r'S:\janzandr\source\QGISPlugins\enmap-box\lamos\usecase\ad_kirgisistan.py', str(i)])
'''