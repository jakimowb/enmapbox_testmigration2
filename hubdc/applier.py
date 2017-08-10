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

DEFAULT_INPUT_RESAMPLEALG = gdal.GRA_NearestNeighbour
DEFAULT_INPUT_ERRORTHRESHOLD = 0.
DEFAULT_INPUT_WARPMEMORYLIMIT = 100*2**20
DEFAULT_INPUT_MULTITHREAD = False

class Applier(object):

    def __init__(self, controls=None):
        self.inputs = dict()
        self.vectors = dict()
        self.outputs = dict()
        self.controls = controls if controls is not None else ApplierControls()
        self.grid = None

    def setInput(self, name, filename, noData=None,
                 resampleAlg=DEFAULT_INPUT_RESAMPLEALG,
                 errorThreshold=DEFAULT_INPUT_ERRORTHRESHOLD,
                 warpMemoryLimit=DEFAULT_INPUT_WARPMEMORYLIMIT,
                 multithread=DEFAULT_INPUT_MULTITHREAD, options=None):
        """
        Define a new input raster named ``name``, that is located at ``filename``.

        :param name: name of the raster
        :param filename: filename of the raster
        :param noData: overwrite the noData value of the raster
        :param resampleAlg: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :param errorThreshold: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :param warpMemoryLimit: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :param multithread: see `GDAL WarpOptions <http://gdal.org/python/osgeo.gdal-module.html#WarpOptions>`_
        :param options: set all the above options via an :class:`~hubdc.applier.ApplierInputOptions` object
        """
        self.inputs[name] = ApplierInput(filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread, options=options)

    def setVector(self, name, filename, layer=0):
        """
        Define a new input vector layer named ``name``, that is located at ``filename``.

        :param name: name of the vector layer
        :param filename: filename of the vector layer
        :type filename:
        :param layer: specify the layer to be used from the vector datasource
        """
        self.vectors[name] = ApplierVector(filename=filename, layer=layer)

    def setInputList(self, name, filenames, noData=None,
                     resampleAlg = DEFAULT_INPUT_RESAMPLEALG,
                     errorThreshold = DEFAULT_INPUT_ERRORTHRESHOLD,
                     warpMemoryLimit = DEFAULT_INPUT_WARPMEMORYLIMIT,
                     multithread = DEFAULT_INPUT_MULTITHREAD, options = None):

        """
        Define a new list of input rasters named ``name``, that are located at the ``filenames``.
        For each filename a new input raster named ``(name, i)`` is added using :meth:`hubdc.applier.Applier.setInput`.
        """

        for i, filename in enumerate(filenames):
            self.setInput(name=(name, i), filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread, options=options)

    def setOutput(self, name, filename, format=None, creationOptions=None):
        """
        Define a new output raster named ``name``, that will be created at ``filename``.

        :param name: name of the raster
        :param filename: filename of the raster
        :param format: see `GDAL Raster Formats <http://www.gdal.org/formats_list.html>`_
        :param creationOptions: see the `Creation Options` section for a specific `GDAL Raster Format`.
                                Predefined default creation options are used if set to ``None``, see
                                :meth:`hubdc.applier.ApplierOutput.getDefaultCreationOptions` for details.
        :type creationOptions: list of strings
        """
        self.outputs[name] = ApplierOutput(filename=filename, format=format, creationOptions=creationOptions)

    def setOutputList(self, name, filenames, format=None, creationOptions=None):
        """
        Define a new list of output rasters named ``name``, that are located at the ``filenames``.
        For each filename a new output raster named ``(name, i)`` is added using :meth:`hubdc.applier.Applier.setOutput`.
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
        :param ufuncArgs: additional arguments that will be passed to the operators ufunc() method.
        :param ufuncKwargs: additional keyword arguments that will be passed to the operators ufunc() method.
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

        self._runCreateGrid()
        self.controls.progressBar.setLabelText('start {} [{}x{}]'.format(description, self.grid.xSize, self.grid.ySize))
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

        if self.controls._multiwriting:
            for writer in self.writers:
                writer.queue.put([Writer.CLOSE_DATASETS, self.controls.createEnviHeader])
                writer.queue.put([Writer.CLOSE_WRITER, None])
                writer.join()
        else:
            self.queueMock.put([Writer.CLOSE_DATASETS, self.controls.createEnviHeader])

class _Worker(object):
    """
    For internal use only.
    """

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

class ApplierInputOptions(object):

    def __init__(self, noData=None,
                 resampleAlg=DEFAULT_INPUT_RESAMPLEALG,
                 errorThreshold=DEFAULT_INPUT_ERRORTHRESHOLD,
                 warpMemoryLimit=DEFAULT_INPUT_WARPMEMORYLIMIT,
                 multithread=DEFAULT_INPUT_MULTITHREAD):

        self.noData = noData
        self.resampleAlg = resampleAlg
        self.errorThreshold = errorThreshold
        self.warpMemoryLimit = warpMemoryLimit
        self.multithread = multithread

class ApplierInput(object):
    """
    Data structure for storing input specifications defined by :meth:`hubdc.applier.Applier.setInput`.
    For internal use only.
    """
    def __init__(self, filename, noData=None, options=None,
                 resampleAlg=DEFAULT_INPUT_RESAMPLEALG,
                 errorThreshold=DEFAULT_INPUT_ERRORTHRESHOLD,
                 warpMemoryLimit=DEFAULT_INPUT_WARPMEMORYLIMIT,
                 multithread=DEFAULT_INPUT_MULTITHREAD):

        self.filename = filename

        if options is not None:
            assert isinstance(options, ApplierInputOptions)
            self.options = options.__dict__
        else:
            self.options = {'noData' : noData,
                            'resampleAlg' : resampleAlg,
                            'errorThreshold' : errorThreshold,
                            'warpMemoryLimit' : warpMemoryLimit,
                            'multithread' : multithread}

class ApplierOutput(object):
    """
    Data structure for storing output specifications defined by :meth:`hubdc.applier.Applier.setOutput`.
    For internal use only.
    """

    DEFAULT_FORMAT = 'ENVI'

    @staticmethod
    def getDefaultCreationOptions(format):
        if format.lower() == 'ENVI'.lower():
            return ['INTERLEAVE=BSQ']
        elif format.lower() == 'GTiff'.lower():
            return ['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES',
                    'BLOCKXSIZE=256', 'BLOCKYSIZE=256',
                    'SPARSE_OK=TRUE', 'BIGTIFF=YES']
        return []

    def __init__(self, filename, format=None, creationOptions=None):

        if format is None:
            format = self.DEFAULT_FORMAT
        if creationOptions is None:
            creationOptions = self.getDefaultCreationOptions(format)
        self.filename = filename
        self.options = {'format': format, 'creationOptions': creationOptions}

class ApplierVector(object):
    """
    Data structure for storing input specifications defined by :meth:`hubdc.applier.Applier.setVector`.
    For internal use only.
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

    def getSample(self, array, mask):
        """
        Returns a data sample taken from ``array`` at locations given by ``mask``.

        :param array: data array [n, y, x] to be sampled from
        :param mask: boolean mask array [1, y, x] indicating the locations to be sampled
        :return: data sample [n, masked]
        """
        assert isinstance(array, numpy.ndarray) and array.ndim == 3
        assert isinstance(mask, numpy.ndarray) and mask.ndim == 3 and mask.shape[0] == 1
        sample = array[:, mask[0]]
        assert sample.ndim == 2
        return sample

    def setSample(self, sample, array, mask):
        """
        Sets a data sample given by ``sample`` to ``array`` at locations given by ``mask``.

        :param sample: data sample [n, masked]
        :param array: data array [n, y, x] to be updated
        :param mask: boolean mask array [1, y, x] indicating the locations to be updated
        """
        assert isinstance(array, numpy.ndarray) and array.ndim == 3
        assert isinstance(mask, numpy.ndarray) and mask.ndim == 3 and mask.shape[0] == 1
        array[:, mask[0]] = sample

    def applySampleFunction(self, inarray, outarray, mask, ufunc):
        """
        Shortcut for :meth:`hubdc.applier.Applier.getSample` -> ufunc() -> :meth:`hubdc.applier.Applier.setSample` pipeline.
        Ufunc must accept and return a valid data sample [n, masked].
        """
        if numpy.any(mask):
            sample = self.getSample(array=inarray, mask=mask)
            result = ufunc(sample)
            self.setSample(sample=result, array=outarray, mask=mask)

    def getFull(self, value, bands=1, dtype=None, overlap=0):
        return numpy.full(shape=(bands, self.grid.ySize+2*overlap, self.grid.xSize+2*overlap),
                          fill_value=value, dtype=dtype)

    def getArray(self, name, indicies=None, overlap=0, dtype=None, scale=None):
        """
        Returns the input raster image data of the current block in form of a 3-d numpy array.
        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setInput`.

        :param name: input raster name
        :param indicies: subset image bands by a list of indicies
        :param overlap: the amount of margin (number of pixels) added to the image data block in each direction, so that the blocks will overlap; this is important for spatial operators like filters.
        :param dtype: convert image data to given numpy data type (this is done before the data is scaled)
        :param scale: scale image data by given scale factor (this is done after type conversion)
        """

        if indicies is None:
            array = self._getImage(name=name, overlap=overlap, dtype=dtype, scale=scale)
        elif isinstance(indicies, (list, tuple)):
            array = self._getBandSubset(name=name, overlap=overlap, indicies=indicies, dtype=dtype)
        else:
            raise ValueError('wrong value for indicies or wavelength')

        assert isinstance(array, numpy.ndarray)
        assert array.ndim == 3
        return array

    def getMaskArray(self, name, noData=None, ufunc=None, array=None, overlap=0):
        """
        Returns a boolean data/noData mask for an input raster image in form of a 3-d numpy array.
        Pixels that are equal to the image no data value are set to False, all other pixels are set to True.
        In case of a multiband image, the final pixel mask value is False if it was False in all of the bands.

        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setInput`.

        :param name: input raster name
        :param noData: default no data value to use if the image has no no data value specified
        :param ufunc: user function to mask out further pixels,
                      e.g. ``ufunc = lambda array: array > 0.5`` will additionally mask out all pixels that have values larger than 0.5
        :param array: pass in the data array directly if it was already loaded
        :param overlap: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        :param ufunc: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        :return:
        :rtype:
        """

        # read array data if needed
        noData = self.getNoDataValue(name, default=noData)
        if (noData is not None) or (ufunc is not None):
            if array is None:
                array = self.getArray(name, overlap=overlap)

        # create noData mask
        if noData is None:
            valid = self.getFull(value=True, bands=1)
        else:
            valid = numpy.any(array != noData, axis=0, keepdims=True)

        # update noData mask with ufunc mask
        if ufunc is not None:
            numpy.logical_and(valid, numpy.any(ufunc(array), axis=0, keepdims=True), out=valid)

        return valid

    def getWavebandArray(self, name, wavelengths, linear=False, overlap=0, dtype=None, scale=None):
        """
        Returns an image band subset like :meth:`~hubdc.applier.ApplierOperator.getArray` with specified ``indicies``,
        but instead of specifying the bands directly, specify a list of target wavelength.

        :param name: input raster name
        :param wavelengths: list of target wavelengths specified in nanometers
        :param linear: if set to True, linearly interpolated wavebands are returned instead of nearest neighbour wavebands.
        :param overlap: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        :param dtype: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        :param scale: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        """

        if not linear:

            indicies = [index for index, distance in [self.findWavelength(name=name, wavelength=wavelength) for wavelength in wavelengths]]
            array = self.getArray(name=name, overlap=overlap, indicies=indicies, dtype=dtype, scale=scale)

        else:

            tmp = [self.findWavelengthNeighbours(name=name, wavelength=wavelength) for wavelength in wavelengths]
            leftIndicies, leftWeights, rightIndicies, rightWeights = zip(*tmp)

            leftArray = lambda : self.getArray(name=name, overlap=overlap, indicies=leftIndicies, dtype=dtype, scale=scale)
            rightArray = lambda : self.getArray(name=name, overlap=overlap, indicies=rightIndicies, dtype=dtype, scale=scale)

            array = leftArray() * numpy.array(leftWeights).reshape((-1,1,1))
            array += rightArray() * numpy.array(rightWeights).reshape((-1,1,1))


        assert array.ndim == 3
        return array

    def getDerivedArray(self, name, ufunc, resampleAlg=gdal.GRA_Average, overlap=0):
        """
        Returns input raster image data like :meth:`~hubdc.applier.ApplierOperator.getArray`,
        but instead of returning the data directly, a user defined function is applied to it.
        Note that the user function is applied before resampling takes place.
        """
        return self._getDerivedImage(name=name, ufunc=ufunc, resampleAlg=resampleAlg, overlap=overlap)

    def getCategoricalFractionArray(self, name, ids, index=0, overlap=0):
        """
        Returns input raster band data like :meth:`~hubdc.applier.ApplierOperator.getArray`,
        but instead of returning the data directly, aggregated pixel fractions for the given categories (i.e. ``ids``)
        are returned.

        :param name: categorical input raster image
        :param ids: categories to be considered
        :param index: band index for specifying which image band to be used
        :param overlap: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        """

        ufunc = lambda array: numpy.stack(numpy.float32(array[index] == id) for id in ids)
        return self.getDerivedArray(name=name, ufunc=ufunc, overlap=overlap, resampleAlg=gdal.GRA_Average)

    def getCategoricalArray(self, name, ids, noData=0, minOverallCoverage=0., minWinnerCoverage=0., index=0, overlap=0):
        """
        Returns input raster band data like :meth:`~hubdc.applier.ApplierOperator.getArray`,
        but instead of returning the data directly, the category array of maximum aggregated pixel fraction for the given categories (i.e. ``ids``)
        is returned.

        :param name:  categorical input raster image
        :param ids: categories to be considered
        :param noData: no data value for masked pixels
        :param minOverallCoverage: mask out pixels where the overall coverage (regarding to the given categories ``ids``) is less than this threshold
        :param minWinnerCoverage: mask out pixels where the winner category coverage is less than this threshold
        :param index: band index for specifying which image band to be used
        :param overlap: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        """
        fractions = self.getCategoricalFractionArray(name=name, ids=ids, index=index, overlap=overlap)
        categories = numpy.array(ids)[numpy.argmax(fractions, axis=0)[None]]
        if noData is not None:
            invalid = False
            if minOverallCoverage > 0:
                invalid += numpy.sum(fractions, axis=0, keepdims=True) < minOverallCoverage
            if minWinnerCoverage > 0:
                invalid += numpy.max(fractions, axis=0, keepdims=True) < minWinnerCoverage
            categories[invalid] = noData
        assert categories.ndim == 3
        return categories

    def getProbabilityArray(self, name, overlap=0):
        """
        Like :meth:`~hubdc.applier.ApplierOperator.getCategoricalFractionArray`, but all category related information is
        implicitly taken from the class definition metadata.

        :param name: classification input raster image
        :param overlap: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        """

        classes, classNames, classLookup = self.getMetadataClassDefinition(name=name)
        ids = range(1, classes+1)
        return self.getCategoricalFractionArray(name=name, ids=ids, index=0, overlap=overlap)

    def getClassificationArray(self, name, minOverallCoverage=0., minWinnerCoverage=0., overlap=0):
        """
        Like :meth:`~hubdc.applier.ApplierOperator.getCategoricalArray`, but all category related information is
        implicitly taken from the class definition metadata.

        :param name: classification input raster image
        :param minOverallCoverage: see :meth:`~hubdc.applier.ApplierOperator.getCategoricalArray`
        :param minWinnerCoverage: see :meth:`~hubdc.applier.ApplierOperator.getCategoricalArray`
        :param overlap: see :meth:`~hubdc.applier.ApplierOperator.getArray`
        """

        classes, classNames, classLookup = self.getMetadataClassDefinition(name=name)
        ids = range(1, classes)
        return self.getCategoricalArray(name=name, ids=ids, noData=0, minOverallCoverage=minOverallCoverage, minWinnerCoverage=minWinnerCoverage, index=0, overlap=overlap)

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

    def findWavelengthNeighbours(self, name, wavelength):
        """
        Returns the image band indices and inverse distance weigths of the bands that are located around the target wavelength specified in nanometers.
        The sum of ``leftWeight`` and ``rightWeight`` is 1.

        The wavelength information is taken from the ENVI metadata domain.
        An exception is thrown if the ``wavelength`` and ``wavelength units`` metadata items are not correctly specified.

        :return: leftIndex, leftWeight, rightIndex, rightWeight

        """

        wavelengths = self.getMetadataWavelengths(name)
        leftWavelengths = wavelengths.copy()
        leftWavelengths[wavelengths > wavelength] = numpy.nan
        rightWavelengths = wavelengths.copy()
        rightWavelengths[wavelengths < wavelength] = numpy.nan

        if numpy.all(numpy.isnan(leftWavelengths)):
            leftIndex = None
            leftDistance = numpy.inf
        else:
            leftIndex = numpy.nanargmin((leftWavelengths - wavelength)**2)
            leftDistance = abs(wavelengths[leftIndex] - wavelength)

        if numpy.all(numpy.isnan(rightWavelengths)):
            rightIndex = None
            rightDistance = numpy.inf
        else:
            rightIndex = numpy.nanargmin((rightWavelengths - wavelength)**2)
            rightDistance = abs(wavelengths[rightIndex] - wavelength)

        if leftIndex is None:
            leftIndex = rightIndex
            leftWeight = 1.
            rightWeight = 0.
        else:
            if (leftDistance+rightDistance) != 0.:
                leftWeight = 1. - (leftDistance) / (leftDistance+rightDistance)
            else:
                leftWeight = 0.5
            rightWeight = 1. - leftWeight

        if rightIndex is None:
            rightIndex = leftIndex

        return leftIndex, leftWeight, rightIndex, rightWeight

    def findWavelength(self, name, wavelength):
        """
        Returns the image band index for the waveband that is nearest to the target wavelength specified in nanometers,
        and also returns the absolute distance (in nanometers).

        The wavelength information is taken from the ENVI metadata domain.
        An exception is thrown if the ``wavelength`` and ``wavelength units`` metadata items are not correctly specified.

        :return: index, distance
        """

        wavelengths = self.getMetadataWavelengths(name)
        distances = numpy.abs(wavelengths - wavelength)
        index = numpy.argmin(distances)
        return index, distances[index]

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

    def _getDerivedImage(self, name, ufunc, resampleAlg, overlap):

        dataset = self._getInputDataset(name)
        options = self._getInputOptions(name).copy()
        options['resampleAlg'] = resampleAlg
        grid = self.grid.pixelBuffer(buffer=overlap)

        # create tmp dataset
        gridInSourceProjection = grid.reproject(dataset.pixelGrid)
        tmpDataset = dataset.translate(dstPixelGrid=gridInSourceProjection, dstName='', format='MEM',
                                       noData=options['noData'])
        tmpArray = tmpDataset.readAsArray()
        derivedArray = ufunc(tmpArray)
        derivedDataset = CreateFromArray(pixelGrid=gridInSourceProjection, array=derivedArray,
                                         dstName='', format='MEM', creationOptions=[])

        tmpname = '_tmp_'
        self._inputDatasets[tmpname] = derivedDataset
        self._inputOptions[tmpname] = options
        array = self.getArray(name=tmpname, overlap=overlap)
        return array

    def _getBandSubset(self, name, indicies, overlap, dtype):

        dataset = self._getInputDataset(name)
        options = self._getInputOptions(name)
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

    def getVectorArray(self, name, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None, overlap=0, dtype=numpy.float32, scale=None):
        """
        Returns the vector rasterization of the current block in form of a 3-d numpy array.
        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setVector`.

        :param name: vector name
        :param initValue: value to pre-initialize the output array
        :param burnValue: value to burn into the output array for all objects; exclusive with ``burnAttribute``
        :param burnAttribute: identifies an attribute field on the features to be used for a burn-in value; exclusive with ``burnValue``
        :param allTouched: whether to enable that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon
        :param filterSQL: set an SQL WHERE clause which will be used to filter vector features
        :param overlap: the amount of margin (number of pixels) added to the image data block in each direction, so that the blocks will overlap; this is important for spatial operators like filters.
        :param dtype: convert output array to given numpy data type (this is done before the data is scaled)
        :param scale: scale output array by given scale factor (this is done after type conversion)
        """
        layer = self._getVectorDataset(name)
        grid = self.grid.pixelBuffer(buffer=overlap)
        dataset = layer.rasterize(dstPixelGrid=grid, eType=NumericTypeCodeToGDALTypeCode(dtype),
                                  initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute, allTouched=allTouched,
                                  filter=filterSQL, dstName='', format='MEM', creationOptions=[])
        array = dataset.readAsArray(scale=scale)
        return array

    def getVectorCategoricalFractionArray(self, name, ids, oversampling=10, xRes=None, yRes=None, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None,
                       overlap=0):
        """
        Returns input vector rasterization data like :meth:`~hubdc.applier.ApplierOperator.getVectorArray`,
        but instead of returning the data directly, rasterization is performed at a specified resolution ``xRes`` and ``yRes``,
        aggregated pixel fractions for the given categories (i.e. ``ids``) are returned.

        :param name: vector name
        :param ids: list of categry ids to use
        :param oversampling: set the rasterization resolution to a multiple (i.e. the oversampling factor) of the reference grid resolution
        :param xRes: set xRes rasterization resolution explicitely
        :param yRes: set yRes rasterization resolution explicitely

        For all other arguments see :meth:`~hubdc.applier.ApplierOperator.getVector`
        """
        layer = self._getVectorDataset(name)
        grid = self.grid.pixelBuffer(buffer=overlap)

        # rasterize vector layer at fine resolution
        if xRes is None or yRes is None:
            xRes = grid.xRes / float(oversampling)
            yRes = grid.yRes / float(oversampling)

        gridOversampled = grid.newResolution(xRes=xRes, yRes=yRes)
        tmpDataset = layer.rasterize(dstPixelGrid=gridOversampled, eType=NumericTypeCodeToGDALTypeCode(numpy.float32),
                                     initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute, allTouched=allTouched,
                                     filter=filterSQL, dstName='', format='MEM', creationOptions=[])

        tmpArrayCatecories = tmpDataset.readAsArray()
        tmpArrayFractions = numpy.stack(numpy.float32(tmpArrayCatecories[0] == id) for id in ids)

        # store as tmp input raster and aggregate fractions to target grid
        derivedDataset = CreateFromArray(pixelGrid=gridOversampled, array=tmpArrayFractions,
                                         dstName='', format='MEM', creationOptions=[])

        tmpname = '_tmp_'
        self._inputDatasets[tmpname] = derivedDataset
        self._inputOptions[tmpname] = {'resampleAlg' : gdal.GRA_Average, 'noData' : None}
        array = self.getArray(name=tmpname, overlap=overlap)
        return array

    def getVectorCategoricalArray(self, name, ids, noData, minOverallCoverage=0., minWinnerCoverage=0.,
                                  oversampling=10, xRes=None, yRes=None, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None,
                                  overlap=0):
        """
        Returns input raster band data like :meth:`~hubdc.applier.ApplierOperator.getVectorArray`,
        but instead of returning the data directly, the category array of maximum aggregated pixel fraction for the given categories (i.e. ``ids``)
        is returned.

        :param name: vector name
        :param ids:
        :param noData: see :meth:`~hubdc.applier.ApplierOperator.getCategoricalArray`
        :param minOverallCoverage: see :meth:`~hubdc.applier.ApplierOperator.getCategoricalArray`
        :param minWinnerCoverage: see :meth:`~hubdc.applier.ApplierOperator.getCategoricalArray`


        For all other arguments see :meth:`~hubdc.applier.ApplierOperator.getVector`
        and :meth:`~hubdc.applier.ApplierOperator.getVectorCategoricalFractionArray`.
        """
        fractions = self.getVectorCategoricalFractionArray(name=name, ids=ids, oversampling=oversampling, xRes=xRes, yRes=yRes,
                                                           initValue=noData, burnValue=burnValue, burnAttribute=burnAttribute, allTouched=allTouched, filterSQL=filterSQL,
                                                           overlap=overlap)

        categories = numpy.array(ids)[fractions.argmax(axis=0)[None]]
        if minOverallCoverage > 0:
            invalid = numpy.sum(fractions, axis=0, keepdims=True) < minOverallCoverage
            categories[invalid] = noData
        if minWinnerCoverage > 0:
            invalid = numpy.max(fractions, axis=0, keepdims=True) < minWinnerCoverage
            categories[invalid] = noData

        assert categories.ndim == 3
        return categories

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
        :param array: 3-d or 2-d numpy array to be written
        :param overlap: the amount of margin (number of pixels) to be removed from the image data block in each direction;
                        this is useful when the overlap keyword was also used with :meth:`~hubdc.applier.ApplierOperator.getArray`
        :param replace: tuple of ``(sourceValue, targetValue)`` values; replace all occurances of ``sourceValue`` inside the array with ``targetValue``;
                        this is done after type conversion and scaling)
        :param scale: scale array data by given scale factor (this is done after type conversion)
        :param dtype: convert array data to given numpy data type (this is done before the data is scaled)
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
        :param key: metadata item name
        :param value: metadata item value
        :param domain: metadata item domain
        """

        if self.isFirstBlock():
            filename = self.getOutputFilename(name)
            self._queueByFilename[filename].put((Writer.SET_META, filename, key, value, domain))

    def getMetadataItem(self, name, key, domain):
        """
        Returns the metadata item of an input raster image.

        :param name: input raster name
        :param key: metadata item name
        :param value: metadata item value
        :param domain: metadata item domain
        """
        dataset = self._getInputDataset(name)
        return dataset.getMetadataItem(key=key, domain=domain)

    def setMetadataWavelengths(self, name, wavelengths):
        """
        Set wavelengths (in nanometers) metadata information for an output raster.

        The wavelength information is stored in the ENVI metadata domain inside the
        ``wavelength`` and ``wavelength units`` metadata items.
        """

        filename = self.getOutputFilename(name)
        self.setMetadataItem(name=name, key='wavelength', value=wavelengths, domain='ENVI')
        self.setMetadataItem(name=name, key='wavelength units', value='nanometers', domain='ENVI')

    def getMetadataWavelengths(self, name):
        """
        Returns wavelengths (in nanometers) metadata information for an input raster.

        The wavelength information is taken from the ENVI metadata domain.
        An exception is thrown if the ``wavelength`` and ``wavelength units`` metadata items are not correctly specified.
        """

        dataset = self._getInputDataset(name)
        wavelength = dataset.getMetadataItem(key='wavelength', domain='ENVI', dtype=float)
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
        return wavelength

    def setMetadataClassDefinition(self, name, classes, classNames=None, classLookup=None):
        """
        Set class definition metadata information for an output raster.

        The class definition information is stored in the ENVI metadata domain items ``classes``, ``class names`` and ``class lookup``.
        Note that the "unclassified" (class id=0) class is added.
        """

        if classNames is None:
            classNames = ['class {}'.format(i+1) for i in range(classes)]
        if classLookup is None:
            import random
            classLookup = [random.randint(1,255) for i in range(classes*3)]

        if len(classNames) != classes:
            raise Exception('wrong number of class names')
        if len(classLookup) != classes*3:
            raise Exception('wrong number of class colors')

        classes += 1
        classNames = ['unclassified'] + classNames
        classLookup = [0, 0, 0] + classLookup

        filename = self.getOutputFilename(name)
        self.setMetadataItem(name=name, key='file type', value='ENVI Classification', domain='ENVI')
        self.setMetadataItem(name=name, key='classes', value=classes, domain='ENVI')
        self.setMetadataItem(name=name, key='class names', value=classNames, domain='ENVI')
        self.setMetadataItem(name=name, key='class lookup', value=classLookup, domain='ENVI')
        self.setNoDataValue(name=name, value=0)

    def getMetadataClassDefinition(self, name):
        """
        Returns class definition metadata information for an input raster.

        The class definition information is taken from the ENVI metadata domain items ``classes``, ``class names`` and ``class lookup``.
        Note that the "unclassified" (class id=0) class is removed.

        :return: classes, classNames, classLookup
        """

        dataset = self._getInputDataset(name)
        classes = dataset.getMetadataItem(key='classes', domain='ENVI', dtype=int)
        classNames = dataset.getMetadataItem(key='class names', domain='ENVI', dtype=str)
        classLookup = dataset.getMetadataItem(key='class lookup', domain='ENVI', dtype=int)

        return classes-1, classNames[1:], classLookup[3:]

    def setMetadataBandNames(self, name, bandNames):
        """
        Set band names definition metadata information for an output raster.

        The information is stored in the ENVI metadata domain item ``band names`` and in the GDAL band descriptions.
        """
        self.setMetadataItem(name=name, key='band names', value=bandNames, domain='ENVI')

    def setNoDataValue(self, name, value):
        """
        Set the no data value for an output raster image.
        """
        self.setMetadataItem(name=name, key='data ignore value', value=value, domain='ENVI')
        filename = self.getOutputFilename(name)
        self._queueByFilename[filename].put((Writer.SET_NODATA, filename, value))

    def getNoDataValue(self, name, default=None):
        """
        Returns the no data value for an input raster image. If a no data value is not specified, the ``default`` value is returned.
        """
        dataset = self._getInputDataset(name)
        noDataValue = dataset.getNoDataValue(default=default)
        return default

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
        return self

    DEFAULT_WINDOWXSIZE = 256
    def setWindowXSize(self, windowxsize=DEFAULT_WINDOWXSIZE):
        """
        Set the X size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowxsize = windowxsize
        return self

    DEFAULT_WINDOWYSIZE = 256
    def setWindowYSize(self, windowysize=DEFAULT_WINDOWYSIZE):
        """
        Set the Y size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowysize = windowysize
        return self

    def setWindowFullSize(self):
        """
        Set the block size to full extent.
        """

        veryLargeNumber = 10**20
        self.setWindowXSize(veryLargeNumber)
        self.setWindowYSize(veryLargeNumber)
        return self

    DEFAULT_NWORKER = None
    def setNumThreads(self, nworker=DEFAULT_NWORKER):
        """
        Set the number of pool worker for multiprocessing. Set to None to disable multiprocessing (recommended for debugging).
        """
        self.nworker = nworker
        return self

    DEFAULT_NWRITER = None
    def setNumWriter(self, nwriter=DEFAULT_NWRITER):
        """
        Set the number of writer processes. Set to None to disable multiwriting (recommended for debugging).
        """
        self.nwriter = nwriter
        return self

    DEFAULT_CREATEENVIHEADER = True
    def setCreateEnviHeader(self, createEnviHeader=DEFAULT_CREATEENVIHEADER):
        """
        Set to True to create additional ENVI header files for all output rasters.
        The header files store all metadata items from the GDAL PAM ENVI domain,
        so that the images can be correctly interpreted by the ENVI software.
        Currently only the native ENVI format and the GTiff format is supported.
        """
        self.createEnviHeader = createEnviHeader
        return self

    DEFAULT_FOOTPRINTTYPE = const.FOOTPRINT_UNION
    def setAutoFootprint(self, footprintType=DEFAULT_FOOTPRINTTYPE):
        """
        Derive extent of the reference pixel grid from input files. Possible options are 'union' or 'intersect'.
        """
        self.footprintType = footprintType
        return self

    DEFAULT_RESOLUTIONTYPE = const.RESOLUTION_MINIMUM
    def setAutoResolution(self, resolutionType=DEFAULT_RESOLUTIONTYPE):
        """
        Derive resolution of the reference pixel grid from input files. Possible options are 'minimum', 'maximum' or 'average'.
        """
        self.resolutionType = resolutionType
        return self

    def setResolution(self, xRes=None, yRes=None):
        """
        Set resolution of the reference pixel grid.
        """
        self.xRes = xRes
        self.yRes = yRes
        return self

    def setFootprint(self, xMin=None, xMax=None, yMin=None, yMax=None):
        """
        Set spatial footprint of the reference pixel grid.
        """
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        return self

    def setProjection(self, projection=None):
        """
        Set projection of the reference pixel grid.
        """
        self.projection = projection
        return self

    def setReferenceGrid(self, grid=None):
        """
        Set the reference pixel grid. Pass an instance of the :py:class:`~hubdc.model.PixelGrid.PixelGrid` class.
        """
        self.referenceGrid = grid
        return self

    def setReferenceGridByImage(self, filename):
        """
        Set an image defining the reference pixel grid.
        """
        self.setReferenceGrid(grid=PixelGrid.fromFile(filename))
        return self

    def setReferenceGridByVector(self, filename, xRes, yRes, layerNameOrIndex=0):
        """
        Set a vector layer defining the reference pixel grid footprint and projection.
        """

        layer = OpenLayer(filename=filename, layerNameOrIndex=layerNameOrIndex)
        grid = layer.makePixelGrid(xRes=xRes, yRes=yRes)
        self.setReferenceGrid(grid=grid)
        return self

    DEFAULT_GDALCACHEMAX = 100*2**20
    def setGDALCacheMax(self, bytes=DEFAULT_GDALCACHEMAX):
        """
        For details see the `GDAL_CACHEMAX Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_CACHEMAX>`_.
        """
        self.cacheMax = bytes
        return self

    DEFAULT_GDALSWATHSIZE = 100*2**20
    def setGDALSwathSize(self, bytes=DEFAULT_GDALSWATHSIZE):
        """
        For details see the `GDAL_SWATH_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_SWATH_SIZE>`_.
        """
        self.swathSize = bytes
        return self

    DEFAULT_GDALDISABLEREADDIRONOPEN = True
    def setGDALDisableReadDirOnOpen(self, disable=DEFAULT_GDALDISABLEREADDIRONOPEN):
        """
        For details see the `GDAL_DISABLE_READDIR_ON_OPEN Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_DISABLE_READDIR_ON_OPEN>`_.
        """
        self.disableReadDirOnOpen = disable
        return self

    DEFAULT_GDALMAXDATASETPOOLSIZE = 100
    def setGDALMaxDatasetPoolSize(self, nfiles=DEFAULT_GDALMAXDATASETPOOLSIZE):
        """
        For details see the `GDAL_MAX_DATASET_POOL_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_MAX_DATASET_POOL_SIZE>`_.
        """
        self.maxDatasetPoolSize = nfiles
        return self

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
            if len(grids) == 0:
                raise Exception('projection not defined')
            for grid in grids:
                if not grid.equalProjection(grids[0]):
                    raise Exception('input projections do not match')
            projection = grids[0].projection
        else:
            projection = self.projection
        return projection

    def _deriveFootprint(self, grids, projection):

        if None in [self.xMin, self.xMax, self.yMin, self.yMax]:

            if len(grids) == 0:
                raise Exception('footprint not defined')

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
