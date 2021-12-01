import ee

def getQABit(image, start, end, newName):
    pattern = 0
    for i in range(start, end + 1):
        pattern += 2 ** i
    return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)

def maskQuality(image):
    QA = image.select('pixel_qa')
    shadow = getQABit(QA, 3, 3, 'cloud_shadow')
    cloud = getQABit(QA, 5, 5, 'cloud')
    snow = getQABit(QA, 4, 4, 'snow')
    med_cld = getQABit(QA, 7, 7,  'med_cld_conf')
    cirrus = getQABit(QA, 9, 9, 'cirrus')
    return image.updateMask(cloud.eq(0))\
                .updateMask(shadow.eq(0))\
                .updateMask(snow.eq(0))\
                .updateMask(med_cld.eq(0))\
                .updateMask(cirrus.eq(0))

bandNames = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']

l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'], bandNames)
l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'], bandNames)
l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'], bandNames)
l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'], bandNames)
lnd = l4.merge(l5).merge(l7).merge(l8)

lnd = lnd.map(lambda image: image.addBands(image.normalizedDifference(['NIR', 'RED']).rename('NDVI').multiply(1e4).toInt16()))
lnd = lnd.map(lambda image: image.addBands(image.expression("2.5 * ((b('NIR') - b('RED')) / (b('NIR') + 6 * b('RED') - 7.5 * b('BLUE') + 1e4))").rename('EVI').multiply(1e4).toInt16()))
lnd = lnd.map(lambda image: image.addBands(image.expression("0.2043 * b('BLUE') + 0.4158 * b('GREEN') + 0.5524 * b('RED') + 0.5741 * b('NIR') + 0.3124 * b('SWIR1') + 0.2303 * b('SWIR2')").rename('TCB').toInt16()))
lnd = lnd.map(lambda image: image.addBands(image.expression("-0.1603 * b('BLUE') - 0.2819 * b('GREEN') - 0.4934 * b('RED') + 0.7940 * b('NIR') - 0.0002 * b('SWIR1') - 0.1446 * b('SWIR2')").rename('TCG').toInt16()))
lnd = lnd.map(lambda image: image.addBands(image.expression("0.0315 * b('BLUE') + 0.2021 * b('GREEN') + 0.3102 * b('RED') + 0.1594 * b('NIR') - 0.6806 * b('SWIR1') - 0.6109 * b('SWIR2')").rename('TCW').toInt16()))

lnd = lnd.map(maskQuality)
lnd = lnd.set('colors',
    {
        'BLUE': '#003fbd',
        'GREEN': '#008700',
        'RED': '#c50003',
        'NIR': '#af54ff',
        'SWIR1': '#ffaf25',
        'SWIR2': '#b87e1a',
        'pixel_qa': '#b4b4b4',
        'NDVI': '#aaff00',
        'EVI': '#007d00',
        'TCB': '#FF0000',
        'TCG': '#00FF00',
        'TCW': '#0000FF',
    }
)

lnd = lnd.set('description', 'This collection returns a merged Landsat L2 (surface reflectance product) collection, including the Landsat 4 TM, Landsat 5 TM, Landsat 7 ETM+, and Landsat 8 OLI archives. Pixel-based cloud masking is based on CFMask outputs contained in pixel_qa bands to remove clouds at high and medium confidence levels, cirrus clouds (OLI only), cloud shadows and snow. The collection returns renamed bands and includes standard vegetation indices (NDVI + EVI) as well as Tasseled Cap Brightness (TCB), Greenness (TCG), and Wetness (TCW) bands for convenience.')

imageCollection = lnd
