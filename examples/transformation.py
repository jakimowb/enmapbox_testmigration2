from hubflow.core import *
import enmapboxtestdata
from sklearn.decomposition import PCA

enmap = Raster(filename=enmapboxtestdata.enmap)
sample = Sample(raster=enmap, mask=VectorMask(filename=enmapboxtestdata.landcover_polygons))
pca = Transformer(sklEstimator=PCA())
pca.fit(sample=sample)
transformation = pca.transform(raster=enmap, filename='/vsimem/pcaTransformation.bsq')
inverseTransformation = pca.inverseTransform(raster=transformation, filename='/vsimem/pcaInverseTransformation.bsq')

if True:
    from enmapbox.__main__ import run
    run(sources=[transformation.filename(), inverseTransformation.filename()])

