from astropy.convolution import Trapezoid1DKernel

kernel = Trapezoid1DKernel(width=5, slope=1)
