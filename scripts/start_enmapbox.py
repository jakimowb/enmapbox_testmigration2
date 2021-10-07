from enmapbox import EnMAPBox, initAll
from enmapbox.testing import start_app

qgsApp = start_app()
initAll()
enmapBox = EnMAPBox(None)
#enmapBox.openExampleData()
qgsApp.exec_()
