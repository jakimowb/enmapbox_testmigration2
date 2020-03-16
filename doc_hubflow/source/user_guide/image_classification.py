import tempfile
from os.path import join
from sklearn.ensemble import RandomForestClassifier
from hubflow.core import *
import enmapboxtestdata

outdir = join(tempfile.gettempdir(), 'enmap_box')

# open data / preprocessing

enmap = Raster(filename=enmapboxtestdata.enmap)
classDefinition = ClassDefinition(classes=6, names=['Roof', 'Pavement', 'Low vegetation', 'Tree', 'Soil', 'Other'],
                                  colors=['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#f5f57a'])
vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classAttribute='Level_2_ID',
                                            classDefinition=classDefinition)
classification = Classification.fromClassification(classification=vectorClassification,
                                                   grid=enmap.grid(),
                                                   filename=join(outdir, 'classification.bsq'))

# fit classifier

sample = ClassificationSample(raster=enmap, classification=classification)
rfc = Classifier(sklEstimator=RandomForestClassifier())
rfc.fit(sample=sample)

# predict image

rfcClassification = rfc.predict(raster=enmap, filename=join(outdir, 'rfcClassification.bsq'))
rfcProbability = rfc.predictProbability(raster=enmap, filename=join(outdir, 'rfcProbability.bsq'))

print(rfcClassification)
print(rfcProbability)

# accuracy assessment

performance = ClassificationPerformance.fromRaster(prediction=rfcClassification, reference=classification)
report = performance.report().saveHTML(filename=join(outdir, 'accass.html'), open=False)

print(report.filename)

# splitting the reference data

counts = classification.statistics()
n = [int(round(count * 0.3)) for count in counts]
points = Vector.fromRandomPointsFromClassification(filename=join(outdir, 'points.gpkg'), classification=classification,
                                                   n=n)
train = classification.applyMask(filename=join(outdir, 'training.bsq'), mask=points)
test =  classification.applyMask(filename=join(outdir, 'test.bsq'),
                                 mask=VectorMask(filename=points.filename(), invert=True))

print(train.filename())
print(test.filename())
