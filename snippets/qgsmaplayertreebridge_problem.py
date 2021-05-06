from qgis._core import QgsVectorLayer

from qgis.testing import start_app

qgis_app = start_app()
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge, QgsLayerTreeView
from qgis.core import QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem, QgsLayerTree, QgsLayerTreeModel, \
    QgsApplication
import pathlib

# initialize  the main QGIS QgsMapCanvas with a layer and the QgsProject.instance() CRS
path_world = pathlib.Path(QgsApplication.pkgDataPath()) / 'resources' / 'data' / 'world_map.gpkg'
lyr4326 = QgsVectorLayer(path_world.as_posix() + '|layername=countries', 'World')
QgsProject.instance().addMapLayer(lyr4326, True)

# a small application with an QgsLayerTreeView independent of the main QGIS
canvas = QgsMapCanvas()
layerTree = QgsLayerTree()
layerTreeModel = QgsLayerTreeModel(layerTree)
layerTreeView = QgsLayerTreeView()
bridge = QgsLayerTreeMapCanvasBridge(layerTree, canvas)

app = QWidget()
layout = QHBoxLayout()
layout.addWidget(layerTreeView)
layout.addWidget(canvas)
app.setLayout(layout)
app.show()

# add a new layer to the application's layer tree
uri = r'type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D{x}%26y%3D{y}%26z%3D{z}&zmax=19&zmin=0'
lyr = QgsRasterLayer(uri, 'MyWMS', 'WMS')
QgsProject.instance().addMapLayers([lyr], False)
layerTree.addLayer(lyr)

#
# bridge.setAutoSetupOnFirstLayer(False)

print(f'Before setCanvasLayers():'
      f'\nQgsProject CRS:{QgsProject.instance().crs()}'
      f'\nApp Canvas CRS:{canvas.mapSettings().destinationCrs()}')
bridge.setCanvasLayers()
# ensure that all canvas updates are triggered
QApplication.processEvents()
print(f'After setCanvasLayers():'
      f'\nQgsProject CRS:{QgsProject.instance().crs()}'
      f'\nApp Canvas CRS:{canvas.mapSettings().destinationCrs()}')
qgis_app.exec_()