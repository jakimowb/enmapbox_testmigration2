from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubflow.core import *

# open library
speclib = EnviSpectralLibrary(filename=enmapboxtestdata.library)

# treat library as raster with shape (wavelength, profiles, 1)
raster = speclib.raster()

# read profiles
print(raster.dataset().array().shape)

# read metadata
print(raster.dataset().metadataItem(key='wavelength', domain='ENVI', dtype=float))
# END