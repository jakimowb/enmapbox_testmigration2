from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis._core import QgsRasterLayer, QgsRectangle

from enmapbox import EnMAPBox
from enmapbox.gui.applications import EnMAPBoxApplication
from enmapbox.gui.dataviews.docks import DockTypes, MapDock
from enmapbox.gui.mapcanvas import CanvasLink
from geetimeseriesexplorerapp.externals.ee_plugin.provider import register_data_provider
from geetimeseriesexplorerapp.geetemporalprofiledockwidget import GeeTemporalProfileDockWidget
from geetimeseriesexplorerapp.geetimeseriesexplorerdockwidget import GeeTimeseriesExplorerDockWidget
from typeguard import typechecked


def enmapboxApplicationFactory(enmapBox: EnMAPBox):
    # create and store singleton
    instance = GeeTimeseriesExplorerApp(enmapBox)
    enmapBox.setProperty(GeeTimeseriesExplorerApp.__name__, instance)

    return [instance]


@typechecked
class GeeTimeseriesExplorerApp(EnMAPBoxApplication):

    @classmethod
    def instance(cls) -> 'GeeTimeseriesExplorerApp':
        """Return singleton."""
        return EnMAPBox.instance().property(GeeTimeseriesExplorerApp.__name__)

    def __init__(self, enmapBox: EnMAPBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = GeeTimeseriesExplorerApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

        self.backgroundLayer = QgsRasterLayer(
            'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0',
            'Google Maps', 'wms'
        )
        self.initGui()



    def icon(self):
        return QIcon(__file__.replace('__init__.py', '/icon.svg'))

    def initGui(self):

        try:
            import ee
        except ModuleNotFoundError:
            self.action = QAction(self.icon(), 'GEE Time Series Explorer', self.enmapbox.iface.mainWindow())
            message = 'Google Earth Engine plugin not installed.'
            self.action.triggered.connect(
                lambda: QMessageBox.information(
                    self.enmapbox.iface.mainWindow(), 'Missing dependency', message
                )
            )
            self.enmapbox.ui.mPluginsToolbar.addAction(self.action)
            return

        # add main dock and toolbar button
        self.mainDock = GeeTimeseriesExplorerDockWidget(self.enmapbox, parent=self.parent())
        self.enmapbox.addDockWidget(Qt.RightDockWidgetArea, self.mainDock)
        self.mainDock.setWindowIcon(self.icon())
        self.mainDock.hide()

        self.actionToggleMainDock = QAction(self.icon(), 'GEE Time Series Explorer', self.enmapbox.iface.mainWindow())
        self.actionToggleMainDock.triggered.connect(self.toggleMainDockVisibility)
        self.enmapbox.ui.mPluginsToolbar.addAction(self.actionToggleMainDock)

        # add profile dock and toolbar button
        icon = QIcon(__file__.replace('__init__.py', '/icons/plot.svg'))
        self.profileDock = GeeTemporalProfileDockWidget(self.enmapbox, self.mainDock, parent=self.parent())
        self.enmapbox.addDockWidget(Qt.TopDockWidgetArea, self.profileDock)
        self.profileDock.setWindowIcon(icon)
        self.profileDock.hide()

        self.actionToggleProfileDock = QAction(icon, 'GEE Temporal Profile Viewer', self.enmapbox.iface.mainWindow())
        self.actionToggleProfileDock.triggered.connect(self.toggleProfileDockVisibility)
        self.enmapbox.ui.mPluginsToolbar.addAction(self.actionToggleProfileDock)

        # add new map view toolbar button
        icon = QIcon(__file__.replace('__init__.py', '/icons/new_map_view.svg'))
        self.actionNewMapView = QAction(icon, 'Open new map view', self.enmapbox.iface.mainWindow())
        self.actionNewMapView.triggered.connect(self.newMapView)
        self.enmapbox.ui.mPluginsToolbar.addAction(self.actionNewMapView)

        # Create and register the EE data providers
        register_data_provider()

    def toggleMainDockVisibility(self):
        self.mainDock.setVisible(not self.mainDock.isVisible())
        if len(self.enmapbox.docks(DockTypes.MapDock)) == 0:
            self.newMapView()

    def toggleProfileDockVisibility(self):
        visible = not self.profileDock.isVisible()
        self.profileDock.setVisible(visible)
        self.profileDock.mIdentify.setChecked(visible)

    def newMapView(self):
        currentMapDock = self.enmapbox.currentMapDock()

        mapDock: MapDock = self.enmapbox.createDock(DockTypes.MapDock)
        mapDock.addLayers([self.backgroundLayer])

        if currentMapDock is None:  # zoom to Germany
            germany = QgsRectangle(633652, 5971168, 1766199, 7363456)
            mapDock.mapCanvas().setExtent(germany)
        else:
            currentMapDock.linkWithMapDock(mapDock, CanvasLink.LINK_ON_CENTER_SCALE)
