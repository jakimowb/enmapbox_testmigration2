from qgis.testing import start_app
qgis_app = start_app()

from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsFeature, QgsPointXY, QgsGeometry
from qgis.gui import QgsMapCanvas
import pathlib

# similar issues:
#

# add the "world" vectorlayer to QGIS to
# initialize QgsProject.instance() with a project CRS
uri_world = pathlib.Path(QgsApplication.pkgDataPath()) / 'resources' / 'data' / 'world_map.gpkg'
uri_world = uri_world.as_posix() + '|layername=countries'
lyrWorld = QgsVectorLayer(uri_world)
assert lyrWorld.isValid()
QgsProject.instance().addMapLayers([lyrWorld])

# create layer with a smaller extent
uri = r'Point?crs=epsg:32632&field=id:integer&field=name:string(20)&index=yes'
lyr = QgsVectorLayer(uri, 'small layer', 'memory')
assert lyr.startEditing()
# add 2 points
feat1 = QgsFeature(lyr.fields())
feat1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(500000.00, 60000.00)))
feat2 = QgsFeature(lyr.fields())
feat2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(550000.00, 61000.00)))
lyr.addFeatures([feat1, feat2])
assert lyr.commitChanges()

# add layer to canvas
QgsProject.instance().addMapLayer(lyr, False)
canvas = QgsMapCanvas()
canvas.setLayers([lyr])
canvas.setDestinationCrs(lyr.crs())
canvas.setExtent(lyr.extent())

print(f' Layer extent: {lyr.extent().asWktCoordinates()}')
print(f'Canvas extent: {canvas.extent().asWktCoordinates()}')
print(f' fullExtent(): {canvas.fullExtent().asWktCoordinates()}')
