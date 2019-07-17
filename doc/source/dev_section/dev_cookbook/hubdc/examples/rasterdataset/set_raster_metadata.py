from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

# set multiple domains
copy = rasterDataset.translate()
copy.setMetadataDict(metadataDict={'domain1': {'a': 1, 'b': 2},
                                   'domain2': {'c': 3, 'd': 4}})
print({domain: copy.metadataDict()[domain] for domain in ['domain1', 'domain2']})

# set domain
copy = rasterDataset.translate()
copy.setMetadataDomain(metadataDomain={'a': 1, 'b': 2}, domain='domain')
print(copy.metadataDict()['domain'])

# set item
copy = rasterDataset.translate()
copy.setMetadataItem(key='a', value=1, domain='domain')
print(copy.metadataDict()['domain'])
# END
