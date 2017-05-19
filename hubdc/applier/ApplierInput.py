from osgeo import gdal

class ApplierInput(object):

    def __init__(self, filename, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.125, warpMemoryLimit=100*2**20, multithread=False):
        self.filename = filename
        self.options = {'resampleAlg' : resampleAlg,
                        'errorThreshold' : errorThreshold,
                        'warpMemoryLimit' : warpMemoryLimit,
                        'multithread' : multithread}