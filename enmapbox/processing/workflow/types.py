from __future__ import print_function
import os
import tempfile
import shutil
from collections import OrderedDict

import rios.applier
import rios.readerinfo
from rios.pixelgrid import pixelGridFromFile, findCommonRegion, PixelGridDefn
import numpy

from hub.gdal.api import GDALMeta
from hub.file import mkdir, mkfiledir, filesearch, savePickle, restorePickle, remove
from hub.datetime import Date
from hub.timing import tic, toc
from hub.temp import Temporary

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
        self.setCreationOptions(['INTERLEAVE='+interleave, 'TILED='+tiled, 'BIGTIFF=YES',
                                 'BLOCKXSIZE='+str(blockxsize), 'BLOCKYSIZE='+str(blockysize),
                                 'COMPRESS='+compress, 'PREDICTOR='+str(predictor)])

class ImageBlock():

    def __init__(self, cube=None, meta=None):
        self.cube = assertType(cube, numpy.ndarray)
        self.meta = assertType(meta, GDALMeta)


class Image():

    BlockClass = ImageBlock

    def __init__(self, filename=None):
        self._filename = filename

    def getFilenames(self):
        return [self.filename]

    def mapBlocksFromRios(self, riosBlockAssociations):
        assert isinstance(riosBlockAssociations, rios.applier.BlockAssociations)
        imageBlock = ImageBlock(cube=getattr(riosBlockAssociations, self._filename), meta=self.meta)
        return imageBlock

    def mapBlocksToRios(self, imageBlock, riosBlockAssociations):

        if not isinstance(imageBlock, self.BlockClass):
            raise Exception('Output type (' + self.__class__.__name__ + ') does not match block type (' + imageBlock.__class__.__name__ + ')!')
        cube = imageBlock.cube
        setattr(riosBlockAssociations, self.filename, cube)
        self.mkdirs()

    def linkInputFiles(self):
        self.filename = self._filename

    def linkOutputFiles(self, outputs, extension):
        self.filename = self._filename+extension

    def readMetas(self):
        self.meta = GDALMeta(self.filename)

    def updateOutputMeta(self, imageBlock):
        assert isinstance(imageBlock, ImageBlock)

        # append metas from workflow
        metaRios = imageBlock.meta
        metaWorkflow = self.meta
        metaWorkflow.setMetadataDict(metaRios.getMetadataDict())
        metaWorkflow.writeMeta(self.filename)

    def mkdirs(self):
        mkfiledir(self.filename)


class ImageCollectionBlock():

    def __init__(self, name):
        self.name = name
        self.images = OrderedDict()


class ImageCollection():

    BlockClass = ImageCollectionBlock

    def __init__(self, dirname, extensions=['.img', '.tif', '.vrt']):
        self.dirname = dirname
        self.name = os.path.basename(dirname)
        self.extensions = extensions
        self.images = OrderedDict()

    def getFilenames(self):
        for key, image in self.images.items():
            yield image.filename

    def mapBlocksFromRios(self, riosBlockAssociations):
        assert isinstance(riosBlockAssociations, rios.applier.BlockAssociations)
        imageCollectionBlock = ImageCollectionBlock(name=self.name)

        for key, image in self.images.items():
            imageBlock = image.mapBlocksFromRios(riosBlockAssociations)
            imageCollectionBlock.images[key] = imageBlock
        return imageCollectionBlock

    def mapBlocksToRios(self, collectionBlock, riosBlockAssociations):

        if not isinstance(collectionBlock, self.BlockClass):
            raise Exception('Output type (' + self.__class__.__name__ + ') does not match block type (' + collectionBlock.__class__.__name__ + ')!')

        for key, image in self.images.items():
            imageBlock = collectionBlock.images[key]
            image.mapBlocksToRios(imageBlock=imageBlock, riosBlockAssociations=riosBlockAssociations)

    def linkInputFiles(self):
        for extension in self.extensions:
            filenames = filesearch(self.dirname, '*'+extension)
            for filename in filenames:
                image = Image(filename=filename)
                image.linkInputFiles()
                basename = os.path.splitext(os.path.basename(filename))[0]
                self.images[basename] = image

    def linkOutputFiles(self, imageCollectionBlock, extension):

        assert isinstance(imageCollectionBlock, ImageCollectionBlock)

        for key, imageBlocks in imageCollectionBlock.images.items():
            filename = os.path.join(self.dirname, key + extension)
            image = Image(filename=filename)
            image.linkInputFiles()
            self.images[key] = image

    def readMetas(self):
        for key, image in self.images.items():
            image.readMetas()

    def updateOutputMeta(self, collectionBlock):
        assert isinstance(collectionBlock, ImageCollectionBlock)
        for key, image in self.images.items():
            imageBlock = collectionBlock.images[key]
            image.updateOutputMeta(imageBlock=imageBlock)


class ImageCollectionListBlock():

    def __init__(self, name):
        self.name = name
        self.collections = OrderedDict()


class ImageCollectionList():

    BlockClass = ImageCollectionListBlock

    def __init__(self, dirname, extensions=['.img', '.tif', '.vrt']):
        self.dirname = dirname
        self.name = os.path.basename(dirname)
        self.extensions = extensions
        self.collections = OrderedDict()

    def getFilenames(self):
        for key, collection in self.collections.items():
            for filename in collection.getFilenames():
                yield filename

    def mapBlocksFromRios(self, riosBlockAssociations):
        assert isinstance(riosBlockAssociations, rios.applier.BlockAssociations)
        imageCollectionListBlock = ImageCollectionListBlock(name=self.name)

        for key, collection in self.collections.items():
            imageCollectionListBlock.collections[key] = collection.mapBlocksFromRios(riosBlockAssociations)
        return imageCollectionListBlock

    def mapBlocksToRios(self, listBlock, riosBlockAssociations):
        if not isinstance(listBlock, self.BlockClass):
            raise Exception(
                'Output type (' + self.__class__.__name__ + ') does not match block type (' + listBlock.__class__.__name__ + ')!')

        for key, collection in self.collections.items():
            collectionBlock = listBlock.collections[key]
            collection.mapBlocksToRios(collectionBlock=collectionBlock, riosBlockAssociations=riosBlockAssociations)

    def linkInputFiles(self):

        dirnames = [os.path.join(self.dirname, basename) for basename in  os.listdir(self.dirname)]
        for dirname in dirnames:
            imageCollection = ImageCollection(dirname=dirname, extensions=self.extensions)
            imageCollection.linkInputFiles()
            self.collections[imageCollection.name] =imageCollection

    def linkOutputFiles(self, imageCollectionListBlock, extension):
        assert isinstance(imageCollectionListBlock, ImageCollectionListBlock)

        for key, imageCollectionBlock in imageCollectionListBlock.collections.items():
            dirname = os.path.join(self.dirname, key)
            collection = ImageCollection(dirname=dirname)
            collection.linkOutputFiles(imageCollectionBlock, extension)
            self.collections[key] = collection

    def readMetas(self):
        for key, collection in self.collections.items():
            collection.readMetas()

    def updateOutputMeta(self, listBlock):
        assert isinstance(listBlock, ImageCollectionListBlock)
        for key, collection in self.collections.items():
            collectionBlock = listBlock.collections[key]
            collection.updateOutputMeta(collectionBlock=collectionBlock)

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

    def linkInputFiles(self):
        for infiles in self.infiles.__dict__.values():
            infiles.linkInputFiles()
            infiles.readMetas()

    def linkOutputFiles(self, riosOutfiles):
        assert isinstance(riosOutfiles, rios.applier.FilenameAssociations)

        extension = self.getOutputExtension()

        for key, outfiles in self.outfiles.__dict__.items():
            outputs = getattr(self.outputs, key)
            outfiles.linkOutputFiles(outputs, extension=extension)

            #riosOutfiles.__dict__.update(outfiles._filenameAssociations.__dict__)
            for filename in outfiles.getFilenames():
                setattr(riosOutfiles, filename, filename)


    def getOutputExtension(self):

        if self.controls.drivername == 'ENVI':  return '.img'
        if self.controls.drivername == 'GTiff': return '.tif'
        raise Exception('unknown driver: '+self.controls.drivername)


    def getRiosFilenameAssociations(self):

        riosInfiles = rios.applier.FilenameAssociations()
        riosOutfiles = rios.applier.FilenameAssociations()
        for infiles in self.infiles.__dict__.values():
            for filename in infiles.getFilenames():
                setattr(riosInfiles, filename, filename)

#        for outfiles in self.outfiles.__dict__.values():
#            for filename in outfiles.getFilenames():
#                setattr(riosOutfiles, filename, filename)

        return riosInfiles, riosOutfiles

    def mapRiosInputs(self, riosInputs):
        assert isinstance(riosInputs, rios.applier.BlockAssociations)

        for key, infiles in self.infiles.__dict__.items():
            inputs = infiles.mapBlocksFromRios(riosBlockAssociations=riosInputs)
            setattr(self.inputs, key, inputs)

    def mapRiosOutputs(self, riosOutputs):
        assert isinstance(riosOutputs, rios.applier.BlockAssociations)

        for key, outfiles in self.outfiles.__dict__.items():
            outputs = getattr(self.outputs, key)
            outfiles.mapBlocksToRios(outputs, riosOutputs)

    def pickleOutputArguments(self, xblock, yblock):

        filename = os.path.join(self.tempdir, 'output_arguments_'+str(xblock)+'_'+str(yblock)+'.pkl')
        savePickle(var=self.outargs, filename=filename)

    def unpickleOutputArguments(self):

        filenames = filesearch(dir=self.tempdir, pattern='*.pkl')
        outargsList = [restorePickle(filename=filename) for filename in filenames]

        for key in self.outargs.__dict__.keys():
            self.outargs.__dict__[key] = [outargs.__dict__[key] for outargs in outargsList]
        shutil.rmtree(self.tempdir)

    def run(self, userFunction=None, verbose=True):

        self.verbose = verbose
        self.userFunction = userFunction # if is None, self.apply() must be provided

        # link input filenames
        self.linkInputFiles()

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
            outfiles.readMetas()

            outfiles.updateOutputMeta(outputs)

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
    if workflow.userFunction is not None:
        workflow.userFunction(riosInfo, workflow.inputs, workflow.outputs, workflow.inargs, workflow.outargs)
    else:
        workflow.apply(riosInfo)

    # link output files to RIOS
    # Note: this is redundantly done for each block, to be able to infere the filenames of more complex outputs types
    #       (e.g. Landsat Products/Collections) dynamically after the complete workflow is executed. Doing this before
    #       hand would complicate the user's workflow specification.
    workflow.linkOutputFiles(riosOutfiles=riosOtherArgs.riosOutfiles)

    # map output blocks to RIOS
    workflow.mapRiosOutputs(riosOutputs=riosOutputs)

    # pickle output arguments to file (necessary for multi processing)
    workflow.pickleOutputArguments(xblock=riosInfo.xblock, yblock=riosInfo.yblock)


##############################
### define some test cases ###

class MyWorkflowParameters(Workflow):

    def apply(self, info):

        self.outargs.myAnswer = self.inargs.myQuestion+' I am in block (x, y) = ('+str(info.xblock)+', '+str(info.yblock)+') of image: '+self.infiles.image.filename

def testIOParameters():

    workflow = MyWorkflowParameters()
    workflow.infiles.image = Image(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.inargs.myQuestion = 'Hello process, what is your block number? ... '
    workflow.controls.setNumThreads(10)
    workflow.run()

    for answer in workflow.outargs.myAnswer:
        print(answer)

class MyWorkflowIOImage(Workflow):
    def apply(self, info):
        image = assertType(self.inputs.image, ImageBlock)
        imageCopy = ImageBlock(cube=image.cube, meta=image.meta)
        self.outputs.image = imageCopy


def testIOImage():

    workflow = MyWorkflowIOImage()
    workflow.infiles.image = Image(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.outfiles.image = Image(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyImage\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr')
    workflow.controls.setNumThreads(2)
    workflow.run()

    return

class MyWorkflowIOImageCollection(Workflow):

    def apply(self, info):
        imageCollection = assertType(self.inputs.imageCollection, ImageCollectionBlock)
        imageCollectionCopy = ImageCollectionBlock(name=imageCollection.name)

        for key, image in imageCollection.images.items():
            imageCopy = ImageBlock(cube=image.cube, meta=image.meta)
            imageCollectionCopy.images[key] = imageCopy

        self.outputs.imageCollection = imageCollectionCopy

def testIOImageCollection():

    workflow = MyWorkflowIOImageCollection()
    #workflow.infiles.imageCollection = ImageCollection(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    #workflow.outfiles.imageCollection = ImageCollection(r'C:\Work\data\gms\landsat_copyImageCollection\193\024\LC81930242015276LGN00')
    workflow.infiles.imageCollection = ImageCollection(r'C:\Work\data\gms\landsatXMGRS_ENVI\33\33UUT\LC81930242015276LGN00')
    workflow.outfiles.imageCollection = ImageCollection(r'C:\Work\data\gms\landsatXMGRS_ENVI_copy\33\33UUT\LC81930242015276LGN00')
    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()
    workflow.run()

class MyWorkflowIOImageCollectionList(Workflow):

    def apply(self, info):
        imageCollectionList = assertType(self.inputs.imageCollectionList, ImageCollectionListBlock)
        imageCollectionListCopy = ImageCollectionListBlock(name=imageCollectionList.name)

        for keyCollection, collection in imageCollectionList.collections.items():
            imageCollectionCopy = ImageCollectionBlock(name=keyCollection)
            imageCollectionListCopy.collections[keyCollection] = imageCollectionCopy
            for keyImage, image in collection.images.items():
                imageCopy = ImageBlock(cube=image.cube, meta=image.meta)
                imageCollectionCopy.images[keyImage] = imageCopy

        self.outputs.imageCollectionList = imageCollectionListCopy

def testIOImageCollectionList():

    workflow = MyWorkflowIOImageCollectionList()
    workflow.infiles.imageCollectionList = ImageCollectionList(r'C:\Work\data\gms\landsatXMGRS_ENVI\33\33UUT')
    workflow.outfiles.imageCollectionList = ImageCollectionList(r'C:\Work\data\gms\landsatXMGRS_ENVI_copy\33\33UUT')
    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()
    workflow.run()

class MyWorkflowJustEnterAndHoldOnBreakPoint(Workflow):

    def apply(self, info):
        print()


def testOnTheFlySubsetting():

    workflow = MyWorkflowJustEnterAndHoldOnBreakPoint()
    workflow.infiles.image1 = Image(r'C:\Work\data\gms\landsatX\194\024\LC81940242015235LGN00\LC81940242015235LGN00_qa.vrt')
    workflow.infiles.image2 = Image(r'C:\Work\data\gms\landsatX\193\024\LC81930242015276LGN00\LC81930242015276LGN00_qa.vrt')
    #workflow.infiles.image1 = ImageCollectionList(r'C:\Work\data\gms\landsatX\193\024')
    #workflow.infiles.image2 = ImageCollectionList(r'C:\Work\data\gms\landsatX\194\024')

    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()


    pixelGrid1 = pixelGridFromFile(r'C:\Work\data\gms\landsatX\194\024\LC81940242015235LGN00\LC81940242015235LGN00_qa.vrt')
    pixelGrid2 = pixelGridFromFile(r'C:\Work\data\gms\landsatX\193\024\LC81930242015276LGN00\LC81930242015276LGN00_qa.vrt')
    pixelGrid2Reprojected = pixelGrid2.reproject(pixelGrid1)
    pixelGrid = pixelGrid1.union(pixelGrid2Reprojected)
    print(pixelGrid)
    workflow.controls.setReferencePixgrid(pixelGrid)
    workflow.controls.setResampleMethod('near')
    workflow.controls.setFootprintType('UNION')
    workflow.controls.setWindowXsize(99999)
    workflow.controls.setWindowYsize(99999)
    workflow.run()


'''def testExtractSampleFromProduct():

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
    w.run()'''


if __name__ == '__main__':
    tic()
    #testIOParameters()
    #testIOImage()
    #testIOImageCollection()
    #testIOImageCollectionList()
    testOnTheFlySubsetting()


    #testIOProductCollection()
    #testExtractSampleFromProduct()
    #testExtractSampleFromProductCollection()
    #testStackFromBlockAssociations()
    toc()

'''
BlockAssociations
-getBlocks() # (cube,meta) list

FilenameAssociations
-getFilenames() # filenames list


ImageBA(BlockAssociations)
ImageCollection(BlockAssociations)

'''