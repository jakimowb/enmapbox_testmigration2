# this example shows the QgsRasterRenderer used by default
# when opening a gdal.Dataset image with categories
# see discussion #674
# https://bitbucket.org/hu-geomatics/enmap-box/issues/674/symbol-for-categorized-raster-looks-like-a
import numpy as np
from osgeo import gdal_array, gdal
from qgis.core import QgsRasterLayer, QgsPalettedRasterRenderer

array = np.asarray([[1, 2, 3, 2],
                    [0, 1, 1, 2]]).astype(np.uint8)

path = '/vsimem/myimage.tif'
ds: gdal.Dataset = gdal_array.SaveArray(array, path)
band: gdal.Band = ds.GetRasterBand(1)
band.SetCategoryNames(['none', 'A', 'B', 'C', 'D'])

# set True to add colors and get a QgsPalettedRasterRenderer instead
if False:
    ct = gdal.ColorTable()
    ct.SetColorEntry(0, (0, 0, 0))
    ct.SetColorEntry(1, (0, 255, 0))
    ct.SetColorEntry(3, (255, 0, 0))
    band.SetColorTable(ct)

ds.FlushCache()
lyr = QgsRasterLayer(path)
assert lyr.isValid()
renderer = lyr.renderer()
print(renderer)
s = ""

