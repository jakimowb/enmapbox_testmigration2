from osgeo import gdal

class ApplierInput(object):

    def __init__(self, filename, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.):
        self.filename = filename
        self.options = {'resampleAlg' : resampleAlg, 'errorThreshold' : errorThreshold}