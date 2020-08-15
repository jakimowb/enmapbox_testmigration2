from qgis.core import *
from qgis.core import QgsVectorFileWriter, QgsFeature, QgsCoordinateTransformContext
import pathlib


# 1. Create an in-memory vector layer to store tabular data
uri = 'None?field=id:integer&field=name:string&field=measurement:double'
# see docs for QgsVectorLayer. "None" means not Geometry
lyr = QgsVectorLayer(uri, 'Scratch layer', 'memory')
assert lyr.startEditing()
# add 2 new lines / features
f = QgsFeature(lyr.fields())
assert f.setAttribute(lyr.fields().lookupField('name'), 'My Name')
assert f.setAttribute(lyr.fields().lookupField('measurement'), 23.42)
lyr.addFeature(f)


f = QgsFeature(lyr.fields())
assert f.setAttribute(lyr.fields().lookupField('name'), 'Another name')
assert f.setAttribute(lyr.fields().lookupField('measurement'), 2344)
lyr.addFeature(f)

assert lyr.commitChanges()


# 2. Save QgsVectorLayer as XLSX
path_xlxs = pathlib.Path(__file__).parent / 'new_excel_file.xlsx'

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = 'XLSX'
context = QgsCoordinateTransformContext()
results = QgsVectorFileWriter.writeAsVectorFormatV2(
    lyr, # layer
    path_xlxs.as_posix(),
    context,
    options
)


# 3. Read the XLSX file as vector layer
lyr = QgsVectorLayer(path_xlxs.as_posix())
for field in lyr.fields():
    print(field)
for feature in lyr.getFeatures():
    assert isinstance(feature, QgsFeature)
    print(f'Feature {feature.id()}:')
    for field in lyr.fields():
        print(f'\t{field.name()} = {feature.attribute(field.name())}')

s = ""