from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, Optional, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorLayer,
                        QgsProcessingParameterRasterDestination, QgsProcessingContext, QgsProcessingFeedback,
                        QgsRasterLayer, QgsVectorLayer, QgsProcessingParameterNumber, QgsProcessingParameterDefinition,
                        QgsProcessingParameterField, QgsProcessingParameterBoolean, QgsProcessingParameterEnum, Qgis,
                        QgsProcessingParameterString, QgsProcessingParameterBand, QgsCategorizedSymbolRenderer,
                        QgsPalettedRasterRenderer, QgsProcessingParameterMapLayer, QgsMapLayer,
                        QgsProcessingParameterCoordinateOperation, QgsProcessingParameterAggregate,
                        QgsProcessingParameterExtent, QgsCoordinateReferenceSystem, QgsRectangle,
                        QgsProcessingParameterFileDestination, QgsProcessingParameterExpression,
                        QgsProcessingParameterFile)

from enmapboxprocessing.typing import QgisDataType, CreationOptions, GdalResamplingAlgorithm
from typeguard import typechecked


class AlgorithmCanceledException(Exception):
    pass


@typechecked
class EnMAPProcessingAlgorithm(QgsProcessingAlgorithm):
    O_CREATION_PROFILE = ['GeoTiff', 'Compressed GeoTiff', 'Tiled GeoTiff', 'Tiled and compressed GeoTiff',
                          'ENVI BSQ', 'ENVI BIL', 'ENVI BIP', 'Virtual Raster']
    GTiffProfile, CompressedGTiffProfile, TiledGTiffProfile, TiledAndCompressedGTiffProfile, EnviBsqProfile, \
    EnviBilProfile, EnviBipProfile, VrtProfile = range(8)
    GTiffFormat, EnviFormat, VrtFormat = ['GTiff', 'ENVI', 'VRT']
    GTiffCreationOptions = ['INTERLEAVE=BAND']
    CompressedGTiffCreationOptions = 'INTERLEAVE=BAND COMPRESS=LZW PREDICTOR=2 BIGTIFF=YES'.split()
    TiledGTiffCreationOptions = 'INTERLEAVE=BAND TILED=YES'.split()
    TiledAndCompressedGTiffCreationOptions = 'INTERLEAVE=BAND COMPRESS=LZW PREDICTOR=2 TILED=YES BIGTIFF=YES'.split()
    EnviBsqCreationOptions = 'INTERLEAVE=BSQ'.split()
    EnviBilCreationOptions = 'INTERLEAVE=BIL'.split()
    EnviBipCreationOptions = 'INTERLEAVE=BIP'.split()
    VrtCreationOptions = ['']

    O_RESAMPLE_ALG = 'NearestNeighbour Bilinear Cubic CubicSpline Lanczos Average Mode Min Q1 Med Q3 Max'.split()
    NearestNeighbourResampleAlg, BilinearResampleAlg, CubicResampleAlg, CubicSplineResampleAlg, LanczosResampleAlg, \
    AverageResampleAlg, ModeResampleAlg, MinResampleAlg, Q1ResampleAlg, MedResampleAlg, Q3ResampleAlg, \
    MaxResampleAlg = range(12)

    O_DATA_TYPE = 'Byte Int16 UInt16 Int32 UInt32 Float32 Float64'.split()
    Byte, Int16, UInt16, Int32, UInt32, Float32, Float64 = range(7)

    SkipValue = '[Skip output]'

    def createInstance(self):
        return type(self)()

    def group(self) -> str:
        raise NotImplementedError()

    def displayName(self) -> str:
        raise NotImplementedError()

    def _generateId(self, name):
        nameId = name
        for c in '!?-+/*()[]{}':
            nameId = nameId.replace(c, '')
        nameId = ''.join([s.title() for s in nameId.split(' ')])
        return nameId

    def groupId(self) -> str:
        return self._generateId(self.group())

    def name(self) -> str:
        return self._generateId(self.displayName())

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        raise NotImplementedError

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raise NotImplementedError()

    def parameterDefinition(self, name: str) -> QgsProcessingParameterDefinition:
        parameter = super().parameterDefinition(name)
        assert parameter is not None, name
        return parameter

    def parameterAsLayer(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[QgsMapLayer]:
        return super().parameterAsLayer(parameters, name, context)

    def parameterAsRasterLayer(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[QgsRasterLayer]:
        return super().parameterAsRasterLayer(parameters, name, context)

    def parameterAsVectorLayer(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> QgsVectorLayer:
        return super().parameterAsVectorLayer(parameters, name, context)

    def parameterAsFields(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> List[str]:
        return super().parameterAsFields(parameters, name, context)

    def parameterAsField(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[str]:
        fields = self.parameterAsFields(parameters, name, context)
        if len(fields) == 0:
            return None
        else:
            return fields[0]

    def parameterAsFile(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> str:
        return super().parameterAsFile(parameters, name, context)

    def parameterAsEnum(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> int:
        return super().parameterAsEnum(parameters, name, context)

    def parameterAsString(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> str:
        return super().parameterAsString(parameters, name, context)

    def parameterAsDouble(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[float]:
        if self.parameterIsSet(parameters, name):
            return super().parameterAsDouble(parameters, name, context)
        else:
            return self.parameterDefinition(name).defaultValue()

    def parameterAsInt(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> int:
        return super().parameterAsInt(parameters, name, context)

    def parameterAsInts(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[List[int]]:
        ints = super().parameterAsInts(parameters, name, context)
        if len(ints) == 0:
            return None
        else:
            return ints

    def parameterAsBool(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> bool:
        return super().parameterAsBool(parameters, name, context)

    def parameterAsBoolean(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> bool:
        return super().parameterAsBoolean(parameters, name, context)

    def parameterAsFileOutput(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> str:
        return super().parameterAsFileOutput(parameters, name, context)

    def parameterAsExtent(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext,
            crs: QgsCoordinateReferenceSystem
    ) -> QgsRectangle:
        return super().parameterAsExtent(parameters, name, context, crs)

    def parameterAsQgsDataType(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[QgisDataType]:
        index = self.parameterAsEnum(parameters, name, context)
        if index == -1:
            return None
        label = self.O_DATA_TYPE[index]
        return getattr(Qgis, label)

    def parameterAsGdalResampleAlg(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[GdalResamplingAlgorithm]:
        index = self.parameterAsInt(parameters, name, context)
        if index == -1:
            return None
        label = self.O_RESAMPLE_ALG[index]
        return getattr(gdal, f'GRA_{label}')

    def parameterAsCreationProfile(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Tuple[str, CreationOptions]:
        index = self.parameterAsInt(parameters, name, context)
        format, options = [
            ('GTiff', 'INTERLEAVE=BAND'),
            ('GTiff', 'INTERLEAVE=BAND COMPRESS=LZW PREDICTOR=2 BIGTIFF=YES'),
            ('GTiff', 'INTERLEAVE=BAND TILED=YES'),
            ('GTiff', 'INTERLEAVE=BAND COMPRESS=LZW PREDICTOR=2 TILED=YES BIGTIFF=YES'),
            ('ENVI', 'INTERLEAVE=BSQ'),
            ('ENVI', 'INTERLEAVE=BIL'),
            ('ENVI', 'INTERLEAVE=BIP'),
            ('VRT', '')
        ][index]
        return format, options.split()

    def parameterIsSet(self, parameters: Dict[str, Any], name: str):
        return parameters.get(name, None) is not None

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return super().checkParameterValues(parameters, context)

    def checkParameterVectorClassification(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Tuple[bool, str]:
        renderer = self.parameterAsVectorLayer(parameters, name, context).renderer()
        return (
            isinstance(renderer, QgsCategorizedSymbolRenderer),
            f'Invalid vector classification, '
            f'requires categorized symbol renderer ({self.parameterDefinition(name).description()})'
        )

    def checkParameterRasterClassification(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Tuple[bool, str]:
        layer = self.parameterAsRasterLayer(parameters, name, context)
        renderer = layer.renderer()
        return (
            isinstance(renderer, QgsPalettedRasterRenderer),
            f'Invalid classification, '
            f'requires paletted/unique values renderer ({self.parameterDefinition(name).description()})'
        )

    def checkParameterMapClassification(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Tuple[bool, str]:
        layer = self.parameterAsLayer(parameters, name, context)
        if layer is None:
            return True, ''
        elif isinstance(layer, QgsRasterLayer):
            return self.checkParameterRasterClassification(parameters, name, context)
        elif isinstance(layer, QgsVectorLayer):
            return self.checkParameterVectorClassification(parameters, name, context)
        else:
            assert 0

    def shortDescription(self):
        raise NotImplementedError()

    def helpCookbookUrls(self) -> List[Tuple[str, str]]:
        return []

    def helpParameters(self) -> List[Tuple[str, str]]:
        return []

    def helpParameterRaster(self):
        return 'Source raster layer.'

    def helpParameterMapClassification(self):
        return 'Source raster or vector layer styled with a paletted/unique values (raster) ' \
               'or categorized symbol (vector) renderer.'

    def helpParameterClassification(self):
        return 'Source raster layer styled with a paletted/unique values renderer.'

    def helpParameterMask(self):
        return 'Source raster or vector layer interpreted as binary mask. ' \
               'In case of a raster, all pixels with no data (zero, if undefined) ' \
               'are excluded from processing (only the first band used by the renderer is considered). ' \
               'In case of a vector, all pixels not covered by geometries are excluded. '

    def helpParameterVector(self):
        return 'Source vector layer.'

    def helpParameterVectorClassification(self):
        return 'Source vector layer styled with a categorized symbol renderer.'

    def helpParameterClassifier(self):
        return 'Classifier created with <i>Classification / Fit *Classifier</i>.'

    def helpParameterGrid(self):
        return 'A raster layer defining the destination extent, resolution and coordinate reference system ' \
               '(inputs are reprojected if necessary).'

    def helpParameterMaximumMemoryUsage(self):
        return 'Maximum amount of memory (as bytes) for processing (defaults to 5 % of total memory).'

    def helpParameterDataType(self):
        return 'Output data type.'

    def helpParameterNoDataValue(self):
        return 'Output no data value.'

    def helpParameterRasterDestination(self):
        return 'Output raster destination.'

    def helpParameterCreationProfile(self):
        return 'Output format and creation options.'

    def helpHeader(self) -> Optional[Tuple[str, str]]:
        return None

    def shortHelpString(self):
        text = '<p>' + self.shortDescription() + '</p>'
        if self.helpHeader() is not None:
            title, text2 = self.helpHeader()
            text += f'<h3>{title}</h3><p>{text2}</p>'
        if len(self.helpCookbookUrls()) > 0:
            text += '<p>Used in the Cookbook Recipes: '
            text += ', '.join(
                [f'<a href="{url}">{name}</a>' for name, url in
                 self.helpCookbookUrls()]
            )
            text += '</p>\n\n'
        for name, text2 in self.helpParameters():
            parameter = self.parameterDefinition(name)
            text += f'<h3>{parameter.description()}</h3><p>{text2}</p>'
        return text

    def helpString(self):
        return self.shortHelpString()

    def helpUrl(self, *args, **kwargs):
        return 'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider/overview'

    def addParameterMapLayer(self, name: str, description: str, defaultValue=None, optional=False, advanced=False):
        self.addParameter(QgsProcessingParameterMapLayer(name, description, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterRasterLayer(
            self, name: str, description: str, defaultValue=None, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterRasterLayer(name, description, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterBand(
            self, name: str, description: str, defaultValue: int = None, parentLayerParameterName: str = None,
            optional=False, allowMultiple=False, advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterBand(
                name, description, defaultValue, parentLayerParameterName, optional, allowMultiple
            )
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterBandList(
            self, name: str, description: str, defaultValue: List[int] = None, parentLayerParameterName: str = None,
            optional=False, advanced=False
    ):
        assert parentLayerParameterName is not None
        self.addParameterBand(name, description, defaultValue, parentLayerParameterName, optional, True)
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterVectorLayer(
            self, name: str, description: str, types: Iterable[int] = None, defaultValue=None, optional=False,
            advanced=False
    ):
        if types is None:
            types = []
        self.addParameter(QgsProcessingParameterVectorLayer(name, description, types, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterExtent(
            self, name: str, description: str, defaultValue=None, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterExtent(name, description, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterRasterDestination(
            self, name: str, description='Output Raster', defaultValue=None, optional=False, createByDefault=True,
            advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterRasterDestination(name, description, defaultValue, optional, createByDefault)
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterFile(
            self, name: str, description: str,
            behavior: QgsProcessingParameterFile.Behavior = QgsProcessingParameterFile.File, extension: str = '',
            defaultValue=None, optional=False, fileFilter='', advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterFile(
                name, description, behavior, extension, defaultValue, optional, fileFilter
            )
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterFileDestination(
            self, name: str, description: str, fileFilter='', defaultValue=None, optional=False,
            createByDefault=True, advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterFileDestination(
                name, description, fileFilter, defaultValue, optional, createByDefault
            )
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterNumber(
            self, name: str, description: str, type: QgsProcessingParameterNumber.Type, defaultValue=None,
            optional=False, minValue: float = None, maxValue: float = None, advanced=False
    ):
        if minValue is None:
            minValue = np.finfo(float).min
        if maxValue is None:
            maxValue = np.finfo(float).max

        self.addParameter(
            QgsProcessingParameterNumber(name, description, type, defaultValue, optional, minValue, maxValue)
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterInt(
            self, name: str, description: str, defaultValue=None, optional=False, minValue: int = None,
            maxValue: int = None, advanced=False, hidden=False
    ):
        type = QgsProcessingParameterNumber.Integer
        self.addParameterNumber(name, description, type, defaultValue, optional, minValue, maxValue)
        self.flagParameterAsAdvanced(name, advanced)
        self.flagParameterAsHidden(name, hidden)

    def addParameterFloat(
            self, name: str, description: str, defaultValue=None, optional=False, minValue: float = None,
            maxValue: float = None, advanced=False
    ):
        type = QgsProcessingParameterNumber.Double
        self.addParameterNumber(name, description, type, defaultValue, optional, minValue, maxValue)
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterBoolean(self, name: str, description: str, defaultValue=None, optional=False, advanced=False):
        self.addParameter(QgsProcessingParameterBoolean(name, description, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterField(
            self, name: str, description: str, defaultValue=None, parentLayerParameterName: str = '',
            type: QgsProcessingParameterField.DataType = QgsProcessingParameterField.Any, allowMultiple=False,
            optional=False, defaultToAllFields=False, advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterField(
                name, description, defaultValue, parentLayerParameterName, type, allowMultiple, optional,
                defaultToAllFields
            )
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterEnum(
            self, name: str, description: str, options: Iterable[str], allowMultiple=False, defaultValue=None,
            optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterEnum(name, description, options, allowMultiple, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterString(
            self, name: str, description: str, defaultValue=None, multiLine=False, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterString(name, description, defaultValue, multiLine, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterDataType(
            self, name: str, description='Data Type', defaultValue: int = None, optional=False,
            advanced=False
    ):
        options = self.O_DATA_TYPE
        self.addParameterEnum(name, description, options, False, defaultValue, optional, advanced)

    def addParameterMaximumMemoryUsage(self, name: str, description='Maximum Memory Usage', advanced=False):
        self.addParameterInt(name, description, gdal.GetCacheMax(), True, 0, None, advanced)

    def addParameterCreationProfile(
            self, name: str, description='Output Options', defaultValue=0, advanced=False, allowVrt=False
    ):
        if allowVrt:
            options = self.O_CREATION_PROFILE
        else:
            options = self.O_CREATION_PROFILE[:-1]
        self.addParameterEnum(name, description, options, False, defaultValue=defaultValue, advanced=advanced)

    def addParameterResampleAlg(
            self, name: str, description='Resample Algorithm', defaultValue=0, optional=False, advanced=False
    ):
        options = self.O_RESAMPLE_ALG
        self.addParameterEnum(name, description, options, False, defaultValue, optional, advanced)

    def flagParameterAsAdvanced(self, name: str, advanced: bool):
        if advanced:
            p = self.parameterDefinition(name)
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

    def flagParameterAsHidden(self, name: str, hidden: bool):
        if hidden:
            p = self.parameterDefinition(name)
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagHidden)


class Group(Enum):
    AccuracyAssessment = 'Accuracy Assessment'
    Auxilliary = 'Auxilliary'
    ConvolutionMorphologyAndFiltering = 'Convolution, Morphology and Filtering'
    CreateRaster = 'Create Raster'
    CreateSample = 'Create Sample'
    Classification = 'Classification'
    Clustering = 'Clustering'
    ImportData = 'Import Data'
    Masking = 'Masking'
    Options = 'Options'
    Preprocessing = 'Pre-Processing'
    Postprocessing = 'Post-Processing'
    ResamplingAndSubsetting = 'Resampling and Subsetting'
    Random = 'Random'
    Regression = 'Regression'
    Test = 'TEST/'
    Testdata = 'Testdata'
    Transformation = 'Transformation'


class CookbookUrls(object):
    URL = r'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook'
    URL_CLASSIFICATION = ('Classification', URL + '/classification.html')
    URL_REGRESSION = ('Regression', URL + '/regression.html')
    URL_CLUSTERING = ('Clustering', URL + '/clustering.html')
    URL_TRANSFORMATION = ('Transformation', URL + '/transformation.html')
    URL_FILTERING = ('Filtering', URL + '/filtering.html')
    URL_GRAPHICAL_MODELER = ('Graphical Modeler', URL + '/graphical_modeler.html')
    URL_GENERIC_FILTER = ('Generic Filter', URL + '/generic_filter.html')
