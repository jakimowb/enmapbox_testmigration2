from enmapbox.testing import start_app
from enmapbox import EnMAPBox

qgsApp = start_app()
enmapBox = EnMAPBox(None)
enmapBox.openExampleData()
qgsApp.exec_()
