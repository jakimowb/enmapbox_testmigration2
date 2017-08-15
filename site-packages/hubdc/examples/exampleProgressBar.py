from hubdc.applier import PixelGrid, Applier, ApplierOperator, CUIProgressBar, SilentProgressBar

def script():

    #filename = r'H:\EuropeanDataCube\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img'
    filename = r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img'

    grid = PixelGrid(projection='EPSG:3035', xRes=1000, yRes=1000, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)
    applier = Applier()
    applier.setInput('in', filename=filename)
    applier.setOutput('out', filename=r'c:\output\out.tif', format='ENVI')
    applier.controls.setProgressBar(progressBar=SilentProgressBar())
    applier.apply(operator=SimpleIO)

class SimpleIO(ApplierOperator):

    def ufunc(self):
        pass


if __name__ == '__main__':
    script()
