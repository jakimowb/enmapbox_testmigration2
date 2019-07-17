from hubdc.docutils import createDocPrint, createClassLegend

print = createDocPrint(__file__)

# START
from hubdc.core import *

rasterDataset = RasterDataset.fromArray(array=[[[0, 1, 2, 3]]], filename='raster.bsq', driver=EnviDriver())
band = rasterDataset.band(index=0)
band.setCategoryNames(names=['unclassified', 'class 1', 'class 2', 'class 3'])
band.setCategoryColors(colors=[(0,0,0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]) # list of rgb or rgba tuples
print(band.categoryNames())
print(band.categoryColors())
# END
rasterDataset = rasterDataset.reopen()
MapViewer().addLayer(rasterDataset.mapLayer()).save((basename(__file__.replace('.py', '.png'))))
from hubflow.core import Classification
classification = Classification.fromRasterDataset(rasterDataset)
createClassLegend(__file__,
                  colors=[c.name() for c in classification.classDefinition().colors()],
                  names=classification.classDefinition().names())
