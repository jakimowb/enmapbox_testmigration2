Wavelength Information
======================

If wavelength information is defined for each band of a
raster image, the EnMAP-Box can use it to easily select pre-defined band combinations or to
better compare spectral profiles of sensors with different number of bands.

The wavelength information needs to be defined similar to the ENVI metadata standard:

1. *wavelength units* defines the metric unit of the wavelength, e.g. nm, mu, cm,..

2. *wavelength* defines the band values in *wavelength units*, e.g. 450 nm.

The wavelength information needs to be accessible by the GDAL metadata model.

The wavelength information needs to be defined in the image metadata and for each band.


