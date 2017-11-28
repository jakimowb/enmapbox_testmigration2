#import matplotlib
#matplotlib.use('QT4Agg')
#from matplotlib import pyplot

from tempfile import gettempdir
from os.path import join
from osgeo import gdal
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from hubflow.types import *
import hubflow.testdata
import enmapboxtestdata


overwrite = not True
vector = hubflow.testdata.vector()
hymap =  hubflow.testdata.hymap()
enmap =  hubflow.testdata.enmap()

hymapClassification = hubflow.testdata.hymapClassification(overwrite=overwrite)
enmapClassification = hubflow.testdata.enmapClassification(overwrite=overwrite)
vectorClassification = hubflow.testdata.vectorClassification()
hymapProbability = hubflow.testdata.hymapProbability(overwrite=overwrite)
enmapProbability = hubflow.testdata.enmapProbability(overwrite=overwrite)
enmapMask = enmapClassification.asMask()

enmapProbabilitySample = hubflow.testdata.enmapProbabilitySample(overwrite=overwrite)
enmapClassificationSample = hubflow.testdata.enmapClassificationSample(overwrite=overwrite)
enmapUnsupervisedSample = hubflow.testdata.enmapUnsupervisedSample(overwrite=overwrite)

outdir = join(gettempdir(), 'hubflow_test')

def test_Classification():
    print(Classification.fromVectorClassification(filename=join(outdir, 'hymapLandCover.img'), vectorClassification=vectorClassification, grid=hymap.pixelGrid, oversampling=10, overwrite=overwrite))
    print(hymapClassification.reclassify(filename=join(outdir, 'classificationReclassify.img'),
                                         classDefinition=hubflow.testdata.classDefinitionL1,
                                         mapping=enmapboxtestdata.landcoverClassDefinition.level2.mappingToLevel1ByName))


def test_ClassificationPerformance():
    obj = ClassificationPerformance.fromClassification(prediction=enmapClassification, reference=enmapClassification)
    print(obj)
    #obj.report().saveHTML(filename=join(outdir, 'report.html'))

def test_ClassificationSample():
    print(ClassificationSample.fromImageAndClassification(image=enmapClassification, classification=hymapClassification, grid=enmap, mask=vector))
    print(ClassificationSample.fromImageAndClassification(image=enmapProbability, classification=hymapClassification, grid=enmap, mask=vector))
    print(ClassificationSample.fromImageAndClassification(image=enmap, classification=hymapClassification, grid=enmap, mask=vector))
    print(ClassificationSample.fromImageAndProbability(image=enmap, probability=hymapProbability, grid=enmap, mask=vector))
    print(ClassificationSample.fromProbabilitySample(sample=enmapProbabilitySample))

    print(enmapClassificationSample.asProbabilitySample())
    classificationSample = ClassificationSample.fromENVISpectralLibrary(enmapboxtestdata.speclib, classificationSchemeName='level 2 ')
    print(classificationSample)
    print(classificationSample.synthMix(mixingComplexities={2:0.7, 3:0.3}, classLikelihoods='equalized', n=10))

def test_Classifier():
    rfc = Classifier(sklEstimator=RandomForestClassifier())
    print(rfc)
    rfc.fit(sample=enmapClassificationSample)
    print(rfc.predict(filename=join(outdir, 'rfcClassification.img'), image=enmap, mask=vector))

def test_Clusterer():
    kmeans = Clusterer(sklEstimator=KMeans())
    print(kmeans)
    kmeans.fit(sample=enmapClassificationSample)
    print(kmeans.predict(filename=join(outdir, 'kmeansClustering.img'), image=enmap, mask=vector))

def test_Image():
    print(Image.fromVector(filename=join(outdir, 'imageFromVector.img'), vector=vector, grid=hymap.pixelGrid, overwrite=overwrite))
    print(enmap.basicStatistics(bandIndicies=None, mask=vector, grid=enmap))

    i1, i2 = 0, 1
    (min1, min2), (max1, max2), (mean1, mean2), (n1, n2) = enmap.basicStatistics(bandIndicies=[i1, i2], mask=vector)
    H, xedges, yedges = enmap.scatterMatrix(image2=enmap, bandIndex1=i1, bandIndex2=i2, range1=[min1, max1], range2=[min2, max2], bins=10,
                                            mask=vector, stratification=hymapClassification)
    print(H)

def test_Mask():
    print(Mask.fromVector(filename=join(outdir, 'maskFromVector.img'), vector=vector, grid=enmap))

def test_Probability():
    print(enmapProbability.asClassColorRGBImage(filename=join(outdir, 'probabilityAsClassColorRGBImage.img'), overwrite=overwrite))
    print(Probability.fromVectorClassification(filename=join(outdir, 'enmapProbability.img'), vectorClassification=vectorClassification, grid=enmap.pixelGrid, oversampling=10, overwrite=overwrite))
    print(enmapProbability.subsetClassesByName(filename=join(outdir, 'probabilitySubsetClassesByName.img'), names=enmapProbability.classDefinition.names))

def test_ProbabilitySample():
    print(ProbabilitySample.fromImageAndProbability(image=enmap, probability=hymapProbability, grid=enmap, mask=vector))
    print(ProbabilitySample.fromImageAndProbability(image=enmap, probability=hymapClassification, grid=enmap))
    print(ProbabilitySample.fromImageAndProbability(image=enmap, probability=vectorClassification, grid=enmap))
    print(ProbabilitySample.fromImageAndClassification(image=enmap, classification=hymapClassification, grid=enmap))
    print(enmapProbabilitySample.subsetClasses(labels=[1,3]))
    print(enmapProbabilitySample.subsetClassesByName(names=enmapProbabilitySample.classDefinition.names))
    print()

def test_Regression():
    print(enmapProbability.asMask())

def test_RegressionPerformance():
    obj = RegressionPerformance.fromRegression(prediction=enmapProbability, reference=enmapProbability)
    print(obj)
    #obj.report().saveHTML(filename=join(outdir, 'report.html'))

def test_RegressionSample():
    print(RegressionSample.fromImageAndRegression(image=enmap, regression=hymapProbability, grid=enmap, mask=vector))

def test_Regressor():
    rfr = Regressor(sklEstimator=RandomForestRegressor())
    print(rfr)
    rfr.fit(sample=enmapProbabilitySample)
    print(rfr.predict(filename=join(outdir, 'rfrRegression.img'), image=enmap, mask=vector))

def test_Transformer():
    pca = Transformer(sklEstimator=PCA())
    print(pca)
    pca.fit(sample=enmapUnsupervisedSample)
    pcaTransformation = pca.transform(filename=join(outdir, 'pcaTransformation.img'), image=enmap, mask=vector)
    print(pcaTransformation)
    pcaInverseTransform = pca.inverseTransform(filename=join(outdir, 'pcaInverseTransformation.img'), image=pcaTransformation, mask=vector)
    print(pcaInverseTransform)

def test_UnsupervisedSample():
    unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=enmapboxtestdata.speclib)
    print(unsupervisedSample)
    unsupervisedSample.saveAsENVISpectralLibrary(filename=join(outdir, 'speclib.sli'))
    unsupervisedSample.scaleFeaturesInplace(factor=10000)
    print(unsupervisedSample.classifyByName(names=unsupervisedSample.metadata['level 2 class spectra names'], classDefinition=hubflow.testdata.classDefinitionL2))
    print(UnsupervisedSample.fromImageAndMask(image=enmap, mask=vector, grid=enmap))

def test_Vector():
    print(vector.uniqueValues(attribute=hubflow.testdata.landcoverAttributes.Level_2_ID))
    print(vector.uniqueValues(attribute=hubflow.testdata.landcoverAttributes.Level_2))
    print(vector)

def test_VectorClassification():
    print(vectorClassification.asVector())

def run():

    test_Classification()
    test_ClassificationPerformance()
    test_ClassificationSample()
    test_Classifier()
    test_Clusterer()
    test_Image()
    test_Mask()
    test_Probability()
    test_ProbabilitySample()
    test_Regression()
    test_RegressionPerformance()
    test_RegressionSample()
    test_Regressor()
    test_Transformer()
    test_UnsupervisedSample()
    test_Vector()
    test_VectorClassification()

if __name__ == '__main__':
    print('output directory: ' + outdir)
    run()