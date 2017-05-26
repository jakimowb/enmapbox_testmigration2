from osgeo import gdal
import random
from hubdc import Open
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.Applier import Applier
from hubdc import CreateFromArray, Create
from hubdc.applier.WriterProcess import WriterProcess

class ApplierOperator(object):

    def __init__(self, maingrid, inputDatasets, inputFilenames, inputOptions, outputFilenames, outputOptions, queueByFilename, ufuncArgs, ufuncKwargs):
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

    def getArray(self, name, indicies=None, dtype=None, scale=None):

        if indicies is None:
            array = self._getImage(name=name, dtype=dtype, scale=scale)
        elif isinstance(indicies, (list, tuple)):
            array = self._getBandSubset(name=name, indicies=indicies, dtype=dtype)
        elif isinstance(indicies, int):
            array = self._getBandSubset(name=name, indicies=[indicies], dtype=dtype)
        else:
            raise ValueError('indicies must be a list/tuble of integers or a scalar integer.')

        return array

    def getArrayIterator(self, name, indicies=None, dtype=None, scale=None):

        for name, i in self.getSubnames(name):

            if indicies is None:
                iindicies = None
            elif isinstance(indicies, int):
                iindicies = [indicies]
            elif isinstance(indicies, list):
                iindicies = indicies[i]
            else:
                raise ValueError(
                    'indicies must be a) an integer, b) a list of integers, c) a list of lists of integers, d) a mixture of c) and d), or f) None')

            yield self.getArray(name=(name, i), indicies=iindicies, dtype=dtype, scale=scale)

    def getSubnames(self, name):
        i = 0
        if (name, 0) not in self.inputDatasets:
            raise KeyError('{name} is not an image list'.format(name=name))

        while True:
            if (name, i) in self.inputDatasets:
                yield (name, i)
                i += 1
            else:
                break

    def _getDataset(self, name):
        if name not in self.inputDatasets:
            raise Exception('{name} is not a single image input'.format(name=name))

        if self.inputDatasets[name] is None:
            self.inputDatasets[name] = Open(filename=self.inputFilenames[name])
        return self.inputDatasets[name], self.inputOptions[name]

    def _getImage(self, name, dtype, scale):

        dataset, options = self._getDataset(name)

        if self.grid.equalProjection(dataset.pixelGrid):
            datasetResampled = dataset.translate(dstPixelGrid=self.grid, dstName='', format='MEM',
                                                 resampleAlg=options['resampleAlg'],
                                                 noData=options['noData'])
        else:
            datasetResampled = dataset.warp(dstPixelGrid=self.grid, dstName='', format='MEM',
                                            resampleAlg=options['resampleAlg'],
                                            errorThreshold=options['errorThreshold'],
                                            warpMemoryLimit=options['warpMemoryLimit'],
                                            multithread=options['multithread'],
                                            srcNodata=options['noData'])
        array = datasetResampled.readAsArray(dtype=dtype, scale=scale)
        datasetResampled.close()
        return array

    def _getBandSubset(self, name, indicies, dtype):

        dataset, options = self._getDataset(name)
        try:
            bandList = [i + 1 for i in indicies]
        except:
            a=1
        if self.grid.equalProjection(dataset.pixelGrid):
            datasetResampled = dataset.translate(dstPixelGrid=self.grid, dstName='', format='MEM',
                                                 bandList=bandList,
                                                 resampleAlg=options['resampleAlg'],
                                                 noData=options['noData'])
        else:
            selfGridReprojected = self.grid.reproject(dataset.pixelGrid)
            height, width = selfGridReprojected.getDimensions()
            selfGridReprojectedWithBuffer = selfGridReprojected.subsetPixelWindow(xoff=-1, yoff=-1, width=width + 2,
                                                                                  height=height + 2)
            datasetClipped = dataset.translate(dstPixelGrid=selfGridReprojectedWithBuffer, dstName='', format='MEM',
                                               bandList=bandList,
                                               noData=options['noData'])

            datasetResampled = datasetClipped.warp(dstPixelGrid=self.grid, dstName='', format='MEM',
                                                   resampleAlg=options['resampleAlg'],
                                                   errorThreshold=options['errorThreshold'],
                                                   warpMemoryLimit=options['warpMemoryLimit'],
                                                   multithread=options['multithread'],
                                                   srcNodata=options['noData'])
            datasetClipped.close()

        array = datasetResampled.readAsArray(dtype=dtype)
        datasetResampled.close()
        return array

    def getFilename(self, name):
        return self.outputFilenames[name]

    def setData(self, name, array, replace=None, scale=None, dtype=None):

        from numpy import nan, isnan, equal
        if replace is not None:
            mask = isnan(array) if replace[0] is nan else equal(array, replace[0])

        if scale is not None:
            array *= scale

        if dtype is not None:
            array = array.astype(dtype)

        if replace is not None:
            array[mask] = replace[1]

        filename = self.getFilename(name)
        self.queueByFilename[filename].put((WriterProcess.WRITE_ARRAY, filename, array, self.grid, self.maingrid, self.outputOptions[name]['format'], self.outputOptions[name]['creationOptions']))

    def setMetadataItem(self, name, key, value, domain):
        filename = self.getFilename(name)
        self.queueByFilename[filename].put((WriterProcess.SET_META, filename, key, value, domain))
        #self.queueByFilename[filename].put((WriterProcess.FLUSH_CACHE, filename))

    def setNoDataValue(self, name, value):
        filename = self.getFilename(name)
        self.queueByFilename[filename].put((WriterProcess.SET_NODATA, filename, value))

    def run(self, subgrid, iblock, nblock):
        self.iblock = iblock
        self.nblock = nblock
        self.subgrid = subgrid
        self.ufunc(*self.ufuncArgs, **self.ufuncKwargs)

    def ufunc(self, *args, **kwargs):
        raise NotImplementedError()
