class HUBFLOWError(Exception):
    pass

class FlowObjectPickleFileError(HUBFLOWError):
    '''File is not a valid pickle file.'''

class FlowObjectTypeError(HUBFLOWError):
    '''Wrong flow object type.'''