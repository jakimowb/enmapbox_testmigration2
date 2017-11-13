from __future__ import print_function
# import matplotlib
# matplotlib.use('QT4Agg')
# from matplotlib import pyplot
import numpy
from osgeo import gdal
from tempfile import gettempdir
from os.path import join, exists, basename, dirname
import enmapboxtestdata
from hubdc.applier import *
from hubdc.testdata import LT51940232010189KIS01, LT51940242010189KIS01, BrandenburgDistricts, root

outdir = join(gettempdir(), 'hubdc_test')


def test_applier():

    applier = Applier()

    # add a single cfmask raster
    applier.inputRaster.setRaster(key='cfmask',
                                  value=ApplierInputRaster(filename=LT51940232010189KIS01.cfmask))
    print(applier.inputRaster.getRaster(key='cfmask'))
    print()

    # add all '.img' rasters from a scene folder
    applier.inputRaster.setGroup(key='scene',
                                 value=ApplierInputRasterGroup.fromFolder(folder=LT51940242010189KIS01.root,
                                                                          extensions=['.img']))
    print(applier.inputRaster.getGroup(key='scene'))

    # add all '.img' rasters from a scene folder, but filter out cfmask rasters
    applier.inputRaster.setGroup(key='scene2',
                                 value=ApplierInputRasterGroup.fromFolder(folder=LT51940242010189KIS01.root,
                                                                          extensions=['.img'],
                                                                          ufunc=lambda basename,
                                                                                       **kwarg: not basename.endswith(
                                                                              'cfmask')))
    print(applier.inputRaster.getGroup(key='scene2'))

    # add all '.img' rasters from folder with multiple scenes
    applier.inputRaster.setGroup(key='archive',
                                 value=ApplierInputRasterGroup.fromFolder(folder=root,
                                                                          extensions=['.img']))
    print(applier.inputRaster.getGroup(key='archive'))

    # use an input raster index
    # - create index from folder
    index = ApplierInputRasterIndex.fromFolder(folder=root, extensions=['.img'])
    # - pickle and unpickle index
    filename = join(outdir, 'index.pkl')
    index.pickle(filename=filename)
    index = ApplierInputRasterIndex.unpickle(filename=filename)
    print(index)
    # - get intersection that covers both scenes
    grid = Open(filename=LT51940232010189KIS01.cfmask).grid
    index2 = index.getIntersection(grid=grid)
    print(index2)
    # - get intersection that covers only one scene
    grid = grid.subsetPixelWindow(xOff=10, yOff=10, xSize=1, ySize=1)  # 1x1 pixel extent
    index3 = index.getIntersection(grid=grid)
    print(index3)

    # add all rasters from index
    applier.inputRaster.setGroup(key='index', value=ApplierInputRasterGroup.fromIndex(index=index))
    print(applier.inputRaster.getGroup(key='index'))

    # add vector
    applier.inputVector.setVector(key='vector', value=ApplierInputVector(filename=BrandenburgDistricts.shp))
    print(applier.inputVector.getVector(key='vector'))

    class Operator(ApplierOperator):
        def ufunc(operator, *args, **kwargs):
            cfmask = operator.inputRaster.getRaster(key='cfmask')
            print(cfmask.getImageArray().shape)

    applier.apply(operator=Operator, description='MyOperator')
def run():
    test_applier()


if __name__ == '__main__':
    print(outdir)
    run()
