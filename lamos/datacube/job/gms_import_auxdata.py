from lamos.datacube.types import MGRSFootprint, MGRSFootprintCollection, Image, LANDSAT_ANCHOR
from os.path import join
from hub.timing import tic, toc

def doit():
    root = r'H:\EuropeanDataCube\auxiliary'
    roi = MGRSFootprintCollection(['33UUT','33UUU','33UVT','33UVU'])

    # import elevation data
    image = Image(filename=join(root, 'elevation', 'srtm1arcsecond.vrt'))
    tiles = image.importIntoDataCube(dirname=join(root, 'auxiliaryMGRS'), footprints=roi,
                                     productname='auxiliary',
                                     imagename='elevation',
                                     bandnames=['elevation'],
                                     r='bilinear', ot='Int16',
                                     resolution=30, buffer=300, anchor=LANDSAT_ANCHOR)
    for tile in tiles:
        tile.saveAsGTiff()

    # import climate data
    image = Image(filename=join(root, 'climate', 'bioclim.tif'))
    tiles = image.importIntoDataCube(dirname=join(root, 'auxiliaryMGRS'), footprints=roi,
                                     productname='auxiliary',
                                     imagename='bioclim',
                                     bandnames=['BIO'+str(i).zfill(2) for i in range(1,20)],
                                     r='bilinear', ot='Int16',
                                     resolution=30, buffer=300, anchor=LANDSAT_ANCHOR)
    for tile in tiles:
        tile.saveAsGTiff()

if __name__ == '__main__':
    MGRSFootprint.loadLookup(r'H:\EuropeanDataCube\lookup\mgrsFootprintUTMLookup.json')
    tic()
    doit()
    toc()
