__author__ = 'janzandr'
import numpy

from emb.hub.timing import tic, toc


def nanargpercentile(a, q, axis=0, out=None, overwrite_input=False, interpolation='linear'):

    if axis != 0: raise Exception('Sorry, only axis=0 is supported.')

#    hub.debug.copy(a)
#    for ab in a:
#        print numpy.any(numpy.invert(numpy.isnan(ab))) # any valid data?

    try:
        ps =  numpy.nanpercentile(a, q, axis, out, overwrite_input, interpolation)
    except:
        ashape = a.shape
        ps = numpy.zeros((len(q),ashape[1],ashape[2]))
        print('Exception catched: '+numpy.nanpercentile.__module__)

    # handle bug that appears when all data is nan
    if ps.shape[0] != len(q):
        ps = numpy.array([ps for i in range(len(q))])

    def arg(p):
        diff = numpy.abs(a-p)
        diff[numpy.isnan(diff)] = numpy.inf
        index = numpy.nanargmin(diff, axis=axis)
        return numpy.expand_dims(index, 0)

    indexes = numpy.vstack((arg(p) for p in ps))
    return indexes

def nanargmedian(a, axis=0, out=None, overwrite_input=False, keepdims=False):

    if axis != 0: raise Exception('Sorry, only axis=0 is supported.')

#check is some pixel prifiles are completely masked out
    median = numpy.nanmedian(a, axis,  out, overwrite_input, keepdims)
    diff = numpy.abs(a-median)
    diff[numpy.isnan(diff)] = numpy.inf
    argmedian = numpy.nanargmin(diff, axis=axis)
    missing = numpy.min(diff, axis=axis) == numpy.inf
    return argmedian, missing

if __name__ == '__main__':

    nb,ns,nl = 5,2,2
    a = numpy.array(range(nb*ns*nl), dtype=numpy.float32).reshape((nb,ns,nl))
    print((a[0,:,:]).shape)
    for i in range(5): a[i,:,:] = numpy.nan

    print(a)
    tic()
    print(nanargmedian(a, axis=0, keepdims=True))
 #   print(nanargpercentile(a, [50], axis=0))
    toc()