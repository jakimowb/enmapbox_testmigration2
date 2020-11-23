from enmapbox.testing import start_app
qgsApp = start_app()
from enmapbox import EnMAPBox
enmapBox = EnMAPBox(None)
enmapBox.openExampleData()
qgsApp.exec_()
