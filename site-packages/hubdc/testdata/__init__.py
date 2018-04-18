'''
Two Landsat 5 scenes from the same overflight path (i.e. 194) and date (2010/189) resampled to 500 m
and a vector polygon layer with the districs of Brandenburg (a federated state of Germany).
The Landsat surface reflectance band names (i.e. band1, ..., band5, band7) are also assigned to more explanatory clear names (i.e. blue, green, red, nir swir1, swir2).
Reflectance values are stored as byte data, scaled between 0 and 100, with no data value set to 255.
'''

from os.path import join, dirname, basename
root = dirname(__file__)

class LT51940232010189KIS01(object):
    root = join(root, 'LT51940232010189KIS01')
    band1 = blue = join(root, 'LT51940232010189KIS01_sr_band{}.img'.format(1))
    band2 = green = join(root, 'LT51940232010189KIS01_sr_band{}.img'.format(2))
    band3 = red = join(root, 'LT51940232010189KIS01_sr_band{}.img'.format(3))
    band4 = nir = join(root, 'LT51940232010189KIS01_sr_band{}.img'.format(4))
    band5 = swir1 = join(root, 'LT51940232010189KIS01_sr_band{}.img'.format(5))
    band7 = swir2 = join(root, 'LT51940232010189KIS01_sr_band{}.img'.format(7))
    cfmask = join(root, 'LT51940232010189KIS01_cfmask.img')

class LT51940242010189KIS01(object):
    root = join(root, 'LT51940242010189KIS01')
    band1 = blue = join(root, 'LT51940242010189KIS01_sr_band{}.img'.format(1))
    band2 = green = join(root, 'LT51940242010189KIS01_sr_band{}.img'.format(2))
    band3 = red = join(root, 'LT51940242010189KIS01_sr_band{}.img'.format(3))
    band4 = nir = join(root, 'LT51940242010189KIS01_sr_band{}.img'.format(4))
    band5 = swir1 = join(root, 'LT51940242010189KIS01_sr_band{}.img'.format(5))
    band7 = swir2 = join(root, 'LT51940242010189KIS01_sr_band{}.img'.format(7))
    cfmask = join(root, 'LT51940242010189KIS01_cfmask.img')

class CFMaskCategory(object):
    '''
    Enumerate-like holding the CFMask category values.
    '''
    land = 0
    water = 1
    cloudShadow = 2
    snowOrIce = 3
    cloud = 4

class BrandenburgDistricts(object):
    root = join(root, 'BrandenburgDistricts')
    shp = join(root, 'BrandenburgDistricts.shp')
    nameAttribute = 'name'
