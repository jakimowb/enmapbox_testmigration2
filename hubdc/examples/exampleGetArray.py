from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator

def script():

    # use grid from input file, but enlarge the resolution
    grid = PixelGrid.fromFile(r'C:\Work\data\gms\LC81940242015235LGN00_sr.img')
    grid.xRes = grid.yRes = 3000
    applier = Applier(grid=grid)

    applier.setInput('LC8', filename=r'C:\Work\data\gms\LC81940242015235LGN00_sr.img')
    applier.setInputList('LC8_LE7', filenames=[r'C:\Work\data\gms\LC81940242015235LGN00_sr.img', r'C:\Work\data\gms\LE71940242015275NSG00_sr.img'])

    applier.run(ufuncClass=SimpleReader)

class SimpleReader(ApplierOperator):

    def ufunc(self):

        print('\nread image array')
        print(self.getArray('LC8').shape)

        print('\nread image band array')
        print(self.getArray('LC8', indicies=3).shape)

        print('\nread image band subset array')
        print(self.getArray('LC8', indicies=[0, 3, 5]).shape)

        print('\nread image band array by wavelength (red)')
        print(self.getArray('LC8', wavelength=655).shape)

        print('\nread image band array subset by wavelength (red and nir)')
        print(self.getArray('LC8', wavelength=[655, 865]).shape)

        print('\nread image list arrays')
        for array in self.getArrayIterator('LC8_LE7'):
            print(array.shape)

        print('\nread image list band arrays (fixed band index for all images)')
        for array in self.getArrayIterator('LC8_LE7', indicies=3):
            print(array.shape)

        print('\nread image list band arrays (variable band index for each image)')
        for array in self.getArrayIterator('LC8_LE7', indicies=[6, 5]):
            print(array.shape)

        print('\nread image list band arrays (variable band indicies for each image)')
        for array in self.getArrayIterator('LC8_LE7', indicies=[[1, 2, 3], [3, 2, 1]]):
            print(array.shape)

        print('\nread image list band arrays by wavelength (single wavelength)')
        for array in self.getArrayIterator('LC8_LE7', wavelength=655):
            print(array.shape)

        print('\nread image list band arrays by wavelength (multiple wavelength)')
        for array in self.getArrayIterator('LC8_LE7', wavelength=[655, 865]):
            print(array.shape)

if __name__ == '__main__':
    script()
