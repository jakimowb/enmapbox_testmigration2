from __future__ import print_function
import rios.applier
#from rios.applier import FilenameAssociations, BlockAssociations, OtherInputs
import rios.readerinfo
import os
from hub.gdal.api import GDALMeta
from hub.file import mkdir, filesearch
from hub.timing import tic, toc
import numpy

class ApplierControls(rios.applier.ApplierControls):

    defaultOutputDriverName = "ENVI"
    defaultCreationOptions = ["INTERLEAVE=BSQ"]
    defaultWindowXsize = 256
    defaultWindowYsize = 256

    def __init__(self):
        rios.applier.ApplierControls.__init__(self)
        self.setNumThreads(1)
        self.setJobManagerType('multiprocessing')
        self.setOutputDriverName(ApplierControls.defaultOutputDriverName)
        self.setCreationOptions(ApplierControls.defaultCreationOptions)
        self.setWindowXsize(ApplierControls.defaultWindowXsize)
        self.setWindowYsize(ApplierControls.defaultWindowYsize)
        self.setCalcStats(False)
        self.setOmitPyramids(True)


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

    def __getitem__(self, item):
        cube = self._blockAssociations.__dict__[item]
        meta = self._meta[item]
        return cube, meta

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

    def _linkOutputFiles(self, outputs):
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
        BlockAssociations._addBlock(self, key=self.key, cube=cube, meta=meta)
        return self

    @property
    def cube(self):
        return self.getCube(key=self.key)

    @property
    def meta(self):
        return BlockAssociations.getMeta(self, key=self.key)


class ImageFA(FilenameAssociations):

    BlockAssociationsClass = ImageBA
    key = 'image'

    def __init__(self, filename):
        FilenameAssociations.__init__(self)
        self.filename = filename

    def _linkInputFiles(self):
        self._addImage(key=self.key, filename=self.filename)

    def _linkOutputFiles(self, outputs):
        self._addImage(key=self.key, filename=self.filename)


class ProductFA(FilenameAssociations):

    BlockAssociationsClass = BlockAssociations

    def __init__(self, dirname, extensions=['.img', '.tif', '.vrt']):
        FilenameAssociations.__init__(self)
        self.dirname = dirname
        self.extensions = extensions

    def _linkInputFiles(self):
        for extension in self.extensions:
            filenames = filesearch(self.dirname, '*'+extension)
            for filename in filenames:
                key = os.path.splitext(os.path.basename(filename))[0]
                self._addImage(key=key, filename=filename)

    def _linkOutputFiles(self, outputs):
        raise Exception('ProductFA is read only!')


class LandsatBA(BlockAssociations):

    def addBlock(self, sr_cube, qa_cube, sr_meta, qa_meta):

        BlockAssociations._addBlock(self, 'sr', sr_cube, sr_meta)
        BlockAssociations._addBlock(self, 'qa', qa_cube, qa_meta)
        return self

    @property
    def sr(self):
        return self.getCube('sr')

    @property
    def srMeta(self):
        return self.getMeta('sr')

    @property
    def qa(self):
        return self.getCube('qa')

    @property
    def qaMeta(self):
        return self.getMeta('qa')

    @property
    def blue(self):
        return self.getCube('sr')[0]

    @property
    def green(self):
        return self.getCube('sr')[1]

    @property
    def red(self):
        return self.getCube('sr')[2]

    @property
    def nir(self):
        return self.getCube('sr')[3]

    @property
    def swir1(self):
        return self.getCube('sr')[4]

    @property
    def swir2(self):
        return self.getCube('sr')[5]

    @property
    def fmask(self):
        return self.getCube('qa')[0]


class LandsatFA(FilenameAssociations):

    BlockAssociationsClass = LandsatBA
    inExtensions = ['.img','.tif','.vrt']
    outExtension = '.img'

    def __init__(self, dirname):
        FilenameAssociations.__init__(self)
        self.dirname = dirname
        self.scene = os.path.basename(dirname)

    def _linkInputFiles(self):
        for key in ['sr', 'qa']:
            filename = None
            for ext in self.inExtensions:
                basename = self.scene + '_' + key + ext
                filename = os.path.join(self.dirname, basename)
                if os.path.exists(filename):
                    break
            if filename is None:
                raise Exception('No filename found.')
            self._addImage(key=key, filename=filename)

    def _linkOutputFiles(self, outputs):
        for key in ['sr', 'qa']:
            basename = self.scene + '_' + key + self.outExtension
            filename = os.path.join(self.dirname, basename)
            self._addImage(key=key, filename=filename)

class LandsatTimeseriesBA(BlockAssociations):
    pass

class LandsatTimeseriesFA(FilenameAssociations):

    BlockAssociationsClass = LandsatTimeseriesBA

    def __init__(self, dirname):
        FilenameAssociations.__init__(self)
        self.dirname = dirname

    '''def _linkInputFiles(self, keyPrefix=''):
        for key in ['sr', 'qa']:
            filename = None
            for ext in self.inExtensions:
                basename = self.scene + '_' + key + ext
                filename = os.path.join(self.dirname, basename)
                if os.path.exists(filename):
                    break
            if filename is None:
                raise Exception('No filename found.')
            self._addImage(key=keyPrefix+key, filename=filename)'''

    def _linkOutputFiles(self, outputs):
        for key in ['sr', 'qa']:
            basename = self.scene + '_' + key + self.outExtension
            filename = os.path.join(self.dirname, basename)
            self._addImage(key=key, filename=filename)


'''class LandsatCollectionBA(BlockAssociations):

    def __init__(self):
        BlockAssociations.__init__(self)
        self._collection = list()

    def _addBlock(self, key, cube, meta):
        BlockAssociations._addBlock(self, key=key, cube=cube, meta=meta)
        return self


    def buildTimeseries(self):
        dates = [meta.getMetadataItem(key='acq') for meta in self._meta.values()]
        return

class LandsatCollectionFA(FilenameAssociations):

    BlockAssociations = LandsatCollectionBA

    def __init__(self, dirname):
        FilenameAssociations.__init__(self)
        self._collection = list()
        self.dirname = dirname

    def _linkInputFiles(self):

        landsatDirnames = [os.path.join(self.dirname, scene) for scene in os.listdir(self.dirname)]

        for landsatDirname in landsatDirnames:
            landsatFA = LandsatFA(dirname=landsatDirname)
            landsatFA._linkInputFiles(keyPrefix=landsatFA.scene+'_')
            for filename, imageKey in landsatFA._keyLookup.items():
                self._addImage(key=imageKey, filename=filename)


    def _linkOutputFiles(self, outputs):
        assert isinstance(outputs, BlockAssociations)

        basenames = outputs._blockAssociations.__dict__.keys()

        filenames = [os.path.join(self.dirname, basename[:-3], basename+LandsatFA.outExtension) for basename in basenames]
        for filename, basename in zip(filenames, basenames):
            self._addImage(key=basename, filename=filename)
            #landsatFA = LandsatFA(dirname=landsatDirname)
            #landsatFA._linkOutputFiles()
            #self._collection.append(landsatFA)
'''

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


class FilenameAssociationsCollection():

    BlockAssociationsClass = BlockAssociationsCollection

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
        assert isinstance(outputs, BlockAssociations)

        basenames = outputs._blockAssociations.__dict__.keys()

        filenames = [os.path.join(self.dirname, basename[:-3], basename+LandsatFA.outExtension) for basename in basenames]
        for filename, basename in zip(filenames, basenames):
            self._addImage(key=basename, filename=filename)
            #landsatFA = LandsatFA(dirname=landsatDirname)
            #landsatFA._linkOutputFiles()
            #self._collection.append(landsatFA)

    def _readMetas(self):
        for infiles in self._collection:
            infiles._readMetas()


    def append(self, filenameAssociations):
        assert isinstance(filenameAssociations, FilenameAssociations)
        self._collection.append(filenameAssociations)
        return self


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
            try:
                outputs = getattr(self.outputs, key)
            except AttributeError:
                raise Exception('Missing workflow output key: '+key)
            assert isinstance(outputs, BlockAssociations)
            outfiles._linkOutputFiles(outputs=outputs)
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

        pan = numpy.zeros((info.blockheight, info.blockwidth), dtype=numpy.float32)
        productBA = self.inputs.product
        for key, (cube, meta) in productBA.items():
            if key.find('band') != -1:
                pan += numpy.clip(cube[0], 0, numpy.inf)
        meta = GDALMeta().setNoDataValue(0)

        self.outputs.pan = ImageBA().addBlock(cube=pan, meta=meta)


class MyWorkflowIOLandsat(Workflow):

    def apply(self, info):

        landsatBA = self.inputs.landsat
        landsatCopyBA = LandsatBA().addBlock(sr_cube=landsatBA.sr,
                                             qa_cube=landsatBA.qa,
                                             sr_meta=landsatBA.srMeta,
                                             qa_meta=landsatBA.qaMeta)
        self.outputs.landsat = landsatCopyBA


class MyWorkflowIOCollection(Workflow):

    def apply(self, info):
        assert isinstance(self.inputs.collection, BlockAssociationsCollection)

        collectionBA = self.inputs.collection
        cube = numpy.zeros_like(collectionBA[0].cube, dtype=numpy.float32)
        for landsatBA in collectionBA:
            cube += numpy.clip(landsatBA.cube, 0, numpy.inf)
        meta=GDALMeta().setNoDataValue(0)
        self.outputs.image = ImageBA().addBlock(cube=cube, meta=meta)


class MyWorkflowIOLandsatCollection(Workflow):

    def apply(self, info):

        collectionBA = self.inputs.collection
        bands, lines, samples = collectionBA[0].sr.shape
        sr = numpy.zeros((bands, lines, samples), dtype=numpy.float32)
        count = numpy.zeros((lines, samples), dtype=numpy.float32)
        for landsatBA in collectionBA:
            valid = landsatBA.fmask <= 1
            count += valid
            sr += landsatBA.sr * valid
        sr /= numpy.clip(count, 1, numpy.inf)
        meta=GDALMeta().setNoDataValue(0)
        self.outputs.image = ImageBA().addBlock(cube=sr, meta=meta)


class MyWorkflowLandsatTimeseries(Workflow):

    def apply(self, info):

        landsatCollectionBA = self.inputs.landsatCollection
        landsatTimeseriesBA = landsatCollectionBA.buildTimeseries()
        self.outputs.landsatTimeseries = landsatTimeseriesBA


def test1():

    workflow = MyWorkflow()
    workflow.infiles.landsat = LandsatFA(dirname=r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00')
    workflow.outfiles.ndvi = ImageFA(filename=r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC_ndvi.img')
    workflow.controls.setNumThreads(10)
    workflow.run()

def testIOImage():

    workflow = MyWorkflowIOImage()
    workflow.infiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.outfiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyImage\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOProduct():

    workflow = MyWorkflowIOProduct()
    workflow.infiles.product = ProductFA(r'C:\Work\data\gms\landsat\193\024\LC81930242015276LGN00')
    workflow.outfiles.pan = ImageFA(r'C:\Work\data\gms\pan.img')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOLandsat():

    workflow = MyWorkflowIOLandsat()
    workflow.infiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00')
    #workflow.infiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS\32\32UPC\LC81930242015276LGN00')

    workflow.outfiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyLandsat\32\32UPC\LC81930242015276LGN00')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOCollection():

    workflow = MyWorkflowIOCollection()

    workflow.infiles.collection =  FilenameAssociationsCollection()\
        .append(ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00\LC81930242015276LGN00_sr.img'))\
        .append(ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LE71930242015284NSG00\LE71930242015284NSG00_sr.img'))
    workflow.outfiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_ImageSum\sum_sr.img')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOLandsatCollection():

    workflow = MyWorkflowIOLandsatCollection()
    mgrs = r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC'
    scenes = [os.path.join(mgrs, scene) for scene in os.listdir(mgrs)]
    workflow.infiles.collection =  FilenameAssociationsCollection()
    for scene in scenes:
        workflow.infiles.collection.append(LandsatFA(scene))
    workflow.outfiles.image = ImageFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_ImageSum\sum_sr.img')
    workflow.controls.setNumThreads(1)
    workflow.run()

def __testIOLandsatCollection():

    workflow = MyWorkflowIOLandsatCollection()
    workflow.infiles.landsatCollection =  LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC')
    workflow.outfiles.landsatCollection = LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_Copy\32\32UPC')
    workflow.controls.setNumThreads(1)
    workflow.run()


if __name__ == '__main__':
    tic()
    #test1()
    #testIOImage()
    #testIOLandsat()
    #testIOCollection()
    #testIOProduct()
    testIOLandsatCollection()
    #testLandsatTimeseries()
    toc()