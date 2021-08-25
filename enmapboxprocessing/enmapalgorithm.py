from enum import Enum
from os import makedirs
from os.path import isabs, join, dirname, exists, splitext
from time import time
from typing import Any, Dict, Iterable, Optional, List, Tuple, TextIO

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorLayer,
                        QgsProcessingContext, QgsProcessingFeedback,
                        QgsRasterLayer, QgsVectorLayer, QgsProcessingParameterNumber, QgsProcessingParameterDefinition,
                        QgsProcessingParameterField, QgsProcessingParameterBoolean, QgsProcessingParameterEnum, Qgis,
                        QgsProcessingParameterString, QgsProcessingParameterBand, QgsCategorizedSymbolRenderer,
                        QgsPalettedRasterRenderer, QgsProcessingParameterMapLayer, QgsMapLayer,
                        QgsProcessingParameterExtent, QgsCoordinateReferenceSystem, QgsRectangle,
                        QgsProcessingParameterFileDestination, QgsProcessingParameterFile, QgsProcessingParameterRange,
                        QgsProcessingParameterCrs, QgsProcessingParameterVectorDestination, QgsProcessing,
                        QgsProcessingUtils, QgsProcessingParameterMultipleLayers, QgsProcessingException,
                        QgsProcessingParameterFolderDestination)

import processing
from enmapboxprocessing.glossary import injectGlossaryLinks
from enmapboxprocessing.parameter.processingparametercodeeditwidget import ProcessingParameterCodeEditWidgetWrapper
from enmapboxprocessing.parameter.processingparametercreationprofilewidget import \
    ProcessingParameterCreationProfileWidgetWrapper
from enmapboxprocessing.parameter.processingparameterrasterdestination import ProcessingParameterRasterDestination
from enmapboxprocessing.processingfeedback import ProcessingFeedback
from enmapboxprocessing.typing import QgisDataType, CreationOptions, GdalResamplingAlgorithm
from typeguard import typechecked


class AlgorithmCanceledException(Exception):
    pass


@typechecked
class EnMAPProcessingAlgorithm(QgsProcessingAlgorithm):
    O_RESAMPLE_ALG = 'NearestNeighbour Bilinear Cubic CubicSpline Lanczos Average Mode Min Q1 Med Q3 Max'.split()
    NearestNeighbourResampleAlg, BilinearResampleAlg, CubicResampleAlg, CubicSplineResampleAlg, LanczosResampleAlg, \
    AverageResampleAlg, ModeResampleAlg, MinResampleAlg, Q1ResampleAlg, MedResampleAlg, Q3ResampleAlg, \
    MaxResampleAlg = range(12)
    O_DATA_TYPE = 'Byte Int16 UInt16 Int32 UInt32 Float32 Float64'.split()
    Byte, Int16, UInt16, Int32, UInt32, Float32, Float64 = range(len(O_DATA_TYPE))
    PickleFileFilter = 'Pickle (*.pkl)'
    PickleFileExtension = 'pkl'
    PickleFileDestination = 'Destination pickle file.'
    RasterFileDestination = 'Raster file destination.'
    VectorFileDestination = 'Vector file destination.'
    ReportFileFilter = 'HTML (*.html)'
    ReportFileDestination = 'Output report file destination.'
    FolderDestination = 'Folder destination.'

    VrtFormat = 'VRT'
    DefaultVrtCreationOptions = ''.split()
    DefaultVrtCreationProfile = VrtFormat + ' ' + ' '.join(DefaultVrtCreationOptions)
    GTiffFormat = 'GTiff'
    DefaultGTiffCreationOptions = 'INTERLEAVE=BAND COMPRESS=LZW PREDICTOR=2 TILED=YES BIGTIFF=YES'.split()
    DefaultGTiffCreationProfile = GTiffFormat + ' ' + ' '.join(DefaultGTiffCreationOptions)
    EnviFormat = 'ENVI'
    DefaultEnviCreationOptions = 'INTERLEAVE=BSQ'.split()
    DefaultEnviCreationProfile = EnviFormat + ' ' + ' '.join(DefaultEnviCreationOptions)

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
        layer = super().parameterAsLayer(parameters, name, context)
        if isinstance(layer, QgsMapLayer) and isinstance(parameters[name], str):
            layer.loadDefaultStyle()
        return layer

    def parameterAsLayerList(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[List[QgsMapLayer]]:
        layers = super().parameterAsLayerList(parameters, name, context)
        if layers is None or len(layers) == 0:
            return None
        #for layer in layers:
        #    if isinstance(layer, QgsMapLayer) and isinstance(parameters[name], str):
        #        layer.loadDefaultStyle()
        return layers

    def parameterAsRasterLayer(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[QgsRasterLayer]:
        layer = super().parameterAsRasterLayer(parameters, name, context)
        if isinstance(layer, QgsRasterLayer) and isinstance(parameters[name], str):
            layer.loadDefaultStyle()
        return layer

    def parameterAsSpectralRasterLayer(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext, checkWavelength=True,
            checkFwhm=False
    ) -> Optional[QgsRasterLayer]:
        from enmapboxprocessing.rasterreader import RasterReader

        layer = self.parameterAsRasterLayer(parameters, name, context)
        if layer is not None:
            if checkWavelength:
                if not RasterReader(layer).isSpectralRasterLayer():
                    message = f'Missing wavelength definition for spectral raster layer: {name}'
                    raise QgsProcessingException(message)
            if checkFwhm:
                if not RasterReader(layer).isSpectralRasterLayer():
                    message = f'Missing FWHM definition for spectral raster layer: {name}'
                    raise QgsProcessingException(message)
        return layer

    def parameterAsVectorLayer(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[QgsVectorLayer]:
        layer = super().parameterAsVectorLayer(parameters, name, context)
        if isinstance(layer, QgsVectorLayer) and isinstance(parameters[name], str):
            layer.loadDefaultStyle()
        return layer

    def parameterAsFields(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[List[str]]:
        fields = super().parameterAsFields(parameters, name, context)
        if len(fields) == 0:
            return None
        else:
            return fields

    def parameterAsField(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[str]:
        fields = self.parameterAsFields(parameters, name, context)
        if fields is None:
            return None
        else:
            return fields[0]

    def parameterAsFile(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> Optional[str]:
        filename = super().parameterAsFile(parameters, name, context)
        if filename == '':
            return None
        return filename

    def parameterAsEnum(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> int:
        return super().parameterAsEnum(parameters, name, context)

    def parameterAsEnums(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> List[int]:
        return super().parameterAsEnums(parameters, name, context)

    def parameterAsString(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> Optional[str]:
        string = super().parameterAsString(parameters, name, context)
        if string == '':
            if isinstance(parameters.get(name), str):  # workaround a QGIS bug, where super().parameterAsString would return an empty string instead of the actual string
                return parameters.get(name)
            return None
        return string

    def parameterAsDouble(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[float]:
        if self.parameterIsNone(parameters, name):
            return self.parameterDefinition(name).defaultValue()
        else:
            return super().parameterAsDouble(parameters, name, context)

    parameterAsFloat = parameterAsDouble

    def parameterAsInt(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> Optional[int]:
        if self.parameterIsNone(parameters, name):
            return self.parameterDefinition(name).defaultValue()
        else:
            return super().parameterAsInt(parameters, name, context)

    def parameterAsInts(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[List[int]]:
        ints = super().parameterAsInts(parameters, name, context)
        if len(ints) == 0:
            ints = None
        return ints

    def parameterAsValues(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[List[Any]]:
        string = self.parameterAsString(parameters, name, context)
        if string is None:
            return None
        string = string.replace('\n', '')
        values = eval(string)
        if not isinstance(values, (tuple, list)):
            values = [values]
        values = list(values)
        return values

    def parameterAsBool(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> bool:
        return super().parameterAsBool(parameters, name, context)

    def parameterAsBoolean(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> bool:
        return super().parameterAsBoolean(parameters, name, context)

    def parameterAsFileOutput(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> Optional[str]:
        filename = super().parameterAsFileOutput(parameters, name, context)
        if filename == '':
            filename = parameters.get(name, '')
        if filename == '':
            return None
        if not isabs(filename):
            filename = join(QgsProcessingUtils.tempFolder(), filename)
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        return filename

    def parameterAsRange(self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext) -> List[float]:
        return super().parameterAsRange(parameters, name, context)

    def parameterAsCrs(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext
    ) -> QgsCoordinateReferenceSystem:
        if self.parameterIsNone(parameters, name):
            return self.parameterDefinition(name).defaultValue()
        else:
            return super().parameterAsCrs(parameters, name, context)

    def parameterAsExtent(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext,
            crs: QgsCoordinateReferenceSystem
    ) -> QgsRectangle:
        return super().parameterAsExtent(parameters, name, context, crs)

    def parameterAsQgsDataType(
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext, default: QgisDataType = None
    ) -> Optional[QgisDataType]:
        if self.parameterIsNone(parameters, name):
            return default
        else:
            index = self.parameterAsEnum(parameters, name, context)
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
            self, parameters: Dict[str, Any], name: str, context: QgsProcessingContext, filename: str
    ) -> Tuple[str, CreationOptions]:
        text = self.parameterAsString(parameters, name, context)
        if text is None:
            extension = splitext(filename)[1].lower()
            defaultCreationProfilesByExtension = {
                '.tif': self.DefaultGTiffCreationProfile,
                '.bsq': 'ENVI INTERLEAVE=BSQ',
                '.bil': 'ENVI INTERLEAVE=BIL',
                '.bip': 'ENVI INTERLEAVE=BIP',
                '.vrt': self.DefaultVrtCreationProfile,
            }
            text = defaultCreationProfilesByExtension[extension]
        format, *options = text.split()

        # check that extension is correct
        extension = splitext(filename)[1]
        extensions = {'VRT': '.vrt', 'ENVI': '.bsq .bil .bip', 'GTiff': '.tif'}[format].split()
        if extension not in extensions:
            extensions = ' '.join([f'{extension}' for extension in extensions])
            message = f'unsupported file extension ({extension}) for format ({format}), ' \
                      f'use {extensions} instead'
            raise QgsProcessingException(message)
        return format, options

    def parameterIsNone(self, parameters: Dict[str, Any], name: str):
        return parameters.get(name, None) is None

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = super().checkParameterValues(parameters, context)
        return valid, message

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
        if layer is None:
            return True, ''
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

    def helpHeader(self) -> Optional[Tuple[str, str]]:
        return None

    def shortHelpString(self):
        text = '<p>' + injectGlossaryLinks(self.shortDescription()) + '</p>'
        if self.helpHeader() is not None:
            title, text2 = self.helpHeader()
            text += f' <i><h3>{title}</h3> </i><p>{injectGlossaryLinks(text2)}</p>'
        for name, text2 in self.helpParameters():
            text += f'<h3>{name}</h3><p>{injectGlossaryLinks(text2)}</p>'
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

    def addParameterMultipleLayers(
            self, name: str, description: str, layerType: QgsProcessing.SourceType = QgsProcessing.TypeMapLayer,
            defaultValue=None, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterMultipleLayers(name, description, layerType, defaultValue, optional))
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

    def addParameterField(
            self, name: str, description: str, defaultValue=None, parentLayerParameterName='',
            type=QgsProcessingParameterField.Any, allowMultiple=False, optional=False, defaultToAllFields=False,
            advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterField(
                name, description, defaultValue, parentLayerParameterName, type, allowMultiple, optional,
                defaultToAllFields
            )
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterCrs(
            self, name: str, description: str, defaultValue=None, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterCrs(name, description, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterExtent(
            self, name: str, description: str, defaultValue=None, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterExtent(name, description, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterRasterDestination(
            self, name: str, description: str, defaultValue=None, optional=False, createByDefault=True,
            allowTif=True, allowEnvi=False, allowVrt=False, advanced=False
    ):
        self.addParameter(
            ProcessingParameterRasterDestination(
                name, description, defaultValue, optional, createByDefault, allowTif, allowEnvi, allowVrt
            )
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterVrtDestination(
            self, name: str, description: str, defaultValue=None, optional=False, createByDefault=True,
            advanced=False
    ):
        self.addParameterRasterDestination(
            name, description, defaultValue, optional, createByDefault, False, False, True, advanced
        )
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterVectorDestination(
            self, name: str, description='Output vector', type=QgsProcessing.TypeVectorAnyGeometry, defaultValue=None,
            optional=False, createByDefault=True, advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterVectorDestination(name, description, type, defaultValue, optional, createByDefault)
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

    def addParameterFolderDestination(
            self, name: str, description: str, defaultValue=None, optional=False, createByDefault=True,
            advanced=False
    ):
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name, description, defaultValue, optional, createByDefault
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
            maxValue: int = None, advanced=False
    ):
        type = QgsProcessingParameterNumber.Integer
        self.addParameterNumber(name, description, type, defaultValue, optional, minValue, maxValue)
        self.flagParameterAsAdvanced(name, advanced)

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

    def addParameterIntRange(
            self, name: str, description: str, defaultValue: List[int] = None,
            optional=False, advanced=False
    ):
        type = QgsProcessingParameterNumber.Integer
        self.addParameter(QgsProcessingParameterRange(name, description, type, defaultValue, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterString(
            self, name: str, description: str, defaultValue=None, multiLine=False, optional=False, advanced=False
    ):
        self.addParameter(QgsProcessingParameterString(name, description, defaultValue, multiLine, optional))
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterCode(
            self, name: str, description: str, defaultValue=None, optional=False, advanced=False
    ):
        param = QgsProcessingParameterString(name, description, optional=optional)
        param.setMetadata({'widget_wrapper': {'class': ProcessingParameterCodeEditWidgetWrapper}})
        param.setDefaultValue(defaultValue)
        self.addParameter(param)
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterDataType(
            self, name: str, description='Data type', defaultValue: int = None, optional=False,
            advanced=False
    ):
        options = self.O_DATA_TYPE
        self.addParameterEnum(name, description, options, False, defaultValue, optional, advanced)

    def addParameterCreationProfile(
            self, name: str, description='Output options', defaultValue: str = None, optional=False, advanced=False
    ):
        param = QgsProcessingParameterString(name, description, optional=optional)
        param.setMetadata({'widget_wrapper': {'class': ProcessingParameterCreationProfileWidgetWrapper}})
        param.setDefaultValue(defaultValue)
        self.addParameter(param)
        self.flagParameterAsAdvanced(name, advanced)

    def addParameterResampleAlg(
            self, name: str, description='Resample algorithm', defaultValue=0, optional=False, advanced=False
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

    def asConsoleCommand(self, parameters: Dict[str, Any], context: QgsProcessingContext):
        cmd = f'qgis_process run enmapbox:{self.id()} '
        parameter: QgsProcessingParameterDefinition
        for parameter in self.parameterDefinitions():
            value = parameters.get(parameter.name())
            if value is None:
                continue
            value = parameter.valueAsPythonString(value, context)
            cmd += f'--{parameter.name()}={value} '
        return cmd

    def asPythonCommand(self, parameters: Dict[str, Any], context: QgsProcessingContext):
        cmdParameters = list()
        for parameter in self.parameterDefinitions():
            value_ = parameters.get(parameter.name())
            if value_ is None:
                continue
            value = parameter.valueAsPythonString(value_, context)
            cmdParameters.append(f'{parameter.name()}={value}')

        cmd = f"processing.run('enmapbox:{self.name()}', dict({', '.join(cmdParameters)}))"
        return cmd

    def createLoggingFeedback(
            cls, feedback: QgsProcessingFeedback, logfile: TextIO
    ) -> Tuple[ProcessingFeedback, ProcessingFeedback]:
        feedbackMainAlgo = ProcessingFeedback(feedback, logfile=logfile)
        feedbackChildAlgo = ProcessingFeedback(feedback, logfile=logfile, isChildFeedback=True, silenced=True)
        return feedbackMainAlgo, feedbackChildAlgo

    @classmethod
    def htmlItalic(cls, text: str) -> str:
        return f'<i>{text}</i>'

    @classmethod
    def htmlBold(cls, text: str) -> str:
        return f'<b>{text}</b>'

    @classmethod
    def htmlLink(cls, link: str, text: str = None) -> str:
        if text is None:
            text = link
        return '<a href="' + link + '">' + text + '</a>'

    def tic(self, feedback: ProcessingFeedback, parameters: Dict[str, Any], context: QgsProcessingContext):
        feedback.pushPythonCommand(self.asPythonCommand(parameters, context) + '\n')
        feedback.pushConsoleCommand(self.asConsoleCommand(parameters, context) + '\n')
        self._startTime = time()

    def toc(self, feedback: ProcessingFeedback, result: Dict):
        feedback.pushTiming(time() - self._startTime)
        feedback.pushResult(result)

    @staticmethod
    def runAlg(algOrName, parameters, onFinish, feedback, context, is_child_algorithm) -> Dict:
        return processing.run(algOrName, parameters, onFinish, feedback, context, is_child_algorithm)


class Group(Enum):
    AccuracyAssessment = 'Accuracy Assessment'
    Auxilliary = 'Auxilliary'
    ConvolutionMorphologyAndFiltering = 'Convolution, morphology and filtering'
    RasterCreation = 'Raster creation'
    VectorCreation = 'Vector creation'
    Classification = 'Classification'
    Clustering = 'Clustering'
    DatasetCreation = 'Dataset creation'
    Experimental = 'Experimental'
    FeatureSelection = 'Feature selection'
    ImportData = 'Import data'
    Masking = 'Masking'
    Options = 'Options'
    Preprocessing = 'Pre-processing'
    Postprocessing = 'Post-processing'
    SpectralResampling = 'Spectral resampling'
    Regression = 'Regression'
    Sampling = 'Sampling'
    Test = 'TEST_'
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
