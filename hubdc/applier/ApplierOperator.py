from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.Applier import Applier
from hubdc import CreateFromArray, Create
from hubdc.applier.WriterProcess import WriterProcess

class ApplierOperator(object):

    def __init__(self, applier, grid, initialization=False):
        assert isinstance(applier, Applier)
        assert isinstance(grid, PixelGrid)
        self._applier = applier
        self.grid = grid
        self._initialization=initialization

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
        for name, i in self.getSubnames(name):
            yield self.getData(name=(name,i), indicies=indicies, dtype=dtype, scale=scale)

    def getSubnames(self, name):
        i = 0
        while True:
            if (name, i) in self._applier.inputDatasets:
                yield (name, i)
                i += 1
            else:
                break

    def _getImage(self, name, dtype, scale):

        dataset = self._applier.inputDatasets[name]
        options = self._applier.inputs[name].options
        if self.grid.equalProjection(dataset.pixelGrid):
            datasetResampled = dataset.translate(dstPixelGrid=self.grid, dstName='', format='MEM',
                                                 resampleAlg=options['resampleAlg'])
        else:
            datasetResampled = dataset.warp(dstPixelGrid=self.grid, dstName='', format='MEM',
                                            resampleAlg=options['resampleAlg'],
                                            errorThreshold=options['errorThreshold'])

        array = datasetResampled.readAsArray(dtype=dtype, scale=scale)
        datasetResampled.close()


        return array

    def _getBandSubset(self, name, indicies, dtype):

        dataset = self._applier.inputDatasets[name]
        options = self._applier.inputs[name].options
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

    def setData(self, name, array, replace=None, scale=None, dtype=None):

        if replace is not None:
            srcValue, dstValue = replace
            array[array==srcValue] = dstValue

        if scale is not None:
            array *= scale

        if dtype is not None:
            array = array.astype(dtype)

        if self._initialization:
            self._applier.queues[name].put((WriterProcess.CREATE_DATASET, name, array))
        else:
            self._applier.queues[name].put((WriterProcess.WRITE_ARRAY, name, array, self.grid))

    def setMetadataItem(self, name, key, value, domain):
        self._applier.queues[name].put((WriterProcess.SET_META, name, key, value, domain))
        self._applier.queues[name].put((WriterProcess.FLUSH_CACHE, name))

    def setNoDataValue(self, name, value):
        self._applier.queues[name].put((WriterProcess.SET_NODATA, name, value))

    def ufunc(self, *args, **kwargs):
        raise NotImplementedError()

    def umeta(self, *args, **kwargs):
        '''
        Use this methode to set metadata for output datasets using self.setMetadataItem().
        This methode is called once after the first call to self.ufunc().
        At this point in time all output datasets are already created.
        '''
        pass
