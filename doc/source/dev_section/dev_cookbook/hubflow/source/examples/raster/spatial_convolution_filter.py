from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
from astropy.convolution import Gaussian2DKernel, Kernel2D
import enmapboxtestdata
from hubflow.core import *

raster = Raster(filename=enmapboxtestdata.enmap)

# apply a Gaussian filter
kernel = Gaussian2DKernel(x_stddev=1, y_stddev=1, x_size=7, y_size=7)
print(np.round(kernel.array, 3))
filteredGaussian = raster.convolve(filename='filteredGaussian.bsq', kernel=kernel)

# apply a Highpass filter
kernel = Kernel2D(array=[[-1, -1, -1],
                         [-1,  8, -1],
                         [-1, -1, -1]])
print(kernel.array)
filteredHighpass = raster.convolve(filename='filteredHighpass.bsq', kernel=kernel)

# END

MapViewer().addLayer(filteredGaussian.dataset().mapLayer().initTrueColorRenderer()).save(basename(__file__).replace('.py', '1.png'))
MapViewer().addLayer(filteredHighpass.dataset().mapLayer().initTrueColorRenderer()).save(basename(__file__).replace('.py', '2.png'))
