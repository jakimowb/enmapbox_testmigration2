"""
Basic tools for setting up a function to be applied over a raster processing chain.
The :class:`~hubdc.applier.Applier` class is the main point of entry in this module.

See :doc:`ApplierExamples` for more information.

"""

from __future__ import print_function
import sys
from multiprocessing import Pool
from timeit import default_timer as now
import numpy
from osgeo import gdal
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
from hubdc.model import Open, OpenLayer, CreateFromArray
from hubdc import const
from hubdc.writer import Writer, WriterProcess, QueueMock
from hubdc.model import PixelGrid
from hubdc.progressbar import CUIProgressBar, SilentProgressBar, ProgressBar


class Applier(object):

    def __init__(self):
        self.inputs = dict()
        self.vectors = dict()
        self.outputs = dict()
        self.controls = ApplierControls()
        self.grid = None

    def setInput(self, name, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=1000 * 2 ** 20, multithread=True):
        """
        Define a new input raster named ``name``, that is located at ``filename``.

        :param name: name of the raster
        :type name:
        :param filename: filename of the raster
        :type filename:
        :param noData: overwrite the noData value of the raster
        :type noData: None or number
        :param resampleAlg: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type resampleAlg:
        :param errorThreshold: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type errorThreshold:
        :param warpMemoryLimit: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type warpMemoryLimit:
        :param multithread: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type multithread:
        """
        self.inputs[name] = ApplierInput(filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setVector(self, name, filename, layer=0):
        """
        Define a new input vector layer named ``name``, that is located at ``filename``.

        :param name: name of the vector layer
        :type name:
        :param filename: filename of the vector layer
        :type filename:
        :param layer: specify the layer to be used from the vector datasource
        :type layer: index or name
        """
        self.vectors[name] = ApplierVector(filename=filename, layer=layer)

    def setInputList(self, name, filenames, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=1000 * 2 ** 20, multithread=True):
        """
        Define a new list of input rasters named ``name``, that are located at the ``filenames``.

        :param name: name of the raster list
        :type name:
        :param filenames: list of filenames
        :type filenames:
        :param noData: overwrite the noData value of all rasters
        :type noData: None or number
        :param resampleAlg: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type resampleAlg:
        :param errorThreshold: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type errorThreshold:
        :param warpMemoryLimit: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type warpMemoryLimit:
        :param multithread: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :type multithread:
        """

        for i, filename in enumerate(filenames):
            self.setInput(name=(name, i), filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setOutput(self, name, filename, format='GTiff', creationOptions=None):
        """
        Define a new output raster named ``name``, that will be created at ``filename``.

        :param name: name of the raster
        :type name:
        :param filename: filename of the raster
        :type filename:
        :param format: see `GDAL Raster Formats <http://www.gdal.org/formats_list.html>`_
        :type format:
        :param creationOptions: see the `Creation Options` section for a specific `GDAL Raster Format`.
                                Predefined default creation options are used if set to ``None``, see
                                :meth:`hubdc.io.ApplierOutput.getDefaultCreationOptions` for details.
        :type creationOptions: list of strings
        """
        self.outputs[name] = ApplierOutput(filename=filename, format=format, creationOptions=creationOptions)

    def setOutputList(self, name, filenames, format='GTiff', creationOptions=None):
        """
        Define a new list of output rasters named ``name``, that will be created at ``filenames``.

        :param name: name of the raster list
        :type name:
        :param filenames: list of filenames
        :type filenames:
        :param format: see `GDAL Raster Formats <http://www.gdal.org/formats_list.html>`_
        :type format:
        :param creationOptions: see the `Creation Options` section for a specific `GDAL Raster Format`.
                                Predefined default creation options are used if set to ``None``, see
                                :meth:`hubdc.io.ApplierOutput.getDefaultCreationOptions` for details.
        :type creationOptions: list of strings
        """
        for i, filename in enumerate(filenames):
            self.setOutput(name=(name, i), filename=filename, format=format, creationOptions=creationOptions)

    def apply(self, operator, description=None, *ufuncArgs, **ufuncKwargs):
        """
        Applies the ``operator`` blockwise over a raster processing chain and returns a list of results, one for each block.

        The ``operator`` must be a subclass of :class:`~hubdc.applier.ApplierOperator` and needs to implement the
        :meth:`~hubdc.applier.ApplierOperator.ufunc` method to specify the image processing.

        For example::

            class MyOperator(ApplierOperator):
                def ufunc(self):
                    # process the data

            applier.apply(operator=MyOperator)

        or::

            def my_ufunc(operator):
                # process the data

            applier.apply(operator=my_ufunc)


        :param operator: applier operator
        :type operator: :class:`~hubdc.applier.ApplierOperator` or function
        :param description: short description that is displayed on the progress bar
        :type description:
        :param ufuncArgs: additional arguments that will be passed to the operators ufunc() method.
        :type ufuncArgs:
        :param ufuncKwargs: additional keyword arguments that will be passed to the operators ufunc() method.
        :type ufuncKwargs:
        :return: list of results, one for each processed block
        """

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
        if description is None:
            description = operator.__name__

        self.controls.progressBar.setLabelText('start {}'.format(description))

        self._runCreateGrid()
        self._runInitWriters()
        self._runInitPool()
        results = self._runProcessSubgrids()
        self._runClose()

        self.controls.progressBar.setLabelText('100%')
        s = (now()-runT0); m = s/60; h = m/60

        self.controls.progressBar.setLabelText('done {description} in {s} sec | {m}  min | {h} hours'.format(description=description, s=int(s), m=round(m, 2), h=round(h, 2))); sys.stdout.flush()
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

        self.controls.progressBar.setTotalSteps(len(subgrids))

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
    applier = None
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
        cls.applier = applier
        cls.inputDatasets = dict()
        cls.inputOptions = dict()
        cls.inputFilenames = dict()
        cls.outputFilenames = dict()
        cls.outputOptions = dict()
        cls.vectorDatasets = dict()
        cls.vectorFilenames = dict()
        cls.vectorLayers = dict()

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
            cls.vectorLayers[key] = applierVector.layer

        # create operator
        cls.operator = applier.ufuncClass(maingrid=applier.grid,
                                          inputDatasets=cls.inputDatasets, inputFilenames=cls.inputFilenames, inputOptions=cls.inputOptions,
                                          outputFilenames=cls.outputFilenames, outputOptions=cls.outputOptions,
                                          vectorDatasets=cls.vectorDatasets, vectorFilenames=cls.vectorFilenames, vectorLayers=cls.vectorLayers,
                                          queueByFilename=applier.queueByFilename,
                                          progressBar=applier.controls.progressBar,
                                          ufuncFunction=applier.ufuncFunction, ufuncArgs=applier.ufuncArgs, ufuncKwargs=applier.ufuncKwargs)

    @classmethod
    def processSubgrid(cls, i, n, subgrid):
        cls.operator.progressBar.setProgress(i)
        return cls.operator._apply(subgrid=subgrid, iblock=i, nblock=n)

def _pickableWorkerProcessSubgrid(**kwargs):
    return _Worker.processSubgrid(**kwargs)

def _pickableWorkerInitialize(*args):
    return _Worker.initialize(*args)

class ApplierInput(object):
    """
    Data structure for storing input specifications defined by :meth:`hubdc.applier.Applier.setInput`.
    For internally use only.
    """
    def __init__(self, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.125, warpMemoryLimit=100*2**20, multithread=False):
        self.filename = filename
        self.options = {'noData' : noData,
                        'resampleAlg' : resampleAlg,
                        'errorThreshold' : errorThreshold,
                        'warpMemoryLimit' : warpMemoryLimit,
                        'multithread' : multithread}

class ApplierOutput(object):
    """
    Data structure for storing output specifications defined by :meth:`hubdc.applier.Applier.setOutput`.
    For internally use only.
    """

    @staticmethod
    def getDefaultCreationOptions(format):
        if format.lower() == 'ENVI'.lower():
            return ['INTERLEAVE=BSQ']
        elif format.lower() == 'GTiff'.lower():
            return ['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES',
                    'BLOCKXSIZE=256', 'BLOCKYSIZE=256',
                    'SPARSE_OK=TRUE', 'BIGTIFF=YES']
        return []

    def __init__(self, filename, format='GTiff', creationOptions=None):
        if creationOptions is None:
            creationOptions = self.getDefaultCreationOptions(format)
        self.filename = filename
        self.options = {'format': format, 'creationOptions': creationOptions}

class ApplierVector(object):
    """
    Data structure for storing input specifications defined by :meth:`hubdc.applier.Applier.setVector`.
    For internally use only.
    """

    def __init__(self, filename, layer=0):
        self.filename = filename
        self.layer = layer

class ApplierOperator(object):
    """
    This is the baseclass for an user defined applier operator.
    For details on user defined operators see :meth:`hubdc.applier.Applier.apply`
    """

    def __init__(self, maingrid, inputDatasets, inputFilenames, inputOptions,
                 outputFilenames, outputOptions,
                 vectorDatasets, vectorFilenames, vectorLayers,
                 progressBar, queueByFilename, ufuncArgs, ufuncKwargs, ufuncFunction=None):
        assert isinstance(maingrid, PixelGrid)
        self._grid = None
        self._maingrid = maingrid
        self._inputDatasets = inputDatasets
        self._inputFilenames = inputFilenames
        self._inputOptions = inputOptions
        self._outputFilenames = outputFilenames
        self._outputOptions = outputOptions
        self._vectorDatasets = vectorDatasets
        self._vectorFilenames = vectorFilenames
        self._vectorLayers = vectorLayers
        self._queueByFilename = queueByFilename
        self._progressBar = progressBar
        self._ufuncArgs = ufuncArgs
        self._ufuncKwargs = ufuncKwargs
        self._ufuncFunction = ufuncFunction
        self._iblock = 0
        self._nblock = 0

    @property
    def grid(self):
        """
        Returns the :class:`~hubdc.applier.PixelGrid` object of the currently processed block.
        """
        assert isinstance(self._grid, PixelGrid)
        return self._grid

    @property
    def progressBar(self):
        """
        Returns the progress bar.
        """
        assert isinstance(self._progressBar, ProgressBar)
        return self._progressBar

    def isFirstBlock(self):
        """
        Returns wether or not the current block is the first one.
        """
        return self._iblock == 0

    def isLastBlock(self):
        """
        Returns wether or not the current block is the last one.
        """
        return self._iblock == self._nblock - 1

    def getArray(self, name, indicies=None, wavelengths=None, overlap=0, dtype=None, scale=None):
        """
        Returns the input raster image data of the current block in form of a 3-d numpy array.
        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setInput`.

        :param name: input raster name
        :type name:
        :param indicies: subset image bands by a list of indicies
        :type indicies:
        :param wavelengths: subset image bands by a list of wavelengths specified in nanometers;
                            see :meth:`~hubdc.applier.ApplierOperator.findWaveband` for details
        :type wavelengths:
        :param overlap: the amount of margin (number of pixels) added to the image data block in each direction, so that the blocks will overlap; this is important for spatial operators like filters.
        :type overlap:
        :param dtype: convert image data to given numpy data type (this is done before the data is scaled)
        :type dtype:
        :param scale: scale image data by given scale factor (this is done after type conversion)
        :type scale:
        """

        if indicies is None and wavelengths is None:
            array = self._getImage(name=name, overlap=overlap, dtype=dtype, scale=scale)
        elif isinstance(indicies, list):
            array = self._getBandSubset(name=name, overlap=overlap, indicies=indicies, dtype=dtype)
        elif isinstance(indicies, int):
            array = self._getBandSubset(name=name, overlap=overlap, indicies=[indicies], dtype=dtype)
        elif isinstance(wavelengths, list):
            indicies = [self.findWaveband(name=name, wavelength=wl) for wl in wavelengths]
            array = self.getArray(name=name, overlap=overlap, indicies=indicies)
        elif isinstance(wavelengths, int):
            indicies = self.findWaveband(name=name, wavelength=wavelengths)
            array = self.getArray(name=name, overlap=overlap, indicies=indicies)
        else:
            raise ValueError('wrong value for indicies or wavelength')

        assert array.ndim == 3
        return array

    def getDerivedArray(self, name, ufunc, overlap=0):

        return self._getDerivedImage(name=name, ufunc=ufunc, overlap=overlap)

    def getInputListSubnames(self, name):
        """
        Returns an iterator over the subnames of a input raster list.
        Such subnames can be used with single input raster methods like :meth:`~hubdc.applier.ApplierOperator.getArray`
        or :meth:`~hubdc.applier.ApplierOperator.getMetadataItem`.
        """
        for subname in self._getSubnames(name, self._inputFilenames):
            yield subname

    def getOutputListSubnames(self, name):
        """
        Returns an iterator over the subnames of a output raster list.
        Such subnames can be used with single output raster methods like :meth:`~hubdc.applier.ApplierOperator.setArray`
        or :meth:`~hubdc.applier.ApplierOperator.setMetadataItem`.
        """

        for subname in self._getSubnames(name, self._outputFilenames):
            yield subname

    def getInputListLen(self, name):
        """
        Returns the lenth of an input raster list.
        """
        return len(list(self.getInputListSubnames(name)))

    def getOutputListLen(self, name):
        """
        Returns the lenth of an output raster list.
        """
        return len(list(self.getOutputListSubnames(name)))

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

    def findWaveband(self, name, wavelength):
        """
        Returns the image band index of the band that is located nearest to target wavelength specified in nanometers.

        The wavelength information is taken from the ENVI metadata domain.
        An exception is thrown if the ``wavelength`` and ``wavelength units`` metadata items are not correctly specified.
        """

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
        if name not in self._inputDatasets:
            raise Exception('{name} is not a single image input'.format(name=name))

        if self._inputDatasets[name] is None:
            self._inputDatasets[name] = Open(filename=self._inputFilenames[name])
        return self._inputDatasets[name]

    def _getInputOptions(self, name):
        return self._inputOptions[name]

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

    def _getDerivedImage(self, name, ufunc, overlap):

        dataset = self._getInputDataset(name)
        options = self._getInputOptions(name)
        grid = self.grid.pixelBuffer(buffer=overlap)

        # create tmp dataset
        gridInSourceProjection = grid.reproject(dataset.pixelGrid)
        tmpDataset = dataset.translate(dstPixelGrid=gridInSourceProjection, dstName='', format='MEM',
                                       noData=options['noData'])
        tmpArray = tmpDataset.readAsArray()
        derivedArray = ufunc(tmpArray)
        derivedDataset = CreateFromArray(pixelGrid=gridInSourceProjection, array=derivedArray,
                                         dstName='', format='MEM', creationOptions=[])

        tmpname = '_tmp_derived'
        self._inputDatasets[tmpname] = derivedDataset
        self._inputOptions[tmpname] = options
        array = self.getArray(name=tmpname, overlap=overlap)
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
        if name not in self._vectorDatasets:
            raise Exception('{name} is not a vector input'.format(name=name))

        if self._vectorDatasets[name] is None:
            self._vectorDatasets[name] = OpenLayer(filename=self._vectorFilenames[name], layerNameOrIndex=self._vectorLayers[name])

        return self._vectorDatasets[name]

    def getRasterization(self, name, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None, overlap=0, dtype=numpy.float32, scale=None):
        """
        Returns the vector rasterization of the current block in form of a 3-d numpy array.
        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setVector`.

        :param name: vector name
        :type name:
        :param initValue: value to pre-initialize the output array
        :type initValue:
        :param burnValue: value to burn into the output array for all objects; exclusive with ``burnAttribute``
        :type burnValue:
        :param burnAttribute: identifies an attribute field on the features to be used for a burn-in value; exclusive with ``burnValue``
        :type burnAttribute:
        :param allTouched: whether to enable that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon
        :type allTouched:
        :param filterSQL: set an SQL WHERE clause which will be used to filter vector features
        :type filterSQL:
        :param overlap: the amount of margin (number of pixels) added to the image data block in each direction, so that the blocks will overlap; this is important for spatial operators like filters.
        :type overlap:
        :param dtype: convert output array to given numpy data type (this is done before the data is scaled)
        :type dtype:
        :param scale: scale output array by given scale factor (this is done after type conversion)
        :type scale:
        """
        layer = self._getVectorDataset(name)
        dataset = layer.rasterize(dstPixelGrid=self.grid, eType=NumericTypeCodeToGDALTypeCode(dtype),
                                  initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute, allTouched=allTouched,
                                  filter=filterSQL, dstName='', format='MEM', creationOptions=[])
        array = dataset.readAsArray(scale=scale)
        return array

    def getInputFilename(self, name):
        """
        Returns the input image filename
        """
        return self._inputFilenames[name]

    def getOutputFilename(self, name):
        """
        Returns the output image filename
        """
        return self._outputFilenames[name]

    def getVectorFilename(self, name):
        """
        Returns the vector layer filename.
        """
        return self._vectorFilenames[name]

    def setArray(self, name, array, overlap=0, replace=None, scale=None, dtype=None):
        """
        Write data to an output raster image.
        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setOutput`.

        :param name:  output raster name
        :type name:
        :param array: 3-d or 2-d numpy array to be written
        :type array:
        :param overlap: the amount of margin (number of pixels) to be removed from the image data block in each direction;
                        this is useful when the overlap keyword was also used with :meth:`~hubdc.applier.ApplierOperator.getArray`
        :type overlap:
        :param replace: tuple of ``(sourceValue, targetValue)`` values; replace all occurances of ``sourceValue`` inside the array with ``targetValue``;
                        this is done after type conversion and scaling)
        :type replace:
        :param scale: scale array data by given scale factor (this is done after type conversion)
        :type scale:
        :param dtype: convert array data to given numpy data type (this is done before the data is scaled)
        :type dtype:
        """

        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)

        if array.ndim == 2:
            array = array[None]

        if overlap > 0:
            array = array[:, overlap:-overlap, overlap:-overlap]

        if replace is not None:
            if replace[0] is numpy.nan:
                mask = numpy.isnan(array)
            else:
                mask = numpy.equal(array, replace[0])

        if scale is not None:
            array *= scale

        if dtype is not None:
            array = array.astype(dtype)

        if replace is not None:
            array[mask] = replace[1]

        filename = self.getOutputFilename(name)
        self._queueByFilename[filename].put((Writer.WRITE_ARRAY, filename, array, self.grid, self._maingrid, self._outputOptions[name]['format'], self._outputOptions[name]['creationOptions']))

    def setMetadataItem(self, name, key, value, domain):
        """
        Set the metadata item to an output raster image.

        :param name: output image name
        :type name:
        :param key: metadata item name
        :type key:
        :param value: metadata item value
        :type value:
        :param domain: metadata item domain
        :type domain:
        """
        filename = self.getOutputFilename(name)
        self._queueByFilename[filename].put((Writer.SET_META, filename, key, value, domain))

    def getMetadataItem(self, name, key, domain):
        """
        Returns the metadata item of an input raster image.

        :param name: output raster name
        :type name:
        :param key: metadata item name
        :type key:
        :param value: metadata item value
        :type value:
        :param domain: metadata item domain
        :type domain:
        """
        dataset = self._getInputDataset(name)
        return dataset.getMetadataItem(key=key, domain=domain)

    def setNoDataValue(self, name, value):
        """
        Set the no data value of an output raster image.
        """
        filename = self.getOutputFilename(name)
        self._queueByFilename[filename].put((Writer.SET_NODATA, filename, value))

    def _apply(self, subgrid, iblock, nblock):
        self._iblock = iblock
        self._nblock = nblock
        self._grid = subgrid
        return self.ufunc(*self._ufuncArgs, **self._ufuncKwargs)

    def ufunc(self, *args, **kwargs):
        """
        Overwrite this method to specify the image processing.

        See :doc:`ApplierExamples` for more information.
        """
        if self._ufuncFunction is None:
            raise NotImplementedError()
        else:
            return self._ufuncFunction(self, *args, **kwargs)


class ApplierControls(object):

    def __init__(self):

        self.setWindowXSize()
        self.setWindowYSize()
        self.setNumThreads()
        self.setNumWriter()
        self.setCreateEnviHeader()
        self.setAutoFootprint()
        self.setAutoResolution()
        self.setResolution()
        self.setFootprint()
        self.setProjection()
        self.setReferenceGrid()
        self.setGDALCacheMax()
        self.setGDALSwathSize()
        self.setGDALDisableReadDirOnOpen()
        self.setGDALMaxDatasetPoolSize()
        self.setProgressBar()

    def setProgressBar(self, progressBar=None):
        """
        Set the progress display object. Default is an :class:`~hubdc.progressbar.CUIProgress` object.
        For suppressing outputs use an :class:`~hubdc.progressbar.SilentProgress` object
        """
        if progressBar is None:
            progressBar = CUIProgressBar()
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

    def setResolution(self, xRes=None, yRes=None):
        """
        Set resolution of the reference pixel grid.
        """
        self.xRes = xRes
        self.yRes = yRes

    def setFootprint(self, xMin=None, xMax=None, yMin=None, yMax=None):
        """
        Set spatial footprint of the reference pixel grid.
        """
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax

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

        projection = self._deriveProjection(grids)
        xMin, xMax, yMin, yMax = self._deriveFootprint(grids, projection)
        xRes, yRes = self._deriveResolution(grids)
        return PixelGrid(projection=projection, xRes=xRes, yRes=yRes, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)

    def _deriveProjection(self, grids):

        if self.projection is None:
            for grid in grids:
                if not grid.equalProjection(grids[0]):
                    raise Exception('input projections do not match')
            projection = grids[0].projection
        else:
            projection = self.projection
        return projection

    def _deriveFootprint(self, grids, projection):

        if None in [self.xMin, self.xMax, self.yMin, self.yMax]:

            xMins, xMaxs, yMins, yMaxs = numpy.array([grid.reprojectExtent(targetProjection=projection) for grid in grids]).T
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

        else:
            xMin, xMax, yMin, yMax = self.xMin, self.xMax, self.yMin, self.yMax

        return xMin, xMax, yMin,yMax

    def _deriveResolution(self, grids):

        if self.xRes is None or self.yRes is None:
            xResList = numpy.array([grid.xRes for grid in grids])
            yResList = numpy.array([grid.yRes for grid in grids])
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
        else:
            xRes = self.xRes
            yRes = self.yRes

        return xRes, yRes
