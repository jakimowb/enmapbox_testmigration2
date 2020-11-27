from PyQt5.QtCore import QTimer
from qgis._core import QgsRasterLayer

from enmapbox import EnMAPBox
from enmapbox.gui.mapcanvas import MapDock, LINK_ON_CENTER
from enmapbox.testing import start_app
from enmapboxtestdata import enmap, hires

qgsApp = start_app()
enmapBox = EnMAPBox(None)

layer = QgsRasterLayer(hires, 'hires_berlin')

mapImage: MapDock = enmapBox.createDock('MAP', lockNativeResolution=True, nativeResolutionLayer=layer)
mapImage.setTitle(f'{layer.name()} 1:1 View')
mapImage.insertLayer(idx=0, layerSource=layer)

mapOverview: MapDock = enmapBox.createDock('MAP', lockFullExtent=True)
mapOverview.setTitle(f'{layer.name()} Overview')
mapOverview.insertLayer(idx=0, layerSource=layer)

mapZoom: MapDock = enmapBox.createDock('MAP', lockNativeResolution=True, nativeResolutionLayer=layer, nativeResolutionMagnificationFactor=10)
mapZoom.setTitle(f'{layer.name()} Zoom')
mapZoom.insertLayer(idx=0, layerSource=layer)
#mapZoom.linkWithMapDock(mapDock=mapImage, linkType=LINK_ON_CENTER)  # this give me an error, not sure why

qgsApp.exec_()
