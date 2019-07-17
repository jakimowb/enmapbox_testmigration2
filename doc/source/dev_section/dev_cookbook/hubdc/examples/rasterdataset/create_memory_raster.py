import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(enmapboxtestdata.enmap)

# option a) with MemDriver
driver = MemDriver()
copy = rasterDataset.translate(driver=driver)

# option b) with in-memory files and any driver
driver = GTiffDriver()
options = [driver.Option.INTERLEAVE.BAND, driver.Option.COMPRESS.LZW]
copy = rasterDataset.translate(filename='/vsimem/raster.tif', driver=driver, options=options)
