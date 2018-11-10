from astropy.convolution import Gaussian2DKernel

kernel = Gaussian2DKernel(x_stddev=1, y_stddev=1)
