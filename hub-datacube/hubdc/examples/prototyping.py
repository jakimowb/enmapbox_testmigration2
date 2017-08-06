from osgeo import gdal, ogr
from hubdc import Open, OpenLayer

vector = OpenLayer(r'C:\Work\data\EnMAPUrbanGradient2009\test\bug2009.shp')
#vector = OpenLayer(r'C:\Work\data\EnMAPUrbanGradient2009\02_additional_data\land_cover\LandCov_Vec_Berlin_Urban_Gradient_2009.shp')

raster = Open(r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\EnMAP01_Berlin_Urban_Gradient_2009.bsq')
bug = vector.rasterize(dstPixelGrid=raster.pixelGrid, dstName=r'C:\Work\data\EnMAPUrbanGradient2009\test\bugRasterized.img', format='ENVI',
                       burnAttribute='ID_L2', initValue=-1, noDataValue=-1,
                       filter='ID_L2 > 3')
