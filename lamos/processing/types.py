from __future__ import division, print_function
import os
import ogr, gdal, osr
from hub.datetime import Date
import hub.file
import hub.gdal.util, hub.gdal.api
import hub.rs.virtual
import hub.envi
import rios.applier
import numpy
from enmapbox import processing
from enmapbox.processing.types import Meta

from enmapbox.processing.applier import ApplierHelper
from hub.timing import tic, toc
from multiprocessing.pool import ThreadPool
import subprocess

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

    def getUL(self):
        return self.ul


    def getLR(self):
        return self.lr


    def subfolders(self):
        raise Exception('must be overwritten')


class MGRSFootprint(Footprint):

    bb = dict()
    shpRoot = r'<insert path>\MGRS_100km_1MIL_Files'

    @staticmethod
    def fromShp(name):

        if MGRSFootprint.bb.has_key(name):
            bb = MGRSFootprint.bb[name]
        else:
            assert os.path.exists(MGRSFootprint.shpRoot), MGRSFootprint.shpRoot
            shp = os.path.join(MGRSFootprint.shpRoot, r'MGRS_100kmSQ_ID_' + name[0:3] + '\MGRS_100kmSQ_ID_' + name[0:3] + '.shp')
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


    def getBoundingBox(self, buffer=0, snap=None):

        # apply buffer
        ul_x, ul_y = (self.ul[0] - buffer, self.ul[1] + buffer)
        lr_x, lr_y = (self.lr[0] + buffer, self.lr[1] - buffer)

        # get snapping offset
        if snap is None:
            ul_xoff = 0
            ul_yoff = 0
            lr_xoff = 0
            lr_yoff = 0
        elif snap == 'landsat':
            pixelSize = 30
            pixelOrigin_x, pixelOrigin_y = 15, 15
            ul_xoff = (ul_x - pixelOrigin_x) % pixelSize
            ul_yoff = (ul_y - pixelOrigin_y) % pixelSize
            lr_xoff = (lr_x - pixelOrigin_x) % pixelSize
            lr_yoff = (lr_y - pixelOrigin_y) % pixelSize
        else:
            raise Exception('snap: unknown option')

        if snap is not None:
            # round snapping offset
            if ul_xoff > pixelSize / 2.: ul_xoff -= pixelSize
            if ul_yoff > pixelSize / 2.: ul_yoff -= pixelSize
            if lr_xoff > pixelSize / 2.: lr_xoff -= pixelSize
            if lr_yoff > pixelSize / 2.: lr_yoff -= pixelSize

        ul = (ul_x - ul_xoff, ul_y - ul_yoff)
        lr = (lr_x - lr_xoff, lr_y - lr_yoff)

        return ul, lr


    def getLR(self):
        return self.lr



    def subfolders(self):

        return os.path.join(self.utm, self.name)


    def report(self):

        report = Type.report(self)
        report.append(processing.ReportParagraph('name =     ' + self.name))
        report.append(processing.ReportParagraph('utm zone = ' + self.utm))
        report.append(processing.ReportParagraph('bounding box ul, lr = ' + str(self.ul) + ' ' + str(self.lr)))
        return report


class WRS2Footprint(Footprint):

    utmLookup = {}#{'193024': '33', '194024': '32',
#                 '172034': '37', '173034': '37',
#                 '169032': '38', '170032': '38',
#                 '178034': '36', '177034': '36', '176034': '36', '173035': '37', '172035': '37'}

    @staticmethod
    def createUtmLookup(infolder):
        print('Create UTM Zone lookup')
        archive = WRS2Archive(infolder)
        for footprintFolder in archive.yieldFootprintFolders():
            sceneFolder = os.path.join(footprintFolder, os.listdir(footprintFolder)[0])
            firstProduct = Product(sceneFolder, extensions=['.img','.tif'])
            firstImage = None
            for firstImage in firstProduct.yieldImages(): break
            if firstImage is None: continue

            ds = gdal.Open(firstImage.filename)
            wkt = ds.GetProjection()
            ds = None
            if wkt.startswith('PROJCS["UTM Zone'):
                utm = wkt[17:19]
            elif wkt.startswith('PROJCS["WGS 84 / UTM zone'):
                utm = wkt[26:28]
            else:
                raise Exception('check wkt')

            row = os.path.basename(footprintFolder)
            path = os.path.basename(os.path.dirname(footprintFolder))

            WRS2Footprint.utmLookup[path+row] = utm

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

    def __init__(self, ufuncs, start=None, end=None):

        if start is None:
            start = Date(1, 1, 1)
        if end is None:
            end = Date(9999, 1, 1)

        assert isinstance(start, Date)
        assert isinstance(end, Date)

        self.start = start
        self.end = end
        self.ufuncs = ufuncs


    def composeProduct(self, product, folder):

        assert isinstance(product, Product)

        print(product.name)
        for ufunc in self.ufuncs:

            imageStack = ufunc(product)
            assert isinstance(imageStack, ImageStack)
            outfile = os.path.join(folder, imageStack.name)
            infiles = [band.filename for band in imageStack.images]
            inbands = [1] * len(infiles)

            if os.path.exists(outfile): continue

            # dirty quick fix to habdle .tif and .img extensions in one archive
            if not os.path.exists(infiles[0]): continue
            hub.gdal.util.stack_bands(outfile=outfile, infiles=infiles, inbands=inbands, verbose=False)

            meta = Meta(outfile)
            meta.setBandNames(imageStack.metas['band names'])
            meta.setNoDataValue(imageStack.metas['data ignore value'])
            for key, value in imageStack.metas.items():
                meta.setMetadataItem(key=key, value=value)
            meta.writeMeta(outfile)

        return Product(folder)


    def composeWRS2Archive(self, infolder, outfolder, footprints=None, processes=1):

        archive = WRS2Archive(infolder)

        print('Compose Sensor X')

        def yieldArgs():
            for footprint in archive.yieldFootprints(filter=footprints):
                print(footprint.name)
                for product in archive.yieldProducts(footprint):
                    if self.filterDate(product):
                        folder = os.path.join(outfolder, footprint.subfolders(), product.name)
                        yield product, folder

        def job(args):
            product, folder = args
            self.composeProduct(product=product, folder=folder)

        if processes == 1:
            for args in yieldArgs():
                job(args)
        else:
            pool = ThreadPool(processes=processes)
            pool.map(job, yieldArgs())

        return archive.__class__(folder=outfolder)


class Archive(Type):

    def __init__(self, folder):
        if folder is not None:
            assert os.path.exists(folder)
        self.folder = folder


    def yieldFootprints(self, filter=None):
        pass


    def yieldProducts(self, footprint, extensions):
        pass



    def saveAsGTiff(self, outfolder, inextensions=['.vrt'], outextension='.img', compress='LZW', interleave='BAND', predictor='2', filter=None, processes=1):
        '''
        see http://www.gdal.org/frmt_gtiff.html
            https://havecamerawilltravel.com/photographer/tiff-image-compression
        '''

        print('Save as GTiff')
        options = '-co "TILED=YES" -co "BLOCKXSIZE=256" -co "BLOCKYSIZE=256" -co "PROFILE=GeoTIFF" '
        options += '-co "COMPRESS=' + compress + '" -co "PREDICTOR=' + predictor + '" -co "INTERLEAVE=' + interleave + '" '
        self._saveAs(outfolder=outfolder, inextensions=inextensions, outextension='.tif', options=options,
                     filter=filter, processes=processes)


    def saveAsENVI(self, outfolder, inextensions=['.vrt'], outextension='.img', compress=False, filter=None, processes=1):

        print('Save as ENVI')
        options = '-of ENVI'
        self._saveAs(outfolder=outfolder, inextensions=inextensions, outextension=outextension, options=options,
                     compressENVI=compress, filter=filter, processes=processes)


    def _saveAs(self, outfolder, inextensions, outextension, options, compressENVI=False, filter=None, processes=1):

        def yieldArgs():
            for footprint in self.yieldFootprints(filter):
                for product in self.yieldProducts(footprint=footprint, extensions=inextensions):
                    for image in product.yieldImages():
                        infile = image.filename
                        outfile = os.path.join(outfolder, footprint.subfolders(), product.name, image.name)
                        outfile = outfile[:-4] + outextension
                        if not os.path.exists(outfile):
                            yield outfile, infile

        def save(args):
            outfile, infile = args
            hub.gdal.util.gdal_translate(outfile=outfile, infile=infile, options=options)
            meta = hub.gdal.api.GDALMeta(infile)
            if compressENVI:
                #gzips = ['D:\work\AR']

                cmd = ['C:\Program Files\gzip\gzip', '-q', outfile]
                print(' '.join(cmd))
                subprocess.call(cmd)
                os.rename(outfile + '.gz', outfile)
                meta.setMetadataItem('file_compression', 1)
            meta.writeMeta(outfile)

        if processes == 1:
            for args in yieldArgs():
                save(args)
        else:
            pool = ThreadPool(processes=processes)
            pool.map(save, yieldArgs())

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


    def yieldProducts(self, footprint, extensions):

        assert isinstance(footprint, MGRSFootprint)
        for scene in os.listdir(os.path.join(self.folder, footprint.utm, footprint.name)):
            yield Product(folder=os.path.join(self.folder, footprint.utm, footprint.name, scene), extensions=extensions)


class WRS2Archive(Archive):

    def yieldFootprintFolders(self):

        for path in os.listdir(self.folder):
            if path.startswith('.'): continue
            folder = os.path.join(self.folder, path)
            if not os.path.isdir(folder): continue
            for row in os.listdir(os.path.join(self.folder, path)):
                if row.startswith('.'): continue
                folder = os.path.join(self.folder, path, row)
                if not os.path.isdir(folder): continue
                yield folder

    def yieldFootprints(self, filter=None):

        for path in os.listdir(self.folder):
            if path.startswith('.'): continue
            folder = os.path.join(self.folder, path)
            if not os.path.isdir(folder): continue
            for row in os.listdir(os.path.join(self.folder, path)):
                if row.startswith('.'): continue
                folder = os.path.join(self.folder, path, row)
                if not os.path.isdir(folder): continue
                if (filter is not None):
                    if path+row not in filter:
                        continue
                yield WRS2Footprint(path+row)

    def yieldProducts(self, footprint, extensions=['.vrt','.img']):
        assert isinstance(footprint, WRS2Footprint)
        for scene in os.listdir(os.path.join(self.folder, footprint.path, footprint.row)):
            yield Product(folder=os.path.join(self.folder, footprint.path, footprint.row, scene), extensions=extensions)


class MGRSTilingScheme(Type):

    shp = r'<insert path>\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'
    MGRSFootprints = dict()

    def __init__(self, pixelSize):

        self.pixelSize = pixelSize
        self.pixelOrigin = [15,15]


    def cacheMGRSFootprints(self, wrs2Footprints):

        for wrs2Footprint in wrs2Footprints:
            assert isinstance(wrs2Footprint, WRS2Footprint)
            MGRSTilingScheme.MGRSFootprints[wrs2Footprint.name] = list()

        wrs2FootprintNames = [wrs2Footprint.name for wrs2Footprint in wrs2Footprints]

        assert os.path.exists(MGRSTilingScheme.shp), MGRSTilingScheme.shp
        dataSource = ogr.Open(MGRSTilingScheme.shp)
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
                tr = ' -tr ' + str(self.pixelSize) + ' ' + str(self.pixelSize)
                outfile = os.path.join(folder, mgrsFootprint.utm, mgrsFootprint.name, product.name,
                                       os.path.splitext(os.path.basename(infile))[0] + extension)

                if os.path.exists(outfile):
                    continue

                if wrs2Footprint.utm == mgrsFootprint.utm:

                    projwin = ' -projwin ' + str(ul[0]) + ' ' + str(max(lr[1],ul[1])) + ' ' + str(lr[0]) + ' ' + str(min(lr[1],ul[1]))
                    strict  = ' -strict'
                    options = of+projwin+strict+tr
                    hub.gdal.util.gdal_translate(outfile=outfile, infile=infile, options=options, verbose=False)

                else:
                    te = ' -te ' + str(ul[0]) + ' ' + str(min(ul[1],lr[1])) + ' ' + str(lr[0]) + ' ' + str(max(ul[1], lr[1]))
                    t_srs = ' -t_srs  EPSG:326' + mgrsFootprint.utm
                    overwrite = ' -overwrite'
                    multi = ' -multi'
                    wm = '' #'' --config GDAL_CACHEMAX 1000 -wm 1000'
                    options = of + overwrite + t_srs + tr + te + multi + wm
                    hub.gdal.util.gdalwarp(outfile=outfile,
                                           infile=infile,
                                           options=options, verbose=False)

                # prepare meta information
                inmeta = Meta(infile)
                outmeta = Meta(outfile)
                outmeta.setMetadataDict(inmeta.getMetadataDict())
                outmeta.writeMeta(outfile)


    def tileWRS2Archive(self, infolder, outfolder, wrs2Footprints=None, mgrsFootprints=None, buffer=0, processes=1):

        archive = WRS2Archive(infolder)
        self.cacheMGRSFootprints(list(archive.yieldFootprints()))

        print('Cut WRS2 into MGRS Footprints')

        def yieldArgs():
            for footprint in archive.yieldFootprints(filter=wrs2Footprints):
                print(footprint.name)
                for product in archive.yieldProducts(footprint):
                    print(product.name)
                    yield product, footprint, outfolder, buffer, mgrsFootprints

        def job(args):
            product, footprint, outfolder, buffer, mgrsFootprints = args
            self.tileWRS2Product(product=product, wrs2Footprint=footprint, folder=outfolder, buffer=buffer,
                                 mgrsFootprints=mgrsFootprints)


        if processes == 1:
            for args in yieldArgs():
                job(args)
        else:
            pool = ThreadPool(processes=processes)
            pool.map(job, yieldArgs())

    def report(self):

        report = Type.report(self)
        report.append(processing.ReportHeading('MGRS Tiles by WRS-2 Footprints'))
        for footprint in self.mgrstilesByWRS2Footprint.keys():
            report.append(processing.ReportHeading(footprint, 1))
            report.append(processing.ReportParagraph('MGRS Tiles = ' + str([product.name for product in self.mgrstilesByWRS2Footprint[footprint]])))
        return report


class BlockAssociations(rios.applier.BlockAssociations):

    def __init__(self, riosBlockAssociations=None):
        if riosBlockAssociations is not None:
            self.__dict__ = riosBlockAssociations.__dict__


    def reshape2d(self):

        for k, v in self.__dict__.items():
            self.__dict__[k] = self.__dict__[k].reshape((v.shape[0], -1))


    def reshape3d(self, xsize, ysize):

        for k, v in self.__dict__.items():
            self.__dict__[k] = self.__dict__[k].reshape((xsize, ysize, -1))


class ApplierInput():

    def __init__(self, archive, productName, imageNames, extension, bands=None):
        assert isinstance(archive, Archive)
        assert isinstance(productName, str)
        assert isinstance(imageNames, list)
        self.archive = archive
        self.productName = productName
        self.imageNames = imageNames
        self.extension = extension
        self.bands = bands

    def getFilenameAssociations(self, footprint):

        for product in self.archive.yieldProducts(footprint=footprint, extensions=[self.extension]):
            assert isinstance(product, Product)
            if product.name == self.productName:
                return product.getFilenameAssociations(self.imageNames, prefix=self.productName+'_')
        raise Exception('unknown product: '+self.productName)


class ApplierOutput():

    def __init__(self, folder, productName, imageNames, extension):
        if folder is not None:
            assert isinstance(folder, basestring)
        assert isinstance(productName, str)
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

        def __init__(self, riosFilenameAssociations=None):

            if riosFilenameAssociations is not None:
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

        progress = str(ApplierHelper.progress(info))+'%'
        print(progress, end='..')
        inputs = BlockAssociations(riosInputs)
        outputs = BlockAssociations(riosOutputs)
        for key, value in riosOtherArgs.outfiles.__dict__.items():
            outputs.__dict__[key] = None
            hub.file.mkfiledir(value)

        riosOtherArgs.userFunction(info=info, inputs=inputs, outputs=outputs, inmetas=riosOtherArgs.inmetas, otherArgs=riosOtherArgs.otherArgs)

        if ApplierHelper.lastBlock(info):
            print('100%')

    @staticmethod
    def userFunctionMetaWrapper(riosOtherArgs):

        outmetas = Applier.Metas(riosOtherArgs.outfiles)
        riosOtherArgs.userFunctionMeta(inmetas=riosOtherArgs.inmetas, outmetas=outmetas, otherArgs=riosOtherArgs.otherArgs)
        outmetas.write()


    def __init__(self, footprints=None, of='ENVI'):

        assert of in ['ENVI', 'GTiff']
        self.driverName = of
        if self.driverName == 'ENVI':
            self.outextension = '.img'
        elif self.driverName == 'GTiff':
            self.outextension = '.tif'

        self.footprints = footprints
        self.inputs = list()
        self.outputs = list()
        self.controls = self.defaultControls()
        self.otherArgs = self.defaultOtherArgs()
        self.overwrite = False


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

        if self.driverName == 'ENVI':
            controls.setOutputDriverName("ENVI")
            controls.setCreationOptions(["INTERLEAVE=BSQ"])
        elif self.driverName == 'GTiff':
            controls.setOutputDriverName("GTiff")
            controls.setCreationOptions(["INTERLEAVE=BAND", "TILED=YES", "BLOCKXSIZE=256", "BLOCKYSIZE=256", "PROFILE=GeoTIFF",
                                         "COMPRESS=DEFLATE", "PREDICTOR=2"])
        else:
            raise Exception('unknown option')

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
            outfiles.__dict__.update(output.getFilenameAssociations(footprint).__dict__)

        exists = True
        for outfile in outfiles.__dict__.values():
            exists = exists and os.path.exists(outfile)
        if exists and self.overwrite==False:
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
#        if self.compressed:
#            print('compress')
#            for outfile in outfiles.__dict__.values():
#                hub.envi.compress(infile=outfile, outfile=outfile)

    def apply(self):
        print('Apply '+str(self.__class__).split('.')[-1])
        for footprint in self.inputs[0].archive.yieldFootprints(filter=self.footprints): # first input defines the footprints to be processed
            self.applyToFootprint(footprint=footprint)


def test_footprint():

    for key in ['33UUU', '33UVU', '33UUT', '33UVT']:
        mgrs = MGRSFootprint.fromShp(key)
        print(key)
        print(mgrs.ul)
        print(mgrs.lr)
        bb = mgrs.getBoundingBox(buffer=300, snap='landsat')
        print(bb)


def test_product():
    product = Product(r'C:\Work\data\gms\landsat\194\024\LT51940242010189KIS01')
    product = Product(r'C:\Work\data\gms\landsatTimeseriesMGRS\32\32UNB\timeseries')
    #product.info()
    inputs = product.getFilenameAssociations()
    print(inputs.__dict__.keys())

def test_archive():
    #archive = Archive.fromWRS2(r'C:\Work\data\gms\landsat')
    archive = MGRSArchive(r'c:\work\data\gms\landsatTimeseriesMGRS')
    archive.saveAsGTiff(r'c:\work\data\gms\landsatTimeseriesMGRS_GTIFF_ZIP')

    #archive = WRS2Archive(r'c:\work\data\gms\landsatX', extensions=['.img', '.vrt'])
    archive.info()

def test_save_archive():
    #archive = MGRSArchive(r'c:\work\data\gms\landsatTimeseriesMGRS')
    archive = MGRSArchive(r'c:\work\data\gms\landsatXMGRS')
    filter = '33UTT'
    for interleave in ['BAND','PIXEL']:
        for compress in ['DEFLATE', 'LZW', 'NONE']:
            for predictor in ['1', '2', '3']:
                outfolder = archive.folder+'_'+interleave+'_'+compress+predictor
                archive.saveAsGTiff(outfolder=outfolder, filter=filter,
                                    compress=compress, interleave=interleave, predictor=predictor)


if __name__ == '__main__':

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'


    tic()
    test_footprint()
    #test_product()
    #test_archive()
    #test_save_archive()
    toc()