import os
import pathlib

from osgeo import gdal
from osgeo.ogr import DataSource

from enmapboxtestdata import enmap
p = r'/vsimem/myfile.tiff'

ds = gdal.Open(enmap)
if isinstance(ds, gdal.Dataset):
    ds2 = gdal.Translate(p, ds)
    assert isinstance(ds2, gdal.Dataset)

    r1 = gdal.ReadDir(os.path.dirname(enmap))

    r2 = gdal.ReadDir('/vsimem/')

s = ""

p = pathlib.Path(r'D:\LUMOS\Data\LC08_L1TP_198025_20200121_20200128_01_T1.tar.gz')
if os.path.isfile(p):
    vsiPath = '/vsitar/{}'.format(p.as_posix())
    r = gdal.ReadDir(vsiPath)
    s = ""



