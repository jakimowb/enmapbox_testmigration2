import matplotlib
matplotlib.use('QT4Agg')
from matplotlib import pyplot
from tempfile import gettempdir
from os.path import join
import gdal
from hubflow.types import *
from hubflow.testdata import *

outdir = join(gettempdir(), 'hubflow_test')
overwrite = True

#class FlowObject():
#    def pickle():
#    def unpickle():

def vector_rasterize():
    image = vector.rasterize(imageFilename=mask4mFilename, grid=image4m.pixelGrid, overwrite=overwrite)
    return image

def vector_uniqueValues():
    return vector.uniqueValues(attribute='Level_2_ID')

def vectorClassification_rasterizeAsClassification():
    classification = vectorClassification.rasterizeAsClassification(classificationFilename=classification4mFilename, grid=image4m.pixelGrid, oversampling=1, overwrite=overwrite)
    return classification

def vectorClassification_rasterizeAsProbability():
    probability = vectorClassification.rasterizeAsProbability(probabilityFilename=probabilityFilename, grid=image.pixelGrid, oversampling=10, overwrite=overwrite)
    return probability

def probability_asClassColorRGBImage():
    probability = vectorClassification_rasterizeAsProbability()
    image = probability.asClassColorRGBImage(imageFilename=probabilityRGBFilename, overwrite=overwrite)
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
    unsupervisedSample = image.sampleByMask(mask=getMask())
    return unsupervisedSample

def image_basicStatistics():
    grid = image.pixelGrid.newResolution(xRes=image.pixelGrid.xRes, yRes=image.pixelGrid.yRes)
    min, max, mean, n = image.basicStatistics(bandIndicies=None, mask=mask, grid=grid)
    return min, max, mean, n

def image_scatterMatrix(stratify=False):
    stratification = vectorClassification_rasterizeAsClassification()
    i1, i2 = 0, 1
    (min1, min2), (max1, max2), (mean1, mean2), (n1, n2) = image.basicStatistics(bandIndicies=[i1, i2], mask=getMask())

    H, xedges, yedges = image.scatterMatrix(image2=image, bandIndex1=i1, bandIndex2=i2,
                                            range1=[min1, max1], range2=[min2, max2], bins=10,
                                            mask=getMask(), stratification=stratification if stratify else None)
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

def classificationReclassify():
    classification4m.reclassify(filename=join(outdir, 'output_classificationReclassify.img'), classDefinition=classDefinitionL1,
                                mapping=enmapboxtestdata.landcoverClassDefinition.level2.mappingToLevel1ByName)
    print(classDefinitionL1)
    print(enmapboxtestdata.landcoverClassDefinition.level2.mappingToLevel1ByName)

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

    #createAllFlowTypesAsPickle()
    #flowObject_unpickle()
    #vector_rasterize()
    #print(vector_uniqueValues())
    #vectorClassification_rasterizeAsClassification()
    #vectorClassification_rasterizeAsProbability()

    #probability_asClassColorRGBImage()
    #print(image_sampleByClassification())
    #print(image_sampleByRegression())
    #print(image_sampleByProbability())
    #print(image_sampleByMask())
    #print(image_basicStatistics(mask=getRMask()))
    #print(image_basicStatistics(mask=getVMask()))

    #print(image_scatterMatrix(stratify=True))

    #classificationAssessClassificationPerformance().report().saveHTML(filename=reportFilename)
    #regressionAssessRegressionPerformance().report().saveHTML(filename=reportFilename)
    #test_signalingFileCreation()
    #probability_subsetClassesByNames()
    #probabilitySample_subsetClassesByNames()
    #classificationSample_asProbabilitySample()
    classificationReclassify()