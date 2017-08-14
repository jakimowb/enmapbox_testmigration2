import re, os
from osgeo import gdal, gdal_array

pathESL = r'/Users/benjamin.jakimow/Repositories/QGIS_Plugins/enmap-box/snippets/esl/SpecLib_Berlin_Urban_Gradient_2009_244bands.sli'
pathVrt = r'/Users/benjamin.jakimow/Repositories/QGIS_Plugins/enmap-box/snippets/esl/esl.vrt'

from enmapbox.testdata.UrbanGradient import Speclib as pathSpecLib
from enmapbox.gui.spectrallibraries import SpectralProfile, SpectralLibrary
SpecLIB = SpectralLibrary.readFrom(pathSpecLib)
p0 = SpecLIB[0]
p0.plot()
SpecLIB.plot()

