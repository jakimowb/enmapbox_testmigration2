class ApplierOutput(object):

    def __init__(self, filename, format='GTiff', creationOptions=[]):
        self.filename = filename
        self.options = {'format': format, 'creationOptions': creationOptions}
