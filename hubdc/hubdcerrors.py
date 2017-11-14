class HUBDCError(Exception):
    pass


class FileOpenError(HUBDCError):
    '''Failed to open an input or output file.'''


class ApplierOperatorTypeError(HUBDCError):
    '''Applier operator must be a subclass of :class:`~hubdc.applier.ApplierOperator` or function.'''


class MissingApplierProjectionError(HUBDCError):
    '''Applier projection was not explicitely set and could not be derived from raster inputs.'''


class MissingApplierExtentError(HUBDCError):
    '''Applier extent was not explicitely set and could not be derived from raster inputs.'''

class UnknownApplierAutoExtentOption(HUBDCError):
    '''See :class:`~hubdc.applier.Options.AutoExtent` for valid options.'''

class UnknownApplierAutoResolutionOption(HUBDCError):
    '''See :class:`~hubdc.applier.Options.AutoResolution` for valid options.'''
