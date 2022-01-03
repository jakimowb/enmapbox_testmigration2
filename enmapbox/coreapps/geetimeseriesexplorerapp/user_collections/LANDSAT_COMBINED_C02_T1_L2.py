import numpy as np

import ee

ee.Initialize()

# set unified band names
bandNames = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']

# combine all landsat collections
l4 = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') \
    .select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL'], bandNames)
l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') \
    .select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL'], bandNames)
l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') \
    .select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL'], bandNames)
l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL'], bandNames)
collections = [l4, l5, l7, l8]
collection = ee.ImageCollection(ee.FeatureCollection(collections).flatten())

# restrict to common image properties available in all collections
propertyNames = ee.List([]) \
    .cat(l8.first().propertyNames()) \
    .cat(l7.first().propertyNames()) \
    .cat(l5.first().propertyNames()) \
    .cat(l4.first().propertyNames()) \
    .sort().getInfo()
propertyNames = [
    name for name, count in zip(*np.unique(propertyNames, return_counts=True)) if count == len(collections)
]

# set default band colors
bandColors = {
    'BLUE': '#003fbd', 'GREEN': '#008700', 'RED': '#c50003', 'NIR': '#af54ff', 'SWIR1': '#ffaf25', 'SWIR2': '#b87e1a',
    'QA_PIXEL': '#b4b4b4',
    'NDVI': '#aaff00', 'EVI': '#007d00', 'TCB': '#FF0000', 'TCG': '#00FF00', 'TCW': '#0000FF',
}

# mapping from spectral index formular identifiers to image bands
wavebandMapping = {'B': 'BLUE', 'G': 'GREEN', 'R': 'RED', 'N': 'NIR', 'S1': 'SWIR1', 'S2': 'SWIR2'}

spectralIndices = {
    "MY_NDVI": {
        "bands": ["N", "R"],
        "formula": "(N - R)/(N + R)",
        "long_name": "Normalized Difference Vegetation Index",
        "reference": "https://doi.org/10.1016/0034-4257(79)90013-0",
        "short_name": "MY_NDVI",
        "type": "vegetation"
    },
    "MY_EVI": {
        "bands": ["g", "N", "R", "C1", "C2", "B", "L"],
        "formula": "g * (N - R) / (N + C1 * R - C2 * B + L)",
        "long_name": "Enhanced Vegetation Index",
        "reference": "https://doi.org/10.1016/S0034-4257(96)00112-5",
        "short_name": "MY_EVI",
        "type": "vegetation"
    },
}
