from os.path import dirname, join
import enmapboxtestdata

enmap = join(dirname(__file__), 'EnMAP_BerlinUrbanGradient.bsq')
landcover = join(dirname(__file__), 'LandCov_BerlinUrbanGradient.shp')
landcoverAttributes = enmapboxtestdata.landcoverAttributes
landcoverClassDefinition = enmapboxtestdata.landcoverClassDefinition
speclib = join(dirname(__file__), 'SpecLib_BerlinUrbanGradient.sli')
