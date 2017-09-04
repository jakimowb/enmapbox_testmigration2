import matplotlib
matplotlib.use('QT4Agg')
from matplotlib import pyplot
from tempfile import gettempdir
from os.path import join, exists
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import gdal
from hubdc.applier import ApplierControls, ApplierInputOptions
import hubdc.progressbar
from hubflow.types import *
import enmapboxtestdata

overwrite = not True
#progressBar = [hubdc.progressbar.SilentProgressBar(), None][overwrite]
progressBar = hubdc.progressbar.SilentProgressBar()

outdir = join(gettempdir(), 'hubflow_testdata')
mask4mFilename = join(outdir, 'mask4m.img')
mask30mFilename = join(outdir, 'mask30m.img')
classification4mFilename = join(outdir, 'classification4m.img')
classification30mFilename = join(outdir, 'classification30m.img')
probability30mFilename = join(outdir, 'probability30m.img')

unsupervisedSampleFilename = join(outdir, 'unsupervisedSample.pkl')
classificationSampleFilename =  join(outdir, 'classificationSample.pkl')
regressionSampleFilename = join(outdir, 'regressionSample.pkl')
probabilitySampleFilename = join(outdir, 'probabilitySample.pkl')

classifierFilename = join(outdir, 'classifier.pkl')
regressorFilename = join(outdir, 'regressor.pkl')



image4m = Image(filename=enmapboxtestdata.hymap)
image30m = Image(filename=enmapboxtestdata.enmap)
vector = Vector(filename=enmapboxtestdata.landcover, dtype=numpy.uint8)
classDefinitionL1 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level1.names,
                                        lookup=enmapboxtestdata.landcoverClassDefinition.level1.lookup)
classDefinitionL2 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level2.names,
                                        lookup=enmapboxtestdata.landcoverClassDefinition.level2.lookup)
vectorClassificationL2 = VectorClassification(filename=enmapboxtestdata.landcover, idAttribute='Level_2_ID',
                                              classDefinition=classDefinitionL2,
                                              minOverallCoverage=1., minWinnerCoverage=0.5)
classification4m = Classification.fromVectorClassification(filename=classification4mFilename,
                                                           vectorClassification=vectorClassificationL2,
                                                           grid=image4m.pixelGrid, oversampling=10, overwrite=overwrite, progressBar=progressBar)
classification30m = Classification.fromVectorClassification(filename=classification30mFilename,
                                                           vectorClassification=vectorClassificationL2,
                                                           grid=image30m.pixelGrid, oversampling=10, overwrite=overwrite, progressBar=progressBar)
probability30m = Probability.fromVectorClassification(filename=classification30mFilename,
                                                      vectorClassification=vectorClassificationL2,
                                                      grid=image30m.pixelGrid, oversampling=10, overwrite=overwrite, progressBar=progressBar)
regression30m = probability30m.asRegression()
mask4m = classification4m.asMask()

if overwrite:
    unsupervisedSample = UnsupervisedSample.fromImageAndMask(image=image30m, mask=mask4m).pickle(filename=unsupervisedSampleFilename)
    classificationSample = ClassificationSample.fromImageAndClassification(image=image30m, classification=classification4m, mask=mask4m).pickle(filename=classificationSampleFilename)
    regressionSample = RegressionSample.fromImageAndRegression(image=image30m, regression=regression30m).pickle(filename=regressionSampleFilename)
    probabilitySample = ProbabilitySample.fromImageAndProbability(image=image30m, probability=probability30m).pickle(filename=probabilitySampleFilename)
    classifier = Classifier(sklEstimator=RandomForestClassifier()).fit(sample=classificationSample).pickle(filename=classifierFilename)
    regressor = Regressor(sklEstimator=RandomForestRegressor()).fit(sample=regressionSample).pickle(filename=regressorFilename)
else:
    unsupervisedSample = UnsupervisedSample.unpickle(filename=unsupervisedSampleFilename)
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    regressionSample = RegressionSample.unpickle(filename=regressionSampleFilename)
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySampleFilename)
    classifier = Classifier.unpickle(filename=classifierFilename)
    regressor = Regressor.unpickle(filename=regressorFilename)

if __name__ == '__main__':
    print('hubflow testdata directory: ' + outdir)
