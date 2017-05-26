from hubdc import PixelGrid, Applier, ApplierOperator

def script():

    filename = r'H:\EuropeanDataCube\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img'
    #filename = r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img'

    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)
    applier = Applier(grid=grid, nworker=0, nwriter=1, windowxsize=256, windowysize=256)
    applier.setInput('in', filename=filename)
    applier.setOutput('out', filename=r'c:\output\out.tif', format='ENVI')
    applier.run(ufuncClass=SimpleIO)

class SimpleIO(ApplierOperator):

    def ufunc(self):
        self.setData('out', array=self.getArray('in'))

        if self.isFirstBlock():
            self.myValue = 42

        if self.isLastBlock():
            self.setMetadataItem('out', 'my value', self.myValue, 'ENVI')

if __name__ == '__main__':
    script()
