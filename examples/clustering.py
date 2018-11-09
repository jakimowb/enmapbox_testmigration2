from hubflow.core import *
import enmapboxtestdata
from sklearn.cluster import KMeans

enmap = Raster(filename=enmapboxtestdata.enmap)
sample = Sample(raster=enmap, mask=VectorMask(filename=enmapboxtestdata.landcover_polygons))
kmeans = Clusterer(sklEstimator=KMeans())
kmeans.fit(sample=sample)
prediction = kmeans.predict(raster=enmap, filename='/vsimem/kmeansClassification.bsq')

if True:
    from enmapbox.__main__ import run
    run(sources=[prediction.filename()])
