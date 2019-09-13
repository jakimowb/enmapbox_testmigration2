import os

from osgeo import gdal
from osgeo.ogr import DataSource

from enmapboxtestdata import enmap
p = r'/vsimem/myfile.tiff'

ds = gdal.Open(enmap)

ds2 = gdal.Translate(p, ds)
assert isinstance(ds2, gdal.Dataset)

r1 = gdal.ReadDir(os.path.dirname(enmap))

r2 = gdal.ReadDir('/vsimem/')

s = ""



