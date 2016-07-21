from __future__ import division
import os
import hub.datetime
import hub.file
import hub.gdal.util, hub.gdal.api
import hub.rs.virtual
from hub.timing import tic, toc
from hub.datetime import Date
from enmapbox import processing
from lamos.types import SensorXComposer, Product, Image, ImageStack, WRS2Archive, MGRSArchive, Archive, MGRSTilingScheme, MGRSFootprint


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

    MGRSFootprint.shpRoot = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    wrs2Footprints = ['172034','173034','169032','170032','178034','177034','176034','173035','172035']
    mgrsFootprints = ['37SEB','36SVG','38TMK','38SMK','37SEA']

    landsatArchive = WRS2Archive(r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\04_Landsat')
    composer = LandsatXComposer()
    lsXArchive = composer.compose(archive=landsatArchive,
                                         folder=r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatX',
                                         footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    lsXMGRSArchive = tilingScheme.tileWRS2Archive(archive=lsXArchive,
                                                  folder=r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatXMGRS',
                                                  buffer=300,
                                                  wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    lsXMGRSArchive = MGRSArchive(r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatXMGRS')

    tsBuilder = TimeseriesBuilder(names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                  bands=[1, 2, 3, 4, 5, 6],
                                  start=Date(2000, 1, 1),
                                  end=Date(3000, 1, 1))
    lstsMGRSArchive = tsBuilder.buildArchive(lsXMGRSArchive, r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatTimeseriesMGRS',
                                             envi=True, compressed=False,
                                             footprints=mgrsFootprints)


if __name__ == '__main__':

    hub.timing.tic()
    test_pr()
    hub.timing.toc()
