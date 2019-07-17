import enmapboxtestdata
from hubdc.core import *

vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)
vectorDataset.reproject(projection=Projection.wgs84(), filename='vector.gpkg', driver=GeoPackageDriver())
