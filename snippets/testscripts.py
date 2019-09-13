
#required packages that are not delivered with the EnMAP-Box
import qgis
import PyQt5.QtCore
from osgeo import gdal, ogr, osr
import pip
import setuptools
import numpy
import scipy
import sklearn


assert numpy.version.version >= '1.10.0'
assert sklearn.__version__ >= '0.19.0'


print('All required packages available')