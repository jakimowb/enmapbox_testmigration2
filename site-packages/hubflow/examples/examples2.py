import tempfile
from os.path import join
import gdal
from hubdc.applier import ApplierControls, ApplierInputOptions
from hubflow.types import *
import enmapboxtestdata

image = Image(filename=enmapboxtestdata.enmap)
image2 = Image(filename=enmapboxtestdata.hymap)
vector = Vector(filename=enmapboxtestdata.landcover, dtype=numpy.uint8)
vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, idAttribute='Level_2_ID',
                                            classDefinition=ClassDefinition(names=['Roof',  'Pavement',   'Grass',   'Tree',   'Soil',    'Other'],
                                                                            lookup=[168,0,0, 156,156,156,  151,229,0, 35,114,0, 136,89,67, 236,214,0]),
                                            minOverallCoverage=1., minWinnerCoverage=0.5)

outdir = join(tempfile.gettempdir(), 'hubflow_test')
overwrite = not True
rasteredMaskFilename = join(outdir, 'rasteredMask.img')
rasteredClassificationFilename = join(outdir, 'rasteredClassification.img')
rasteredProbabilityFilename = join(outdir, 'rasteredProbability.img')
rasteredProbabilityRGBFilename = join(outdir, 'rasteredProbabilityRGB.img')
reportFilename = join(outdir, 'report.html')

def vectorRasterize():
    image = vector.rasterize(imageFilename=rasteredMaskFilename, grid=image2.pixelGrid, overwrite=overwrite)
    return image

def vectorUniqueValues():
    return vector.uniqueValues(attribute='Level_2_ID')

def vectorClassificationRasterizeAsClassification():
    classification = vectorClassification.rasterizeAsClassification(classificationFilename=rasteredClassificationFilename, grid=image2.pixelGrid, oversampling=1, overwrite=overwrite)
    return classification

def vectorClassificationRasterizeAsProbability():
    probability = vectorClassification.rasterizeAsProbability(probabilityFilename=rasteredProbabilityFilename, grid=image.pixelGrid, oversampling=10, overwrite=overwrite)
    return probability

def probabilityAsClassColorRGBImage():
    probability = vectorClassificationRasterizeAsProbability()
    image = probability.asClassColorRGBImage(imageFilename=rasteredProbabilityRGBFilename, overwrite=overwrite)
    return image

def imageSampleByClassification():
    classification = vectorClassificationRasterizeAsClassification()
    classificationSample = image.sampleByClassification(classification=classification, mask=vectorClassification)
    return classificationSample

def imageSampleByRegression():
    probability = vectorClassificationRasterizeAsProbability()
    regression = Regression(filename=probability.filename)
    classificationSample = image.sampleByRegression(regression=regression, mask=vectorClassification)
    return classificationSample

def imageSampleByProbability():
    probability = vectorClassificationRasterizeAsProbability()
    probabilitySample = image.sampleByProbability(probability=probability, mask=vectorClassification)
    return probabilitySample

def imageSampleByMask():
    mask = vectorRasterize().asMask()
    unsupervisedSample = image.sampleByMask(mask=mask)
    return unsupervisedSample

def classificationAssessClassificationPerformance():
    classification = vectorClassificationRasterizeAsClassification()
    classificationPerformance = classification.assessClassificationPerformance(classification=classification)
    return classificationPerformance

def regressionAssessRegressionPerformance():
    probability = vectorClassificationRasterizeAsProbability()
    regression = Regression(filename=probability.filename)
    regressionPerformance = regression.assessRegressionPerformance(regression=regression)
    return regressionPerformance

def classDefinitionFromText():

    classDefinition = ClassDefinition(names=['c1', 'c2'] ,lookup=[255,0,0, 0,0,255])

    snamesList =  ['c1, c2',               '[c1, c2]',               '{c1, c2}']
    slookupList = ['255, 0, 0, 0, 0, 255', '[255, 0, 0, 0, 0, 255]', '{255, 0, 0, 0, 0, 255}']

    for snames, slookup in zip(snamesList, slookupList):
        assert classDefinition.equal(other=ClassDefinition.fromText(snames=snames, slookup=slookup)), (snames, slookup)
    assert classDefinition.equal(other=ClassDefinition.fromText(snames='c1, c2', slookup=''), compareLookup=False), (snames, slookup)
    assert classDefinition.equal(other=ClassDefinition.fromText(snames='c1, c2', slookup=''), compareLookup=False), (snames, slookup)


if __name__ == '__main__':
    print('tmp directory: ' + outdir)
    #vectorRasterize()
    #print(vectorUniqueValues())
    #vectorClassificationRasterizeAsClassification()
    #vectorClassificationRasterizeAsProbability()

    #probabilityAsClassColorRGBImage()
    #print(imageSampleByClassification())
    #print(imageSampleByRegression())
    #print(imageSampleByProbability())
    #print(imageSampleByMask())

    classificationAssessClassificationPerformance().report().saveHTML(filename=reportFilename)
    #regressionAssessRegressionPerformance().report().saveHTML(filename=reportFilename)
    #classDefinitionFromText()
