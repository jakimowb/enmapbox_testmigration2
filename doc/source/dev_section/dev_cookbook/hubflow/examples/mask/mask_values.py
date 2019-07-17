from hubdc.docutils import createDocPrint, createClassLegend
lprint = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

# create classification
classification = Classification(filename=enmapboxtestdata.createRandomForestClassification())
print(classification)

# create mask for water bodies (id=5)
mask = Mask.fromRaster(filename='mask.bsq', raster=classification, true=[5])
# END

(MapViewer().addLayer(classification.dataset().mapLayer())
   # .setExtent(Extent(xmin=383293, ymin=5818720, xmax=385215, ymax=5820161, projection=classification.grid().projection()))
   #.show())
    .save(basename(__file__).replace('.py', '1.png')))
MapViewer().addLayer(mask.dataset().mapLayer()).save(basename(__file__).replace('.py', '2.png'))
