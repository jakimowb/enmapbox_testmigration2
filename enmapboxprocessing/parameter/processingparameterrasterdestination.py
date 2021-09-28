import pathlib

from qgis._core import QgsProcessingParameterRasterDestination, QgsProcessingParameters


class ProcessingParameterRasterDestination(QgsProcessingParameterRasterDestination):

    def __init__(
            self, name: str, description: str, defaultValue=None, optional=False, createByDefault=True,
            allowTif=True, allowEnvi=False, allowVrt=False
    ):
        super().__init__(name, description, defaultValue, optional, createByDefault)
        self.optional = optional
        self.allowTif = allowTif
        self.allowEnvi = allowEnvi
        self.allowVrt = allowVrt

    def clone(self):
        print(self)
        print(self.name(), self.description(), self.defaultValue(), self.optional, self.createByDefault(),
            self.allowTif, self.allowEnvi, self.allowVrt)
        copy = ProcessingParameterRasterDestination(
            self.name(), self.description(), self.defaultValue(), self.optional, self.createByDefault(),
            self.allowTif, self.allowEnvi, self.allowVrt
        )
        copy.setFlags(self.flags())
        return copy

    def defaultFileExtension(self):
        if self.allowTif:
            return 'tif'
        if self.allowEnvi:
            return 'bsq'
        if self.allowVrt:
            return 'vrt'

    def supportedOutputRasterLayerExtensions(self):
        extensions = list()
        if self.allowTif:
            extensions.append('tif')
        if self.allowEnvi:
            extensions.extend(['bsq', 'bil', 'bip'])
        if self.allowVrt:
            extensions.append('vrt')
        return extensions

    def parameterAsOutputLayer(self, definition, value, context):
        return super(QgsProcessingParameterRasterDestination, self).parameterAsOutputLayer(definition, value, context)

    def isSupportedOutputValue(self, value, context):
        output_path = QgsProcessingParameters.parameterAsOutputLayer(self, value, context)
        extensions = self.supportedOutputRasterLayerExtensions()
        if pathlib.Path(output_path).suffix.lower()[1:] not in extensions:
            extensions = ', '.join([f'"{extension}"' for extension in extensions])
            message = f'unsupported file extension, use {extensions} instead: {self.description()}'
            return False, message
        return True, ''
