from hubdc.core import *
MapViewer.show = lambda self: None # disable show

# START
import enmapboxtestdata
from hubdc.core import *

# setup map viewer
rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
mapViewer = MapViewer()
mapLayer = rasterDataset.mapLayer()
mapViewer.addLayer(mapLayer)

# setup layer rendering

# - default is to apply a 2% - 98% stretch on the selected bands
mapLayer.initMultiBandColorRenderer(redIndex=63, greenIndex=37, blueIndex=23)

# - but it's also possible to set min-max stretch values explicitely
mapLayer.initMultiBandColorRenderer(redIndex=63, greenIndex=37, blueIndex=23,
                                    redMin=809, redMax=2861,
                                    greenMin=183, greenMax=1370,
                                    blueMin=279, blueMax=1275)

mapViewer.show()
# END

mapViewer.save(basename(__file__).replace('.py', '.png'))
