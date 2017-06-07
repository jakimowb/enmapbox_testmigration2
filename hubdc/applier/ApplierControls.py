from hubdc.model.PixelGrid import PixelGrid



FOOTPRINT_UNION, FOOTPRINT_INTERSECT = range(2)
RESOLUTION_MIN, RESOLUTION_MAX, RESOLUTION_AVERAGE = range(3)

class ApplierControls(object):

    def __init__(self):

        self.setWindowXSize()
        self.setWindowYSize()
        self.setNumThreads()
        self.setNumWriter()
        self.setCreateEnviHeader()
        self.setAutoFootprint()
        self.setAutoResolution()
        self.setProjection()
        self.setReferenceGrid()
        self.setGDALCacheMax()
        self.setGDALSwathSize()
        self.setGDALDisableReadDirOnOpen()
        self.setGDALMaxDatasetPoolSize()

    def setWindowXSize(self, windowxsize=256):
        self.windowxsize = windowxsize

    def setWindowYSize(self, windowysize=256):
        self.windowysize = windowysize

    def setWindowFullSize(self):
        veryLargeNumber = 10**20
        self.setWindowXSize(veryLargeNumber)
        self.setWindowYSize(veryLargeNumber)

    def setNumThreads(self, nworker=None):
        self.nworker = nworker

    def setNumWriter(self, nwriter=None):
        self.nwriter = nwriter

    def setCreateEnviHeader(self, createEnviHeader=False):
        self.createEnviHeader = createEnviHeader

    def setAutoFootprint(self, footprintType=FOOTPRINT_UNION):
        self.footprintType = footprintType

    def setAutoResolution(self, resolutionType=RESOLUTION_MIN):
        self.resolutionType = resolutionType

    def setProjection(self, projection=None):
        self.projection = projection

    def setReferenceGrid(self, grid=None):
        self.referenceGrid = grid

    def setReferenceImage(self, filename):
        self.setReferenceGrid(grid=PixelGrid.fromFile(filename))

    def setGDALCacheMax(self, bytes=100*2**20):
        self.cacheMax = bytes

    def setGDALSwathSize(self, bytes=100*2**20):
        self.swathSize = bytes

    def setGDALDisableReadDirOnOpen(self, disable=True):
        self.disableReadDirOnOpen = disable

    def setGDALMaxDatasetPoolSize(self, nfiles=100):
        self.maxDatasetPoolSize = nfiles

    @property
    def multiprocessing(self):
        return self.nworker is not None

    @property
    def multiwriting(self):
        return self.nwriter is not None

    def makeAutoGrid(self, inputs):

        grids = [PixelGrid.fromFile(input.filename) for input in inputs.values()]

        if self.projection is None:
            grid = PixelGrid.fromFile(inputs.values()[0].filename)
            for input in inputs.values():
                if not grid.equalProjection(PixelGrid.fromFile(input.filename)):
                    raise Exception('input projections do not match')
            projection = grid.projection
        else:
            projection = self.projection

        from numpy import array
        xMins, xMaxs, yMins, yMaxs = array([grid.reprojectExtent(targetProjection=projection) for grid in grids]).T
        if self.footprintType == FOOTPRINT_UNION:
            xMin = xMins.min()
            xMax = xMaxs.max()
            yMin = yMins.min()
            yMax = yMaxs.max()
        elif self.footprintType == FOOTPRINT_INTERSECT:
            xMin = xMins.max()
            xMax = xMaxs.min()
            yMin = yMins.max()
            yMax = yMaxs.min()
            if xMax <= xMin or yMax <= yMin:
                raise Exception('input extents do not intersect')
        else:
            raise ValueError('unknown footprint type')

        xResList = array([grid.xRes for grid in grids])
        yResList = array([grid.yRes for grid in grids])
        if self.resolutionType == RESOLUTION_MIN:
            xRes = xResList.min()
            yRes = yResList.min()
        elif self.resolutionType == RESOLUTION_MAX:
            xRes = xResList.max()
            yRes = yResList.max()
        elif self.resolutionType == RESOLUTION_AVERAGE:
            xRes = xResList.mean()
            yRes = yResList.mean()
        else:
            raise ValueError('unknown resolution type')

        return PixelGrid(projection=projection, xRes=xRes, yRes=yRes, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
