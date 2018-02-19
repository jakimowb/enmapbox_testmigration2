import matplotlib
matplotlib.use('QT4Agg')
from matplotlib import pyplot
from tempfile import gettempdir
from os.path import join
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import gdal
from hubdc.applier import ApplierControls, ApplierInputOptions
from hubflow.types import *
import enmapboxtestdata

image = Raster(filename=enmapboxtestdata.enmap)
image2 = Raster(filename=enmapboxtestdata.hymap)
vector = Vector(filename=enmapboxtestdata.landcover, dtype=numpy.uint8)
vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, idAttribute='Level_2_ID',
                                            classDefinition=ClassDefinition(names=['Roof',  'Pavement',   'Grass',   'Tree',   'Soil',    'Other'],
                                                                            colors=[168, 0, 0, 156, 156, 156, 151, 229, 0, 35, 114, 0, 136, 89, 67, 236, 214, 0]),
                                            minOverallCoverage=1., minWinnerCoverage=0.5)
def getRMask(): return vectorClassification_rasterizeAsClassification().asMask()
def getVMask(): return vector
def getClassification(): return vectorClassification_rasterizeAsClassification()
def getProbability(): return vectorClassification_rasterizeAsProbability()
def getRegression(): return getProbability().asRegression()
def getUnsupervisedSample(): return UnsupervisedSample.fromRasterAndMask(raster=image, mask=getRMask())
def getClassificationSample(): return ClassificationSample.fromRasterAndClassification(raster=image, classification=getClassification())
def getRegressionSample(): return RegressionSample.fromRasterAndRegression(raster=image, regression=getRegression())
def getProbabilitySample(): return ProbabilitySample.fromRasterAndProbability(raster=image, probability=getProbability())
def getClassifier(): return Classifier(sklEstimator=RandomForestClassifier()).fit(sample=getClassificationSample())
def getRegressor(): return Regressor(sklEstimator=RandomForestRegressor()).fit(sample=getRegressionSample())

outdir = join(gettempdir(), 'hubflow_test')
overwrite = not True
rasteredMaskFilename = join(outdir, 'rasteredMask.img')
rasteredClassificationFilename = join(outdir, 'rasteredClassification.img')
rasteredProbabilityFilename = join(outdir, 'rasteredProbability.img')
rasteredProbabilityRGBFilename = join(outdir, 'rasteredProbabilityRGB.img')
reportFilename = join(outdir, 'report.html')

def flowObject_unpickle():
    #FlowObject.unpickle(enmapboxtestdata.enmap)

    classDefinition = ClassDefinition(classes=3)
    classDefinition.pickle(filename=r'c:\outputs\classDefinition.pkl')
    x = ClassDefinition.unpickle(filename=r'c:\outputs\classDefinition.pkl')

def vector_rasterize():
    image = vector.rasterize(imageFilename=rasteredMaskFilename, grid=image2.grid, overwrite=overwrite)
    return image

def vector_uniqueValues():
    return vector.uniqueValues(attribute='Level_2_ID')

def vectorClassification_rasterizeAsClassification():
    classification = vectorClassification.rasterizeAsClassification(classificationFilename=rasteredClassificationFilename, grid=image2.grid, oversampling=1, overwrite=overwrite)
    return classification

def vectorClassification_rasterizeAsProbability():
    probability = vectorClassification.rasterizeAsProbability(probabilityFilename=rasteredProbabilityFilename, grid=image.grid, oversampling=10, overwrite=overwrite)
    return probability

def probability_asClassColorRGBImage():
    probability = vectorClassification_rasterizeAsProbability()
    image = probability.asClassColorRGBRaster(imageFilename=rasteredProbabilityRGBFilename, overwrite=overwrite)
    return image

def probability_subsetClassesByNames():
    probability = vectorClassification_rasterizeAsProbability()
    probability2 = probability.subsetClassesByName(filename=join(outdir, 'fractionsSubset.img'), names=probability.classDefinition.names)

def probabilitySample_subsetClassesByNames():
    probabilitySample = image_sampleByProbability()
    probabilitySample2 = probabilitySample.subsetClassesByName(names=probabilitySample.classDefinition.names[-1:])
    print(numpy.all(probabilitySample.features == probabilitySample2.features))
    print(numpy.all(probabilitySample.labels[-1:] == probabilitySample2.labels))

def classificationSample_asProbabilitySample():
    classificationSample = image_sampleByClassification()
    probabilitySample = classificationSample.asProbabilitySample()
    return probabilitySample

def image_sampleByClassification():
    classification = vectorClassification_rasterizeAsClassification()
    classificationSample = image.sampleByClassification(classification=classification, mask=vectorClassification)
    return classificationSample

def image_sampleByRegression():
    probability = vectorClassification_rasterizeAsProbability()
    regression = Regression(filename=probability.filename)
    classificationSample = image.sampleByRegression(regression=regression, mask=vectorClassification)
    return classificationSample

def image_sampleByProbability():
    probability = vectorClassification_rasterizeAsProbability()
    probabilitySample = image.sampleByProbability(probability=probability, mask=vectorClassification)
    return probabilitySample

def image_sampleByMask():
    unsupervisedSample = image.sampleByMask(mask=getRMask())
    return unsupervisedSample

def image_basicStatistics(mask=getRMask()):
    grid = image.grid.newResolution(xRes=image.grid.xRes, yRes=image.grid.yRes)
    min, max, mean, n = image.basicStatistics(bandIndicies=None, mask=mask, grid=grid)
    return min, max, mean, n

def image_scatterMatrix(stratify=False):
    stratification = vectorClassification_rasterizeAsClassification()
    i1, i2 = 0, 1
    (min1, min2), (max1, max2), (mean1, mean2), (n1, n2) = image.basicStatistics(bandIndicies=[i1, i2], mask=getRMask())

    H, xedges, yedges = image.scatterMatrix(raster2=image, bandIndex1=i1, bandIndex2=i2,
                                            range1=[min1, max1], range2=[min2, max2], bins=10,
                                            mask=getRMask(), stratification=stratification if stratify else None)
    return H, xedges, yedges

def classificationAssessClassificationPerformance():
    classification = vectorClassification_rasterizeAsClassification()
    classificationPerformance = classification.assessClassificationPerformance(classification=classification)
    return classificationPerformance

def regressionAssessRegressionPerformance():
    probability = vectorClassification_rasterizeAsProbability()
    regression = Regression(filename=probability.filename)
    regressionPerformance = regression.assessRegressionPerformance(regression=regression)
    return regressionPerformance

def test_signalingFileCreation():
    from hubflow import signals
    def handler(filename):
        print('Handler was invoked by file creation: {}'.format(filename))
    signals.sigFileCreated.connect(handler)

    FlowObject().pickle(filename=join(outdir, 'dummy.pkl'))

def createAllFlowTypesAsPickle():
    print(FlowObject().pickle(join(outdir, 'FlowObject.pkl')))
    print('')
    print(getClassification().classDefinition.pickle(join(outdir, 'ClassDefinition.pkl')))
    print('')
    print(getUnsupervisedSample().pickle(join(outdir, 'UnsupervisedSample.pkl')))
    print('')
    print(getClassificationSample().pickle(join(outdir, 'ClassificationSample.pkl')))
    print('')
    print(getRegressionSample().pickle(join(outdir, 'RegressionSample.pkl')))
    print('')
    print(getProbabilitySample().pickle(join(outdir, 'ProbabilitySample.pkl')))
    print('')
    print(getClassifier().pickle(join(outdir, 'Classifier.pkl')))
    print('')
    print(getRegressor().pickle(join(outdir, 'Regressor.pkl')))
    print('')
    print('created pkl files are here: '+outdir)

if __name__ == '__main__':
    print('output directory: ' + outdir)

    createAllFlowTypesAsPickle()
    exit()
    flowObject_unpickle()
    #vector_rasterize()
    #print(vector_uniqueValues())
    #vectorClassification_rasterizeAsClassification()
    #vectorClassification_rasterizeAsProbability()

    #probability_asClassColorRGBImage()
    print(image_sampleByClassification())
    print(image_sampleByRegression())
    print(image_sampleByProbability())
    print(image_sampleByMask())
    #print(image_basicStatistics(mask=getRMask()))
    #print(image_basicStatistics(mask=getVMask()))

    #print(image_scatterMatrix(stratify=True))

    #classificationAssessClassificationPerformance().report().saveHTML(filename=reportFilename)
    #regressionAssessRegressionPerformance().report().saveHTML(filename=reportFilename)
    #test_signalingFileCreation()
    #probability_subsetClassesByNames()
    #probabilitySample_subsetClassesByNames()
    #classificationSample_asProbabilitySample()