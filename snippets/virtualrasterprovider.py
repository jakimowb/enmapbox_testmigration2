""""
Example that shows how to visualize a spectral index using a virtualraster layer
"""
import pathlib
import re
from PyQt5.QtCore import QUrlQuery
from qgis._core import QgsRasterLayer, QgsProject

from enmapbox.testing import start_app

app = start_app()

from enmapbox.exampledata import enmap
path = pathlib.Path(enmap)


from enmapbox.gui.utils import bandClosestToWavelength


query = QUrlQuery()

# define spatial extent & resolution of output layer
refLayer = QgsRasterLayer(path.as_posix())
query.addQueryItem('crs', refLayer.crs().authid())
query.addQueryItem('extent', re.sub(r'[ ,]+', ',', refLayer.extent().asWktCoordinates()))
query.addQueryItem('width', str(refLayer.width()))
query.addQueryItem('height', str(refLayer.height()))

# calculate NDVI
bNIR = bandClosestToWavelength(refLayer, 'NIR')
bRed = bandClosestToWavelength(refLayer, 'R')
query.addQueryItem('formula', f'("E@{bNIR}" - "E@{bRed}") / ("E@{bNIR}" + "E@{bRed}")')

# define input source(s)
query.addQueryItem('E:provider', 'gdal')
query.addQueryItem('E:uri', path.as_posix())
uri = f'?{query.toString()}'
print(uri)
lyr = QgsRasterLayer(uri, 'MyVirtualLayer', 'virtualraster')

# improve render settings
ce = lyr.renderer().contrastEnhancement()
ce.setMinimumValue(0)
ce.setMaximumValue(1)

print(lyr.error())
assert lyr.dataProvider().isValid()
assert lyr.isValid()

QgsProject.instance().addMapLayer(lyr)

exit(0)