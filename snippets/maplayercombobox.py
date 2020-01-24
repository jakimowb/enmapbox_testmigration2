from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

from enmapbox.testing import initQgisApplication, TestObjects

QAPP = initQgisApplication()


lyrClass = TestObjects.createRasterLayer(100,100,1,nc=4)
lyrClass.setName('Classification layer')

lyrMultiBand = TestObjects.createRasterLayer(100,100,5)
lyrMultiBand.setName('MultiBand')

lyrShape = TestObjects.createVectorLayer()
QgsProject.instance().addMapLayers([lyrClass, lyrMultiBand, lyrShape])

cb = QgsMapLayerComboBox()
cb.setFilters(QgsMapLayerProxyModel.RasterLayer)
cb.show()
def acceptsRow(row, index)->bool:

    return True

model = cb.model()
model.beginResetModel()
model.filterAcceptsRow = acceptsRow
model.endResetModel()
s = ""


QAPP.exec_()
