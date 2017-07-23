import re, os
from osgeo import gdal, gdal_array

pathESL = r'/Users/benjamin.jakimow/Repositories/QGIS_Plugins/enmap-box/snippets/esl/SpecLib_Berlin_Urban_Gradient_2009_244bands.sli'
pathVrt = r'/Users/benjamin.jakimow/Repositories/QGIS_Plugins/enmap-box/snippets/esl/esl.vrt'


from enmapbox.gui.spectrallibraries import SpectralProfile, SpectralLibrary
SpecLIB = SpectralLibrary.readFrom(pathESL)

SpecLIB.plot()

