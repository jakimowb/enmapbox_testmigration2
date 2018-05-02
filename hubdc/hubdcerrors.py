class HUBDCError(Exception):
    pass

class AccessGridOutOfRangeError(HUBDCError):
    '''Read or write access grid is out of dataset grid range.'''


class ArrayShapeMismatchError(HUBDCError):
    '''Array shape is not matching the expected shape.'''

class FileNotExistError(HUBDCError):
    '''File not exist.'''


class FileOpenError(HUBDCError):
    '''Failed to open an input or output file.'''


class InvalidGDALDatasetError(HUBDCError):
    '''gdal.Open returned None.'''


class InvalidGDALDriverError(HUBDCError):
    '''gdal.GetDriverByName returned None.'''


class InvalidOGRDriverError(HUBDCError):
    '''ogr.GetDriverByName returned None.'''


class InvalidOGRDataSourceError(HUBDCError):
    '''ogr.Open returned None.'''


class ApplierOperatorTypeError(HUBDCError):
    '''Applier operator must be a subclass of :class:`~hubdc.applier.ApplierOperator` or function.'''


class ApplierOutputRasterNotInitializedError(HUBDCError):
    '''Applier output raster is not initialized, use :meth:`~hubdc.applier.ApplierOutputRaster.initialize`.'''


class MissingApplierProjectionError(HUBDCError):
    '''Applier projection was not explicitely set and could not be derived from raster inputs.'''


class MissingApplierExtentError(HUBDCError):
    '''Applier extent was not explicitely set and could not be derived from raster inputs.'''

class MissingApplierResolutionError(HUBDCError):
    '''Applier resolution was not explicitely set and could not be derived from raster inputs.'''

class UnknownApplierAutoExtentOption(HUBDCError):
    '''See :class:`~hubdc.applier.Options.AutoExtent` for valid options.'''


class UnknownApplierAutoResolutionOption(HUBDCError):
    '''See :class:`~hubdc.applier.Options.AutoResolution` for valid options.'''

