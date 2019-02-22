from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubdc.core import *
import numpy as np

array = np.array([[ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [ 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                  [ 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                  [ 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1],
                  [ 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                  [ 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
                  [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

rasterDataset = RasterDataset.fromArray(array=array, filename='raster.tif', driver=GTiffDriver())
# END

rasterDataset.mapViewer().save(basename(__file__.replace('.py', '.png')))