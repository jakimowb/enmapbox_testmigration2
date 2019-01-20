import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
for band in rasterDataset.bands():
    array = band.readAsArray()
    noDataValue = band.noDataValue()
    values = array[array != noDataValue]
    min = values.min()
    max = values.max()
    mean = values.std()
    print('Band {} Stats: Minimum={}, Maximum={}, Mean={}'.format(band.index()+1, min, max, mean))
