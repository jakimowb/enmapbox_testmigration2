#import matplotlib
#matplotlib.use('QT4Agg')
#from matplotlib import pyplot
from tempfile import gettempdir
from os.path import join, exists
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import gdal
import hubdc.progressbar
from hubflow.types import *
import enmapboxtestdata

overwrite=False
progressBar = hubdc.progressbar.CUIProgressBar
outdir = join(gettempdir(), 'hubflow_testdata')

hymap = lambda: Raster(filename=enmapboxtestdata.hymap)
enmap = lambda: Raster(filename=enmapboxtestdata.enmap)
vector = lambda: Vector(filename=enmapboxtestdata.landcover)
landcoverAttributes = enmapboxtestdata.landcoverAttributes
classDefinitionL1 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level1.names,
                                    colors=enmapboxtestdata.landcoverClassDefinition.level1.lookup)
classDefinitionL2 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level2.names,
                                    colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup)
vectorClassification = lambda: VectorClassification(filename=enmapboxtestdata.landcover,
                                                    nameAttribute=enmapboxtestdata.landcoverAttributes.Level_2,
                                                    classDefinition=classDefinitionL2,
                                                    minOverallCoverage=0., minWinnerCoverage=0.)
hymapClassification = lambda overwrite=overwrite: Classification.fromVectorClassification(filename=join(outdir, 'hymapLandCover.bsq'),
                                                                                          vectorClassification=vectorClassification(),
                                                                                          grid=hymap().grid, oversampling=10, overwrite=overwrite)
enmapClassification = lambda overwrite=overwrite: Classification.fromVectorClassification(filename=join(outdir, 'enmaplandCover.bsq'),
                                                                                          vectorClassification=vectorClassification(),
                                                                                          grid=enmap().grid, oversampling=10, overwrite=overwrite)
hymapProbability = lambda overwrite=overwrite: Probability.fromVectorClassification(filename=join(outdir, 'hymapProbability.bsq'),
                                                                                    vectorClassification=vectorClassification(),
                                                                                    grid=hymap().grid, oversampling=10, overwrite=overwrite)
enmapProbability = lambda overwrite=overwrite: Probability.fromVectorClassification(filename=join(outdir, 'enmapProbability.bsq'),
                                                                                    vectorClassification=vectorClassification(),
                                                                                    grid=enmap().grid, oversampling=10, overwrite=overwrite)
enmapRegression = lambda overwrite=overwrite: Regression(filename=enmapProbability(overwrite=overwrite).filename)
enmapProbabilitySample = lambda overwrite=overwrite: ProbabilitySample.fromRasterAndProbability(raster=enmap(), probability=enmapProbability(overwrite), grid=enmap())
enmapClassificationSample = lambda overwrite=overwrite: ClassificationSample.fromRasterAndClassification(raster=enmap(), classification=enmapClassification(overwrite), grid=enmap())
enmapUnsupervisedSample = lambda overwrite=overwrite: UnsupervisedSample.fromRasterAndMask(raster=enmap(), mask=vector(), grid=enmap())


#hymapMask = lambda: hymapClassification.asMask()
#enmapMask = lambda: enmapClassification.asMask()
#unsupervisedSample = lambda: UnsupervisedSample.fromImageAndMask(image=enmap, mask=enmapMask)
#classificationSample = lambda: ClassificationSample.fromImageAndClassification(image=enmap, classification=hymapClassification)
#regressionSample = lambda: RegressionSample.fromImageAndRegression(image=enmap, regression=enmapProbability)
#probabilitySample = lambda: ProbabilitySample.fromImageAndProbability(image=enmap, probability=enmapProbability)
#classifier = lambda: Classifier(sklEstimator=RandomForestClassifier()).fit(sample=classificationSample)
#regressor = lambda: Regressor(sklEstimator=RandomForestRegressor()).fit(sample=regressionSample)


if __name__ == '__main__':
    print('hubflow testdata directory: ' + outdir)

