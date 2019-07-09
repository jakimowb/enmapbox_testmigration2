from hubdc.docutils import createDocPrint, createClassLegend
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

# create test classification
classification = Classification(filename=enmapboxtestdata.createClassification(gridOrResolution=5, level='level_3_id', oversampling=1))

# reclassify
reclassified = classification.reclassify(filename='classification.bsq',
                                         classDefinition=ClassDefinition(names=['urban', 'non-urban'], colors=['red', 'green']),
                                         mapping={1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2})

print(classification.classDefinition())
print(reclassified.classDefinition())
# END

extent = Extent(xmin=383982, ymin=5816395, xmax=384943, ymax=5817115, projection=classification.grid().projection())
MapViewer().addLayer(classification.dataset().mapLayer()).setExtent(extent).save(basename(__file__).replace('.py', '1.png'))
MapViewer().addLayer(reclassified.dataset().mapLayer()).setExtent(extent).save(basename(__file__).replace('.py', '2.png'))
createClassLegend(__file__, i=1,
                  colors=[c.name() for c in classification.classDefinition().colors()],
                  names=classification.classDefinition().names())
createClassLegend(__file__, i=2,
                  colors=[c.name() for c in reclassified.classDefinition().colors()],
                  names=reclassified.classDefinition().names())
