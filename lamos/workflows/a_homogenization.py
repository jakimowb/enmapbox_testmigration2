from __future__ import division
import os
import hub.datetime
import hub.file
import hub.gdal.util, hub.gdal.api
import hub.rs.virtual
from hub.datetime import Date
from enmapbox import processing
from lamos.types import SensorXComposer, Product, Image, ImageStack, WRS2Archive, MGRSArchive, Archive, MGRSTilingScheme


class LandsatXComposer(SensorXComposer):

    def __init__(self):

        FMaskFile = lambda product: os.path.join(product.folder, product.name + '_cfmask.img')
        SRBandFile = lambda product, i: os.path.join(product.folder, product.name + '_sr_band' + str(i) + '.img')
        TOABandFile = lambda product, i: os.path.join(product.folder, product.name + '_toa_band' + str(i) + '.img')

        def sr(product):

            assert isinstance(product, Product)

            # landsat band assignments
            if product.name.startswith('LT'):
                bandNames =       ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir']
                wavelengthLower = [ 450,    520,     630,   760,   1550,    2080,    10400]
                wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500]
                filenames       = [SRBandFile(product, i) for i in [1,2,3,4,5,7]] + [TOABandFile(product, 6)]
                noDataValue        = -9999
            elif product.name.startswith('LE7'):
                bandNames       = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir',               'pan']
                wavelengthLower = [ 450,    520,     630,   770,   1550,    2090,    10400,               520]
                wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500,               900]
                filenames       = [SRBandFile(product, i) for i in [1,2,3,4,5,7]] + [TOABandFile(product, 6), None]
                noDataValue        = -9999
            elif product.name.startswith('LC8'):
                bandNames          = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pan', 'cirrus', 'tir1', 'tir2']
                wavelengthLower    = [ 430,       450,    530,     640,   850,   1570,    2110,    500,   1360,     10600,  11500 ]
                wavelengthUpper    = [ 450,       510,    590,     670,   880,   1600,    2290,    680,   1380,     11190,  12510 ]
                filenames          = [SRBandFile(product, i) for i in [1,2,3,4,5,6,7]] +          [None,  None] +  [TOABandFile(product, i) for i in [10,11]]
                noDataValue        = -9999
            else:
                raise Exception('not a landsat product!')

            images = list()
            bandNamesFiltered = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
            wavelengthFiltered = list()

            for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
                if bn in bandNamesFiltered:
                    wavelengthFiltered.append((wl+wu)/2.)
                    images.append(Image(name=bn, filename=fn))

            # prepare meta information
            MTLFile = os.path.join(product.folder, product.name + '_MTL.txt')
            ESPAFile = os.path.join(product.folder, product.name + '.xml')
            metas = hub.rs.virtual.parseLandsatMeta(mtlfilename=MTLFile, espafilename=ESPAFile)
            metas['band names'] = bandNamesFiltered
            metas['wavelength'] = wavelengthFiltered
            metas['data ignore value'] = noDataValue
            return ImageStack(name=product.name + '_sr.vrt', images=images, metas=metas)


        def qa(product):

            assert isinstance(product, Product)

            metas = {'band names' : ['cfmask'], 'data ignore value' : 255}

            return ImageStack(name=product.name + '_qa.vrt', images=[Image('cfmask', FMaskFile(product))], metas=metas)

        SensorXComposer.__init__(self, [sr, qa])


class TimeseriesBuilder():

    def __init__(self, names, bands, start=None, end=None):

        if start is None:
            start = Date(1, 1, 1)
        if end is None:
            end = Date(9999, 1, 1)

        assert isinstance(start, Date)
        assert isinstance(end, Date)

        self.names = names
        self.bands = bands
        self.start = start
        self.end = end


    def buildProduct(self, products, folder, envi=False, compressed=False):

        # surface reflectance stacks
        images_sr = list()
        images_qa = list()
        for product in products:
            assert isinstance(product, Product)
            date = hub.datetime.Date.fromYearDoy(year=int(product.name[9:13]),
                                                 doy=int(product.name[13:16]))
            if (date < self.start) or (date > self.end):
                continue

            images_sr += product.yieldImages('_sr.vrt')
            images_sr += product.yieldImages('_sr.img')
            images_qa += product.yieldImages('_qa.vrt')
            images_qa += product.yieldImages('_qa.img')

        infiles_sr = [image.filename for image in images_sr]
        infiles_qa = [image.filename for image in images_qa]
        inmetas = [processing.Meta(infile) for infile in infiles_sr]

        indecimalyear = [hub.datetime.Date(int(inmeta.getMetadataItem('acqdate')[0:4]), int(inmeta.getMetadataItem('acqdate')[5:7]), int(inmeta.getMetadataItem('acqdate')[8:10])).decimalYear() for inmeta in inmetas]

        insorted = sorted(list(zip(infiles_sr, infiles_qa, inmetas, indecimalyear)), key=lambda tup: tup[3])
        infiles_sr, infiles_qa, inmetas, indecimalyear = zip(*insorted)

        metaKeysIgnore = {'band_names', 'data_ignore_value', 'wavelength'}
        metaKeys = set(inmetas[0].getMetadataDict().keys()) - metaKeysIgnore

        for name, band, infiles in zip(self.names+['cfmask'], self.bands+[1], [infiles_sr]*len(self.bands)+[infiles_qa]):
            outfile = os.path.join(folder, name+'.vrt')
            inbands = [band]*len(infiles_sr)

            if os.path.exists(outfile):
                continue

            hub.gdal.util.stack_bands(outfile=outfile, infiles=infiles, inbands=inbands, verbose=False)

            # prepare output meta information
            outmeta = processing.Meta(outfile)
            for metaKey in metaKeys:
                outmeta.setMetadataItem(metaKey, [meta.getMetadataItem(metaKey) for meta in inmetas])
            outmeta.setMetadataItem('wavelength', indecimalyear)
            outmeta.setBandNames([meta.getMetadataItem('sceneid') for meta in inmetas])
            if name == 'cfmask':
                outmeta.setNoDataValue(255)
            else:
                outmeta.setNoDataValue(inmetas[0].getNoDataValue())
            outmeta.writeMeta(outfile)

            if envi:
                outfile = hub.gdal.util.gdal_translate(outfile=outfile.replace('.vrt', '.img'), infile=outfile, options='-of ENVI')
                outmeta.writeMeta(outfile)
                if compressed:
                    hub.envi.compress(infile=outfile, outfile=outfile)


    def buildArchive(self, archive, folder, name='timeseries', footprints=None, envi=False, compressed=False):

        assert isinstance(archive, Archive)
        print('Build Timeseries')
        for footprint in archive.yieldFootprints(filter=footprints):
            print(footprint.name)
            products = list(archive.yieldProducts(footprint))
            self.buildProduct(products, os.path.join(folder, footprint.subfolders(), name), envi=envi, compressed=compressed)

        return archive.__class__(folder=folder)


def test_sensorX(root, wrs2Footprints):

    landsatArchive = WRS2Archive(r'C:\Work\data\gms\landsat')
    composer = LandsatXComposer()
    lsXArchive = composer.composeArchive(archive=landsatArchive,
                                         folder=r'C:\Work\data\gms\landsatX',
                                         footprints=wrs2Footprints)
    lsXArchive.info()


def test_tiling(wrs2Footprints, mgrsFootprints):

    lsXWRS2Archive = WRS2Archive(r'C:\Work\data\gms\landsatX')
    tilingScheme = MGRSTilingScheme(pixelSize=30)
    lsXMGRSArchive = tilingScheme.tileWRS2Archive(archive=lsXWRS2Archive,
                                                  folder=r'c:\work\data\gms\landsatXMGRS',
                                                  buffer=300,
                                                  wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)
    lsXMGRSArchive.info()


def test_buildTimeseries(mgrsFootprints):

    lsXMGRSArchive = MGRSArchive(r'c:\work\data\gms\landsatXMGRS')
    tsBuilder = TimeseriesBuilder(names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                  bands=[1,2,3,4,5,6],
                                  start=Date(2015, 1, 1),
                                  end=Date(2017, 1, 1))
    lstsMGRSArchive = tsBuilder.buildArchive(lsXMGRSArchive, r'c:\work\data\gms\landsatTimeseriesMGRS',
                                             envi=True, compressed=True,
                                             footprints=mgrsFootprints)
    lstsMGRSArchive.info()


def test_pr():


    wrs2Footprints = ['172034','173034','169032','170032','178034','177034','176034','173035','172035']
    mgrsFootprints = ['37SEB','36SVG','38TMK','38SMK','37SEA','','','','','','','']
    '''
    landsatArchive = WRS2Archive(r'M:\LandsatData\Landsat_Turkey\04_Landsat')
    composer = LandsatXComposer()
    lsXArchive = composer.composeArchive(archive=landsatArchive,
                                         folder=r'M:\LandsatData\Landsat_Turkey\landsatX',
                                         footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    lsXMGRSArchive = tilingScheme.tileWRS2Archive(archive=lsXArchive,
                                                  folder=r'M:\LandsatData\Landsat_Turkey\landsatXMGRS',
                                                  buffer=300,
                                                  wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)
    '''
    lsXMGRSArchive = MGRSArchive(r'M:\LandsatData\Landsat_Turkey\landsatXMGRS')

    tsBuilder = TimeseriesBuilder(names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                  bands=[1, 2, 3, 4, 5, 6],
                                  start=Date(2000, 1, 1),
                                  end=Date(3000, 1, 1))
    lstsMGRSArchive = tsBuilder.buildArchive(lsXMGRSArchive, r'M:\LandsatData\Landsat_Turkey\landsatTimeseriesMGRS',
                                             envi=False, compressed=False,
                                             footprints=mgrsFootprints)


if __name__ == '__main__':
    import hub.timing
    hub.timing.tic()

    landsatArchive = WRS2Archive(r'M:\LandsatData\Landsat_Turkey\04_Landsat')
    wrs2Footprints = ['193024','194024']
    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']

    test_sensorX(wrs2Footprints=wrs2Footprints)
    test_tiling(wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)
    test_buildTimeseries(mgrsFootprints=mgrsFootprints)

#    test_pr()
    hub.timing.toc()
