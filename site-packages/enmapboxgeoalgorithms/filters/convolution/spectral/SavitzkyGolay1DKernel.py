from astropy.convolution import Kernel1D
from scipy.signal import savgol_coeffs

kernel = Kernel1D(array=savgol_coeffs(window_length=11, polyorder=3, deriv=0))
