from __future__ import division

import os

import ogr

import hub.datetime
import hub.file
import hub.gdal.util
import hub.rs.virtual
import rios.applier
from enmapbox import processing


class Type:

    def report(self):
        return processing.Report(str(self.__class__).split('.')[-1])

    def info(self):
        self.report().saveHTML().open()


class Image(Type):

    def __init__(self, name, filename, meta={}):

        self.name = name
        self.filename = filename
        self.meta = meta

    def report(self, title='Image'):

        report = processing.Report(title)
        report.append(processing.ReportParagraph('name = ' + self.name))
        report.append(processing.ReportParagraph('filename = ' + str(self.filename)))
        for k, v in self.meta.items():
            report.append(processing.ReportParagraph(k + ' = ' + str(v)))
        return report


class ImageStack(Type):

    def __init__(self, name, images, metas={}):

        for image in images:
            assert isinstance(image, Image)

#        self.metaKeys = metaKeys
        self.name = name
        self.images = images
        self.metas = metas

class Product(Type):

    def __init__(self, folder, extensions=['.vrt', '.img']):

        self.folder = folder
        self.scene = os.path.basename(folder)
        self.extensions = extensions


    def yieldImages(self, suffix=''):

        for extension in self.extensions:
            for basename in os.listdir(self.folder):
                if basename.endswith(extension):
                    filename = os.path.join(self.folder, basename)
                    if filename.endswith(suffix):
                        yield Image(name=basename, filename=filename)


    def getFilenameAssociations(self, prefix=''):

        infiles = rios.applier.FilenameAssociations()
        for image in self.yieldImages():
            infiles.__dict__[prefix+os.path.splitext(image.name)[0]] = image.filename
        return infiles


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportParagraph('folder = ' + self.folder))
        report.append(processing.ReportParagraph('scene = ' + self.scene))

        for image in self.yieldImages():
            report.appendReport(image.report(image.name))

        return report


class Footprint(Type):

    def __init__(self, name, ul, lr):

        self.name = name
        self.ul = ul
        self.lr = lr


    def subfolders(self):
        raise Exception('must be overwritten')

class MGRSFootprint(Footprint):

    bb = dict()

    @staticmethod
    def fromShp(name):

        if MGRSFootprint.bb.has_key(name):
            bb = MGRSFootprint.bb[name]
        else:
            shpRoot = r'C:\Work\data\gms\MGRS_100km_1MIL_Files'
            shp = os.path.join(shpRoot, r'MGRS_100kmSQ_ID_' + name[0:3] + '\MGRS_100kmSQ_ID_' + name[0:3] + '.shp')
            dataSource = ogr.Open(shp)
            layer = dataSource.GetLayer(0)
            for feature in layer:
                if feature.GetField('MGRS') == name:
                    e = feature.geometry().GetEnvelope()
                    bb = map(int, map(round, (e[0], e[3], e[1], e[2])))
                    break

        return MGRSFootprint(name=name, ul=bb[0:2], lr=bb[2:4])


    def __init__(self, name, ul, lr):

        Footprint.__init__(self, name, ul, lr)
        self.utm = name[0:2]


    def subfolders(self):

        return os.path.join(self.utm, self.name)


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportParagraph('name =     ' + self.name))
        report.append(processing.ReportParagraph('utm zone = ' + self.utm))
        report.append(processing.ReportParagraph('bounding box ul, lr = ' + str(self.ul) + ' ' + str(self.lr)))
        return report


class WRS2Footprint(Footprint):

    utmLookup = {'193024': '33', '194024': '32'}

    def __init__(self, name, ul=None, lr=None):

        Footprint.__init__(self, name, ul, lr)
        self.utm = WRS2Footprint.utmLookup[name]
        self.path = self.name[ :3]
        self.row =  self.name[3: ]


    def subfolders(self):

        return os.path.join(self.path, self.row)


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportParagraph('name =     ' + self.name))
        report.append(processing.ReportParagraph('utm zone = ' + self.utm))
        report.append(processing.ReportParagraph('path = ' + self.path))
        report.append(processing.ReportParagraph('row = ' + self.row))
        report.append(processing.ReportParagraph('bounding box ul, lr = ' + str(self.ul) + ' ' + str(self.lr)))
        return report






'''
class LandsatProduct(Product):

    @staticmethod
    def open(folder):

        scene = os.path.basename(folder)
        if scene.startswith('LC8'):
            result = LandsatLC8Product(folder)
        elif scene.startswith('LE7'):
            result = LandsatLE7Product(folder)
        elif scene.startswith('LT'):
            result = LandsatLTProduct(folder)
        else:
            raise Exception('unknown landsat product')

        return result

    def __init__(self, folder):

        scene = os.path.basename(folder)
        footprint = WRS2Footprint(scene[3:9])
        Product.__init__(self, folder=folder, footprint=footprint)
        self.MTLFile = os.path.join(self.folder, self.scene + '_MTL.txt')
        self.ESPAFile = os.path.join(self.folder, self.scene + '.xml')
        self.addImage(Image(name='fmask', filename=self.FMaskFile(), meta={'noDataValue':255}))


    def FMaskFile(self):
        return os.path.join(self.folder, self.scene + '_cfmask.img')


    def SRBandFile(self, i):
        return os.path.join(self.folder, self.scene + '_sr_band' + str(i) + '.img')


    def TOABandFile(self, i):
        return os.path.join(self.folder, self.scene + '_toa_band' + str(i) + '.img')


class LandsatLC8Product(LandsatProduct):

    def __init__(self, folder):

        LandsatProduct.__init__(self, folder=folder)

        bandNames          = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pan', 'cirrus', 'tir1', 'tir2']
        wavelengthLower    = [ 430,       450,    530,     640,   850,   1570,    2110,    500,   1360,     10600,  11500 ]
        wavelengthUpper    = [ 450,       510,    590,     670,   880,   1600,    2290,    680,   1380,     11190,  12510 ]
        filenames          = [self.SRBandFile(i) for i in [1,2,3,4,5,6,7]] +               [None,  None] +  [self.TOABandFile(i) for i in [10,11]]
        noDataValue        = -9999

        for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
            meta = {'wavelength' : (wl + wu) / 2., 'noDataValue' : noDataValue}
            self.addImage(Image(name=bn, filename=fn, meta=meta))


class LandsatLE7Product(LandsatProduct):

    def __init__(self, folder):

        LandsatProduct.__init__(self, folder)

        bandNames       = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir',               'pan']
        wavelengthLower = [ 450,    520,     630,   770,   1550,    2090,    10400,               520]
        wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500,               900]
        filenames       = [self.SRBandFile(i) for i in [1,2,3,4,5,7]] +     [self.TOABandFile(6), None]
        noDataValue        = -9999

        for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
            meta = {'wavelength' : (wl + wu) / 2., 'noDataValue' : noDataValue}
            self.addImage(Image(name=bn, filename=fn, meta=meta))


class LandsatLTProduct(LandsatProduct):

    def __init__(self, folder):

        LandsatProduct.__init__(self, folder)


        bandNames =       ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir']
        wavelengthLower = [ 450,    520,     630,   760,   1550,    2080,    10400]
        wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500]
        filenames       = [self.SRBandFile(i) for i in [1,2,3,4,5,7]] +      [self.TOABandFile(6)]
        noDataValue        = -9999

        for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
            meta = {'wavelength' : (wl + wu) / 2., 'noDataValue' : noDataValue}
            self.addImage(Image(name=bn, filename=fn, meta=meta))


class MGRSProduct(Product):

    def __init__(self, folder):

        footprint = MGRSFootprint.fromShp(os.path.basename(os.path.dirname(folder)))
        Product.__init__(self, folder=folder, footprint=footprint)


class WRS2Product(Product):


    def __init__(self, folder, footprint, extensions=[]):

        footprint = WRS2Footprint(os.path.basename(folder)[3:9])
        Product.__init__(self, folder=folder, footprint=footprint, extensions=extensions)
'''


class SensorXComposer:

    def __init__(self, ufuncs):

        self.ufuncs = ufuncs


    def composeProduct(self, product, folder=None):

        assert isinstance(product, Product)

        if folder is None: folder = os.path.join(processing.env.tempfile(), product.scene)

        for ufunc in self.ufuncs:

            imageStack = ufunc(product)
            assert isinstance(imageStack, ImageStack)
            outfile = os.path.join(folder, imageStack.name)
            infiles = [band.filename for band in imageStack.images]
            hub.gdal.util.stack(outfile=outfile, infiles=infiles)

            meta = processing.Meta(outfile)
            meta.setBandNames(imageStack.metas['band names'])
            meta.setNoDataValue(imageStack.metas['data ignore value'])
            for key, value in imageStack.metas.items():
                meta.setMetadataItem(key=key, value=value)
            meta.writeMeta(outfile)

        return Product(folder)


    def composeArchive(self, archive, folder):

        assert isinstance(archive, Archive)
        for footprint in archive.yieldFootprints():
            for product in archive.yieldProducts(footprint):
                self.composeProduct(product, os.path.join(folder, footprint.subfolders(), product.scene))
        return Archive(folder=folder, yieldProducts=archive.yieldProducts, yieldFootprints=archive.yieldFootprints)


class LandsatXComposer(SensorXComposer):

    def __init__(self):

        FMaskFile = lambda product: os.path.join(product.folder, product.scene + '_cfmask.img')
        SRBandFile = lambda product, i: os.path.join(product.folder, product.scene + '_sr_band' + str(i) + '.img')
        TOABandFile = lambda product, i: os.path.join(product.folder, product.scene + '_toa_band' + str(i) + '.img')

        def sr(product):

            assert isinstance(product, Product)

            # landsat band assignments
            if product.scene.startswith('LT'):
                bandNames =       ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir']
                wavelengthLower = [ 450,    520,     630,   760,   1550,    2080,    10400]
                wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500]
                filenames       = [SRBandFile(product, i) for i in [1,2,3,4,5,7]] + [TOABandFile(product, 6)]
                noDataValue        = -9999
            elif product.scene.startswith('LE7'):
                bandNames       = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir',               'pan']
                wavelengthLower = [ 450,    520,     630,   770,   1550,    2090,    10400,               520]
                wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500,               900]
                filenames       = [SRBandFile(product, i) for i in [1,2,3,4,5,7]] + [TOABandFile(product, 6), None]
                noDataValue        = -9999
            elif product.scene.startswith('LC8'):
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
            MTLFile = os.path.join(product.folder, product.scene + '_MTL.txt')
            ESPAFile = os.path.join(product.folder, product.scene + '.xml')
            metas = hub.rs.virtual.parseLandsatMeta(mtlfilename=MTLFile, espafilename=ESPAFile)
            metas['band names'] = bandNamesFiltered
            metas['wavelength'] = wavelengthFiltered
            metas['data ignore value'] = noDataValue
            return ImageStack(name=product.scene+'_sr.vrt', images=images, metas=metas)


        def qa(product):

            assert isinstance(product, Product)

            metas = {'band names' : ['cfmask'], 'data ignore value' : 255}

            return ImageStack(name=product.scene+'_qa.vrt', images=[Image('cfmask', FMaskFile(product))], metas=metas)

        SensorXComposer.__init__(self, [sr, qa])


class Archive(Type):

    @staticmethod
    def fromWRS2(folder, extensions=['.img', '.vrt']):

        def yieldFootprints():
            for path in os.listdir(folder):
                for row in os.listdir(os.path.join(folder, path)):
                    yield WRS2Footprint(path+row)

        def yieldProducts(footprint):
            assert isinstance(footprint, WRS2Footprint)
            for scene in os.listdir(os.path.join(folder, footprint.path, footprint.row)):
                yield Product(folder=os.path.join(folder, footprint.path, footprint.row, scene), extensions=extensions)

        return Archive(folder=folder, yieldFootprints=yieldFootprints, yieldProducts=yieldProducts, type='wrs2')


    @staticmethod
    def fromMGRS(folder, extensions=['.img', '.vrt']):

        def yieldFootprints():
            for utm in os.listdir(folder):
                for mgrs in os.listdir(os.path.join(folder, utm)):
                    yield MGRSFootprint.fromShp(mgrs)

        def yieldProducts(footprint):
            assert isinstance(footprint, MGRSFootprint)
            for scene in os.listdir(os.path.join(folder, footprint.utm, footprint.name)):
                yield Product(folder=os.path.join(folder, footprint.utm, footprint.name, scene), extensions=extensions)

        return Archive(folder=folder, yieldFootprints=yieldFootprints, yieldProducts=yieldProducts, type='mgrs')


    def __init__(self, folder, yieldFootprints, yieldProducts, type=None):

        self.folder = folder
        self.yieldFootprints = yieldFootprints
        self.yieldProducts = yieldProducts
        self.type = type

    def report(self):

        report = processing.Report(str(self.__class__).split('.')[-1])
        report.append(processing.ReportParagraph('foldername = ' + self.folder))
        report.append(processing.ReportHeading('Footprints'))
        for footprint in self.yieldFootprints():
            report.append(processing.ReportHeading(footprint.name, 1))
            report.append(
                processing.ReportParagraph('Products = ' + str([product.scene for product in self.yieldProducts(footprint)])))

        return report

'''
class LandsatArchive(Archive):

    def openProduct(self, folder):

        return LandsatProduct.open(folder)

    def getProductFolders(self):
        for path in os.listdir(self.folder):
            for row in os.listdir(os.path.join(self.folder, path)):
                for scene in os.listdir(os.path.join(self.folder, path, row)):
                    folder = os.path.join(self.folder, path, row, scene)
                    yield folder


class MGRSArchive(Archive):

    def openProduct(self, folder):
        return MGRSProduct(folder)


    def getProductFolders(self):
        for utm in os.listdir(self.folder):
            for mgrs in os.listdir(os.path.join(self.folder, utm)):
                for scene in os.listdir(os.path.join(self.folder, utm, mgrs)):
                    folder = os.path.join(self.folder, utm, mgrs, scene)
                    yield folder


class WRS2Archive(Archive):

    def openProduct(self, folder):
        return WRS2Product(folder)
'''


class MGRSTilingScheme(Type):

    shp = r'C:\Work\data\gms\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'
    MGRSFootprints = dict()

    def __init__(self, pixelSize):

        self.pixelSize = pixelSize
        self.pixelOrigin = [15,15]


    def cacheMGRSFootprints(self, wrs2Footprints):

        for wrs2Footprint in wrs2Footprints:
            assert isinstance(wrs2Footprint, WRS2Footprint)
            MGRSTilingScheme.MGRSFootprints[wrs2Footprint.name] = list()

        wrs2FootprintNames = [wrs2Footprint.name for wrs2Footprint in wrs2Footprints]

        dataSource = ogr.Open(self.shp)
        layer = dataSource.GetLayer(0)
        for feature in layer:
            wrs2FootprintName = str(int(feature.GetField('WRSPR')))
            if wrs2FootprintName in wrs2FootprintNames:
                mgrsFootprint = MGRSFootprint.fromShp(name=feature.GetField('GRID1MIL')+ feature.GetField('GRID100K'))
                MGRSTilingScheme.MGRSFootprints[wrs2FootprintName].append(mgrsFootprint)


    def tileWRS2Product(self, product, wrs2Footprint, folder, buffer=0):

        assert isinstance(product, Product)
        assert isinstance(wrs2Footprint, WRS2Footprint)

        print list(MGRSTilingScheme.MGRSFootprints[wrs2Footprint.name])
        for mgrsFootprint in MGRSTilingScheme.MGRSFootprints[wrs2Footprint.name]:

            # - snap bounding box to target pixel grid
            xoff = (mgrsFootprint.ul[0] - self.pixelOrigin[0]) % self.pixelSize
            yoff = (mgrsFootprint.ul[1] - self.pixelOrigin[1]) % self.pixelSize

            ul = (mgrsFootprint.ul[0] - xoff - buffer, mgrsFootprint.ul[1] - yoff + buffer)
            lr = (mgrsFootprint.lr[0] - xoff + buffer, mgrsFootprint.lr[1] - yoff - buffer)


            for image in product.yieldImages():

                infile = image.filename

                if wrs2Footprint.utm == mgrsFootprint.utm:
                    of, extension = [(' -of ENVI', '.img'), (' -of VRT', '.vrt')][1]
                    projwin = ' -projwin ' + str(ul[0]) + ' ' + str(max(lr[1],ul[1])) + ' ' + str(lr[0]) + ' ' + str(min(lr[1],ul[1]))
                    outfile = os.path.join(folder, mgrsFootprint.utm, mgrsFootprint.name, product.scene,
                                           os.path.splitext(os.path.basename(infile))[0] + extension)

                    hub.gdal.util.gdal_translate(outfile=outfile, infile=infile, options=of+projwin)

                else:
                    envi = False
                    of, extension = [(' -of VRT', '.vrt'), (' -of ENVI', '.img')][envi]
                    te = ' -te ' + str(ul[0]) + ' ' + str(min(ul[1],lr[1])) + ' ' + str(lr[0]) + ' ' + str(max(ul[1], lr[1]))
                    t_srs = ' -t_srs  EPSG:326' + mgrsFootprint.utm
                    tr = ' -tr ' + str(self.pixelSize) + ' ' + str(self.pixelSize)
                    overwrite = ' -overwrite'
                    multi = ' -multi'
                    wm = ' -wm 5000'
                    outfile = os.path.join(folder, mgrsFootprint.utm, mgrsFootprint.name, product.scene,
                                           os.path.splitext(os.path.basename(infile))[0] + extension)

                    hub.gdal.util.gdalwarp(outfile=outfile,
                                           infile=infile,
                                           options=of+overwrite+t_srs+tr+te+multi+wm)

                    if envi:
                        hub.envi.compress(infile=outfile, outfile=outfile)

                # prepare meta information
                inmeta = processing.Meta(infile)
                outmeta = processing.Meta(outfile)
                outmeta.setMetadataDict(inmeta.getMetadataDict())
                outmeta.writeMeta(outfile)


    def tileWRS2Archive(self, archive, folder, buffer=0):

        assert isinstance(archive, Archive)

        self.cacheMGRSFootprints(list(archive.yieldFootprints()))

        for footprint in archive.yieldFootprints():
            for product in archive.yieldProducts(footprint):
                print footprint.name, product.scene
                self.tileWRS2Product(product=product, wrs2Footprint=footprint, folder=folder, buffer=buffer)

        return Archive.fromMGRS(folder)


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportHeading('MGRS Tiles by WRS-2 Footprints'))
        for footprint in self.mgrstilesByWRS2Footprint.keys():
            report.append(processing.ReportHeading(footprint, 1))
            report.append(processing.ReportParagraph('MGRS Tiles = ' + str([product.name for product in self.mgrstilesByWRS2Footprint[footprint]])))
        return report


class TimeseriesBuilder(Type):

    def __init__(self, names, bands):

        self.names = names
        self.bands = bands


    def buildProduct(self, products, folder, envi=False):

        # surface reflectance stacks
        images_sr = list()
        images_qa = list()
        for product in products:
            assert isinstance(product, Product)
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
            hub.gdal.util.stack_bands(outfile=outfile, infiles=infiles, inbands=inbands)

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

    def buildArchive(self, archive, folder, name='timeseries', envi=False):

        assert isinstance(archive, Archive)
        for footprint in archive.yieldFootprints():
            products = list(archive.yieldProducts(footprint))
            self.buildProduct(products, os.path.join(folder, footprint.subfolders(), name), envi=envi)
            break

        extensions = ['.vrt', '.img'][envi]
        if archive.type == 'mgrs':
            return Archive.fromMGRS(folder=folder, extensions=extensions)
        elif archive.type == 'wrs2':
            return Archive.fromWRS2(folder=folder, extensions=extensions)
        else:
            raise Exception('unknown archive type!')


def ufunc(info, inputs, outputs, args):
    pass


class Applier:

    def applyToFootprint(self, products, folder, ufunc):

        pass
        # Apply the function to the inputs, creating the outputs.
        #rios.applier.apply(ufunc, infiles, outfiles, args, controls)


    def applyToArchives(self, inputs, outputs, ufunc):

        for input in inputs:
            assert isinstance(input, ApplierInput)

        for output in outputs:
            assert isinstance(output, ApplierOutput)

        for footprint in inputs[0].archive.yieldFootprints(): # use first input as master
            for input in inputs:
                assert isinstance(input, ApplierInput)


                products = [product for product in  input.archive.yieldProducts(footprint)]
               # self.buildProduct(products, os.path.join(folder, footprint.subfolders(), name), envi=envi)

#            def applyToFootprint(self, products, folder, ufunc)

 #       return Archive.fromMGRS(folder=folder)


class ApplierInput():

    def __init__(self, key, archive, productName, imageNames):
        assert isinstance(key, basestring)
        assert isinstance(archive, Archive)
        assert isinstance(productName, basestring)
        assert isinstance(imageNames, list)
        self.key = key
        self.archive = archive
        self.productName = productName
        self.imageNames = imageNames

    def getFilenameAssociations(self, footprint):

        products = self.archive.yieldProducts(footprint)


class ApplierOutput():

    def __init__(self, key, folder, productName, imageNames):
        assert isinstance(key, basestring)
        assert isinstance(folder, basestring)
        assert isinstance(productName, basestring)
        assert isinstance(imageNames, list)
        self.key = key
        self.folder = folder
        self.productName = productName
        self.imageNames = imageNames


def test_footprint():

#    footprint = MGRSFootprint.fromShp('32UPB')
    footprint = WRS2Footprint('193024')
    footprint.info()


def test_product():
    product = Product(r'C:\Work\data\gms\landsat\194\024\LT51940242010189KIS01')
    product = Product(r'C:\Work\data\gms\landsatTimeseriesMGRS\32\32UNB\timeseries')
    #product.info()
    inputs = product.getFilenameAssociations()
    print inputs.__dict__.keys()

def test_archive():
    archive = Archive.fromWRS2(r'C:\Work\data\gms\landsat')
    #archive = MGRSArchive(r'c:\work\data\gms\sensorXMGRS')
    #archive = WRS2Archive(r'c:\work\data\gms\landsatX', extensions=['.img', '.vrt'])
    archive.info()


def test_composeProduct():

    lc8 = Product(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    composer = LandsatXComposer()
    lsX = composer.composeProduct(lc8, r'c:\work\data\gms\test\LandsatComposition\LC81930242015276LGN00')
    lsX.info()


def test_composeArchive():

    landsatArchive = Archive.fromWRS2(r'C:\Work\data\gms\landsat')
    composer = LandsatXComposer()
    lsXArchive = composer.composeArchive(landsatArchive, r'C:\Work\data\gms\landsatX')
    lsXArchive.info()


def test_tileProduct():

    lsX = Product(r'c:\work\data\gms\test\LandsatComposition\LC81930242015276LGN00')
    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Product(lsX, r'c:\work\data\gms\test\tiles', buffer=300)


def test_tileArchive():

    lsXArchive = Archive.fromWRS2(r'C:\Work\data\gms\landsatX')
    tilingScheme = MGRSTilingScheme(pixelSize=30)
    lsXMGRSArchive = tilingScheme.tileWRS2Archive(lsXArchive, r'c:\work\data\gms\landsatXMGRS', buffer=300)

    lsXMGRSArchive.info()


def test_buildTimeseries():

    lsXMGRSArchive = Archive.fromMGRS(r'c:\work\data\gms\landsatXMGRS')
    tsBuilder = TimeseriesBuilder(names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                  bands=[1,2,3,4,5,6])
    lstsMGRSArchive = tsBuilder.buildArchive(lsXMGRSArchive, r'c:\work\data\gms\landsatTimeseriesMGRS', envi=False)
    lstsMGRSArchive.info()

def test_applierInput():

    input = ApplierInput(key='ts', archive=Archive.fromMGRS(r'c:\work\data\gms\landsatTimeseriesMGRS'),
                           productName='timeseries', imageNames=['nir', 'red'])
    print input.getFilenameAssociations(MGRSFootprint.fromShp('32UNP'))


def test_apply():

    inputs = [ApplierInput(key='ts', archive=Archive.fromMGRS(r'c:\work\data\gms\landsatTimeseriesMGRS'),
                           productName='timeseries', imageNames=['nir', 'red'])]
    outputs = [ApplierOutput(key='vi', folder=r'c:\work\data\gms\products', productName='vi', imageNames=['ndvi'])]
    applier = Applier()
    productsArchive = applier.applyToArchives(inputs=inputs, outputs=outputs, ufunc=ufunc)
    productsArchive.info()

if __name__ == '__main__':

    import hub.timing
    hub.timing.tic()
    #test_footprint()
    #test_product()
    #test_archive()
    #test_composeProduct()
    #test_composeArchive()
    #test_tileProduct()
    #test_tileArchive()
    #test_buildTimeseries()
    test_applierInput()
    #test_apply()


    hub.timing.toc()
