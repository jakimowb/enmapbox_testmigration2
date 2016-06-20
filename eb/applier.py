import rios
import numpy

class ApplierControls(rios.applier.ApplierControls):

    def __init__(self):
        rios.applier.ApplierControls.__init__(self)
        self.setNumThreads(1)
        self.setJobManagerType('multiprocessing')
        self.setOutputDriverName("ENVI")
        self.setCreationOptions(["INTERLEAVE=BSQ"])
        self.setCalcStats(False)
        self.setOmitPyramids(True)


    def __repr__(self):
        d = self.__dict__
        return 'ApplierControls(' + ', '.join([k + '=' + str(d[k]) for k in sorted(d.keys())])


class ApplierHelper:

    @staticmethod
    def progress(info):

        return int((info.xblock + info.yblock * info.xtotalblocks) / float(info.xtotalblocks * info.ytotalblocks) * 100)


    @staticmethod
    def reshape2d(inputs):

        for k, v in inputs.__dict__.items():
            inputs.__dict__[k] = inputs.__dict__[k].reshape((v.shape[0], -1))


    @staticmethod
    def mask(input, noDataValue, all=False, inverse=False):

        assert isinstance(input, numpy.ndarray)

        if noDataValue is not None:
            result = input == noDataValue
            if all:
                result = numpy.all(result, axis=0, keepdims=True)
            else:
                result = numpy.any(result, axis=0, keepdims=True)
        else:
            result = False

        if inverse:
            result = numpy.logical_not(result)

        return result


    @staticmethod
    def extract(input, mask):

        vector = numpy.full((input.shape[0], 1), True, numpy.bool)
        mask3d = mask*vector
        return input[mask3d].reshape((input.shape[0],-1))


    @staticmethod
    def maskedArray(input, mask):

        if numpy.ndim(mask) == 0:
            mask = mask * numpy.full(input.shape, True, dtype=numpy.bool)
        else:
            mask = mask * numpy.full([input.shape[0], 1], True, dtype=numpy.bool)

        return numpy.ma.array(input, mask=mask)


    @staticmethod
    def firstBlock(info):

        return (info.xblock == 0) and (info.yblock == 0)


if __name__ == '__main__':

    pass