from osgeo import gdal
import random
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.Applier import Applier
from hubdc import CreateFromArray, Create
from hubdc.applier.WriterProcess import WriterProcess

class ApplierOperator(object):

    def __init__(self, maingrid, inputDatasets, inputOptions, outputFilenames, outputOptions, queueByFilename, ufuncArgs, ufuncKwargs):
        assert isinstance(maingrid, PixelGrid)
        self.subgrid = None
        self.maingrid = maingrid
        self.inputDatasets = inputDatasets
        self.inputOptions = inputOptions
        self.outputFilenames = outputFilenames
        self.outputOptions = outputOptions
        self.queueByFilename = queueByFilename
        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

    @property
    def grid(self):
        assert isinstance(self.subgrid, PixelGrid)
        return self.subgrid

    def getData(self, name, indicies=None, dtype=None, scale=None):

        if indicies is None:
            array = self._getImage(name=name, dtype=dtype, scale=scale)
        elif isinstance(indicies, (list, tuple)):
            array = self._getBandSubset(name=name, indicies=indicies, dtype=dtype)
        elif isinstance(indicies, int):
            array = self._getBandSubset(name=name, indicies=[indicies], dtype=dtype)
        else:
            raise ValueError('indicies must be a list/tuble of integers or a scalar integer.')

        return array

    def getDatas(self, name, indicies=None, dtype=None, scale=None):
        n = len(list(self.getSubnames(name)))
        for name, i in self.getSubnames(name):
            print(i,n)
            yield self.getData(name=(name,i), indicies=indicies, dtype=dtype, scale=scale)

    def getSubnames(self, name):
        i = 0
        while True:
            if (name, i) in self.inputDatasets:
                yield (name, i)
                i += 1
            else:
                break

    def _getImage(self, name, dtype, scale):

        dataset = self.inputDatasets[name]
        options = self.inputOptions[name]

        #tmpvrtfilename = r'a:\getimage' + str(random.randint(0, 10 ** 20)) + '.vrt'
        tmpvrtfilename = ''
        if self.grid.equalProjection(dataset.pixelGrid):
            Applier.NTRANS += 1
            datasetResampled = dataset.translate(dstPixelGrid=self.grid, dstName=tmpvrtfilename, format='MEM',
                                                 resampleAlg=options['resampleAlg'])

        else:
            Applier.NWARP += 1
            datasetResampled = dataset.warp(dstPixelGrid=self.grid, dstName=tmpvrtfilename, format='MEM',
                                            resampleAlg=options['resampleAlg'],
                                            errorThreshold=options['errorThreshold'],
                                            warpMemoryLimit=options['warpMemoryLimit'],
                                            multithread=options['multithread'])
        print(options)
        array = datasetResampled.readAsArray(dtype=dtype, scale=scale)
        datasetResampled.close()
        #driver = gdal.GetDriverByName('VRT')
        #driver.Delete(tmpvrtfilename)

        return array

    def _getImage2(self, name, dtype, scale):

        dataset = self.inputDatasets[name]
        options = self.inputOptions[name]
        import random
        filename = r'a:\getimage'+str(random.randint(0, 10**20))+'.vrt'
        datasetWarped = gdal.Warp(destNameOrDestDS='', srcDSOrSrcDSTab=dataset.gdalDataset,
                                  options=dataset.warpOptions(dstPixelGrid=self.grid,
                                                        format='MEM', creationOptions=[],
                                                        resampleAlg=options['resampleAlg'],
                                                        errorThreshold=options['errorThreshold']))
        array = datasetWarped.ReadAsArray()
        #gdal.Dataset.__swig_destroy__(datasetWarped)
        datasetWarped = None
        #driver = gdal.GetDriverByName('VRT')
        #driver.Delete(filename)

        return array

    def _getBandSubset(self, name, indicies, dtype):

        dataset = self.inputDatasets[name]
        options = self.inputOptions[name]
        bandList = [i + 1 for i in indicies]
        if self.grid.equalProjection(dataset.pixelGrid):
            datasetResampled = dataset.translate(dstPixelGrid=self.grid, dstName='', format='MEM',
                                                 bandList=bandList,
                                                 resampleAlg=options['resampleAlg'])
        else:
            selfGridReprojected = self.grid.reproject(dataset.pixelGrid)
            height, width = selfGridReprojected.getDimensions()
            selfGridReprojectedWithBuffer = selfGridReprojected.subsetPixelWindow(xoff=-1, yoff=-1, width=width + 2,
                                                                                  height=height + 2)
            datasetClipped = dataset.translate(dstPixelGrid=selfGridReprojectedWithBuffer, dstName='', format='MEM',
                                               bandList=bandList)
            datasetResampled = datasetClipped.warp(dstPixelGrid=self.grid, dstName='', format='MEM',
                                                   resampleAlg=options['resampleAlg'],
                                                   errorThreshold=options['errorThreshold'])
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
        if self.initialization:
            self.queueByFilename[filename].put((WriterProcess.CREATE_DATASET, filename, array, self.maingrid, self.outputOptions[name]['format'], self.outputOptions[name]['creationOptions']))
        else:
            self.queueByFilename[filename].put((WriterProcess.WRITE_ARRAY, filename, array, self.grid))

    def setMetadataItem(self, name, key, value, domain):
        filename = self.getFilename(name)
        self.queueByFilename[filename].put((WriterProcess.SET_META, filename, key, value, domain))
        self.queueByFilename[filename].put((WriterProcess.FLUSH_CACHE, filename))

    def setNoDataValue(self, name, value):
        filename = self.getFilename(name)
        self.queueByFilename[filename].put((WriterProcess.SET_NODATA, filename, value))

    def run(self, subgrid, initialization):
        self.initialization = initialization
        self.subgrid = subgrid
        self.ufunc(*self.ufuncArgs, **self.ufuncKwargs)

    def ufunc(self, *args, **kwargs):
        raise NotImplementedError()

    def umeta(self, *args, **kwargs):
        '''
        Use this methode to set metadata for output datasets using self.setMetadataItem().
        This methode is called once after the first call to self.ufunc().
        At this point in time all output datasets are already created.
        '''
        pass
