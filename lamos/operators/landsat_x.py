from __future__ import division
import os
import hub.datetime
import hub.file
import hub.gdal.util, hub.gdal.api
import hub.rs.virtual
from hub.timing import tic, toc
from hub.datetime import Date
from enmapbox import processing
from lamos.types import SensorXComposer, Product, Image, ImageStack, MGRSArchive, MGRSTilingScheme, MGRSFootprint, WRS2Footprint


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

    def __init__(self, names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'], bands=[1, 2, 3, 4, 5, 6], start=None, end=None):

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

            # prepare output meta information
            def prepareMeta(outfile):
                outmeta = processing.Meta(outfile)
                for metaKey in metaKeys:
                    outmeta.setMetadataItem(metaKey, [meta.getMetadataItem(metaKey) for meta in inmetas])
                outmeta.setMetadataItem('wavelength', indecimalyear)
                outmeta.setBandNames([meta.getMetadataItem('sceneid') for meta in inmetas])
                if name == 'cfmask':
                    outmeta.setNoDataValue(255)
                else:
                    outmeta.setNoDataValue(inmetas[0].getNoDataValue())
                return outmeta

            if not os.path.exists(outfile):
                hub.gdal.util.stack_bands(outfile=outfile, infiles=infiles, inbands=inbands, verbose=False)
                outmeta = prepareMeta(outfile)
                outmeta.writeMeta(outfile)

            if envi:
                outfile2 = outfile.replace('.vrt', '.img')
                if not os.path.exists(outfile2):
                    hub.gdal.util.gdal_translate(outfile=outfile2, infile=outfile, options='-of ENVI')
                    outmeta = prepareMeta(outfile2)
                    outmeta.writeMeta(outfile2)
                    if compressed:
                        hub.envi.compress(infile=outfile2, outfile=outfile2)


    def build(self, infolder, outfolder, name='timeseries', footprints=None, envi=False, compressed=False):

        archive = MGRSArchive(infolder)
        print('Build Timeseries')
        for footprint in archive.yieldFootprints(filter=footprints):
            print(footprint.name)
            products = list(archive.yieldProducts(footprint))
            self.buildProduct(products, os.path.join(outfolder, footprint.subfolders(), name), envi=envi, compressed=compressed)


def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'C:\Work\data\gms\landsat'
    folder2 = r'C:\Work\data\gms\landsatX'
    folder3 = r'C:\Work\data\gms\landsatXMGRS'
    folder4 = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['193024','194024']
    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    composer = LandsatXComposer()
    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300,
                                 wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    tsBuilder = TimeseriesBuilder(start=Date(1900, 1, 1), end=Date(2017, 1, 1))
    tsBuilder.build(infolder=folder3, outfolder=folder4, envi=True, compressed=False, footprints=mgrsFootprints)


if __name__ == '__main__':

    tic()
    test()
    toc()
