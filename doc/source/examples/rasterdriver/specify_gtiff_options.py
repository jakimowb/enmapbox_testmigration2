from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubdc.core import *

driver = GTiffDriver()

# GTiff default options
print(driver.options())

# options for LZW compressed GTiff
print(driver.options() + [driver.Option.COMPRESS.LZW])

# options for JPEG compressed GTiff
print(driver.options() + [driver.Option.COMPRESS.JPEG, driver.Option.JPEG_QUALITY(75)])

# options for tiled GTiff
print(driver.options() + [driver.Option.TILED.YES, driver.Option.BLOCKXSIZE(256), driver.Option.BLOCKYSIZE(256)])
# END