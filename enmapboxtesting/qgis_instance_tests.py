import sys, os, importlib
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *
p = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapbox\gui'
if p not in sys.path:
    sys.path.append(p)

import enmapbox.gui.maplayers
importlib.reload(enmapbox.gui.maplayers)
from enmapbox.gui.maplayers import EnMAPBoxRasterLayerConfigWidgetFactory, EnMAPBoxRasterLayerConfigWidget
assert isinstance(iface, QgisInterface)


factory = EnMAPBoxRasterLayerConfigWidgetFactory()

mapLayers = QgsProject.instance().mapLayers().values()
rasterLayers = [l for l in mapLayers if isinstance(l, QgsRasterLayer)]
lyr = rasterLayers[0]
assert factory.supportsLayer(lyr)
w = factory.createWidget(lyr, iface.mapCanvas(), dockWidget=True, parent=None)
assert isinstance(w, EnMAPBoxRasterLayerConfigWidget)
w.show()



import enmapbox
import enmapboxtestdata

layers = [QgsRasterLayer(enmapboxtestdata.enmap, 'EnMAP'), QgsRasterLayer(enmapboxtestdata.hires, 'HyMAP')]
QgsProject.instance().addMapLayers(layers)