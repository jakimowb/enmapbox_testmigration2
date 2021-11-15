from qgis._core import QgsRasterLayer

from enmapbox import EnMAPBox, initAll
from enmapbox.exampledata import enmap
from enmapbox.testing import start_app
from spectralindexcreatorapp.spectralindexcreatordialog import SpectralIndexCreatorDialog

qgsApp = start_app()
initAll()

enmapBox = EnMAPBox(None)
layer = QgsRasterLayer(enmap, 'enmap_berlin.bsq')
mapDock = enmapBox._dropObject(layer)

widget = SpectralIndexCreatorDialog()
widget.mLayer.setLayer(layer)
widget.mTable2.selectAll()
widget.mCreate2.clicked.emit()

widget.show()

qgsApp.exec_()
