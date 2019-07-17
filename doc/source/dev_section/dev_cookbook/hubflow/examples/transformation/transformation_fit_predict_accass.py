from hubdc.docutils import createDocPrint, createReportSaveHTML
from hubflow.report import Report
print = createDocPrint(__file__)
Report.saveHTML = createReportSaveHTML()

# START
import enmapboxtestdata
from hubflow.core import *

# create (unsupervised) sample
raster = Raster(filename=enmapboxtestdata.enmap)
sample = Sample(raster=raster)

# fit transformer
from sklearn.decomposition import PCA
transformer = Transformer(sklEstimator=PCA(n_components=3))
transformer.fit(sample=sample)

# transform a raster
transformation = transformer.transform(filename='transformation.bsq', raster=raster)

# inverse transform
inverseTransformation = transformer.inverseTransform(filename='inverseTransformation.bsq', raster=transformation)
# END
MapViewer().addLayer(transformation.dataset().mapLayer()).\
    save(basename(__file__).replace('.py', '1.png'))
MapViewer().addLayer(inverseTransformation.dataset().mapLayer().initMultiBandColorRenderer(37, 22, 4)).\
    save(basename(__file__).replace('.py', '2.png'))
