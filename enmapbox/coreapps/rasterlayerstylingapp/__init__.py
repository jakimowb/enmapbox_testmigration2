from PyQt5.QtCore import Qt

from enmapbox import EnMAPBox
from enmapbox.gui.applications import EnMAPBoxApplication
from typeguard import typechecked
from rasterlayerstylingapp.rasterlayerstylingpanel import RasterLayerStylingPanel


def enmapboxApplicationFactory(enmapBox: EnMAPBox):
    return [RasterLayerStylingApp(enmapBox)]


@typechecked
class RasterLayerStylingApp(EnMAPBoxApplication):

    def __init__(self, enmapBox: EnMAPBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = RasterLayerStylingApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

        self.initGui()

    def initGui(self):
        panel = RasterLayerStylingPanel(self.enmapbox, self.enmapbox.ui)
        self.enmapbox.addPanel(Qt.LeftDockWidgetArea, panel, True)

