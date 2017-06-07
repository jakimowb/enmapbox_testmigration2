from hubdc import Open
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.Writer import Writer
import numpy

class ApplierOperator(object):

    def __init__(self, maingrid, inputDatasets, inputFilenames, inputOptions, outputFilenames, outputOptions, queueByFilename, ufuncArgs, ufuncKwargs, ufuncFunction=None):
        assert isinstance(maingrid, PixelGrid)
        self.subgrid = None
        self.maingrid = maingrid
        self.inputDatasets = inputDatasets
        self.inputFilenames = inputFilenames
        self.inputOptions = inputOptions
        self.outputFilenames = outputFilenames
        self.outputOptions = outputOptions
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
        dataset, options = self._getDataset(name)

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

