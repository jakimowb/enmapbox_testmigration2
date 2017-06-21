from __future__ import print_function

import sys
from multiprocessing import Pool
from timeit import default_timer as now
import numpy
from osgeo import gdal
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
from hubdc.model import Open, OpenLayer
from hubdc import const
from hubdc._applier.io import ApplierInput, ApplierVector, ApplierOutput
from hubdc._applier.writer import Writer, WriterProcess, QueueMock
from hubdc.model import PixelGrid
from hubdc.progressbar import CUIProgress


class Applier(object):

    def __init__(self):
        self.inputs = dict()
        self.vectors = dict()
        self.outputs = dict()
        self.controls = ApplierControls()
        self.grid = None

    #@property
    #def grid(self):
    #    assert isinstance(self._grid, PixelGrid)
    #    return self._grid

    def setInput(self, key, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=1000*2**20, multithread=True):
        self.inputs[key] = ApplierInput(filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setVector(self, key, filename, layer=0):
        self.vectors[key] = ApplierVector(filename=filename, layer=layer)

    #def getInput(self, key):
    #    return self.inputs[key].filename

    def setInputList(self, key, filenames, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=1000*2**20, multithread=True):
        for i, filename in enumerate(filenames):
            self.setInput(key=(key, i), filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setOutput(self, key, filename, format='GTiff', creationOptions=[]):
        self.outputs[key] = ApplierOutput(filename=filename, format=format, creationOptions=creationOptions)

    def setOutputList(self, key, filenames, format='GTiff', creationOptions=[]):
        for i, filename in enumerate(filenames):
            self.setOutput(key=(key, i), filename=filename, format=format, creationOptions=creationOptions)

    def apply(self, operator, description=' ', *ufuncArgs, **ufuncKwargs):

        import inspect
        if inspect.isclass(operator):
            self.ufuncClass = operator
            self.ufuncFunction = None
        elif callable(operator):
            self.ufuncClass = ApplierOperator
            self.ufuncFunction = operator
        else:
            raise ValueError('operator must be a class or callable')

        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        runT0 = now()
        print('start{description}\n..<init>'.format(description=description), end='..'); sys.stdout.flush()

        self._runCreateGrid()
        self._runInitWriters()
        self._runInitPool()
        results = self._runProcessSubgrids()
        self._runClose()

        print('100%')
        s = (now()-runT0); m = s/60; h = m/60
        print('done{description}in {s} sec | {m}  min | {h} hours'.format(description=description, s=int(s), m=round(m, 2), h=round(h, 2))); sys.stdout.flush()
        return results

    def _runCreateGrid(self):

        if self.controls.referenceGrid is not None:
            self.grid = self.controls.referenceGrid
        else:
            self.grid = self.controls._makeAutoGrid(inputs=self.inputs)

    def _runInitWriters(self):
        self.writers = list()
        self.queues = list()
        self.queueMock = QueueMock()
        if self.controls._multiwriting:
            for w in range(max(1, self.controls.nwriter)):
                w = WriterProcess()
                w.start()
                self.writers.append(w)
                self.queues.append(w.queue)
        self.queueByFilename = self._getQueueByFilenameDict()

    def _runInitPool(self):
        if self.controls._multiprocessing:
            writers, self.writers = self.writers, None  # writers arn't pickable, need to detache them before passing self to Pool initializer
            self.pool = Pool(processes=self.controls.nworker, initializer=_pickableWorkerInitialize, initargs=(self,))
            self.writers = writers  # put writers back
        else:
            _Worker.initialize(applier=self)

    def _runProcessSubgrids(self):

        subgrids = self.grid.subgrids(windowxsize=self.controls.windowxsize,
                                      windowysize=self.controls.windowysize)
        if self.controls._multiprocessing:
            applyResults = list()
        else:
            results = list()

        for i, subgrid in enumerate(subgrids):
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'subgrid': subgrid}

            if self.controls._multiprocessing:
                applyResults.append(self.pool.apply_async(func=_pickableWorkerProcessSubgrid, kwds=kwargs))
            else:
                results.append(_Worker.processSubgrid(**kwargs))

        if self.controls._multiprocessing:
            results = [applyResult.get() for applyResult in applyResults]

        return results

    def _getQueueByFilenameDict(self):

        def lessFilledQueue():
            lfq = self.queues[0]
            for q in self.queues:
                if lfq.qsize() > q.qsize():
                    lfq = q
            return lfq

        queueByFilename = dict()
        for output in self.outputs.values():
            if self.controls._multiwriting:
                queueByFilename[output.filename] = lessFilledQueue()
            else:
                queueByFilename[output.filename] = self.queueMock
        return queueByFilename

    def _runClose(self):
        if self.controls._multiprocessing:
            self.pool.close()
            self.pool.join()

        for writer in self.writers:
            writer.queue.put([Writer.CLOSE_DATASETS, self.controls.createEnviHeader])
            writer.queue.put([Writer.CLOSE_WRITER, None])
            writer.join()


class _Worker(object):

    queues = list()
    inputDatasets = dict()
    inputOptions = dict()
    outputFilenames = dict()
    outputOptions = dict()
    operator = None

    def __init__(self):
        raise Exception('singleton class')

    @classmethod
    def initialize(cls, applier):

        gdal.SetCacheMax(applier.controls.cacheMax)
        gdal.SetConfigOption('GDAL_SWATH_SIZE', str(applier.controls.swathSize))
        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', str(applier.controls.disableReadDirOnOpen))
        gdal.SetConfigOption('GDAL_MAX_DATASET_POOL_SIZE', str(applier.controls.maxDatasetPoolSize))

        assert isinstance(applier, Applier)
        cls.inputDatasets = dict()
        cls.inputOptions = dict()
        cls.inputFilenames = dict()
        cls.outputFilenames = dict()
        cls.outputOptions = dict()
        cls.vectorDatasets = dict()
        cls.vectorFilenames = dict()
        cls.vecdtorLayers = dict()

        # prepare datasets of current main grid without opening
        for key, applierInput in applier.inputs.items():
            assert isinstance(applierInput, ApplierInput)
            cls.inputDatasets[key] = None
            cls.inputFilenames[key] = applierInput.filename
            cls.inputOptions[key] = applierInput.options

        for key, applierOutput in applier.outputs.items():
            assert isinstance(applierOutput, ApplierOutput)
            cls.outputFilenames[key] = applierOutput.filename
            cls.outputOptions[key] = applierOutput.options

        for key, applierVector in applier.vectors.items():
            assert isinstance(applierVector, ApplierVector)
            cls.vectorDatasets[key] = None
            cls.vectorFilenames[key] = applierVector.filename
            cls.vecdtorLayers[key] = applierVector.layer

        # create operator
        cls.operator = applier.ufuncClass(maingrid=applier.grid,
                                          inputDatasets=cls.inputDatasets, inputFilenames=cls.inputFilenames, inputOptions=cls.inputOptions,
                                          outputFilenames=cls.outputFilenames, outputOptions=cls.outputOptions,
                                          vectorDatasets=cls.vectorDatasets, vectorFilenames=cls.vectorFilenames, vectorLayers=cls.vecdtorLayers,
                                          queueByFilename=applier.queueByFilename,
                                          ufuncFunction=applier.ufuncFunction, ufuncArgs=applier.ufuncArgs, ufuncKwargs=applier.ufuncKwargs)

    @classmethod
    def processSubgrid(cls, i, n, subgrid):
        print(int(float(i)/n*100), end='%..'); sys.stdout.flush()
        return cls.operator.apply(subgrid=subgrid, iblock=i, nblock=n)

def _pickableWorkerProcessSubgrid(**kwargs):
    return _Worker.processSubgrid(**kwargs)

def _pickableWorkerInitialize(*args):
    return _Worker.initialize(*args)

class ApplierOperator(object):

    def __init__(self, maingrid, inputDatasets, inputFilenames, inputOptions,
                 outputFilenames, outputOptions,
                 vectorDatasets, vectorFilenames, vectorLayers,
                 queueByFilename, ufuncArgs, ufuncKwargs, ufuncFunction=None):
        assert isinstance(maingrid, PixelGrid)
        self.subgrid = None
        self.maingrid = maingrid
        self.inputDatasets = inputDatasets
        self.inputFilenames = inputFilenames
        self.inputOptions = inputOptions
        self.outputFilenames = outputFilenames
        self.outputOptions = outputOptions
        self.vectorDatasets = vectorDatasets
        self.vectorFilenames = vectorFilenames
        self.vectorLayers = vectorLayers
        self.queueByFilename = queueByFilename
        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs
        self.ufuncFunction = ufuncFunction
        self.iblock = 0
        self.nblock = 0

    @property
    def grid(self):
        assert isinstance(self.subgrid, PixelGrid)
        return self.subgrid

    def isFirstBlock(self):
        return self.iblock == 0

    def isLastBlock(self):
        return self.iblock == self.nblock-1

    def getArray(self, name, indicies=None, wavelength=None, overlap=0, dtype=None, scale=None):

        if indicies is None and wavelength is None:
            array = self._getImage(name=name, overlap=overlap, dtype=dtype, scale=scale)
        elif isinstance(indicies, list):
            array = self._getBandSubset(name=name, overlap=overlap, indicies=indicies, dtype=dtype)
        elif isinstance(indicies, int):
            array = self._getBandSubset(name=name, overlap=overlap, indicies=[indicies], dtype=dtype)
        elif isinstance(wavelength, list):
            indicies = [self.findWavebandIndex(name=name, targetWavelength=wl) for wl in wavelength]
            array = self.getArray(name=name, overlap=overlap, indicies=indicies)
        elif isinstance(wavelength, int):
            indicies = self.findWavebandIndex(name=name, targetWavelength=wavelength)
            array = self.getArray(name=name, overlap=overlap, indicies=indicies)
        else:
            raise ValueError('wrong value for indicies or wavelength')

        assert array.ndim == 3
        return array

    def getArrayIterator(self, name, indicies=None, wavelength=None, dtype=None, scale=None):

        for name, i in self.getInputSubnames(name):

            if indicies is None:
                iindicies = None
            elif isinstance(indicies, int):
                iindicies = [indicies]
            elif isinstance(indicies, list):
                iindicies = indicies[i]
            else:
                raise ValueError(
                    'indicies must be a) an integer, b) a list of integers, c) a list of lists of integers, d) a mixture of c) and d), or f) None')

            if wavelength is None:
                iwavelength = None
            elif isinstance(wavelength, (int, float)):
                iwavelength = [wavelength]
            elif isinstance(wavelength, list):
                iwavelength = wavelength
            else:
                raise ValueError(
                    'wavelength must be a) an integer/float, b) a list of integers/floats, or c) None')

            yield self.getArray(name=(name, i), indicies=iindicies, wavelength=iwavelength, dtype=dtype, scale=scale)

    def getInputSubnames(self, name):
        for subname in self._getSubnames(name, self.inputFilenames):
            yield subname

    def getOutputSubnames(self, name):
        for subname in self._getSubnames(name, self.outputFilenames):
            yield subname

    def _getSubnames(self, name, subnames):
        i = 0
        if (name, 0) not in subnames:
            raise KeyError('{name} is not an image list'.format(name=name))

        while True:
            if (name, i) in subnames:
                yield (name, i)
                i += 1
            else:
                break

    def findWavebandIndex(self, name, targetWavelength):
        dataset, options = self._getInputDataset(name)

        wavelength = dataset.getMetadataItem(key='wavelength', domain='ENVI', type=float)
        wavelengthUnits = dataset.getMetadataItem(key='wavelength units', domain='ENVI')

        if wavelength is None or wavelengthUnits is None:
            raise Exception('missing wavelength or wavelength units information')

        wavelength = numpy.array(wavelength)
        if wavelengthUnits.lower() == 'micrometers':
            wavelength *= 1000.
        elif wavelengthUnits.lower() == 'nanometers':
            pass
        else:
            raise Exception('wavelength units must be nanometers or micrometers')

        return int(numpy.argmin(abs(wavelength - wavelength)))

    def _getInputDataset(self, name):
        if name not in self.inputDatasets:
            raise Exception('{name} is not a single image input'.format(name=name))

        if self.inputDatasets[name] is None:
            self.inputDatasets[name] = Open(filename=self.inputFilenames[name])
        return self.inputDatasets[name]

    def _getInputOptions(self, name):
        return self.inputOptions[name]

    def _getImage(self, name, overlap, dtype, scale):

        dataset = self._getInputDataset(name)
        options = self._getInputOptions(name)
        grid = self.grid.pixelBuffer(buffer=overlap)
        if self.grid.equalProjection(dataset.pixelGrid):
            datasetResampled = dataset.translate(dstPixelGrid=grid, dstName='', format='MEM',
                                                 resampleAlg=options['resampleAlg'],
                                                 noData=options['noData'])
        else:
            datasetResampled = dataset.warp(dstPixelGrid=grid, dstName='', format='MEM',
                                            resampleAlg=options['resampleAlg'],
                                            errorThreshold=options['errorThreshold'],
                                            warpMemoryLimit=options['warpMemoryLimit'],
                                            multithread=options['multithread'],
                                            srcNodata=options['noData'])
        array = datasetResampled.readAsArray(dtype=dtype, scale=scale)
        datasetResampled.close()
        return array

    def _getBandSubset(self, name, indicies, overlap, dtype):

        dataset, options = self._getInputDataset(name)
        bandList = [i + 1 for i in indicies]
        grid = self.grid.pixelBuffer(buffer=overlap)
        if self.grid.equalProjection(dataset.pixelGrid):
            datasetResampled = dataset.translate(dstPixelGrid=grid, dstName='', format='MEM',
                                                 bandList=bandList,
                                                 resampleAlg=options['resampleAlg'],
                                                 noData=options['noData'])
        else:
            selfGridReprojected = self.grid.reproject(dataset.pixelGrid)
            selfGridReprojectedWithBuffer = selfGridReprojected.pixelBuffer(buffer=1+overlap)

            datasetClipped = dataset.translate(dstPixelGrid=selfGridReprojectedWithBuffer, dstName='', format='MEM',
                                               bandList=bandList,
                                               noData=options['noData'])

            datasetResampled = datasetClipped.warp(dstPixelGrid=grid, dstName='', format='MEM',
                                                   resampleAlg=options['resampleAlg'],
                                                   errorThreshold=options['errorThreshold'],
                                                   warpMemoryLimit=options['warpMemoryLimit'],
                                                   multithread=options['multithread'],
                                                   srcNodata=options['noData'])
            datasetClipped.close()

        array = datasetResampled.readAsArray(dtype=dtype)
        datasetResampled.close()
        return array

    def _getVectorDataset(self, name):
        if name not in self.vectorDatasets:
            raise Exception('{name} is not a vector input'.format(name=name))

        if self.vectorDatasets[name] is None:
            self.vectorDatasets[name] = OpenLayer(filename=self.vectorFilenames[name], layerNameOrIndex=self.vectorLayers[name])

        return self.vectorDatasets[name]

    def getRasterization(self, name, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filter=None, overlap=0, dtype=numpy.float32, scale=None):
        layer = self._getVectorDataset(name)
        dataset = layer.rasterize(dstPixelGrid=self.grid, eType=NumericTypeCodeToGDALTypeCode(dtype),
                                  initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute, allTouched=allTouched,
                                  filter=filter, dstName='', format='MEM', creationOptions=[])
        array = dataset.readAsArray(scale=scale)
        return array

    def getInputFilename(self, name):
        return self.inputFilenames[name]

    def getOutputFilename(self, name):
        return self.outputFilenames[name]

    def setArray(self, name, array, overlap=0, replace=None, scale=None, dtype=None):

        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)

        if array.ndim == 2:
            array = array[None]

        if overlap > 0:
            array = array[:, overlap:-overlap, overlap:-overlap]

        if replace is not None:
            mask = numpy.isnan(array) if replace[0] is numpy.nan else numpy.equal(array, replace[0])

        if scale is not None:
            array *= scale

        if dtype is not None:
            array = array.astype(dtype)

        if replace is not None:
            array[mask] = replace[1]

        filename = self.getOutputFilename(name)
        self.queueByFilename[filename].put((Writer.WRITE_ARRAY, filename, array, self.grid, self.maingrid, self.outputOptions[name]['format'], self.outputOptions[name]['creationOptions']))

    def setArrayList(self, name, arrays, overlap=0, replace=None, scale=None, dtype=None):

        for (subname, i) in self.getOutputSubnames(name):
            self.setArray(name=(subname, i), array=arrays[i], overlap=overlap,
                          replace=replace[i] if isinstance(replace, list) else replace,
                          scale=scale[i] if isinstance(scale, list) else scale,
                          dtype=dtype[i] if isinstance(dtype, list) else dtype,)

    def setMetadataItem(self, name, key, value, domain):
        filename = self.getOutputFilename(name)
        self.queueByFilename[filename].put((Writer.SET_META, filename, key, value, domain))

    def getMetadataItem(self, name, key, domain):
        dataset = self._getInputDataset(name)
        return dataset.getMetadataItem(key=key, domain=domain)

    def setNoDataValue(self, name, value):
        filename = self.getOutputFilename(name)
        self.queueByFilename[filename].put((Writer.SET_NODATA, filename, value))

    def apply(self, subgrid, iblock, nblock):
        self.iblock = iblock
        self.nblock = nblock
        self.subgrid = subgrid
        return self.ufunc(*self.ufuncArgs, **self.ufuncKwargs)

    def ufunc(self, *args, **kwargs):
        if self.ufuncFunction is None:
            raise NotImplementedError()
        else:
            return self.ufuncFunction(self, *args, **kwargs)


class ApplierControls(object):

    def __init__(self):

        self.setWindowXSize()
        self.setWindowYSize()
        self.setNumThreads()
        self.setNumWriter()
        self.setCreateEnviHeader()
        self.setAutoFootprint()
        self.setAutoResolution()
        self.setProjection()
        self.setReferenceGrid()
        self.setGDALCacheMax()
        self.setGDALSwathSize()
        self.setGDALDisableReadDirOnOpen()
        self.setGDALMaxDatasetPoolSize()
        self.setProgressBar()

    def setProgressBar(self, progressBar=CUIProgress()):
        """
        Set the progress display object. Default is an :class:`~hubdc.progressbar.CUIProgress` object.
        For suppressing outputs use an :class:`~hubdc.progressbar.SilentProgress` object
        """
        self.progressBar = progressBar

    def setWindowXSize(self, windowxsize=256):
        """
        Set the X size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowxsize = windowxsize

    def setWindowYSize(self, windowysize=256):
        """
        Set the Y size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowysize = windowysize

    def setWindowFullSize(self):
        """
        Set the block size to full extent.
        """

        veryLargeNumber = 10**20
        self.setWindowXSize(veryLargeNumber)
        self.setWindowYSize(veryLargeNumber)

    def setNumThreads(self, nworker=None):
        """
        Set the number of pool worker for multiprocessing. Set to None to disable multiprocessing (recommended for debugging).
        """
        self.nworker = nworker

    def setNumWriter(self, nwriter=None):
        """
        Set the number of writer processes. Set to None to disable multiwriting (recommended for debugging).
        """
        self.nwriter = nwriter

    def setCreateEnviHeader(self, createEnviHeader=False):
        """
        Set to True to create additional ENVI header files for all output rasters.
        The header files store all metadata items from the GDAL PAM ENVI domain,
        so that the images can be correctly interpreted by the ENVI software.
        Currently only the native ENVI format and the GTiff format is supported.
        """
        self.createEnviHeader = createEnviHeader

    def setAutoFootprint(self, footprintType=const.FOOTPRINT_UNION):
        """
        Derive extent of the reference pixel grid from input files. Possible options are 'union' or 'intersect'.
        """
        self.footprintType = footprintType

    def setAutoResolution(self, resolutionType=const.RESOLUTION_MINIMUM):
        """
        Derive resolution of the reference pixel grid from input files. Possible options are 'min', 'max' or 'average'.
        """
        self.resolutionType = resolutionType

    def setProjection(self, projection=None):
        """
        Set projection of the reference pixel grid.
        """
        self.projection = projection

    def setReferenceGrid(self, grid=None):
        """
        Set the reference pixel grid. Pass an instance of the :py:class:`~hubdc.model.PixelGrid.PixelGrid` class.
        """
        self.referenceGrid = grid

    def setReferenceImage(self, filename):
        """
        Set an image defining the reference pixel grid.
        """
        self.setReferenceGrid(grid=PixelGrid.fromFile(filename))

    def setGDALCacheMax(self, bytes=100*2**20):
        """
        For details see the `GDAL_CACHEMAX Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_CACHEMAX>`_.
        """
        self.cacheMax = bytes

    def setGDALSwathSize(self, bytes=100*2**20):
        """
        For details see the `GDAL_SWATH_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_SWATH_SIZE>`_.
        """
        self.swathSize = bytes

    def setGDALDisableReadDirOnOpen(self, disable=True):
        """
        For details see the `GDAL_DISABLE_READDIR_ON_OPEN Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_DISABLE_READDIR_ON_OPEN>`_.
        """
        self.disableReadDirOnOpen = disable

    def setGDALMaxDatasetPoolSize(self, nfiles=100):
        """
        For details see the `GDAL_MAX_DATASET_POOL_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_MAX_DATASET_POOL_SIZE>`_.
        """
        self.maxDatasetPoolSize = nfiles

    @property
    def _multiprocessing(self):
        return self.nworker is not None

    @property
    def _multiwriting(self):
        return self._multiprocessing or (self.nwriter is not None)

    def _makeAutoGrid(self, inputs):
        grids = [PixelGrid.fromFile(input.filename) for input in inputs.values()]

        if self.projection is None:
            grid = PixelGrid.fromFile(inputs.values()[0].filename)
            for input in inputs.values():
                if not grid.equalProjection(PixelGrid.fromFile(input.filename)):
                    raise Exception('input projections do not match')
            projection = grid.projection
        else:
            projection = self.projection

        from numpy import array
        xMins, xMaxs, yMins, yMaxs = array([grid.reprojectExtent(targetProjection=projection) for grid in grids]).T
        if self.footprintType == const.FOOTPRINT_UNION:
            xMin = xMins.min()
            xMax = xMaxs.max()
            yMin = yMins.min()
            yMax = yMaxs.max()
        elif self.footprintType == const.FOOTPRINT_INTERSECTION:
            xMin = xMins.max()
            xMax = xMaxs.min()
            yMin = yMins.max()
            yMax = yMaxs.min()
            if xMax <= xMin or yMax <= yMin:
                raise Exception('input extents do not intersect')
        else:
            raise ValueError('unknown footprint type')

        xResList = array([grid.xRes for grid in grids])
        yResList = array([grid.yRes for grid in grids])
        if self.resolutionType == const.RESOLUTION_MINIMUM:
            xRes = xResList.min()
            yRes = yResList.min()
        elif self.resolutionType == const.RESOLUTION_MAXIMUM:
            xRes = xResList.max()
            yRes = yResList.max()
        elif self.resolutionType == const.RESOLUTION_AVERAGE:
            xRes = xResList.mean()
            yRes = yResList.mean()
        else:
            raise ValueError('unknown resolution type')

        return PixelGrid(projection=projection, xRes=xRes, yRes=yRes, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
