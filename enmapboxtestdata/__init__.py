from distutils.version import LooseVersion
from os.path import dirname, join

ENMAPBOXTESTDATA_VERSION = 'dev'
ENMAPBOXTESTDATA_VERSION_OBJ = LooseVersion(ENMAPBOXTESTDATA_VERSION)
__version__ = ENMAPBOXTESTDATA_VERSION

enmap = join(dirname(__file__), 'EnMAP02_Berlin_Urban_Gradient_2009_testData_compressed.bsq')
hymap = join(dirname(__file__), 'HighResolution_Berlin_Urban_Gradient_2009_testData_compressed.bsq')
landcover = join(dirname(__file__), 'LandCov_Vec_Berlin_Urban_Gradient_2009_subset.shp')
speclib = join(dirname(__file__), 'SpecLib_Berlin_Urban_Gradient_2009_244bands.sli')

