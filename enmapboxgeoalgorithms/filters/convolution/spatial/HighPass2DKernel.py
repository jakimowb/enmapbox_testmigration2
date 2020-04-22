from astropy.convolution import Kernel2D

kernel = Kernel2D(array=
  [[-1, -1, -1],
   [-1,  8, -1],
   [-1, -1, -1]])
