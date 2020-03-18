from hubdc.docutils import createDocPrint, createClassLegend
_print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

raster = Raster(filename=enmapboxtestdata.enmap)

mask = Mask.fromRaster(filename='mask.bsq', raster=raster, false=[range(0, 100)], initValue=True,
                       aggregateFunction=lambda a: np.all(a, axis=0))

# END
print(np.min(mask.array()), np.max(mask.array()))
MapViewer().addLayer(mask.dataset().mapLayer().initSingleBandGrayRenderer(grayMin=0, grayMax=1)).save(basename(__file__).replace('.py', '.png'))
