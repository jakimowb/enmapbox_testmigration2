#from hubdc.applier import Applier, ApplierOperator
#from hubdc.model import PixelGrid, Dataset, Layer, Create, CreateFromArray, Open, OpenLayer

from distutils.version import LooseVersion

HUBDC_VERSION = '0.4.1'
HUBDC_VERSION_OBJ = LooseVersion(HUBDC_VERSION)
__version__ = HUBDC_VERSION