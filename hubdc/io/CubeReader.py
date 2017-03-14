from osgeo import gdal, gdalconst
from hubdc.model.PixelGrid import PixelGrid
from hubdc.model.Cube import Cube
from hubdc.model.Dataset import Dataset


class CubeReader(object):

    def __init__(self, referenceGrid, **kwargsWarpOptions):
        assert isinstance(referenceGrid, PixelGrid)
        self.referenceGrid = referenceGrid
        self.kwargsWarpOptions = kwargsWarpOptions
        self.filenames = list()
        self.keys = list()
        self.kwargss = list()

    def __setitem__(self, key, filenameOrFilenameKwargs):
        if isinstance(filenameOrFilenameKwargs, tuple):
            filename, kwargs = filenameOrFilenameKwargs
        else:
            filename, kwargs = filenameOrFilenameKwargs, dict()
        self.addImage(key, filename, **kwargs)

    def addImage(self, key, filename, **kwargsWarpOptions):
        kwargs = kwargsWarpOptions.copy()
        kwargs.update(self.kwargsWarpOptions)
        self.filenames.append(filename)
        self.keys.append(key)
        self.kwargss.append(kwargs)

    def read(self):
        # see **kwargs here http://gdal.org/python/osgeo.gdal-module.html#WarpOptions

        cube = Cube(self.referenceGrid)
        for filename, key, kwargs in zip(self.filenames, self.keys, self.kwargss):

            xRes, yRes, dstSRS = (getattr(self.referenceGrid, key) for key in ('xRes', 'yRes', 'projection'))
            outputBounds = tuple(getattr(self.referenceGrid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax'))

            warpOptions = gdal.WarpOptions(format='MEM', outputBounds=outputBounds, xRes=xRes, yRes=yRes, dstSRS=dstSRS, **kwargs)
            ds = gdal.Warp(destNameOrDestDS='', srcDSOrSrcDSTab=filename, options=warpOptions)
            dataset = Dataset(ds)
            cube.addDataset(dataset=dataset, key=key)

        return cube

    @staticmethod
    def makeWarpOptions(outputBoundsSRS=None,
                        targetAlignedPixels=False,
                        width=0, height=0,
                        srcSRS=None,
                        srcAlpha=False, dstAlpha=False,
                        warpOptions=None, errorThreshold=None,
                        warpMemoryLimit=None, outputType=gdalconst.GDT_Unknown,
                        workingType=gdalconst.GDT_Unknown, resampleAlg=None,
                        srcNodata=None, dstNodata=None, multithread=False,
                        tps=False, rpc=False, geoloc=False, polynomialOrder=None,
                        transformerOptions=None, cutlineDSName=None,
                        cutlineLayer=None, cutlineWhere=None, cutlineSQL=None, cutlineBlend=None, cropToCutline=False,
                        copyMetadata=True, metadataConflictValue=None,
                        setColorInterpretation=False,
                        callback=None, callback_data=None):

        kwargs = {'outputBoundsSRS': outputBoundsSRS,
                  'targetAlignedPixels': targetAlignedPixels,
                  'width': width, 'height': height,
                  'srcSRS': srcSRS,
                  'srcAlpha': srcAlpha, 'dstAlpha': dstAlpha,
                  'warpOptions': warpOptions, 'errorThreshold': errorThreshold,
                  'warpMemoryLimit': warpMemoryLimit, 'outputType': outputType,
                  'workingType': workingType, 'resampleAlg': resampleAlg,
                  'srcNodata': srcNodata, 'dstNodata': dstNodata, 'multithread': multithread,
                  'tps': tps, 'rpc': rpc, 'geoloc': geoloc, 'polynomialOrder': polynomialOrder,
                  'transformerOptions': transformerOptions, 'cutlineDSName': cutlineDSName,
                  'cutlineLayer': cutlineLayer, 'cutlineWhere': cutlineWhere, 'cutlineSQL': cutlineSQL, 'cutlineBlend': cutlineBlend, 'cropToCutline': cropToCutline,
                  'copyMetadata': copyMetadata, 'metadataConflictValue': metadataConflictValue,
                  'setColorInterpretation': setColorInterpretation,
                  'callback': callback, 'callback_data': callback_data}

        return kwargs
