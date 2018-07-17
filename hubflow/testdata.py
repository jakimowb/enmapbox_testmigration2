#import matplotlib
#matplotlib.use('QT4Agg')
#from matplotlib import pyplot
from tempfile import gettempdir
from os.path import join, exists
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from osgeo import gdal
import hubdc.progressbar
from hubflow.core import *
import enmapboxtestdata

overwrite = not True
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
                                                    classAttribute=enmapboxtestdata.landcoverAttributes.Level_2_ID,
                                                    classDefinition=classDefinitionL2,
                                                    minOverallCoverage=0., minDominantCoverage=0.,
                                                    oversampling=3)
hymapClassification = lambda overwrite=overwrite: Classification.fromClassification(filename=join(outdir, 'hymapLandCover.bsq'),
                                                                                    classification=vectorClassification(),
                                                                                    grid=hymap().grid(), overwrite=overwrite)

enmapClassification = lambda overwrite=overwrite: Classification.fromClassification(filename=join(outdir, 'enmapLandCover.bsq'),
                                                                                    classification=vectorClassification(),
                                                                                    grid=enmap().grid(), overwrite=overwrite)
hymapFraction = lambda overwrite=overwrite: Fraction.fromClassification(filename=join(outdir, 'hymapFraction.bsq'),
                                                                        classification=vectorClassification(),
                                                                        grid=hymap().grid(), overwrite=overwrite)
enmapFraction = lambda overwrite=overwrite: Fraction.fromClassification(filename=join(outdir, 'enmapFraction.bsq'),
                                                                        classification=vectorClassification(),
                                                                        grid=enmap().grid(), overwrite=overwrite)
hymapRegression = lambda overwrite=overwrite: Regression(filename=hymapFraction(overwrite=overwrite).filename())
enmapRegression = lambda overwrite=overwrite: Regression(filename=enmapFraction(overwrite=overwrite).filename())

enmapSample = lambda:Sample(raster=enmap(), mask=vector())
enmapClassificationSample = lambda: ClassificationSample(raster=enmap(), classification=enmapClassification(overwrite))
enmapFractionSample = lambda: FractionSample(raster=enmap(), fraction=enmapFraction(overwrite))
enmapRegressionSample = lambda: RegressionSample(raster=enmap(), regression=enmapRegression())

#hymapMask = lambda: hymapClassification.asMask()
#enmapMask = lambda: enmapClassification.asMask()
#unsupervisedSample = lambda: UnsupervisedSample.fromImageAndMask(image=enmap, mask=enmapMask)
#classificationSample = lambda: ClassificationSample.fromImageAndClassification(image=enmap, classification=hymapClassification)
#regressionSample = lambda: RegressionSample.fromImageAndRegression(image=enmap, regression=enmapFraction)
#fractionSample = lambda: FractionSample.fromImageAndFraction(image=enmap, fraction=enmapFraction)
#classifier = lambda: Classifier(sklEstimator=RandomForestClassifier()).fit(sample=classificationSample)
#regressor = lambda: Regressor(sklEstimator=RandomForestRegressor()).fit(sample=regressionSample)


if __name__ == '__main__':
    print('hubflow testdata directory: ' + outdir)

