#copy with high-contrast theme

from enmapbox.testing import initQgisApplication
APP = initQgisApplication()

# start the EnMAP-Box
from enmapbox import EnMAPBox
enmapBox = EnMAPBox(None)
enmapBox.loadExampleData()

enmapBox.createDock('MAP') # add a new map
enmapBox.createDock('SPECLIB') # add a spectral library viewer



APP.exec_()
myApp = MyEnMAPBoxWorkshopApplication(enmapBox)
assert isinstance(myApp, EnMAPBoxApplication)
enmapBox.addApplication(myApp)


from hubflow.core import *
from sklearn.ensemble import RandomForestClassifier
import enmapboxtestdata

# resample library spectra to EnMAP wavelength
library = EnviSpectralLibrary(filename=enmapboxtestdata.speclib)
enmapSensor = SensorDefinition.EnMAP()
enmapSpectra = enmapSensor.resampleRaster(filename='/vsimem/enmapSpectra.bsq',
                                          raster=library.raster())

# fit Random Forest Classifier and apply to an image
# get class labels from library metadata
labels = Classification.fromRasterMetadata(filename='/vsimem/labels.bsq',
                                           raster=library.raster(),
                                           classificationSchemeName='level 2')
# fit classifier on labeled spectra
classifier = Classifier(sklEstimator=RandomForestClassifier())
classifier.fit(sample=ClassificationSample(raster=enmapSpectra,
                                           classification=labels))
# apply classifier to another image
classification = classifier.predict(filename='/vsimem/classification.bsq',
                                    raster=Raster(filename=enmapboxtestdata.enmap))

