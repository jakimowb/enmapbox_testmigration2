from distutils.version import LooseVersion
from os.path import dirname, join

ENMAPBOXTESTDATA_VERSION = '0.2'
ENMAPBOXTESTDATA_VERSION_OBJ = LooseVersion(ENMAPBOXTESTDATA_VERSION)
__version__ = ENMAPBOXTESTDATA_VERSION

enmap = join(dirname(__file__), 'EnMAP_BerlinUrbanGradient.bsq')
hymap = join(dirname(__file__), 'HighResolution_BerlinUrbanGradient.bsq')
landcover = join(dirname(__file__), 'LandCov_BerlinUrbanGradient.shp')
class landcoverAttributes():
    Level_1 = 'Level_1'
    Level_2 = 'Level_2'
    Level_1_ID = 'Level_1_ID'
    Level_2_ID = 'Level_2_ID'
class landcoverClassDefinition():
    class level1():
        names = ['Impervious', 'Vegetation', 'Soil', 'Other']
        lookup = [(156, 156, 156), (56, 168, 0), (168, 112, 0), (245, 245, 122)]
    class level2():
        names = ['Roof', 'Pavement', 'Low vegetation', 'Tree', 'Soil', 'Other']
        lookup = [(230, 0, 0),   (156, 156, 156),   (152, 230, 0),   (38, 115, 0),   (168, 112, 0), (245, 245, 122)]
        mappingToLevel1ByName = {'Roof':'Impervious', 'Pavement':'Impervious',
                                 'Low vegetation':'Vegetation', 'Tree':'Vegetation',
                                 'Soil':'Soil',
                                 'Other':'Other'}
        mappingToLevel1ById = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4}

speclib = join(dirname(__file__), 'SpecLib_BerlinUrbanGradient.sli')
