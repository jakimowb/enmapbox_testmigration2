from __future__ import print_function

from lamos.processing.types import MGRSArchive, MGRSFootprint, MGRSTilingScheme, WRS2Footprint, WRS2Archive

MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'


def test():
    folder = r'C:\Work\data\gms\landsat'
    WRS2Footprint.createUtmLookup(infolder=folder)

    wrs2FootprintNames = ['193024', '194024']
    mgrsFootprintNames = ['32UPC', '32UQC', '33UTT', '33UUT']
    buffer = 300
    MGRSTilingScheme.cacheMGRSFootprints([WRS2Footprint(wrs2FootprintName) for wrs2FootprintName in wrs2FootprintNames])

    for wrs2FootprintName in wrs2FootprintNames:
        wrs2Footprint = WRS2Footprint(wrs2FootprintName)
        print('WRS2: '+wrs2Footprint.name, 'UTM='+wrs2Footprint.utm)
        for mgrsFootprint in MGRSTilingScheme.MGRSFootprints[wrs2Footprint.name]:
            if mgrsFootprint.name in mgrsFootprintNames:
                ul, lr = mgrsFootprint.getBoundingBox(buffer=buffer, snap='landsat')
                reproject = wrs2Footprint.utm == mgrsFootprint.utm
                print('MGRS: '+mgrsFootprint.name, ul, lr, 'UTM='+mgrsFootprint.utm, 'reproject='+str(reproject))

if __name__ == '__main__':
    test()