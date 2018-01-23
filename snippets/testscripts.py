
#required packages that are not delivered with the EnMAP-Box
import qgis
import PyQt4.QtCore
from osgeo import gdal, ogr, osr
import pip
import setuptools
import numpy
import scipy
import sklearn


def hasMinimumVersion(version, requiredVersion):
    version = [int(n) for n in version.split('.')]
    requiredVersion = [int(n) for n in requiredVersion.split('.')]

    for n1, n2 in zip(version, requiredVersion):
        if n1 < n2:
            return False
    return True

assert hasMinimumVersion(numpy.version.version, '1.10.0')
assert hasMinimumVersion(sklearn.__version__, '0.19.0')
assert sklearn.__version__ == '0.1.9'



print('All required packages available')