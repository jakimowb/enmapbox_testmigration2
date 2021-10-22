from qgis._core import QgsRasterLayer

from enmapbox import EnMAPBox, initAll
from enmapbox.testing import start_app
from enmapboxprocessing.renderer.classfractionrenderer import ClassFractionRenderer
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import landcover_map_l3
from tests.testdata import fraction_map_l3_tif

renderer = ClassFractionRenderer()
classification = QgsRasterLayer(landcover_map_l3)
categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
for category in categories:
    renderer.addCategory(category)
layer = QgsRasterLayer(fraction_map_l3_tif)
layer.setRenderer(renderer)

qgsApp = start_app()
initAll()

enmapBox = EnMAPBox(None)
enmapBox.dropObject(layer)

qgsApp.exec_()
