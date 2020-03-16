from hubdc.core import *

MapViewer.show = lambda self: None # disable show

# START1
import enmapboxtestdata
from hubdc.core import *

# Starting a map viewer from a multiband raster results in a MultiBandColorRenderer representation.
# Note that enmapboxtestdata.enmap has a default style defined (see .qml file next to it).
rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
MapViewer().addLayer(rasterDataset.mapLayer()).show()

# END1
# START2
# Starting a map viewer from a raster band results in a SingleBandGrayRenderer representation.
rasterBandDataset = rasterDataset.band(index=0)
MapViewer().addLayer(rasterBandDataset.mapLayer()).show()

# END2
# START3
# Starting a map viewer from a vector results in a SingleSymbolRenderer representation by default.
# Note that enmapboxtestdata.landcover_points uses a CategorizedSymbolRenderer as default (see .qml file next to it).
vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_points)
#vectorDataset.mapLayer().show()
#vectorDataset.mapViewer().show()
MapViewer().addLayer(vectorDataset.mapLayer()).show()

# END3
# START4
# Starting a map viewer from a raster band with a color lookup table results in a PalettedRasterRenderer representation.
rasterDatasetWithLookupTable = openRasterDataset(enmapboxtestdata.createClassification(gridOrResolution=10, level='level_3_id'))
MapViewer().addLayer(rasterDatasetWithLookupTable.mapLayer()).show()
# END4

MapViewer().addLayer(rasterDataset.mapLayer()).save(basename(__file__).replace('.py', '1.png'))
MapViewer().addLayer(rasterDataset.band(index=0).mapLayer()).save(basename(__file__).replace('.py', '2.png'))
MapViewer().addLayer(vectorDataset.mapLayer()).save(basename(__file__).replace('.py', '3.png'))
extent = Extent(xmin=383382, ymin=5818224, xmax=385304, ymax=5819664, projection=rasterDataset.projection())
MapViewer().addLayer(rasterDatasetWithLookupTable.mapLayer()).setExtent(extent).save(basename(__file__).replace('.py', '4.png'))
