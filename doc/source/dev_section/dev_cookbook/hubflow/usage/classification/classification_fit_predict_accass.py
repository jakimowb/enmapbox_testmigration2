from hubdc.docutils import createDocPrint, createReportSaveHTML, createClassLegend, createPyPlotSavefig
from hubflow.core import *

print = createDocPrint(__file__)
Report.saveHTML = createReportSaveHTML()
plt.show = createPyPlotSavefig(filename=basename(__file__).replace('.py', '1.png'))

# START
import enmapboxtestdata
from hubflow.core import *

# create classification sample
raster = Raster(filename=enmapboxtestdata.enmap)
classification = Classification(filename=enmapboxtestdata.createClassification(gridOrResolution=raster.grid(), level='level_2_id', oversampling=5))
sample = ClassificationSample(raster=raster, classification=classification)

# fit classifier
from sklearn.ensemble import RandomForestClassifier
classifier = Classifier(sklEstimator=RandomForestClassifier(n_estimators=10))
classifier.fit(sample=sample)

# plot feature importances
plt.plot(classifier.sklEstimator().feature_importances_)
plt.show()

# classify a raster
prediction = classifier.predict(filename='randonForestClassification.bsq', raster=raster)

# asses accuracy
performance = ClassificationPerformance.fromRaster(prediction=prediction, reference=classification)
performance.report().saveHTML(filename='ClassificationPerformance.html')
# END
MapViewer().addLayer(prediction.dataset().mapLayer()).save(basename(__file__).replace('.py', '2.png'))
createClassLegend(__file__,
                  colors=[c.name() for c in classification.classDefinition().colors()],
                  names=classification.classDefinition().names())
