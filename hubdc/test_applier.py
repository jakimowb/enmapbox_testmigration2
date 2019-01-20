from __future__ import print_function
from tempfile import gettempdir
from os.path import join, exists, basename, dirname
from unittest import TestCase

from hubdc.applier import *
from hubdc.testdata import LT51940232010189KIS01, LT51940242010189KIS01, BrandenburgDistricts, root

outdir = join(gettempdir(), 'hubdc_test')

class TestApplierInputRaster(TestCase):

    def test(self):
        class Operator(ApplierOperator):
            def ufunc(operator, *args, **kwargs):
                overlap = 10
                cfmask = operator.inputRaster.raster(key='cfmask')
                cfmaskArray = cfmask.array()
                print(cfmaskArray.shape)
                print(cfmask.array(indices=[0], overlap=overlap).shape)

                print(cfmask.fractionArray(categories=[0, 1, 2, 3, 4, 255], overlap=overlap).shape)
                print(cfmask.sample(mask=cfmaskArray == 1).shape)  # water sample
                print(cfmask.sample(mask=cfmaskArray == 31241).shape)  # empty sample

                # read raster metadata
                print(cfmask.metadataItem(key='abc', domain=''))
                print(cfmask.metadataDict())
                print(cfmask.noDataValues())
                print(cfmask.noDataValue())
                print(cfmask.categoryColors(index=0))
                print(cfmask.categoryNames(index=0))

        applier = Applier()
        applier.inputRaster.setRaster(key='cfmask', value=ApplierInputRaster(filename=LT51940232010189KIS01.cfmask))
        print(applier.inputRaster.raster(key='cfmask'))
        applier.apply(operatorType=Operator)

        applier.controls.setProjection(projection=Projection.wgs84())
        applier.controls.setExtent(
            extent=openRasterDataset(filename=LT51940232010189KIS01.cfmask).grid().extent().reproject(
                projection=Projection.wgs84()))
        applier.controls.setResolution(resolution=0.01)
        applier.apply(operatorType=Operator)

class TestApplierInputRasterGroup(TestCase):
    def test(self):
        class Operator(ApplierOperator):
            def ufunc(operator, *args, **kwargs):
                overlap = 10
                cfmask = operator.inputRaster.raster(key='LT51940242010189KIS01/LT51940242010189KIS01_cfmask')
                cfmaskArray = cfmask.array()
                print(cfmaskArray.shape)
                print(cfmask.fractionArray(categories=[0, 1, 2, 3, 4, 255], overlap=overlap).shape)
                print(applier.inputRaster.findRaster(ufunc=lambda key, raster: key.endswith('cfmask')))
                print(applier.inputRaster.findRaster(ufunc=lambda key, raster: False))
                print(applier.inputRaster.findRasterKey(ufunc=lambda key, raster: key == 'LT51940242010189KIS01'))
                print(applier.inputRaster.findRasterKey(ufunc=lambda key, raster: False))
                print(list(applier.inputRaster.flatRasters()))
                print(list(applier.inputRaster.flatRasterKeys()))
                print(list(applier.inputRaster.rasters()))
                print(list(applier.inputRaster.rasterKeys()))
                print(list(applier.inputRaster.groups()))
                print(list(applier.inputRaster.groupKeys()))

        applier = Applier()

        # add scene folder
        applier.inputRaster.setGroup(key='LT51940242010189KIS01',
                                     value=ApplierInputRasterGroup.fromFolder(folder=LT51940242010189KIS01.root,
                                                                              extensions=['.img']))
        applier.inputRaster.setGroup(key='landsat/LT51940242010189KIS01',
                                     value=ApplierInputRasterGroup.fromFolder(folder=LT51940242010189KIS01.root,
                                                                              extensions=['.img']))
        applier.inputRaster.setRaster(key='cfmask', value=ApplierInputRaster(filename=LT51940232010189KIS01.cfmask))
        print(applier.inputRaster.group(key='LT51940242010189KIS01'))
        applier.apply(operatorType=Operator)

        # scene folder without cfmask
        print(ApplierInputRasterGroup.fromFolder(folder=LT51940242010189KIS01.root, extensions=['.img'],
                                                 ufunc=lambda basename, **kwarg: not basename.endswith('cfmask')))

        # archive folder
        print(ApplierInputRasterGroup.fromFolder(folder=root, extensions=['.img']))

'''
class TestApplierInputRasterIndex(TestCase):

    def test(self):
        # create index from folder
        index = ApplierInputRasterIndex.fromFolder(folder=root, extensions=['.img'])
        print(index)
        # - pickle and unpickle index
        filename = join(outdir, 'index.pkl')
        index.pickle(filename=filename)
        index = ApplierInputRasterIndex.unpickle(filename=filename)
        print(index)
        # - get intersection that covers both scenes
        grid = openRasterDataset(filename=LT51940232010189KIS01.cfmask).grid()
        index2 = index.intersection(grid=grid)
        print(index2)
        # - get intersection that covers only one scene
        grid = grid.subset(offset=Pixel(x=10, y=10), size=Size(x=1, y=1))  # 1x1 pixel extent
        index3 = index.intersection(grid=grid)
        print(index3)
        print(ApplierInputRasterGroup.fromIndex(index=index))
'''


class TestApplierInputVector(TestCase):

    def test(self):
        class Operator(ApplierOperator):
            def ufunc(operator, *args, **kwargs):
                overlap = 10
                vector = operator.inputVector.vector(key='vector')
                print(vector.operator)
                print(vector.array().shape)
                print(vector.fractionArray(categories=[1, 4, 7, 9], categoryAttribute='id').shape)

        # add vector
        applier = Applier()
        applier.controls.setGrid(openRasterDataset(LT51940232010189KIS01.cfmask).grid())
        applier.inputVector.setVector(key='vector', value=ApplierInputVector(filename=BrandenburgDistricts.shp))
        print(applier.inputVector.vector(key='vector'))
        applier.inputVector.setVector(key='vectorFolder/vector',
                                      value=ApplierInputVector(filename=BrandenburgDistricts.shp))
        applier.apply(operatorType=Operator)

        print(list(applier.inputVector.flatVectorKeys()))
        print(list(applier.inputVector.flatVectors()))
        print(list(applier.inputVector.groups()))
        print(list(applier.inputVector.groupKeys()))


class TestApplierOutputRaster(TestCase):
    def test(self):

        class Operator(ApplierOperator):
            def ufunc(operator, *args, **kwargs):
                overlap = 10
                array = operator.full(value=42, bands=1, overlap=overlap)

                # write bands individual
                stack = operator.outputRaster.raster(key='stack')

                # - try writing without initialization
                try:
                    stack.zsize()
                except errors.ApplierOutputRasterNotInitializedError as error:
                    print(error)
                stack.setZsize(zsize=1)
                print(stack.zsize())
                for band, bandArray in zip(stack.bands(), array):
                    band.setArray(array=bandArray, overlap=overlap)  # 2d
                    band.setArray(array=bandArray[None], overlap=overlap)  # 3d
                    band.setArray(array=list(bandArray[None]), overlap=overlap)  # list of 2d

                # write stack at once
                stack.setArray(array=array, overlap=overlap)  # 3d
                stack.setArray(array=list(array), overlap=overlap)  # list of 2d
                stack.setArray(array=array[0], overlap=overlap)  # 2d

                # set image no data, metadata and category names/colors
                stack.setNoDataValue(value=0)
                stack.setNoDataValues(values=[0])
                stack.setMetadataItem(key='my key', value=42, domain='ENVI')
                stack.setMetadataDict({'ENVI': {'my key': 42}})
                stack.band(0).setCategoryNames(['a', 'b', 'c'])
                stack.band(0).setCategoryColors([(1,1,1), (10,10,10), (100,100,100)])

                # set band no data and metadata
                for band in stack.bands():
                    band.setNoDataValue(value=0)
                    band.setMetadataItem(key='my key', value=42, domain='ENVI')
                    band.setDescription(value='Hello World')

                # set/get categories
                stack.setCategoryColors([(0,0,0)])
                stack.setCategoryNames(['class 1'])

                # assess key/values
                print(list(applier.outputRaster.flatRasters()))
                print(list(applier.outputRaster.flatRasterKeys()))
                print(applier.outputRaster.operator)
                print(list(stack.flatList()))

        applier = Applier()
        applier.outputRaster.setRaster(key='stack', value=ApplierOutputRaster(filename=join(outdir, 'stack.img')))
        applier.outputRaster.setRaster(key='folder/stack',
                                       value=ApplierOutputRaster(filename=join(outdir, 'folder', 'stack.img')))
        applier.controls.setGrid(grid=openRasterDataset(LT51940242010189KIS01.cfmask).grid())
        applier.apply(operatorType=Operator)

        applier.inputRaster.operator()
        applier.inputRaster._freeUnpickableResources()

    def test_multiprocessing(self):

        applier = Applier()
        applier.controls.setNumThreads(nworker=2)
        applier.controls.setNumWriter(nwriter=2)
        applier.controls.setGrid(grid=openRasterDataset(LT51940242010189KIS01.cfmask).grid())
        applier.apply(operatorType=Operator)

class Operator(ApplierOperator):
    def ufunc(operator, *args, **kwargs):
        pass


class TestApplier(TestCase):
    def test_apply(self):
        class Operator(ApplierOperator):
            def ufunc(self, *args, **kwargs):
                self.isFirstBlock()
                self.isLastBlock()
                self.isLastXBlock()
                self.isLastYBlock()
                self.iblock()
                self.nblock()
                self.yblock()
                self.xblock()
                self.yblockSize()
                self.xblockSize()
                self.yblockOffset()
                self.xblockOffset()
                self.grid()
                constArray = self.full(value=42)
                constArray = self.full(value=[1, 2, 3], bands=3)

        applier = Applier()
        applier.controls.setGrid(grid=openRasterDataset(LT51940232010189KIS01.cfmask).grid())
        applier.apply(operatorType=Operator)
        applier.apply(operatorType=Operator, overwrite=False)
        applier.apply(operatorFunction=lambda operator, *args, **kwargs: None)

        try:
            applier.apply(operatorType='not a correct operator')
        except errors.ApplierOperatorTypeError:
            pass

        # multiwriter
        applier.controls.setNumWriter(nwriter=2)
        applier.apply(operatorType=Operator)


class TestApplierControls(TestCase):
    def test_set(self):
        operatorFunction = lambda *args, **kwargs: None
        applier = Applier()
        applier.inputRaster.setRaster(key='', value=ApplierInputRaster(filename=LT51940232010189KIS01.cfmask))

        ds = openRasterDataset(filename=LT51940232010189KIS01.cfmask)

        with self.assertRaises(ValueError):
            applier.controls.setBlockSize(blockSize='not a number')

        applier.controls.setBlockSize(255)
        applier.controls.setBlockSize((255, 255))
        applier.controls.setBlockSize(RasterSize(x=255, y=255))
        applier.controls.setBlockFullSize()

        with self.assertRaises(ValueError):
            applier.controls.setResolution(resolution='not a resolution')

        applier.controls.setResolution(None)
        applier.controls.setResolution(30)
        applier.controls.setResolution((30, 30))
        applier.controls.setResolution(Resolution(x=30, y=30))

        applier.controls.setExtent(None)
        applier.controls.setExtent(ds.grid().extent())

        applier.controls.setProjection(Projection.wgs84())

        applier.controls.setGrid(ds.grid())
        applier.controls.setGrid(None)

        applier.controls.setNumThreads(nworker=-1)
        applier.controls.setNumThreads(nworker=None)

        # auto resolution
        applier.controls.setAutoResolution(ApplierOptions.AutoResolution.average)
        applier.apply(operatorFunction=operatorFunction)
        applier.controls.setAutoResolution(ApplierOptions.AutoResolution.minimum)
        applier.apply(operatorFunction=operatorFunction)
        applier.controls.setAutoResolution(ApplierOptions.AutoResolution.maximum)
        applier.apply(operatorFunction=operatorFunction)
        try:
            applier.controls.setAutoResolution(26)
        except errors.UnknownApplierAutoResolutionOption:
            pass
        applier.controls.setAutoResolution()

        # auto extent
        applier.controls.setGrid(None)
        applier.controls.setAutoExtent(ApplierOptions.AutoExtent.union)
        applier.apply(operatorFunction=operatorFunction)
        applier.controls.setAutoExtent(ApplierOptions.AutoExtent.intersection)
        applier.apply(operatorFunction=operatorFunction)
        try:
            applier.controls.setAutoExtent(26)
        except errors.UnknownApplierAutoExtentOption:
            pass


