from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

# open raster and vector points
enmap = Raster(filename=enmapboxtestdata.enmap)
points = VectorClassification(filename=enmapboxtestdata.landcover_points, classAttribute='level_2_id')

# rasterize points onto raster grid
classification = Classification.fromClassification(classification=points, grid=enmap.grid(), filename='/vsimem/classification.bsq')

# create classification sample
sample = ClassificationSample(raster=enmap, classification=classification)

# create ENVI spectral library from sample
speclib = EnviSpectralLibrary.fromSample(sample=sample, filename='speclib.sli')
# END

import pyqtgraph as pg
import pyqtgraph.exporters
plot = pg.plot()
for y in range(speclib.raster().dataset().ysize()):
    speclib.raster().dataset().plotZProfile(pixel=Pixel(x=0, y=y), spectral=True, plotWidget=plot)

exporter = pyqtgraph.exporters.ImageExporter(plot.plotItem)
# workaround a bug with float conversion to int
exporter.params.param('width').setValue(600, blockSignal=exporter.widthChanged)
exporter.params.param('height').setValue(400, blockSignal=exporter.heightChanged)
exporter.export('library_from_raster_and_points.png')
