from enmapboxprocessing.driver import Driver
from enmapboxprocessing.raster import RasterReader
from enmapboxprocessing.test.testcase import TestCase
from enmapboxtestdata import enmap


class TestRasterProcessing(TestCase):

    def test_multiband_io(self):
        raster = RasterReader(enmap)
        array = raster.array()
        options = ['COMPRESS=LZW', 'INTERLEAVE=BAND']
        outraster = Driver('c:/vsimem/enmap.tif', options=options).createFromArray(array)
        outraster.setNoDataValue(raster.noDataValue())
        outraster.setMetadata(raster.metadata())

    def test_blockwise_multiband_io(self):
        raster = RasterReader(enmap)
        options = ['COMPRESS=LZW', 'INTERLEAVE=BAND']
        outraster = Driver('c:/vsimem/enmap.tif', options=options).createLike(raster)
        for block in raster.walkGrid(50, 50):
            array = raster.array(block.xOffset, block.yOffset, block.width, block.height)
            print(array[0].shape)
            outraster.writeArray(array, block.xOffset, block.yOffset)
        outraster.setNoDataValue(raster.noDataValue())
        outraster.setMetadata(raster.metadata())

    def test_blockwise_band_io(self):
        raster = RasterReader(enmap)
        options = ['COMPRESS=LZW', 'INTERLEAVE=BAND']
        outraster = Driver('c:/vsimem/enmap.tif', options=options).createLike(raster)
        for block in raster.walkGrid(50, 50):
            for bandNo in range(1, raster.bandCount() + 1):
                array = raster.array2d(bandNo, block.xOffset, block.yOffset, None, block.width, block.height)
                outraster.writeArray2d(array, bandNo, block.xOffset, block.yOffset)
                print(bandNo, array.shape)

        outraster.setNoDataValue(raster.noDataValue())
        outraster.setMetadata(raster.metadata())


    def test_nativeBlocks(self):
        raster = RasterReader(enmap)
        blockSizeX, blockSizeY = raster.gdalBand(1).GetBlockSize()
        for block in raster.walkGrid(blockSizeX, blockSizeY):
            print(block)
