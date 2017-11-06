#import matplotlib
#matplotlib.use('QT4Agg')
#from matplotlib import pyplot
import numpy
from osgeo import gdal
from tempfile import gettempdir
from os.path import join, exists, basename, dirname
import enmapboxtestdata
from hubdc.applier import (Applier, ApplierOperator, ApplierInputRaster, ApplierInputVector, ApplierInputRasterArchive, ApplierOutputRaster, applierInputRasterGroupFromFolder,
                           PixelGrid, CreateFromArray)


outdir = join(gettempdir(), 'hubdc_test')
grid3035 = PixelGrid(projection='EPSG:3035', xRes=30, yRes=30, xMin=4543884, xMax=4545819, yMin=3268692, yMax=3270928)

testGrid = PixelGrid(projection='EPSG:3035', xRes=1, yRes=1, xMin=0, xMax=3, yMin=0, yMax=3)
testArray = numpy.array([[-1, -1, 30],
                         [-1, -1, -1],
                         [-1, 0, 0]])

def getTestFilename():
    testFilename = join(outdir, 'testImageCategory.img')
    if not exists(testFilename):
        ds = CreateFromArray(pixelGrid=testGrid, array=testArray, dstName=testFilename, format='ENVI')
        ds.setNoDataValue(-1)
        ds.close()
    return testFilename
testFilename = getTestFilename()

def ioImage():

    applier = Applier()
    applier.inputRaster.setRaster('inraster', ApplierInputRaster(enmapboxtestdata.enmap))
    applier.inputVector.setVector('invector', ApplierInputVector(enmapboxtestdata.landcover))
    applier.outputRaster.setRaster('outraster', ApplierOutputRaster(join(outdir, 'outraster')))

    class Operator(ApplierOperator):
        def ufunc(self):
            array = self.inputRaster.getRaster('inraster').getImageArray()
            mask = self.inputVector.getVector('invector').getImageArray()
            self.outputRaster.getRaster('outraster').setArray(array=array[0:3])

    applier.apply(operator=Operator)

def readCategory():

    print('1m resolution category')
    print(testArray)

    applier = Applier()
    applier.controls.setResolution(xRes=3, yRes=3)
    applier.inputRaster.setInput('inraster', ApplierInputRaster(testFilename))

    class Operator(ApplierOperator):
        def ufunc(self):

            inraster = self.inputRaster.getInput('inraster')
            print('')
            print('3m nn-resampled raw')
            array = inraster.getImageArray()
            print(array)
            assert array[0,0,0] == -1

            print('3m average-resampled raw')
            array = inraster.getImageArray(resampleAlg=gdal.GRA_Average)
            print(array)
            assert array[0,0,0] == 10

            print('3m category')
            array = inraster.getBinarizedCategoryArray(categories=[-1, 0, 30])
            print(array)
            assert round(array[0, 0, 0], 2) == round(6./9, 2)
            assert round(array[1, 0, 0], 2) == round(2./9, 2)
            assert round(array[2, 0, 0], 2) == round(1./9, 2)

    applier.apply(operator=Operator)

def readVector():
    applier = Applier()
    applier.controls.setReferenceGrid(grid=grid3035.newResolution(3, 3))
    applier.controls.setWindowFullSize()

    applier.setInputVector('invector', filename=enmapboxtestdata.landcover)
    applier.setInputVector('invectorList', filename=[enmapboxtestdata.landcover, enmapboxtestdata.landcover])
    applier.setInputVector('invectorDict', filename={'a':enmapboxtestdata.landcover, 'b':enmapboxtestdata.landcover})
    applier.setInputVector('invectorMixed', filename={'single':enmapboxtestdata.landcover,
                                                      'list':[enmapboxtestdata.landcover],
                                                      'dict':{'a':enmapboxtestdata.landcover, 'b':enmapboxtestdata.landcover}})
    applier.setOutputRaster('outraster', filename=join(outdir, 'rasteredLevel2.img'))
    applier.setOutputRaster('outraster2', filename=join(outdir, 'rasteredLevel2Fraction.img'))

    class Operator(ApplierOperator):
        def ufunc(self):
            invector = self.getInputVector('invector')
            inraster = invector.getImageArray().shape
            array = invector.getImageArray(burnAttribute='Level_2_ID', dtype=numpy.uint8)
            self.setArray('outraster', array=array)
            array2 = invector.getBinarizedCategoryArray(categories=[0,1,2,3,4,5,6], burnAttribute='Level_2_ID')
            self.setArray('outraster2', array=array2)

    applier.apply(operator=Operator)

def inputFromFolder():
    applier = Applier()
    #applier.controls.setNumThreads(1)
    #applier.controls.setNumWriter(1)
    applier.controls.setWindowFullSize()
    grid = PixelGrid.fromFile(r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img').pixelBuffer(100)
    applier.controls.setReferenceGrid(grid=grid)
    applier.inputRasterArchive.setArchive(key='landsat2', value=ApplierInputRasterArchive(folder=r'C:\Work\data\gms\landsat', extensions=['img']))

    applier.apply(operator=InputFromFolder)

class InputFromFolder(ApplierOperator):
    def ufunc(self):

        for k in sorted(self.inputRasterArchive.getArchive(key='landsat2').getIntersection().getFlatRasterKeys()):
            print(k)



#           outraster = self.getOutputRaster('outraster')
#           outraster.setArray(array=inraster.getImageArray())
#           outraster.setMetadataItem(key='wavelength', value=inraster.getMetadataItem(key='wavelength', domain='ENVI'), domain='ENVI')


def createPNG():
    from hubdc.model import Create
    #ds = Create(pixelGrid, bands=1, eType=gdal.GDT_Float32, dstName='', format='PNG', creationOptions=[])

if __name__ == '__main__':
    print(outdir)
    ioImage()
    #readCategory()
    #readVector()
    #inputFromFolder()

