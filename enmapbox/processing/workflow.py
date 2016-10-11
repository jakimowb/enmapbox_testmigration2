from __future__ import print_function
import os
import tempfile
import shutil
from collections import OrderedDict

import rios.applier
import rios.readerinfo
import numpy

from hub.gdal.api import GDALMeta
from hub.file import mkdir, filesearch, savePickle, restorePickle, remove
from hub.datetime import Date
from hub.timing import tic, toc
from hub.temp import Temporary
from enmapbox.processing.types import Image, Mask

def assertType(obj, type):
    assert isinstance(obj, type) # makes PyCharm aware of the type!
    return obj

class ApplierControls(rios.applier.ApplierControls):

    defaultWindowXsize = 256
    defaultWindowYsize = 256

    def __init__(self):
        rios.applier.ApplierControls.__init__(self)
        self.setNumThreads(1)
        self.setJobManagerType('multiprocessing')
        self.setWindowXsize(ApplierControls.defaultWindowXsize)
        self.setWindowYsize(ApplierControls.defaultWindowYsize)
        self.setCalcStats(False)
        self.setOmitPyramids(True)
        self.setOutputDriverGTiff()

    def setOutputDriverENVI(self, interleave='BSQ'):
        assert interleave.lower() in ['bsq', 'bil', 'bip']
        self.setOutputDriverName('ENVI')
        self.setCreationOptions(['INTERLEAVE=' + interleave])

    def setOutputDriverGTiff(self, interleave='BAND', tiled='YES', blockxsize=256, blockysize=256,
                             compress='LZW', predictor=2):
        assert interleave.lower() in ['band', 'pixel']
        assert tiled.lower() in ['yes', 'no']
        assert compress.lower() in ['lzw', 'deflate', 'none']
        assert predictor in [0, 1, 2]

        self.setOutputDriverName('GTiff')
        self.setCreationOptions(['INTERLEAVE='+interleave, 'TILED='+tiled,
                                 'BLOCKXSIZE='+str(blockxsize), 'BLOCKYSIZE='+str(blockysize),
                                 'COMPRESS='+compress, 'PREDICTOR='+str(predictor)])


class BlockAssociations():

    def __init__(self):
        self._blockAssociations = rios.applier.BlockAssociations()
        self._meta = OrderedDict()

    def _addBlock(self, key, cube, meta):
        assert isinstance(cube, numpy.ndarray)
        if cube.ndim == 2:
            cube = cube[None]
        assert cube.ndim == 3
        assert isinstance(meta, GDALMeta)
        setattr(self._blockAssociations, key, cube)
        self._meta[key] = meta
        return self

    def _getBlock(self, key):
        cube = self._blockAssociations.__dict__[key]
        meta = self._meta[key]
        return cube, meta

    def addBlock(self, key, cube, meta):
        return self._addBlock(key=key, cube=cube, meta=meta)

    def getBlock(self, key):
        return self._getBlock(key=key)

    #def __getitem__(self, key):
    #    return self._getBlock(key=key)

    #def __setitem__(self, key, cube_meta):
    #    cube, meta = cube_meta
    #    return self._addBlock(key=key, cube=cube, meta=meta)

    def keys(self): return self._blockAssociations.__dict__.keys()

    def items(self):
        for key in self.keys():
            cube = self.getCube(key)
            meta = self.getMeta(key)
            yield key, (cube, meta)

    def getCube(self, key):
        cube = getattr(self._blockAssociations, key)
        assert isinstance(cube, numpy.ndarray)
        return cube

    def getMeta(self, key):
        meta = self._meta[key]
        assert isinstance(meta, GDALMeta)
        return meta

    def getStackBA(self, filter=None):

        outcube = list()
        outmeta = GDALMeta()
        bandNames = list()
        if filter is None:
            keys = self.keys()
        else:
            keys = filter(self)
        for key in keys:
            cube, meta = self.getBlock(key=key)
            outcube.append(cube)
            #bandNames.extend([key+'_'+bandName for bandName in meta.getBandNames()])
            bandNames.extend(meta.getBandNames())
        outcube = numpy.vstack(outcube)
        outmeta.setBandNames(bandNames)
        stack = ImageBA(cube=outcube, meta=outmeta)
        return stack

class FilenameAssociations():

    BlockAssociationsClass = BlockAssociations

    def __init__(self):
        self._keyLookup = OrderedDict()
        self._filenameAssociations = rios.applier.FilenameAssociations()
        self._meta = OrderedDict()

    def _getRiosFilenameAssociations(self):
        return self._filenameAssociations

    def _mapRiosOutputs(self, blockAssociations, riosBlockAssociations):

        assert isinstance(blockAssociations, BlockAssociations)
        if not isinstance(blockAssociations, self.BlockAssociationsClass):
            raise Exception(
                'Output filename association type (' + self.__class__.__name__ + ') does not match output block association type (' + blockAssociations.__class__.__name__ + ')!')
        self._mkdir()
        for filename, imageKey in self._keyLookup.items():
            cube = getattr(blockAssociations._blockAssociations, imageKey)
            setattr(riosBlockAssociations, filename, cube)

    def _updateOutputMeta(self, outputs):
        assert isinstance(outputs, BlockAssociations)

        # append metas from workflow
        for filename, imageKey in self._keyLookup.items():
            metaRios = outputs._meta[imageKey]
            metaWorkflow = self._meta[filename]
            metaWorkflow.setMetadataDict(metaRios.getMetadataDict())
            metaWorkflow.writeMeta(filename)


    def _addImage(self, key, filename):
        self._keyLookup[filename] = key
        setattr(self._filenameAssociations, filename, filename)
        return self

    def _createBlockAssociations(self, riosBlockAssociations):
        assert isinstance(riosBlockAssociations, rios.applier.BlockAssociations)
        blockAssociations = self._initBlockAssociations()


        for filename, imageKey in self._keyLookup.items():
            cube = getattr(riosBlockAssociations, filename)
            meta = self._getMeta(filename=filename)
            blockAssociations._addBlock(key=imageKey, cube=cube, meta=meta)
        return blockAssociations

    def _initBlockAssociations(self):
        return self.BlockAssociationsClass()

    def _linkInputFiles(self):
        pass

    def _linkOutputFiles(self, outputs, extension):
        pass

    def _readMetas(self):
        for filename in self._filenameAssociations.__dict__.keys():
            self._meta[filename] = GDALMeta(filename)

    def _setMeta(self, filename, meta):
        self._meta[filename] = meta

    def _getMeta(self, filename):
        return self._meta[filename]

    def _mkdir(self):
        dirnames = set([os.path.dirname(filename) for filename in self._filenameAssociations.__dict__.keys()])
        for dirname in dirnames:
            mkdir(dirname)

class ImageBA(BlockAssociations):

    key = 'image'

    def __init__(self, cube=None, meta=None):
        BlockAssociations.__init__(self)
        if cube is not None and meta is not None:
            self.addBlock(cube=cube, meta=meta)

    def addBlock(self, cube, meta):
        self._addBlock(key=self.key, cube=cube, meta=meta)
        return self

    @property
    def cube(self):
        return self.getCube(key=self.key)

    @property
    def meta(self):
        return self.getMeta(key=self.key)


class ImageFA(FilenameAssociations):

    BlockAssociationsClass = ImageBA
    key = 'image'

    def __init__(self, filename):
        FilenameAssociations.__init__(self)
        self.filename = filename

    def _linkInputFiles(self):
        self._addImage(key=self.key, filename=self.filename)

    def _linkOutputFiles(self, outputs, extension):

        hasExtension = os.path.splitext(self.filename)[1] != ''
        if hasExtension: extension = ''

        # Note: output extension is ignored
        self._addImage(key=self.key, filename=self.filename+extension)

class ProductBA(BlockAssociations):

    def __init__(self, productName):
        BlockAssociations.__init__(self)
        self.productName = productName


class ProductFA(FilenameAssociations):

    BlockAssociationsClass = ProductBA

    def __init__(self, dirname, extensions=['.img', '.tif', '.vrt']):
        FilenameAssociations.__init__(self)
        self.dirname = dirname
        self.productName = os.path.basename(dirname)
        self.extensions = extensions

    def _linkInputFiles(self):
        for extension in self.extensions:
            filenames = filesearch(self.dirname, '*'+extension)
            for filename in filenames:
                basename = os.path.splitext(os.path.basename(filename))[0]
                self._addImage(key=basename, filename=filename)
        return self

    def _linkOutputFiles(self, outputs, extension):

        for basename in outputs.keys():
            filename = os.path.join(self.dirname, basename+extension)
            self._addImage(key=basename, filename=filename)
        return self

    def _initBlockAssociations(self):
        return self.BlockAssociationsClass(productName=self.productName)

    def getAcquisitionDate(self):
        #ToDO: look into all images for acquisition dates, if all dates are the same, then use this date
        raise Exception(self.__class__.__name__+ ' does not provide acquisition date information')

    def extractByMask(self, maskFA, dirname):

        assert isinstance(maskFA, ImageFA)
        self._linkInputFiles()

        resultFA = self.__class__(dirname=dirname)
        mask = Mask(maskFA.filename)
        for infilename, imageKey in self._keyLookup.items():
            outfilename = os.path.join(dirname, imageKey+'.img')
            Image(infilename).extractByMask(mask=mask, filename=outfilename)
            resultFA._addImage(key=imageKey, filename=outfilename)
        resultFA._linkInputFiles()
        return resultFA

class BlockAssociationsCollection():

    def __init__(self):
        self.collection = list()

    def __iter__(self):
        for blockAssociations in self.collection:
            yield blockAssociations

    def __getitem__(self, item):
        return self.collection[item]

    def append(self, blockAssociations):
        assert isinstance(blockAssociations, BlockAssociations)
        self.collection.append(blockAssociations)
        return self

    def filter(self, filterFunction):
        filteredCollection = filterFunction(self)
        assert isinstance(filteredCollection, BlockAssociationsCollection)
        return filteredCollection

class FilenameAssociationsCollection():

    BlockAssociationsClass = BlockAssociationsCollection

    def __init__(self):
        self.collection = list()

    def _getRiosFilenameAssociations(self):

        allFilenameAssociations = rios.applier.FilenameAssociations()
        for filenameAssociations in self.collection:
            allFilenameAssociations.__dict__.update(filenameAssociations._getRiosFilenameAssociations().__dict__)
        return allFilenameAssociations

    def _createBlockAssociations(self, riosBlockAssociations):

        allBlockAssociations = self.BlockAssociationsClass()
        for blockAssociations in self.collection:
            allBlockAssociations.append(blockAssociations._createBlockAssociations(riosBlockAssociations=riosBlockAssociations))
        return allBlockAssociations

    def _linkInputFiles(self):
        for inputs in self.collection:
            inputs._linkInputFiles()

    def _linkOutputFiles(self, outputs, extension):
        raise Exception(self.__class__.__name__ +' type is read only.')

    def _readMetas(self):
        for infiles in self.collection:
            infiles._readMetas()

    def append(self, filenameAssociations):
        assert isinstance(filenameAssociations, FilenameAssociations)
        self.collection.append(filenameAssociations)
        return self


class ProductCollectionBA(BlockAssociationsCollection):

    ProductBAClass = ProductBA

    def append(self, productBA):
        assert isinstance(productBA, self.ProductBAClass)
        BlockAssociationsCollection.append(self, blockAssociations=productBA)

    def filterDate(self, start, end):
        assert isinstance(start, Date)
        assert isinstance(end, Date)
        filteredCollection = self.__class__()
        for productBA in self.collection:
            date = productBA.getAcquisitionDate()
            if date >= start and date <= end:
                filteredCollection.append(productBA)
        return filteredCollection

    def getStack(self):

        outcube = list()
        bandNames = list()
        for productBA in self.collection:
            for key, (cube, meta) in productBA.items():
                if key.startswith('count'): continue
                outcube.append(cube)
                bandNames.extend([key+bandName for bandName in meta.getBandNames()])
        outcube = numpy.vstack(outcube)
        outmeta = GDALMeta()
        outmeta.setBandNames(bandNames)

        stack = ImageBA().addBlock(cube=outcube, meta=outmeta)
        return stack


class ProductCollectionFA(FilenameAssociationsCollection):

    BlockAssociationsClass = ProductCollectionBA
    ProductFAClass = ProductFA

    def __init__(self, dirname):
        FilenameAssociationsCollection.__init__(self)
        self.dirname = dirname
        self.useDateFilter = False
        self.filterDateStart = Date(1,1,1)
        self.filterDateEnd = Date(9999,1,1)

    def _mapRiosOutputs(self, blockAssociations, riosBlockAssociations):
        for productFA, productBA in zip(self.collection, blockAssociations.collection):
            productFA._mapRiosOutputs(blockAssociations=productBA, riosBlockAssociations=riosBlockAssociations)

    def _linkInputFiles(self):

        for productName in os.listdir(self.dirname):
            dirname = os.path.join(self.dirname, productName)
            productFA = self.ProductFAClass(dirname=dirname)
            if self.useDateFilter:
                acquisitionDate = productFA.getAcquisitionDate()
                assert isinstance(acquisitionDate, Date)
                if not (acquisitionDate >= self.filterDateStart and acquisitionDate <= self.filterDateEnd):
                   continue
            self.append(productFA)
        FilenameAssociationsCollection._linkInputFiles(self)

    def _linkOutputFiles(self, outputs, extension):

        assert isinstance(outputs, ProductCollectionBA)
        self.collection = [None]*len(outputs.collection)
        for i, productBA in enumerate(outputs):
            assert isinstance(productBA, ProductBA)
            dirname = os.path.join(self.dirname, productBA.productName)
            productFA = ProductFA(dirname=dirname)
            productFA._linkOutputFiles(outputs=productBA, extension=extension)
            self.collection[i] = productFA # can not use self.append, because it is done in each block redundantly!

    def _updateOutputMeta(self, outputs):
        for filenameAssociations, blockAssociations in zip(self.collection, outputs):
            filenameAssociations._updateOutputMeta(outputs=blockAssociations)

    def filterDate(self, start, end):
        assert isinstance(start, Date)
        assert isinstance(end, Date)
        self.filterDateStart = start
        self.filterDateEnd = end
        return self

    def extractByMask(self, maskFA, dirname):
        assert isinstance(maskFA, ImageFA)
        self._linkInputFiles()

        resultFA = self.__class__(dirname=dirname)

        for inproductFA in self.collection:
            outdirname = os.path.join(dirname, inproductFA.productName)
            outproductFA = inproductFA.extractByMask(maskFA=maskFA, dirname=outdirname)
            resultFA.append(filenameAssociations=outproductFA)

        return resultFA

class WorkflowFilenameAssociations():
    # container for workflow input/output files
    # ToDo: implement as sorted dict
    pass


class WorkflowBlockAssociations():
    # container for workflow input/outputs blocks
    # ToDo: implement as sorted dict
    pass

class WorkflowArguments():
    # container for workflow input/outputs blocks
    # ToDo: implement as sorted dict
    pass

class Workflow:

    def __init__(self):
        self.tempdir = None
        self.infiles = WorkflowFilenameAssociations()
        self.outfiles = WorkflowFilenameAssociations()
        self.inputs = WorkflowBlockAssociations()
        self.outputs = WorkflowBlockAssociations()
        self.inargs = WorkflowArguments()
        self.outargs = WorkflowArguments()
        self.controls = ApplierControls()
        self.verbose = True
        self.setTempdir(tempfile.gettempdir())

    def setTempdir(self, root):
        self.tempdir = Temporary(root=root).path('workflowOutputArguments_')

    def _linkInputFiles(self):
        for infiles in self.infiles.__dict__.values():
            infiles._linkInputFiles()
            infiles._readMetas()

    def _linkOutputFiles(self, riosOutfiles):
        assert isinstance(riosOutfiles, rios.applier.FilenameAssociations)

        extension = self.getOutputExtension()

        for key, outfiles in self.outfiles.__dict__.items():
            outputs = getattr(self.outputs, key)
            outfiles._linkOutputFiles(outputs=outputs, extension=extension)

            #riosOutfiles.__dict__.update(outfiles._filenameAssociations.__dict__)
            riosOutfiles.__dict__.update(outfiles._getRiosFilenameAssociations().__dict__)


    def getOutputExtension(self):

        if self.controls.drivername == 'ENVI':  return '.img'
        if self.controls.drivername == 'GTiff': return '.tif'
        raise Exception('unknown driver: '+self.controls.drivername)


    def getRiosFilenameAssociations(self):

        riosInfiles = rios.applier.FilenameAssociations()
        riosOutfiles = rios.applier.FilenameAssociations()
        for infiles in self.infiles.__dict__.values():
            riosInfiles.__dict__.update(infiles._getRiosFilenameAssociations().__dict__)
        for outfiles in self.outfiles.__dict__.values():
            riosOutfiles.__dict__.update(outfiles._getRiosFilenameAssociations().__dict__)

        return riosInfiles, riosOutfiles

    def mapRiosInputs(self, riosInputs):
        assert isinstance(riosInputs, rios.applier.BlockAssociations)

        for key, infiles in self.infiles.__dict__.items():
            assert isinstance(infiles, (FilenameAssociations, FilenameAssociationsCollection))
            inputs = infiles._createBlockAssociations(riosBlockAssociations=riosInputs)
            setattr(self.inputs, key, inputs)

    def mapRiosOutputs(self, riosOutputs):
        assert isinstance(riosOutputs, rios.applier.BlockAssociations)

        for key, outfiles in self.outfiles.__dict__.items():
            outputs = getattr(self.outputs, key)
            outfiles._mapRiosOutputs(blockAssociations=outputs, riosBlockAssociations=riosOutputs)

    def pickleOutputArguments(self, xblock, yblock):

        filename = os.path.join(self.tempdir, 'output_arguments_'+str(xblock)+'_'+str(yblock)+'.pkl')
        savePickle(var=self.outargs, filename=filename)

    #for key, value in self.outargs.__dict__.items():
        #    filename = os.path.join(self.tempdir, key+'_'+str(xblock)+'_'+str(yblock)+'.pkl')
        #    savePickle(var=value, filename=filename)

    def unpickleOutputArguments(self):

        filenames = filesearch(dir=self.tempdir, pattern='*.pkl')
        outargsList = [restorePickle(filename=filename) for filename in filenames]

        for key in self.outargs.__dict__.keys():
            self.outargs.__dict__[key] = [outargs.__dict__[key] for outargs in outargsList]
        shutil.rmtree(self.tempdir)

    def run(self, verbose=True):

        self.verbose = verbose

        # link input filenames
        self._linkInputFiles()

        # prepare Rios parameters
        riosOtherArgs = rios.applier.OtherInputs()
        riosOtherArgs.workflow = self
        riosInfiles, riosOutfiles = self.getRiosFilenameAssociations()
        riosOtherArgs.riosInfiles = riosInfiles
        riosOtherArgs.riosOutfiles = riosOutfiles

        # call rios applier
        rios.applier.apply(userFunction=workflowUserFunctionWrapper, infiles=riosInfiles, outfiles=riosOutfiles, otherArgs=riosOtherArgs,
              controls=self.controls)

        # set metadata for result images
        for key, outfiles in self.outfiles.__dict__.items():
            outputs = getattr(self.outputs, key)

            # read metas written by RIOS/GDAL
            outfiles._readMetas()

            outfiles._updateOutputMeta(outputs=outputs)

        # unpickle output parameters
        self.unpickleOutputArguments()

        if self.verbose:
            print(100)

    def apply(self, info):
        # define the data processing workflow here
        pass

def workflowUserFunctionWrapper(riosInfo, riosInputs, riosOutputs, riosOtherArgs):

    assert isinstance(riosInfo, rios.readerinfo.ReaderInfo)
    assert isinstance(riosInputs, rios.applier.BlockAssociations)
    assert isinstance(riosOutputs, rios.applier.BlockAssociations)
    assert isinstance(riosOtherArgs, rios.applier.OtherInputs)
    assert isinstance(riosOtherArgs.workflow, Workflow)

    workflow = riosOtherArgs.workflow

    # print progress
    if workflow.verbose:
        print(int((riosInfo.xblock + riosInfo.yblock * riosInfo.xtotalblocks) / float(riosInfo.xtotalblocks * riosInfo.ytotalblocks) * 100), end='..')
        #print(riosInfo.xblock+1, '/', riosInfo.xtotalblocks, '---',  riosInfo.yblock+1, '/', riosInfo.ytotalblocks)


    workflow.mapRiosInputs(riosInputs=riosInputs)

    # run the workflow
    workflow.apply(riosInfo)

    # link output files to RIOS
    # Note: this is redundantly done for each block, to be able to infere the filenames of more complex outputs types
    #       (e.g. Landsat Products/Collections) dynamically after the complete workflow is executed. Doing this before
    #       hand would complicate the user's workflow specification.
    workflow._linkOutputFiles(riosOutfiles=riosOtherArgs.riosOutfiles)

    # map output blocks to RIOS
    workflow.mapRiosOutputs(riosOutputs=riosOutputs)

    # pickle output arguments to file (necessary for multi processing)
    workflow.pickleOutputArguments(xblock=riosInfo.xblock, yblock=riosInfo.yblock)


class MyWorkflowIOImage(Workflow):

    def apply(self, info):

        imageBA = self.inputs.image
        imageCopyBA = ImageBA().addBlock(cube=imageBA.cube, meta=imageBA.meta)
        self.outputs.image = imageCopyBA


class MyWorkflowIOProduct(Workflow):

    def apply(self, info):

        assert isinstance(self.inputs.product, ProductBA)

        inProductBA = self.inputs.product

        outProductBA = ProductBA(productName=inProductBA.productName)
        for key, (cube, meta) in inProductBA.items():
            outProductBA[key] = (cube, meta)

        self.outputs.product = outProductBA
        #self.outputs.xyz = outProductBA


class MyWorkflowIOCollection(Workflow):

    def apply(self, info):
        assert isinstance(self.inputs.collection, BlockAssociationsCollection)

        collectionBA = self.inputs.collection
        cube = numpy.zeros_like(collectionBA[0].cube, dtype=numpy.float32)
        for landsatBA in collectionBA:
            cube += numpy.clip(landsatBA.cube, 0, numpy.inf)
        meta=GDALMeta().setNoDataValue(0)
        self.outputs.image = ImageBA().addBlock(cube=cube, meta=meta)

class MyWorkflowIOProductCollection(Workflow):

    def apply(self, info):

        collectionBA = self.inputs.collection
        assert isinstance(collectionBA, ProductCollectionBA)
        collectionCopyBA = ProductCollectionBA()
        for productBA in collectionBA:
            collectionCopyBA.append(productBA)
        self.outputs.collection = collectionCopyBA

class MyWorkflowOutputParameters(Workflow):

    def apply(self, info):

        self.outargs.myAnswer = self.inargs.myQuestion+' I am in block (x, y) = ('+str(info.xblock)+', '+str(info.yblock)+')!'


def testIOImage():

    workflow = MyWorkflowIOImage()
    workflow.infiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.outfiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyImage\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.tif')
    workflow.run()

    return


def testIOProduct():

    workflow = MyWorkflowIOProduct()
    workflow.infiles.product = ProductFA(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    workflow.outfiles.product = ProductFA(r'C:\Work\data\gms\landsat_copyProduct\193\024\LC81930242015276LGN00')
    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()
    workflow.run()

def testIOBenchmark():

    workflow = Workflow()
    workflow.controls.setNumThreads(1)

    verbose = False
    for blockSize in [256]:
        workflow.controls.setWindowXsize(blockSize)
        workflow.controls.setWindowYsize(blockSize)
        print('++++++++++++++++++++++++')
        print('block size =', blockSize)

        workflow.infiles.image = ImageFA(r'C:\Work\data\y_band.tif')
        tic('compressed GTiff (interleave=band)')
        workflow.run(verbose=verbose)
        toc()

        workflow.infiles.image = ImageFA(r'C:\Work\data\y_pixel.tif')
        tic('compressed GTiff (interleave=pixel)')
        workflow.run(verbose=verbose)
        toc()

        tic('compressed ENVI BSQ')
        workflow.infiles.image = ImageFA(r'C:\Work\data\x.img')
        workflow.run(verbose=verbose)
        toc()

    #workflow.outfiles.product = ProductFA(r'C:\Work\data\gms\landsat_copyProduct\193\024\LC81930242015276LGN00')


def testIOCollection():

    workflow = MyWorkflowIOCollection()

    workflow.infiles.collection =  FilenameAssociationsCollection()\
        .append(ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img'))\
        .append(ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LE71930242015284NSG00\LE71930242015284NSG00_sr.img'))
    workflow.outfiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_ImageSum\sum_sr.img')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOProductCollection():

    workflow = MyWorkflowIOProductCollection()
    workflow.infiles.collection = ProductCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC')
    workflow.outfiles.collection = ProductCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyCollection\32\32UPC')

    workflow.controls.setNumThreads(10)
    workflow.run()
    print

def testIOParameters():

    workflow = MyWorkflowOutputParameters()
    workflow.infiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.inargs.myQuestion = 'Hello process, what is your block number? ... '
    workflow.controls.setNumThreads(1)
    workflow.run()

    for answer in workflow.outargs.myAnswer:
        print(answer)

def testExtractSampleFromProduct():

    productFA = ProductFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\33\33UUT\LC81930242015276LGN00')
    labelsFA = ImageFA(r'C:\Work\data\gms\lucasMGRS\33\33UUT\lucas\lucas_lc4.img')
    sampledProductFA = productFA.extractByMask(maskFA=labelsFA, dirname=r'C:\Work\data\gms\landsatXMGRS_ENVI_extracted\33\33UUT\LC81930242015276LGN00')

def testExtractSampleFromProductCollection():

    productCollectionFA = ProductCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\33\33UUT')
    labelsFA = ImageFA(r'C:\Work\data\gms\lucasMGRS\33\33UUT\lucas\lucas_lc4.img')
    sampledProductCollectionFA = productCollectionFA.extractByMask(maskFA=labelsFA, dirname=r'C:\Work\data\gms\landsatXMGRS_ENVI_extracted\33\33UUT')

def testStackFromBlockAssociations():

    class W(Workflow):
        def apply(self, info):
            landsatBandsBA = assertType(self.inputs.landsatBands, BlockAssociations)

            # define filter function for stacking order
            def filter(blockAssociations):
                assert isinstance(blockAssociations, BlockAssociations)


            self.outputs.landsatStack = landsatBandsBA.getStackBA()

    w = W()
    w.infiles.landsatBands = ProductFA(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    w.outfiles.landsatStack = ImageFA( r'C:\Work\data\gms\landsat_stack\193\024\LC81930242015276LGN00')
    w.run()



if __name__ == '__main__':
    tic()
    #testIOImage()
    #testIOCollection()
    #testIOProduct()
    #testIOBenchmark()
    #testIOProductCollection()
    #testIOParameters()
    #testExtractSampleFromProduct()
    #testExtractSampleFromProductCollection()
    testStackFromBlockAssociations()
    toc()

'''
BlockAssociations
-getBlocks() # (cube,meta) list

FilenameAssociations
-getFilenames() # filenames list


ImageBA(BlockAssociations)
ImageCollection(BlockAssociations)

'''