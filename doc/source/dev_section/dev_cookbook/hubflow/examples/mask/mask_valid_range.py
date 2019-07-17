from hubdc.docutils import createDocPrint, createClassLegend
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

raster = Raster(filename=enmapboxtestdata.enmap)
mask = Mask.fromRaster(filename='mask.bsq', raster=raster, true=[range(0, 100)],
                       aggregateFunction=lambda a: np.any(a, axis=0))
# END

MapViewer().addLayer(mask.dataset().mapLayer()).save(basename(__file__).replace('.py', '.png'))
