import re, os
from osgeo import gdal, gdal_array


from enmapboxtestdata import speclib as pathSpecLib
from enmapbox.gui.spectrallibraries import SpectralProfile, SpectralLibrary
SpecLIB = SpectralLibrary.readFrom(pathSpecLib)
p0 = SpecLIB[0]
p0.plot()
SpecLIB.plot()

