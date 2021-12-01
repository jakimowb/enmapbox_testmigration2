import ee

def maskS2scl(image):
    scl = image.select('SCL')
    sat = scl.neq(1)
    shadow = scl.neq(3)
    cloud_lo = scl.neq(7)
    cloud_md = scl.neq(8)
    cloud_hi = scl.neq(9)
    cirrus = scl.neq(10)
    snow = scl.neq(11)
    return image.updateMask(sat.eq(1))\
	.updateMask(shadow.eq(1))\
	.updateMask(cloud_lo.eq(1))\
	.updateMask(cloud_md.eq(1))\
	.updateMask(cloud_hi.eq(1))\
	.updateMask(cirrus.eq(1))\
	.updateMask(snow.eq(1))
	
def maskS2cdi(image):
    cdi = ee.Algorithms.Sentinel2.CDI(image)
    return image.updateMask(cdi.gt(-0.8)).addBands(cdi)

bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'QA60', 'SCL', 'cdi'])
band_names = ee.List(['BLUE', 'GREEN', 'RED', 'REDEDGE1', 'REDEDGE2', 'REDEDGE3', 'NIR', 'BROADNIR', 'SWIR1', 'SWIR2', 'QA60', 'SCL', 'CDI'])

sen = ee.ImageCollection('COPERNICUS/S2_SR')\
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50))\
                .map(maskS2scl) \
                .map(maskS2cdi) \
                .select(bands, band_names)

sen = sen.map(lambda image: image.addBands(image.normalizedDifference(['BROADNIR', 'RED'])\
                                               .multiply(10000).toInt16().rename('NDVI')))
sen = sen.set('colors',
    {
        'BLUE': '#003fbd',
        'GREEN': '#008700',
        'RED': '#c50003',
        'REDEDGE1': '#ff7dcb',
		'REDEDGE2': '#d669ab',
		'REDEDGE3': '#bd5d97',
		'NIR': '#af54ff',
		'BROADNIR': '#803ebe',
        'SWIR1': '#ffaf25',
        'SWIR2': '#b87e1a',
        'QA60': '#b4b4b4',
		'SCL': '#9a9a9a',
		'CDI': '#ffff7f',
        'NDVI': '#aaff00'
    }
)

sen = sen.set('description', 'This collection returns the merged Sentinel-2A and -2B L2A (surface reflectance product) archives. It uses an aggressive cloud masking, fully discarding images with >50% cloud cover, uses the scene classification layer to remove saturated pixels, clouds at all confidence levels, cirrus clouds, cloud shadows and snow. Furthermore, the cloud displacement index (CDI; https://doi.org/10.1016/j.rse.2018.04.046 for details) is used to improve cloud masking. The collection returns renamed bands and includes a NDVI band for convenience.')

imageCollection = sen