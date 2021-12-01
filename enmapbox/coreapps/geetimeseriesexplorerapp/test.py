import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMainWindow
from qgis._core import QgsRasterLayer, QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsRectangle
from qgis._gui import QgisInterface, QgsMapCanvas

from enmapbox.testing import initQgisApplication
from geetimeseriesexplorer import Plugin

qgsApp = initQgisApplication()


sys.path.append(r'C:\Users\Andreas\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins')
sys.path.append(r'C:\Users\Andreas\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\ee_plugin\extlibs_windows')

from ee_plugin import utils
utils.check_version = lambda : None


class TestInterface(QgisInterface):

    def __init__(self):
        QgisInterface.__init__(self)

        self.ui = QMainWindow()
        self.ui.setWindowTitle('QGIS')
        self.ui.setWindowIcon(QIcon(r'C:\source\QGIS3-master\images\icons\qgis_icon.svg'))
        self.ui.resize(QSize(1500, 750))
        self.ui.canvas = QgsMapCanvas()
        self.ui.setCentralWidget(self.ui.canvas)

        layer1 = QgsVectorLayer(
            r'C:/QGIS/apps/qgis/resources/data/world_map.gpkg|layername=countries',
            baseName='world_map'
        )
        layer2 = QgsVectorLayer(
            #r'C:\Users\janzandr\Downloads\points.gpkg',
            r'C:\Users\janzandr\Downloads\shepherd_camps\camps_and_random.shp',
            baseName='points'
        )

        QgsProject.instance().addMapLayers([layer1, layer2])

        self.ui.canvas.setLayers([layer2, layer1])
#        self.ui.canvas.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(3857))
#        self.ui.canvas.setExtent(QgsRectangle(-23070454.3,-6996278.9, 26712871.7, 18946006.2))
        self.ui.canvas.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(4326))
        self.ui.canvas.setExtent(layer1.extent())
        self.ui.show()

    def mapCanvas(self) -> QgsMapCanvas:
        return self.ui.canvas

    def addDockWidget(self, area, dockwidget):
        self.ui.addDockWidget(area, dockwidget)

    def messageBar(self):

        class MessageBar():

            def pushCritical(self, *args, **kwars):
                print('CRITICAL', args, kwars)

            def pushInfo(self, *args, **kwars):
                print('INFO', args, kwars)

            def pushSuccess(self, *args, **kwars):
                print('SUCCESS', args, kwars)

            def pushWarning(self, *args, **kwars):
                print('WARNING', args, kwars)

        return MessageBar()


def test_plugin():
    iface = TestInterface()

    plugin = Plugin(iface=iface)
    plugin.initGui()
    #QTimer.singleShot(1000, lambda: qgsApp.setAttribute(QtCore.Qt.AA_Use96Dpi))
    qgsApp.exec_()


if __name__ == '__main__':
    test_plugin()
