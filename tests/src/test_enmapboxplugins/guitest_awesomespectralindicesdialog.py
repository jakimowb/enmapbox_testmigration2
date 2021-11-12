from qgis._core import QgsRasterLayer

from enmapbox import EnMAPBox, initAll
from enmapbox.exampledata import enmap
from enmapbox.testing import start_app
from enmapboxplugins.awesomespectralindicesdialog import AwesomeSpectralIndicesDialog

qgsApp = start_app()
initAll()

enmapBox = EnMAPBox(None)
mapDock = enmapBox._dropObject(QgsRasterLayer(enmap, 'enmap_berlin.bsq'))

widget = AwesomeSpectralIndicesDialog()
widget.show()

qgsApp.exec_()
