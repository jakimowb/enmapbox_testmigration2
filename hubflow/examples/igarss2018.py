import matplotlib
matplotlib.use('QT5Agg')

from hubflow.core import *
from sklearn.ensemble import RandomForestClassifier
import enmapboxtestdata

# resample library spectra to EnMAP wavelength
library = ENVISpectralLibrary(filename=enmapboxtestdata.speclib)
enmapSensor = SensorDefinition.EnMAP()
enmapSpectra = enmapSensor.resampleRaster(filename='/vsimem/enmapSpectra.bsq',
                                          raster=library.raster())
# fit Random Forest Classifier and apply to an image
# - get class labels from library metadata
labels = Classification.fromRasterMetadata(filename='/vsimem/labels.bsq',
                                           raster=library.raster(),
                                           classificationSchemeName='level 2')
# - fit classifier on labeled spectra
classifier = Classifier(sklEstimator=RandomForestClassifier(n_estimators=100))
classifier.fit(sample=ClassificationSample(raster=enmapSpectra,
                                           classification=labels))
# - apply classifier to another image
classification = classifier.predict(filename='/vsimem/classification.bsq',
                                    raster=Raster(filename=enmapboxtestdata.enmap))



classification.dataset().plotCategoryBand()
Raster(filename=enmapboxtestdata.enmap).dataset().plotMultibandColor()