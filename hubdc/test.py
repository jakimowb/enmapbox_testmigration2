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
    grid = grid.subset(offset=Offset(x=10, y=10), size=Size(x=1, y=1))  # 1x1 pixel extent
    index3 = index.getIntersection(grid=grid)
    print(index3)

    # add all rasters from index
    applier.inputRaster.setGroup(key='index', value=ApplierInputRasterGroup.fromIndex(index=index))
    print(applier.inputRaster.getGroup(key='index'))

    # add vector
    applier.inputVector.setVector(key='vector', value=ApplierInputVector(filename=BrandenburgDistricts.shp))
    print(applier.inputVector.getVector(key='vector'))
    applier.inputVector.setVector(key='vectorFolder/vector', value=ApplierInputVector(filename=BrandenburgDistricts.shp))

    # add output raster
    applier.outputRaster.setRaster(key='ls453A', value=ApplierOutputRaster(filename=join(outdir, 'ls453A.img')))
    applier.outputRaster.setRaster(key='ls453B', value=ApplierOutputRaster(filename=join(outdir, 'ls453B.img')))

    # assess key/values
    assert isinstance(applier.inputRaster.findRaster(ufunc=lambda key, raster: key.endswith('cfmask')), ApplierInputRaster)
    assert applier.inputRaster.findRaster(ufunc=lambda key, raster: False) is None
    assert applier.inputRaster.findRasterKey(ufunc=lambda key, raster: key.endswith('mask')) == 'cfmask'
    assert applier.inputRaster.findRasterKey(ufunc=lambda key, raster: False) is None
    print(list(applier.inputRaster.getFlatRasters()))
    print(list(applier.inputRaster.getFlatRasterKeys()))
    print(list(applier.inputRaster.getRasters()))
    print(list(applier.inputRaster.getRasterKeys()))
    print(list(applier.inputRaster.getGroups()))
    print(list(applier.inputRaster.getGroupKeys()))

    print(list(applier.inputVector.getGroups()))
    print(list(applier.inputVector.getGroupKeys()))
    print(list(applier.inputVector.getFlatVectors()))
    print(list(applier.inputVector.getFlatVectorKeys()))

    print(list(applier.outputRaster.getFlatRasters()))
    print(list(applier.outputRaster.getFlatRasterKeys()))

    # settings
    applier.controls.setBlockFullSize()

    # run in multi process mode
    applier.controls.setNumThreads(2)
    applier.controls.setNumWriter(2)
    applier.controls.setGrid(grid=Open(LT51940242010189KIS01.cfmask).grid)
    applier.controls.setExtent(extent=Open(filename=LT51940242010189KIS01.cfmask).extent)
    #applier.apply(operator=Operator, description='MyOperator')

    # run in single process mode
    # - with different projection
    applier.controls.setNumThreads(None)
    applier.controls.setNumWriter(None)

    ds = Open(filename=LT51940242010189KIS01.cfmask)
    extentWGS84 = ds.spatialExtent.reproject(targetProjection= Projection.WGS84())

    applier.controls.setExtent(extent=extentWGS84)
    applier.controls.setProjection(projection=4326)
    applier.controls.setProjection(projection=Projection.WGS84().wkt)
    applier.controls.setProjection(projection=Projection.WGS84())
    applier.controls.setResolution(resolution=0.01)
    applier.apply(operator=Operator, description='MyOperator')

    # run in single process mode
    applier.controls.setNumThreads(None)
    applier.controls.setNumWriter(None)
    applier.controls.setGrid(None)
    applier.apply(operator=Operator)

    # run in multi writing mode
    applier.controls.setNumWriter(2)
    applier.apply(operator=Operator)

    # overwrite keyword
    applier.apply(operator=Operator, overwrite=False)

    # test ufunc passing
    applier.apply(operator=lambda *args, **kwargs: None)
    try:
        applier.apply(operator='Hello')
    except errors.ApplierOperatorTypeError:
        pass

    # test auto resolution
    operator = lambda *args, **kwargs: None
    applier.controls.setGrid(None)
    applier.controls.setAutoResolution(Options.AutoResolution.average)
    applier.apply(operator=operator)
    applier.controls.setAutoResolution(Options.AutoResolution.minimum)
    applier.apply(operator=operator)
    applier.controls.setAutoResolution(Options.AutoResolution.maximum)
    applier.apply(operator=operator)
    try:
        applier.controls.setAutoResolution(26)
        applier.apply(operator=operator)
    except errors.UnknownApplierAutoResolutionOption:
        pass

    # test auto extent
    operator = lambda *args, **kwargs: None
    applier.controls.setAutoResolution()
    applier.controls.setGrid(None)
    applier.controls.setAutoExtent(Options.AutoExtent.union)
    applier.apply(operator=operator)
    applier.controls.setAutoExtent(Options.AutoExtent.intersection)
    applier.apply(operator=operator)
    try:
        applier.controls.setAutoExtent(26)
        applier.apply(operator=operator)
    except errors.UnknownApplierAutoExtentOption:
        pass


    print(applier.outputRaster.getRaster(key='ls453A'))
    print(applier.outputRaster.getRaster(key='ls453B'))


    # change projection


class Operator(ApplierOperator):
    def ufunc(operator, *args, **kwargs):
        overlap = 10
        operator.isFirstBlock()
        operator.isLastBlock()
        operator.isLastXBlock()
        operator.isLastYBlock()
        operator.getFull(value=42)

        # read raster
        cfmask = operator.inputRaster.getRaster(key='cfmask')
        cfmaskArray = cfmask.getImageArray()
        print(cfmaskArray.shape)
        print(cfmask.getBandArray(indicies=[0], overlap=overlap).shape)
        print(cfmask.getFractionArray(categories=[0, 1, 2, 3, 4, 255], overlap=overlap).shape)

        # read vector
        vector = operator.inputVector.getVector(key='vector')
        print(vector.getImageArray().shape)
        print(vector.getFractionArray(categories=[1,4,7,9], categoryAttribute='id').shape)

        # read sample
        print(cfmask.getImageSample(mask=cfmaskArray == 1).shape)  # water samples
        print(cfmask.getImageSample(mask=cfmaskArray == 172387).shape)  # empty samples

        # read raster metadata
        print(cfmask.getMetadataDict())
        print(cfmask.getNoDataValues())

        # create landsat 453 stack
        ls4 = operator.inputRaster.getRaster('scene/LT51940242010189KIS01_sr_band4')
        ls5 = operator.inputRaster.getRaster('scene/LT51940242010189KIS01_sr_band5')
        ls3 = operator.inputRaster.getRaster('scene/LT51940242010189KIS01_sr_band3')

        ls4Array, ls5Array, ls3Array = [raster.getImageArray(overlap=overlap) for raster in [ls4, ls5, ls3]]
        ls453Array = numpy.int16(numpy.vstack([ls4Array, ls5Array, ls3Array]))
        print(ls453Array.shape)

        # write bands individual
        ls453A = operator.outputRaster.getRaster(key='ls453A')
        ls453A.initialize(bands=3)
        for band, array in zip (ls453A.getBandIterator(), ls453Array):
            band.setArray(array=array, overlap=overlap)

        # write band stack
        ls453B = operator.outputRaster.getRaster(key='ls453B')
        ls453B.setImageArray(array=ls453Array, overlap=overlap)

        # set image no data and metadata
        for ls453 in [ls453A, ls453B]:
            ls453.setNoDataValue(value=ls3.getNoDataValue())
            ls453.setMetadataItem(key='my key', value=42, domain='ENVI')
            ls453.setMetadataDict({'ENVI' : {'my key' : 42}})

        # set band no data and metadata
        for ls453 in [ls453A, ls453B]:
            for band in ls453.getBandIterator():
                band.setNoDataValue(value=ls3.getNoDataValue())
                band.setMetadataItem(key='my key', value=42, domain='ENVI')
                band.setDescription(value='Hello World')

def run():
    test_applier()


if __name__ == '__main__':
    print(outdir)
    run()
