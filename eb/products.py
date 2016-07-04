from __future__ import division
import os
import hub.gdal.util, hub.file, hub.rs.landsat
import eb
import ogr, gdal

class Type:

    def report(self):
        return eb.Report(str(self.__class__).split('.')[-1])

    def info(self):
        self.report().saveHTML().open()


class Image(Type):

    def __init__(self, name, filename, meta={}):

        self.name = name
        self.filename = filename
        self.meta = meta

    def report(self, title='Image'):

        report = eb.Report(title)
        report.append(eb.ReportParagraph('name = '+self.name))
        report.append(eb.ReportParagraph('filename = '+str(self.filename)))
        return report


class Product(Type):

    def __init__(self, folder):
        self.folder = folder
        self.sceneId = os.path.basename(folder)
        self.images = dict()

    def addImage(self, image):
        assert isinstance(image, Image)
        self.images[image.name] = image

    def Images(self, names):
        return [self.images[name] for name in names]

    def footprint(self):
        raise Exception('methode must be overwritten!')

    def subfolders(self):
        raise Exception('methode must be overwritten!')

    def report(self):

        report = Type.report(self)
        report.append(eb.ReportParagraph('folder = ' + self.folder))
        report.append(eb.ReportParagraph('sceneId = ' + self.sceneId))

        for name in sorted(self.images.keys()):
            report.appendReport(self.images[name].report(name))

        return report


class WRS2Product(Product):

    def footprint(self):
        return self.sceneId[3:9]

    def subfolders(self):
        return os.path.join(self.footprint()[0:3], self.footprint()[3:], self.sceneId)


class LandsatProduct(WRS2Product):

    @staticmethod
    def open(folder):

        sceneId = os.path.basename(folder)
        if sceneId.startswith('LC8'):
            result = LandsatLC8Product(folder)
        elif sceneId.startswith('LE7'):
            result = LandsatLE7Product(folder)
        elif sceneId.startswith('LT'):
            result = LandsatLTProduct(folder)
        else:
            raise Exception('unknown landsat product')

        return result

    def __init__(self, folder):
        Product.__init__(self, folder)
        self.MTLFile = os.path.join(self.folder, self.sceneId + '_MTL.txt')
        self.ESPAFile = os.path.join(self.folder, self.sceneId + '.xml')
        self.addImage(Image(name='fmask', filename=self.FMaskFile()))


    def FMaskFile(self):
        return os.path.join(self.folder, self.sceneId + '_cfmask.img')


    def SRBandFile(self, i):
        return os.path.join(self.folder, self.sceneId + '_sr_band' + str(i) + '.img')


    def TOABandFile(self, i):
        return os.path.join(self.folder, self.sceneId + '_toa_band' + str(i) + '.img')


class LandsatLC8Product(LandsatProduct):

    def __init__(self, folder):

        LandsatProduct.__init__(self, folder)

        bandNames          = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pan', 'cirrus', 'tir1', 'tir2']
        wavelengthLower    = [ 430,       450,    530,     640,   850,   1570,    2110,    500,   1360,     10600,  11500 ]
        wavelengthUpper    = [ 450,       510,    590,     670,   880,   1600,    2290,    680,   1380,     11190,  12510 ]
        filenames          = [self.SRBandFile(i) for i in [1,2,3,4,5,6,7]] +               [None,  None] +  [self.TOABandFile(i) for i in [10,11]]

        for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
            meta = {'wavelength' : (wl + wu) / 2.}
            self.addImage(Image(name=bn, filename=fn, meta=meta))


class LandsatLE7Product(LandsatProduct):

    def __init__(self, folder):

        LandsatProduct.__init__(self, folder)

        bandNames       = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir',               'pan']
        wavelengthLower = [ 450,    520,     630,   770,   1550,    2090,    10400,               520]
        wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500,               900]
        filenames       = [self.SRBandFile(i) for i in [1,2,3,4,5,7]] +     [self.TOABandFile(6), None]

        for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
            self.addImage(Image(name=bn, filename=fn, wavelength=(wl + wu) / 2))


class LandsatLTProduct(LandsatProduct):

    def __init__(self, folder):

        LandsatProduct.__init__(self, folder)


        bandNames =       ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'tir']
        wavelengthLower = [ 450,    520,     630,   760,   1550,    2080,    10400]
        wavelengthUpper = [ 520,    600,     690,   900,   1750,    2350,    12500]
        filenames       = [self.SRBandFile(i) for i in [1,2,3,4,5,7]] +      [self.TOABandFile(6)]

        for bn, wl, wu, fn in zip(bandNames, wavelengthLower, wavelengthUpper, filenames):
            self.addImage(Image(name=bn, filename=fn, wavelength=(wl + wu) / 2))


class SensorXConverter:

    def __init__(self, imageNamesSR, imageNamesQA):

        self.imageNamesSR = imageNamesSR
        self.imageNamesQA = imageNamesQA


    def convertProduct(self, product, folder=None):

        assert isinstance(product, Product)
        if folder is None: folder = os.path.join(eb.env.tempfile(), product.sceneId)

        filenameQA = os.path.join(folder, product.sceneId + '_qa.vrt')
        filenameSR = os.path.join(folder, product.sceneId + '_sr.vrt')

        filenames = [band.filename for band in product.Images(self.imageNamesSR)]
        hub.gdal.util.stack(filenameSR, filenames)

        filenames = [band.filename for band in product.Images(self.imageNamesQA)]
        hub.gdal.util.stack(filenameQA, filenames)

        # set up ENVI Metadata
        meta = eb.Meta(filenameSR)
        meta.setBandNames(self.imageNamesSR)
        meta.writeMeta(filenameSR)

        meta = eb.Meta(filenameQA)
        meta.setBandNames(self.imageNamesQA)
        meta.writeMeta(filenameQA)

        return SensorXWRS2Product(folder)


    def convertArchive(self, archive, folder, WRS2=True):

        assert isinstance(archive, LandsatArchive)
        for footprint in archive.footprints():
            for product in archive.products[footprint]:
                self.convertProduct(product, os.path.join(folder, product.subfolders()))

        return SensorXArchive(folder)


class SensorXWRS2Product(WRS2Product):

    def __init__(self, folder):

        Product.__init__(self, folder)
        self.filenameSR = os.path.join(self.folder, self.sceneId+'_sr.vrt')
        self.filenameQA = os.path.join(self.folder, self.sceneId+'_qa.vrt')


    def getUTMZone(self):

        ds = gdal.Open(self.filenameSR)
        wkt = ds.GetProjection()
        zone = wkt[wkt.find('UTM Zone')+9:19]
        return zone

    def report(self):
        report = Type.report(self)
        text = 'filenameSR = ' + self.filenameSR + '\nfilenameQA = ' + self.filenameQA
        report.append(eb.ReportMonospace(text))
        return report


class Archive(Type):

    def __init__(self, folder):

        self.folder = folder
        self.products = dict()
        self.addProducts()


    def getProducts(self):

        raise Exception()


    def addProducts(self):

        folders = self.getProducts()
        for folder in folders:
            product = self.openProduct(folder)
            if not self.products.has_key(product.footprint()):
                self.products[product.footprint()] = list()
            self.products[product.footprint()].append(product)


    def footprints(self):
        return sorted(self.products.keys())



    def report(self):

        report = eb.Report(str(self.__class__).split('.')[-1])
        report.append(eb.ReportParagraph('foldername = ' + self.folder))
        report.append(eb.ReportHeading('Footprints'))
        for footprint in self.footprints():
            report.append(eb.ReportHeading(footprint, 1))
            report.append(eb.ReportParagraph('Products = ' + str([product.sceneId for product in self.products[footprint]])))

        return report


class LandsatArchive(Archive):

    def openProduct(self, folder):

        return LandsatProduct.open(folder)


    def getProducts(self):

        return [os.path.dirname(mtlFile) for mtlFile in hub.file.filesearch(self.folder, '*_MTL.txt')]


class SensorXArchive(Archive):

    def openProduct(self, folder):

        return SensorXWRS2Product(folder)

    def getProducts(self):

        return [os.path.dirname(file) for file in hub.file.filesearch(self.folder, '*_sr.vrt')]


class MGRSProduct(Product):

    def __init__(self, folder):

        Product.__init__(self, folder)
        self.mgrsTile = MGRSTile(os.path.basename(os.path.dirname(self.folder)))

    def footprint(self):
        return self.mgrsTile.name

    def subfolders(self):
        return os.path.join(self.mgrsTile.utm, self.mgrsTile.name, self.sceneId)


class MGRSArchive(Archive):

    def openProduct(self, folder):

        return MGRSProduct(folder)

    def getProducts(self):
        for utm in os.listdir(self.folder):
            for mgrs in os.listdir(os.path.join(self.folder, utm)):
                for sceneId in os.listdir(os.path.join(self.folder, utm, mgrs)):
                    folder = os.path.join(self.folder, utm, mgrs, sceneId)
                    yield folder


class MGRSTile:

    def __init__(self, name):

        self.name = name
        self.utm = name[0:2]

        self.ul, self.lr = self.getBoundingBox()


    def getBoundingBox(self):

        shp = r'C:\Work\data\gms\MGRS_100km_1MIL_Files\MGRS_100kmSQ_ID_' + self.name[0:3] + '\MGRS_100kmSQ_ID_' + self.name[0:3] + '.shp'
        dataSource = ogr.Open(shp)
        layer = dataSource.GetLayer(0)
        for feature in layer:
            if feature.GetField('MGRS') == self.name:
                e = feature.geometry().GetEnvelope()
                bb =  map(int, map(round,(e[0],e[3],e[1],e[2])))
                break

        return bb[0:2], bb[2:4]


class MGRSTilingScheme(Type):

    shp = r'C:\Work\data\gms\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    def __init__(self, pixelSize):

        self.pixelSize = pixelSize
        self.pixelOrigin = [15,15]
        self.mgrstilesByWRS2Footprint = dict()


    def tileWRS2Product(self, product, folder, buffer=0):

        assert isinstance(product, SensorXWRS2Product)
        tiles = self.cacheWRS2Tiles(product.footprint())
        product_utm = product.getUTMZone()

        for tile in tiles:

            # - snap bounding box to target pixel grid
            xoff = (tile.ul[0] - self.pixelOrigin[0]) % self.pixelSize
            yoff = (tile.ul[1] - self.pixelOrigin[1]) % self.pixelSize

            ul = (tile.ul[0] - xoff - buffer, tile.ul[1] - yoff + buffer)
            lr = (tile.lr[0] - xoff + buffer, tile.lr[1] - yoff - buffer)


            of = ' -of ' + ['ENVI','VRT'][0]
            if of.endswith('VRT'):
                extension = '.vrt'
            else:
                extension = '.img'

            outfile = os.path.join(folder, tile.utm, tile.name, product.sceneId,
                                   os.path.splitext(os.path.basename(product.filenameSR))[0]+'_'+tile.name+extension)
            infile = product.filenameSR

            if product_utm == tile.utm:
                projwin = ' -projwin ' + str(ul[0]) + ' ' + str(max(lr[1],ul[1])) + ' ' + str(lr[0]) + ' ' + str(min(lr[1],ul[1]))

                hub.gdal.util.gdal_translate(outfile=outfile, infile=infile, options=of+projwin)

            else:
                te = ' -te ' + str(ul[0]) + ' ' + str(min(ul[1],lr[1])) + ' ' + str(lr[0]) + ' ' + str(max(ul[1], lr[1]))
                t_srs = ' -t_srs  EPSG:326' + tile.utm
                tr = ' -tr ' + str(self.pixelSize) + ' ' + str(self.pixelSize)
                overwrite = ' -overwrite'

                hub.gdal.util.gdalwarp(outfile=outfile,
                                       infile=infile,
                                       options=of+overwrite+t_srs+tr+te)


    def tileWRS2Archive(self, archive, folder, buffer=0):

        assert isinstance(archive, SensorXArchive)

        for footprint, products in archive.products.items():
            for product in products:
                self.tileWRS2Product(product, folder, buffer=buffer)


    def cacheWRS2Tiles(self, wrs2Footprint):

        if not self.mgrstilesByWRS2Footprint.has_key(wrs2Footprint):

            dataSource = ogr.Open(self.shp)
            layer = dataSource.GetLayer(0)
            for feature in layer:
                if wrs2Footprint == str(int(feature.GetField('WRSPR'))):

                    mgrsTile = MGRSTile(name=feature.GetField('GRID1MIL')+ feature.GetField('GRID100K'))

                    if not self.mgrstilesByWRS2Footprint.has_key(wrs2Footprint):
                        self.mgrstilesByWRS2Footprint[wrs2Footprint] = list()

                    self.mgrstilesByWRS2Footprint[wrs2Footprint].append(mgrsTile)

        return self.mgrstilesByWRS2Footprint[wrs2Footprint]


    def report(self):

        report = Type.report(self)
        report.append(eb.ReportHeading('MGRS Tiles by WRS-2 Footprints'))
        for footprint in self.mgrstilesByWRS2Footprint.keys():
            report.append(eb.ReportHeading(footprint, 1))
            report.append(eb.ReportParagraph('MGRS Tiles = ' + str([product.name for product in self.mgrstilesByWRS2Footprint[footprint]])))
        return report

    def info(self):

        self.report().saveHTML().open()


def test_product():

    product = LandsatLC8Product(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    product.info()

def test_archive():

    #archive = LandsatArchive(r'C:\Work\data\gms\landsat')
    #archive = MGRSArchive(r'c:\work\data\gms\sensorXMGRS')
    archive = SensorXArchive(r'c:\work\data\gms\sensorX')
    archive.info()

def test_sensorXConvertImage():

    lc8 = LandsatLC8Product(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    sensorXConverter = SensorXConverter(imageNamesSR=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                               imageNamesQA=['fmask'])
    x = sensorXConverter.convertProduct(lc8, r'c:\work\x\LC81930242015276LGN00')
    x.info()


def test_sensorXConvertArchive():

    landsatArchive = LandsatArchive(r'C:\Work\data\gms\landsat')
    sensorXConverter = SensorXConverter(imageNamesSR=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                               imageNamesQA=['fmask'])
    sensorXArchive = sensorXConverter.convertArchive(landsatArchive, r'C:\Work\data\gms\sensorX')
    sensorXArchive.info()




def test_tileProduct():

    lc8 = LandsatLC8Product(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    sensorXConverter = SensorXConverter(imageNamesSR=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                               imageNamesQA=['fmask'])
    lc8x = sensorXConverter.convertProduct(lc8, r'c:\work\data\gms\test\LC81930242015276LGN00')

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Product(lc8x, r'c:\work\data\gms\test\tiles', buffer=300)


def test_tileArchive():

    landsatArchive = LandsatArchive(r'C:\Work\data\gms\landsat')
    sensorXConverter = SensorXConverter(imageNamesSR=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                        imageNamesQA=['fmask'])
    sensorXArchive = sensorXConverter.convertArchive(landsatArchive, r'c:\work\data\gms\sensorX')

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(sensorXArchive, r'c:\work\data\gms\sensorXMGRS', buffer=300)


def test_buildCube():

    landsatArchive = LandsatArchive(r'C:\Work\data\gms\landsat')
    sensorXConverter = SensorXConverter(imageNamesSR=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                        imageNamesQA=['fmask'])
    sensorXArchive = sensorXConverter.convertArchive(landsatArchive, r'c:\work\data\gms\sensorX')

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(sensorXArchive, r'c:\work\data\gms\sensorXMGRS', buffer=300)



if __name__ == '__main__':

    import hub.timing
    hub.timing.tic()
    #test_archive()
    test_product()
    #test_sensorXConvertImage()
    #test_sensorXConvertArchive()

    #test_tileProduct()
    # test_tileArchive()
    #test_buildCube()


    hub.timing.toc()