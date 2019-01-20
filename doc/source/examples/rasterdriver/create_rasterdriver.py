from hubdc.core import *

# driver by name
print(RasterDriver(name='GTiff'))

# some predined driver
print(GTiffDriver())
print(EnviDriver())
print(ErdasDriver())

# by file extension
print(RasterDriver.fromFilename('raster.vrt'))
