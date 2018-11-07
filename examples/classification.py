from hubflow.core import *
import enmapboxtestdata
from sklearn.ensemble import RandomForestClassifier

enmap = Raster(filename=enmapboxtestdata.enmap)
points = VectorClassification(filename=enmapboxtestdata.landcover_points, classAttribute='level_2_id')
classification = Classification.fromClassification(filename='/vsimem/points.bsq', classification=points, grid=enmap.grid())
sample = ClassificationSample(raster=enmap, classification=classification)
rfc = Classifier(sklEstimator=RandomForestClassifier())
rfc.fit(sample=sample)
print(rfc.predict(raster=enmap, filename='/vsimem/rfcClassification.bsq'))
