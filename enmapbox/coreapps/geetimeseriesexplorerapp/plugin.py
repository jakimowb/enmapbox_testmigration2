from os.path import join, dirname

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.PyQt import QtCore
from qgis._gui import QgisInterface

from geetimeseriesexplorer.dockwidget import DockWidget


class Plugin(object):

    def __init__(self, iface):
        assert isinstance(iface, QgisInterface)
        self.iface = iface
        self.icon = QIcon(join(dirname(__file__), 'icon.png'))

    def initGui(self):
        self.ui = DockWidget(iface=self.iface, parent=self.iface.parent())
        self.ui.setWindowIcon(self.icon)
        self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.ui)
        self.action = QAction(self.icon, 'GEE Timeseries Explorer', self.iface.mainWindow())
        self.action.triggered.connect(self.toggleUiVisibility)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeDockWidget(self.ui)

    def toggleUiVisibility(self):
        self.ui.setVisible(not self.ui.isVisible())
        if self.ui.isVisible():
            self.ui.onActivateMapToolClicked()
