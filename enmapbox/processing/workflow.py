from __future__ import print_function
import rios.applier
#from rios.applier import FilenameAssociations, BlockAssociations, OtherInputs
import rios.readerinfo
import os
from hub.gdal.api import GDALMeta
from hub.file import mkdir, filesearch
from hub.datetime import Date
from hub.timing import tic, toc
import numpy

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
        self.setOutputDriverName = 'ENVI'
        self.setCreationOptions = ['INTERLEAVE=' + interleave]

    def setOutputDriverGTiff(self, interleave='BAND', tiled='YES', blockxsize=256, blockysize=256,
                             compress='LZW', predictor=2):
        assert interleave.lower() in ['band']
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
        self._meta = dict()

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

    def __getitem__(self, key):
        return self._getBlock(key=key)

    def __setitem__(self, key, cube_meta):
        cube, meta = cube_meta
        return self._addBlock(key=key, cube=cube, meta=meta)

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


class FilenameAssociations():

    BlockAssociationsClass = BlockAssociations

    def __init__(self):
        self._keyLookup = dict()
        self._filenameAssociations = rios.applier.FilenameAssociations()
        self._meta = dict()

    def _getRiosFilenameAssociations(self):
        return self._filenameAssociations

    def _addImage(self, key, filename):
        self._keyLookup[filename] = key
        setattr(self._filenameAssociations, filename, filename)
        return self

    def _createBlockAssociations(self, riosBlockAssociations):
        assert isinstance(riosBlockAssociations, rios.applier.BlockAssociations)
        blockAssociations = self.BlockAssociationsClass()

        for filename, imageKey in self._keyLookup.items():
            cube = getattr(riosBlockAssociations, filename)
            meta = self._getMeta(filename=filename)
            blockAssociations._addBlock(key=imageKey, cube=cube, meta=meta)
        return blockAssociations

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
    pass

class ProductFA(FilenameAssociations):

    BlockAssociationsClass = ProductBA
    #outExtension = '.img'

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

    def _linkOutputFiles(self, outputs, extension):

        for basename in outputs.keys():
            filename = os.path.join(self.dirname, basename+extension)
            self._addImage(key=basename, filename=filename)


class BlockAssociationsCollection():

    def __init__(self):
        self._collection = list()

    def __iter__(self):
        for blockAssociations in self._collection:
            yield blockAssociations

    def __getitem__(self, item):
        return self._collection[item]

    def append(self, blockAssociations):
        assert isinstance(blockAssociations, BlockAssociations)
        self._collection.append(blockAssociations)
        return self

    def filter(self, filterFunction):
        filteredCollection = filterFunction(self)
        assert isinstance(filteredCollection, BlockAssociationsCollection)
        return filteredCollection

class FilenameAssociationsCollection():

    BlockAssociationsClass = BlockAssociationsCollection
    outExtension = '.img'

    def __init__(self):
        self._collection = list()

    def _getRiosFilenameAssociations(self):

        allFilenameAssociations = rios.applier.FilenameAssociations()
        for filenameAssociations in self._collection:
            allFilenameAssociations.__dict__.update(filenameAssociations._getRiosFilenameAssociations().__dict__)
        return allFilenameAssociations

    def _createBlockAssociations(self, riosBlockAssociations):

        allBlockAssociations = self.BlockAssociationsClass()
        for blockAssociations in self._collection:
            allBlockAssociations.append(blockAssociations._createBlockAssociations(riosBlockAssociations=riosBlockAssociations))
        return allBlockAssociations

    def _linkInputFiles(self):
        for inputs in self._collection:
            inputs._linkInputFiles()

    def _linkOutputFiles(self, outputs):
        raise Exception(self.__class__.__name__ +' type is read only.')


    def _readMetas(self):
        for infiles in self._collection:
            infiles._readMetas()

    def append(self, filenameAssociations):
        assert isinstance(filenameAssociations, FilenameAssociations)
        self._collection.append(filenameAssociations)
        return self


class ProductCollectionBA(BlockAssociationsCollection):

    ProductBAClass = ProductBA

    def append(self, productBA):
        assert isinstance(productBA, self.ProductBAClass)
        BlockAssociationsCollection.append(self, blockAssociations=productBA)


class ProductCollectionFA(FilenameAssociationsCollection):

    BlockAssociationsClass = ProductCollectionBA
    ProductFAClass = ProductFA

    def __init__(self, dirname):
        FilenameAssociationsCollection.__init__(self)
        self.dirname = dirname

    def _linkInputFiles(self):

        for productName in os.listdir(self.dirname):
            dirname = os.path.join(self.dirname, productName)
            productFA = self.ProductFAClass(dirname=dirname)
            self.append(productFA)

        FilenameAssociationsCollection._linkInputFiles(self)

class WorkflowFilenameAssociations():
    # container for workflow input/output files
    pass


class WorkflowBlockAssociations():
    # container for workflow input/outputs blocks
    pass

class Workflow:

    def __init__(self):

        self.infiles = WorkflowFilenameAssociations()
        self.outfiles = WorkflowFilenameAssociations()
        self.inputs = WorkflowBlockAssociations()
        self.outputs = WorkflowBlockAssociations()
        self.controls = ApplierControls()

    def _linkInputFiles(self):
        for infiles in self.infiles.__dict__.values():
            infiles._linkInputFiles()
            infiles._readMetas()

    def _linkOutputFiles(self, riosOutfiles):
        assert isinstance(riosOutfiles, rios.applier.FilenameAssociations)

        for key, outfiles in self.outfiles.__dict__.items():
            outputs = getattr(self.outputs, key)
            if self.controls.drivername == 'ENVI':
                extension = '.img'
            elif self.controls.drivername == 'GTiff':
                extension = '.tif'
            else:
                raise Exception('unknown driver')

            outfiles._linkOutputFiles(outputs=outputs, extension=extension)
            riosOutfiles.__dict__.update(outfiles._filenameAssociations.__dict__)

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
            assert isinstance(outfiles, FilenameAssociations)
            assert isinstance(outputs, BlockAssociations)
            if not isinstance(outputs, outfiles.BlockAssociationsClass):
                raise Exception('Output filename association type (' + outfiles.__class__.__name__ + ') does not match output block association type (' + outputs.__class__.__name__ + ')!')
            outfiles._mkdir()
            for filename, imageKey in outfiles._keyLookup.items():
                cube = getattr(outputs._blockAssociations, imageKey)
                setattr(riosOutputs, filename, cube)

    def setReaderInfo(self, info):
        assert isinstance(info, (rios.readerinfo.ReaderInfo))
        self.info = info

    def getReaderInfo(self):
        assert isinstance(self.info, rios.readerinfo.ReaderInfo)
        return self.info

    def run(self):

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
            assert isinstance(outfiles, FilenameAssociations)
            assert isinstance(outputs, BlockAssociations)

            # read metas written by RIOS/GDAL
            outfiles._readMetas()
            # append metas from workflow
            for filename, imageKey in outfiles._keyLookup.items():
                metaRios = outputs._meta[imageKey]
                metaWorkflow = outfiles._meta[filename]
                metaRios.setMetadataDict(metaWorkflow.getMetadataDict())
                metaRios.writeMeta(filename)


    def apply(self):
        # define the data processing workflow here
        pass

def workflowUserFunctionWrapper(riosInfo, riosInputs, riosOutputs, riosOtherArgs):

    assert isinstance(riosInfo, rios.readerinfo.ReaderInfo)
    assert isinstance(riosInputs, rios.applier.BlockAssociations)
    assert isinstance(riosOutputs, rios.applier.BlockAssociations)
    assert isinstance(riosOtherArgs, rios.applier.OtherInputs)
    assert isinstance(riosOtherArgs.workflow, Workflow)

    print(riosInfo.xblock+1, '/', riosInfo.xtotalblocks, '---',  riosInfo.yblock+1, '/', riosInfo.ytotalblocks)

    workflow = riosOtherArgs.workflow
    #workflow.setReaderInfo(info=riosInfo)
    workflow.mapRiosInputs(riosInputs=riosInputs)

    # run the workflow
    workflow.apply(riosInfo)

    # link output files
    # Note: this is redundantly done for each block, to be able to infere the filenames of more complex outputs types
    #       (e.g. Landsat Products/Collections) dynamically after the complete workflow is executed. Doing this before
    #       hand would complicate the workflow specification.
    workflow._linkOutputFiles(riosOutfiles=riosOtherArgs.riosOutfiles)
    workflow.mapRiosOutputs(riosOutputs=riosOutputs)

class MyWorkflowIOImage(Workflow):

    def apply(self, info):

        imageBA = self.inputs.image
        imageCopyBA = ImageBA().addBlock(cube=imageBA.cube, meta=imageBA.meta)
        self.outputs.image = imageCopyBA


class MyWorkflowIOProduct(Workflow):

    def apply(self, info):

        assert isinstance(self.inputs.product, ProductBA)

        inProductBA = self.inputs.product

        outProductBA = ProductBA()
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

def testIOImage():

    workflow = MyWorkflowIOImage()
    #workflow.infiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.infiles.image = ImageFA(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')
    workflow.outfiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyImage\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.tif')
    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()

    workflow.run()

def testIOProduct():

    workflow = MyWorkflowIOProduct()
    workflow.infiles.product = ProductFA(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    workflow.outfiles.product = ProductFA(r'C:\Work\data\gms\landsat_copyProduct\193\024\LC81930242015276LGN00')
    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff(compress='DEFLATE')
    workflow.run()

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
    workflow.infiles.collection =  ProductCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC')
    workflow.controls.setNumThreads(1)
    workflow.run()


if __name__ == '__main__':
    tic()
    testIOImage()
    #testIOCollection()
    #testIOProduct()
    #testIOProductCollection()
    toc()