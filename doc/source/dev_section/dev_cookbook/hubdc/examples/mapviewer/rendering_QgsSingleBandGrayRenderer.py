from hubdc.core import *
MapViewer.show = lambda self: None # disable show

# START
import enmapboxtestdata
from hubdc.core import *
from qgis.core import QgsSingleBandGrayRenderer, QgsContrastEnhancement

# setup map viewer
rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
rasterBandDataset = rasterDataset.band(index=0)
mapViewer = MapViewer()
mapLayer = rasterDataset.band(index=0).mapLayer()
mapViewer.addLayer(mapLayer)

# setup layer rendering

# - default is to apply a 2% - 98% stretch on the selected band
mapLayer.initSingleBandGrayRenderer(grayIndex=0)

# - but it's also possible to set min-max stretch values explicitely
mapLayer.initSingleBandGrayRenderer(grayIndex=0, grayMin=179, grayMax=1026)

mapViewer.show()
# END

mapViewer.save(basename(__file__).replace('.py', '.png'))
