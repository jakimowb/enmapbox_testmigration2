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
    #enmapBox.setProperty(GeeTimeseriesExplorerApp.__name__, instance)

    return [instance]


@typechecked
class GeeTimeseriesExplorerApp(EnMAPBoxApplication):

    #@classmethod
   # def instance(cls) -> 'GeeTimeseriesExplorerApp':
    #    """Return singleton."""
   #    return EnMAPBox.instance().property(GeeTimeseriesExplorerApp.__name__)

    def __init__(self, enmapBox: EnMAPBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = GeeTimeseriesExplorerApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

        self.backgroundLayer = QgsRasterLayer(
            'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0',
            'Google Maps', 'wms'
        )

        # Create and register the EE data providers
        register_data_provider()

        self.initGui()

    @classmethod
    def icon(cls):
        return QIcon(__file__.replace('__init__.py', '/icon.svg'))

    @classmethod
    def iconProfilePlot(cls):
        return QIcon(__file__.replace('__init__.py', '/icons/plot.svg'))

    @classmethod
    def iconMapView(cls):
        return QIcon(__file__.replace('__init__.py', '/icons/new_map_view.svg'))

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

        self.initEnmapGui()

    def initEnmapGui(self):

        # add main dock and toolbar button
        self.mainDock = GeeTimeseriesExplorerDockWidget(parent=self.parent())
        self.enmapbox.addDockWidget(Qt.RightDockWidgetArea, self.mainDock)
        self.mainDock.setWindowIcon(self.icon())
        self.mainDock.hide()

        self.actionTogglemainDock = QAction(self.icon(), 'GEE Time Series Explorer', self.enmapbox.iface.mainWindow())
        self.actionTogglemainDock.triggered.connect(self.togglemainDockVisibility)
        self.enmapbox.ui.mPluginsToolbar.addAction(self.actionTogglemainDock)

        # add profile dock and toolbar button
        icon = self.iconProfilePlot()
        self.profileDock = GeeTemporalProfileDockWidget(self.mainDock, parent=self.parent())
        self.enmapbox.addDockWidget(Qt.TopDockWidgetArea, self.profileDock)
        self.profileDock.setWindowIcon(icon)
        self.profileDock.hide()

        self.actionToggleprofileDock = QAction(icon, 'GEE Temporal Profile Viewer', self.enmapbox.iface.mainWindow())
        self.actionToggleprofileDock.triggered.connect(self.toggleprofileDockVisibility)
        self.enmapbox.ui.mPluginsToolbar.addAction(self.actionToggleprofileDock)

        # add new map view toolbar button
        icon = self.iconMapView()
        self.actionEnmapNewMapView = QAction(icon, 'Open new map view', self.enmapbox.iface.mainWindow())
        self.actionEnmapNewMapView.triggered.connect(self.enmapNewMapView)
        self.enmapbox.ui.mPluginsToolbar.addAction(self.actionEnmapNewMapView)

        # set some members
        self.mainDock.setProfileDock(self.profileDock)
        self.mainDock.setEnmapBox(self.enmapbox)
        self.mainDock.setQgisInterface(None)

        # connect signals between docks
#        self.profileDock.sigCurrentLocationChanged.connect(self.mainDock.onCurrentLocationChanged)


    def togglemainDockVisibility(self):
        self.mainDock.setVisible(not self.mainDock.isVisible())
        if len(self.enmapbox.docks(DockTypes.MapDock)) == 0:
            self.enmapNewMapView()
        self.profileDock.setVisible(self.mainDock.isVisible())

    def toggleprofileDockVisibility(self):
        visible = not self.profileDock.isVisible()
        self.profileDock.setVisible(visible)
        self.profileDock.mIdentify.setChecked(visible)

    def enmapNewMapView(self):
        currentMapDock = self.enmapbox.currentMapDock()

        mapDock: MapDock = self.enmapbox.createDock(DockTypes.MapDock)
        mapDock.addLayers([self.backgroundLayer.clone()])

        if currentMapDock is None:  # zoom to Germany
            germany = QgsRectangle(633652, 5971168, 1766199, 7363456)
            mapDock.mapCanvas().setExtent(germany)
        else:
            currentMapDock.linkWithMapDock(mapDock, CanvasLink.LINK_ON_CENTER_SCALE)
