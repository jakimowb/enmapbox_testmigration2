from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

raster = Raster(filename=enmapboxtestdata.enmap)

# save raster with ENVI driver
copy = raster.saveAs(filename='raster.dat', driver=RasterDriver(name='ENVI'))
print(copy.dataset().driver())

# save raster with driver derived from file extension
copy2 = raster.saveAs(filename='raster.tif')
print(copy2.dataset().driver())
# END
