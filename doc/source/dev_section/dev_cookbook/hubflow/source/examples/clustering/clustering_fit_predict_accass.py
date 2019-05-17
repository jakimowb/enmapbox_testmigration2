from hubdc.docutils import createDocPrint, createReportSaveHTML, createClassLegend
from hubflow.report import Report
print = createDocPrint(__file__)
Report.saveHTML = createReportSaveHTML()

# START
import enmapboxtestdata
from hubflow.core import *

# create (unsupervised) sample
raster = Raster(filename=enmapboxtestdata.enmap)
sample = Sample(raster=raster)

# fit clusterer
from sklearn.cluster import KMeans
clusterer = Clusterer(sklEstimator=KMeans(n_clusters=5))
clusterer.fit(sample=sample)

# cluster a raster
prediction = clusterer.predict(filename='kmeanClustering.bsq', raster=raster)

# asses accuracy
reference = Classification(filename=enmapboxtestdata.createClassification(gridOrResolution=raster.grid(), level='level_2_id', oversampling=5))
performance = ClusteringPerformance.fromRaster(prediction=prediction, reference=reference)
performance.report().saveHTML(filename='ClusteringPerformance.html')
# END
MapViewer().addLayer(prediction.dataset().mapLayer()).save(basename(__file__).replace('.py', '.png'))
createClassLegend(__file__,
                  colors=[c.name() for c in prediction.classDefinition().colors()],
                  names=prediction.classDefinition().names())
