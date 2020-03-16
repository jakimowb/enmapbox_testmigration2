from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

# mask out all pixel that are covered by the vector
raster = Raster(filename=enmapboxtestdata.enmap)
mask = VectorMask(filename=enmapboxtestdata.landcover_polygons)
maskedRaster = raster.applyMask(filename='maskedRaster.bsq', mask=mask)

# mask out all pixel that are NOT covered by the vector
mask2 = VectorMask(filename=enmapboxtestdata.landcover_polygons, invert=True)
maskedRaster2 = raster.applyMask(filename='maskedRaster2.bsq', mask=mask2)

# END

extent = Extent(xmin=383382, ymin=5818224, xmax=385304, ymax=5819664, projection=raster.dataset().projection())
MapViewer().addLayer(maskedRaster.dataset().mapLayer().initMultiBandColorRenderer(63, 37, 23)).setExtent(extent).save(basename(__file__).replace('.py', '1.png'))
MapViewer().addLayer(maskedRaster2.dataset().mapLayer().initMultiBandColorRenderer(63, 37, 23)).setExtent(extent).save(basename(__file__).replace('.py', '2.png'))

