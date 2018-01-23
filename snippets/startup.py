

from enmapbox.gui.utils import initQgisApplication
from enmapbox.gui.enmapboxgui import EnMAPBox


app = initQgisApplication()

enmapBox = EnMAPBox(None)
enmapBox.show()

app.exec_()
