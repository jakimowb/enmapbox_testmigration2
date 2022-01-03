from PyQt5.QtCore import Qt

from enmapbox import EnMAPBox
from enmapbox.gui.applications import EnMAPBoxApplication
from typeguard import typechecked
from wavebandlocatorapp.wavebandlocatordockwidget import WavebandLocatorDockWidget


def enmapboxApplicationFactory(enmapBox: EnMAPBox):
    return [WavebandLocatorApp(enmapBox)]


@typechecked
class WavebandLocatorApp(EnMAPBoxApplication):

    def __init__(self, enmapBox: EnMAPBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = WavebandLocatorApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

        self.initGui()

    def initGui(self):
        panel = WavebandLocatorDockWidget(self.enmapbox, self.enmapbox.ui)
        self.enmapbox.addPanel(Qt.LeftDockWidgetArea, panel, True)

