from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import StatisticsApplier
from hub.timing import tic, toc
from hub.datetime import Date
from lamos.operators.stack import StackApplier
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
import hub.file
from enmapbox.processing.estimators import Classifiers

def test(i):

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatXMGRS'
    folder3b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatXMGRS_GTiff'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatTimeseriesMGRS_GTiff'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\statisticsMGRS_2'
    #folder5XXX = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\statisticsMGRS_XXX'

    folder6 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\referenceMGRS'
    folder7 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\stackMGRS'
    folder8 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\rfcMGRS'

    filename1 = r'\\141.20.140.91\NAS_Projects\Baltrak\Andrey\SHP\2007.shp'
    filename2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\2007_2.pkl'
    filename3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\2007_2.json'




    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['160024','161023','161024']
    mgrsFootprints = ['41ULS','41ULT','41ULU','41UMS','41UMT','41UMU','41UMV','41UNS','41UNT','41UNU','41UNV','41UPS','41UPT','41UPU','41UPV']
    #mgrsFootprints = ['41ULS', '41UPV']

    start = Date(1986, 1, 1)
    end = Date(2014, 12, 31)

    # mgrsFootprints = ['41UNS']
    #mgrsFootprints = mgrsFootprints[i:i+1]

    composer = LandsatXComposer(inextension='.tif')
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=50)


    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=50)

    tsBuilder = TimeseriesBuilder(start=start, end=end)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints)


    #MGRSArchive(folder4).saveAsGTiff(outfolder=folder4b, filter=mgrsFootprints, processes=20)

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5, of='GTiff',
                                footprints=mgrsFootprints, inextension='.tif',
                                percentiles=[0, 5, 25, 50, 75, 95, 100],
                                variables=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr', 'msavi2'],
                                )
    bufferYears = 2
    for year in range(start.year, end.year+1):
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)


#    applier.controls.setWindowXsize(256/16)
#    applier.controls.setWindowYsize(256/16)
#    applier.controls.setNumThreads(16*16)
    #applier.apply()

    # build feature stacks for all years
    for year in range(start.year, end.year+1):

        stacker = StackApplier(outfolder=folder7, outproduct='stack', outimage=str(year)+'_stack', footprints=mgrsFootprints)
        for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr', 'msavi2']:
            stacker.appendFeatures(infolder=folder5, inproduct='statistics', inimage=key+'_'+str(year)+'-01-01_to_'+str(year)+'-12-31_1y', inextension='.img', inbands=None)
        #stacker.apply()

    # draw sample for 2007
    sampleReader = SampleReadApplier(featureFolder=folder7, featureProduct='stack', featureImage='2007_stack', featureExtension='.vrt',
                                     labelFolder=folder6, labelProduct='reference', labelImage='2007_class', labelExtension='.img',
                                     footprints=mgrsFootprints)
    if 1:
        sample = sampleReader.apply()
        hub.file.savePickle(var=sample, file=filename2)
    else:
        sample = hub.file.restorePickle(file=filename2)

    return
    rfc = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100, class_weight='balanced', n_jobs=20)
    rfc._fit(sample)
    exportSampleAsJSON(sample=sample, rfc=rfc, outfile=filename3)

    # build feature stacks for all years
    for year in range(start.year, end.year+1):

        predictor = ClassifierPredictApplier(featureFolder=folder7, featureProduct='stack', featureImage=str(year)+'_stack', featureExtension='.vrt',
                                             outFolder=folder8, outProduct='rfc', outClassification=str(year)+'_rfc', outProbability=str(year)+'_rfprob', outExtension='.img',
                                             classifier=rfc, footprints=mgrsFootprints)
        predictor.apply()


if __name__ == '__main__':

    tic()
    test(0)
    toc()


'''
import subprocess
for i in range(14):
    subprocess.call(['python', r'S:\janzandr\source\QGISPlugins\enmap-box\lamos\usecase\ad_kirgisistan.py', str(i)])
'''