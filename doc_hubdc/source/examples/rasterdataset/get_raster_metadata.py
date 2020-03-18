import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

# get all domains
print('All domains:')
print(rasterDataset.metadataDict())

# get ENVI domain
print('ENVI domain:')
print(rasterDataset.metadataDomain(domain='ENVI'))

# get single item (list with wavelength casted to float)
print('ENVI wavelength:' )
print(rasterDataset.metadataItem(key='wavelength', domain='ENVI', dtype=float))
