from PyQt5.QtWidgets import QMenu, QApplication

from enmapbox.gui.dataviews.dockmanager import DockTreeView
from enmapbox.testing import start_app
from enmapbox.gui.enmapboxgui import EnMAPBox

app = start_app()

def onCreateContextMenu(menu: QMenu):
    view = QApplication.instance().sender()
    if isinstance(view, DockTreeView):
        node = view.currentNode()
        print('Add context menu actions')
        # consider node / selection context
        a = menu.addAction('MyAction')

emb = EnMAPBox()
emb.dockTreeView().sigPopulateContextMenu.connect(onCreateContextMenu)
app.exec_()