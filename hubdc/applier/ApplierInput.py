class ApplierInput(object):

    def __init__(self, filename, **warpKwargs):
        self.filename = filename
        self.warpKwargs = warpKwargs