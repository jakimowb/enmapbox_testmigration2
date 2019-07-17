from hubdc.docutils import createDocPrint, createClassLegend
print = createDocPrint(__file__)

# START
from hubflow.core import *

# create a raster
Raster.fromArray(array=[[[0, 1, 2, 3]]], filename='classification.bsq')

# open the raster as classification in Update mode
classification = Classification(filename='classification.bsq', eAccess=gdal.GA_Update)

# set the class definition
classDefinition = ClassDefinition(classes=3, names=['c1', 'c2', 'c3'], colors=['red', 'green', 'blue'])
classification.setClassDefinition(classDefinition)

# re-open the classification (required!)
classification.close()
classification = Classification(filename='classification.bsq')

print(classification)
# END

MapViewer().addLayer(classification.dataset().mapLayer()).save(basename(__file__).replace('.py', '.png'))
createClassLegend(__file__,
                  colors=[c.name() for c in classification.classDefinition().colors()],
                  names=classification.classDefinition().names())
