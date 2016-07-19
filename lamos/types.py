from __future__ import division
import os
import ogr
import hub.datetime
import hub.file
import hub.gdal.util, hub.gdal.api
import hub.rs.virtual
import hub.envi
import rios.applier
import numpy
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
        self.name = os.path.basename(folder)
        self.extensions = extensions


    def yieldImages(self, suffix=''):

        for extension in self.extensions:
            for basename in os.listdir(self.folder):
                if basename.endswith(extension):
                    filename = os.path.join(self.folder, basename)
                    if filename.endswith(suffix):
                        yield Image(name=basename, filename=filename)


    def getFilenameAssociations(self, imageNames=None, prefix=''):

        infiles = rios.applier.FilenameAssociations()
        for image in self.yieldImages():
            key = os.path.splitext(image.name)[0]
            if key in imageNames:
                infiles.__dict__[prefix+key] = image.filename

        return infiles


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportParagraph('folder = ' + self.folder))
        report.append(processing.ReportParagraph('scene = ' + self.name))

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
            shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
            shp = os.path.join(shpRoot, r'MGRS_100kmSQ_ID_' + name[0:3] + '\MGRS_100kmSQ_ID_' + name[0:3] + '.shp')
            dataSource = ogr.Open(shp)
            layer = dataSource.GetLayer(0)
            found = False
            for feature in layer:
                if feature.GetField('MGRS') == name:
                    e = feature.geometry().GetEnvelope()
                    bb = map(int, map(round, (e[0], e[3], e[1], e[2])))
                    found = True
                    break
            if not found:
                raise Exception('wrong tile name: '+name)

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

    utmLookup = {'193024': '33', '194024': '32',
                 '172034': '37', '173034': '37',
                 '169032': '38', '170032': '38',
                 '178034': '36', '177034': '36', '176034': '36', '173035': '37', '172035': '37'}

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


class SensorXComposer:

    def __init__(self, ufuncs):

        self.ufuncs = ufuncs


    def composeProduct(self, product, folder=None):

        assert isinstance(product, Product)

        if folder is None: folder = os.path.join(processing.env.tempfile(), product.name)

        for ufunc in self.ufuncs:

            imageStack = ufunc(product)
            assert isinstance(imageStack, ImageStack)
            outfile = os.path.join(folder, imageStack.name)
            infiles = [band.filename for band in imageStack.images]
            inbands = [1] * len(infiles)
            hub.gdal.util.stack_bands(outfile=outfile, infiles=infiles, inbands=inbands, verbose=False)

            meta = processing.Meta(outfile)
            meta.setBandNames(imageStack.metas['band names'])
            meta.setNoDataValue(imageStack.metas['data ignore value'])
            for key, value in imageStack.metas.items():
                meta.setMetadataItem(key=key, value=value)
            meta.writeMeta(outfile)

        return Product(folder)


    def composeArchive(self, archive, folder, footprints=None):

        assert isinstance(archive, Archive)
        print('Compose Landsat X')
        for footprint in archive.yieldFootprints(filter=footprints):
            print(footprint.name)
            for product in archive.yieldProducts(footprint):
                self.composeProduct(product, os.path.join(folder, footprint.subfolders(), product.name))
        return archive.__class__(folder=folder)


class Archive(Type):

    def __init__(self, folder):
        assert os.path.exists(folder)
        self.folder = folder


    def yieldFootprints(self, filter=None):
        pass


    def yieldProducts(self, footprint, extensions):
        pass


    def report(self):
        report = processing.Report(str(self.__class__).split('.')[-1])
        report.append(processing.ReportParagraph('foldername = ' + self.folder))
        report.append(processing.ReportHeading('Footprints'))
        for footprint in self.yieldFootprints():
            report.append(processing.ReportHeading(footprint.name, 1))
            report.append(
                processing.ReportParagraph('Products = ' + str([product.name for product in self.yieldProducts(footprint)])))

        return report


class MGRSArchive(Archive):

    def yieldFootprints(self, filter=None):

        for utm in os.listdir(self.folder):
            for mgrs in os.listdir(os.path.join(self.folder, utm)):
                if (filter is not None):
                    if mgrs not in filter:
                        continue
                yield MGRSFootprint.fromShp(mgrs)


    def yieldProducts(self, footprint, extensions=['.vrt','.img']):

        assert isinstance(footprint, MGRSFootprint)
        for scene in os.listdir(os.path.join(self.folder, footprint.utm, footprint.name)):
            yield Product(folder=os.path.join(self.folder, footprint.utm, footprint.name, scene), extensions=extensions)


class WRS2Archive(Archive):

    def yieldFootprints(self, filter=None):
        for path in os.listdir(self.folder):
            for row in os.listdir(os.path.join(self.folder, path)):
                if (filter is not None):
                    if path+row not in filter:
                        continue
                yield WRS2Footprint(path+row)

    def yieldProducts(self, footprint, extensions=['.vrt','.img']):
        assert isinstance(footprint, WRS2Footprint)
        for scene in os.listdir(os.path.join(self.folder, footprint.path, footprint.row)):
            yield Product(folder=os.path.join(self.folder, footprint.path, footprint.row, scene), extensions=extensions)


class MGRSTilingScheme(Type):

    shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'
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


    def tileWRS2Product(self, product, wrs2Footprint, folder, mgrsFootprints=None, buffer=0):

        assert isinstance(product, Product)
        assert isinstance(wrs2Footprint, WRS2Footprint)

        for mgrsFootprint in MGRSTilingScheme.MGRSFootprints[wrs2Footprint.name]:

            if mgrsFootprints is not None:
                if mgrsFootprint.name not in mgrsFootprints:
                    continue

            # - snap bounding box to target pixel grid
            xoff = (mgrsFootprint.ul[0] - self.pixelOrigin[0]) % self.pixelSize
            yoff = (mgrsFootprint.ul[1] - self.pixelOrigin[1]) % self.pixelSize

            ul = (mgrsFootprint.ul[0] - xoff - buffer, mgrsFootprint.ul[1] - yoff + buffer)
            lr = (mgrsFootprint.lr[0] - xoff + buffer, mgrsFootprint.lr[1] - yoff - buffer)


            for image in product.yieldImages():

                infile = image.filename

                of, extension = ' -of VRT', '.vrt'
                outfile = os.path.join(folder, mgrsFootprint.utm, mgrsFootprint.name, product.name,
                                       os.path.splitext(os.path.basename(infile))[0] + extension)

                if os.path.exists(outfile):
                    continue

                if wrs2Footprint.utm == mgrsFootprint.utm:

                    projwin = ' -projwin ' + str(ul[0]) + ' ' + str(max(lr[1],ul[1])) + ' ' + str(lr[0]) + ' ' + str(min(lr[1],ul[1]))


                    hub.gdal.util.gdal_translate(outfile=outfile, infile=infile, options=of+projwin, verbose=False)

                else:
                    te = ' -te ' + str(ul[0]) + ' ' + str(min(ul[1],lr[1])) + ' ' + str(lr[0]) + ' ' + str(max(ul[1], lr[1]))
                    t_srs = ' -t_srs  EPSG:326' + mgrsFootprint.utm
                    tr = ' -tr ' + str(self.pixelSize) + ' ' + str(self.pixelSize)
                    overwrite = ' -overwrite'
                    multi = ' -multi'
                    wm = ' -wm 5000'

                    hub.gdal.util.gdalwarp(outfile=outfile,
                                           infile=infile,
                                           options=of+overwrite+t_srs+tr+te+multi+wm, verbose=False)

                # prepare meta information
                inmeta = processing.Meta(infile)
                outmeta = processing.Meta(outfile)
                outmeta.setMetadataDict(inmeta.getMetadataDict())
                outmeta.writeMeta(outfile)


    def tileWRS2Archive(self, archive, folder, wrs2Footprints=None, mgrsFootprints=None, buffer=0):

        assert isinstance(archive, Archive)

        self.cacheMGRSFootprints(list(archive.yieldFootprints()))
        print('Cut WRS2 into MGRS Footprints')
        for footprint in archive.yieldFootprints(filter=wrs2Footprints):
            print footprint.name
            for product in archive.yieldProducts(footprint):
                print product.name
                self.tileWRS2Product(product=product, wrs2Footprint=footprint, folder=folder, buffer=buffer,
                                     mgrsFootprints=mgrsFootprints)

        return MGRSArchive(folder)


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportHeading('MGRS Tiles by WRS-2 Footprints'))
        for footprint in self.mgrstilesByWRS2Footprint.keys():
            report.append(processing.ReportHeading(footprint, 1))
            report.append(processing.ReportParagraph('MGRS Tiles = ' + str([product.name for product in self.mgrstilesByWRS2Footprint[footprint]])))
        return report


class BlockAssociations(rios.applier.BlockAssociations):

    def __init__(self, riosBlockAssociations):
        self.__dict__ = riosBlockAssociations.__dict__


    def reshape2d(self):

        for k, v in self.__dict__.items():
            self.__dict__[k] = self.__dict__[k].reshape((v.shape[0], -1))


    def reshape3d(self, xsize, ysize):

        for k, v in self.__dict__.items():
            self.__dict__[k] = self.__dict__[k].reshape((xsize, ysize, -1))


class ApplierInput():

    def __init__(self, archive, productName, imageNames, extension):
        assert isinstance(archive, Archive)
        assert isinstance(productName, basestring)
        assert isinstance(imageNames, list)
        self.archive = archive
        self.productName = productName
        self.imageNames = imageNames
        self.extension = extension

    def getFilenameAssociations(self, footprint):

        for product in self.archive.yieldProducts(footprint=footprint, extensions=[self.extension]):
            assert isinstance(product, Product)
            if product.name == self.productName:
                return product.getFilenameAssociations(self.imageNames, prefix=self.productName+'_')
        raise Exception('unknown product: '+self.productName)


class ApplierOutput():

    def __init__(self, folder, productName, imageNames, extension):
        assert isinstance(folder, basestring)
        assert isinstance(productName, basestring)
        assert isinstance(imageNames, list)
        self.folder = folder
        self.productName = productName
        self.imageNames = imageNames
        self.extension = extension


    def getFilenameAssociations(self, footprint):

        filenameAssociations = rios.applier.FilenameAssociations()

        for imageName in self.imageNames:
            filename = os.path.join(self.folder, footprint.subfolders(), self.productName, imageName+self.extension)
            filenameAssociations.__dict__[self.productName+'_'+imageName] = filename

        return filenameAssociations


class Applier:

    class Metas:

        def __init__(self, riosFilenameAssociations):

            assert isinstance(riosFilenameAssociations, rios.applier.FilenameAssociations)
            self._filenames = dict()
            for key, filename in riosFilenameAssociations.__dict__.items():
                self.__dict__[key] = hub.gdal.api.GDALMeta(filename)
                self._filenames[key] = filename

        def write(self):
            for key, filename in self._filenames.items():
                self.__dict__[key].writeMeta(filename)


    @staticmethod
    def userFunctionWrapper(info, riosInputs, riosOutputs, riosOtherArgs):

        inputs = BlockAssociations(riosInputs)
        outputs = BlockAssociations(riosOutputs)
        for key, value in riosOtherArgs.outfiles.__dict__.items():
            outputs.__dict__[key] = None
            hub.file.mkfiledir(value)

        riosOtherArgs.userFunction(info=info, inputs=inputs, outputs=outputs, inmetas=riosOtherArgs.inmetas, otherArgs=riosOtherArgs.otherArgs)


    @staticmethod
    def userFunctionMetaWrapper(riosOtherArgs):

        outmetas = Applier.Metas(riosOtherArgs.outfiles)
        riosOtherArgs.userFunctionMeta(inmetas=riosOtherArgs.inmetas, outmetas=outmetas, otherArgs=riosOtherArgs.otherArgs)
        outmetas.write()


    def __init__(self, compressed=False):
        self.compressed = compressed
        self.inputs = list()
        self.outputs = list()
        self.controls = self.defaultControls()
        self.otherArgs = self.defaultOtherArgs()


    def appendInput(self, input):
        assert isinstance(input, ApplierInput)
        self.inputs.append(input)


    def appendOutput(self, output):
        assert isinstance(output, ApplierOutput)
        self.outputs.append(output)


    def defaultOtherArgs(self):
        return rios.applier.OtherInputs()


    def defaultControls(self):
        controls = rios.applier.ApplierControls()
        controls.setNumThreads(1)
        controls.setJobManagerType('multiprocessing')
        controls.setOutputDriverName("ENVI")
        controls.setCreationOptions(["INTERLEAVE=BSQ"])
        controls.setCalcStats(False)
        controls.setOmitPyramids(True)
        return controls


    def applyToFootprint(self, footprint):

        print(footprint.name)

        infiles = rios.applier.FilenameAssociations()
        for input in self.inputs:
            assert isinstance(input, ApplierInput)
            infiles.__dict__.update(input.getFilenameAssociations(footprint).__dict__)

        outfiles = rios.applier.FilenameAssociations()
        for output in self.outputs:
            assert isinstance(output, ApplierOutput)
            outfiles = rios.applier.FilenameAssociations()
            outfiles.__dict__.update(output.getFilenameAssociations(footprint).__dict__)

        exists = True
        for outfile in outfiles.__dict__.values():
            exists = exists and os.path.exists(outfile)
        if exists:
            return

        riosOtherArgs = rios.applier.OtherInputs()
        riosOtherArgs.otherArgs = self.otherArgs
        riosOtherArgs.userFunction = self.userFunction
        riosOtherArgs.userFunctionMeta = self.userFunctionMeta
        riosOtherArgs.infiles = infiles
        riosOtherArgs.outfiles = outfiles
        riosOtherArgs.inmetas = Applier.Metas(riosOtherArgs.infiles)

        # apply the user function
        rios.applier.apply(userFunction=Applier.userFunctionWrapper, infiles=infiles, outfiles=outfiles, otherArgs=riosOtherArgs, controls=self.controls)

        # set user defined meta information
        Applier.userFunctionMetaWrapper(riosOtherArgs=riosOtherArgs)

        # compress output if needed
        if self.compressed:
            print('compress')
            for outfile in outfiles.__dict__.values():
                hub.envi.compress(infile=outfile, outfile=outfile)

    def apply(self):
        print('Apply '+str(self.__class__).split('.')[-1])
        for footprint in self.inputs[0].archive.yieldFootprints(): # first input defines the footprints to be processed
            self.applyToFootprint(footprint=footprint)


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


if __name__ == '__main__':

    import hub.timing
    hub.timing.tic()
    #test_footprint()
    #test_product()
    #test_archive()
    hub.timing.toc()
