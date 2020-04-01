# from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union, Any, Dict

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from qgis._core import *


class EnMAPAlgorithm(QgisAlgorithm):

    def cookbookRecipes(self):
        return []

    def cookbookDescription(self):
        return 'Used in the Cookbook Recipes:'

    def initAlgorithm(self, configuration=None):
        self._configuration = configuration
        self.defineCharacteristics()

    def group(self) -> str:
        raise NotImplementedError()

    def displayName(self) -> str:
        raise NotImplementedError()

    def _generateId(self, name):
        id = name
        for c in ' !?-+/*()[]{}':
            id = id.replace(c, '')
        return id

    def groupId(self) -> str:
        groupId = self._generateId(self.group())
        return groupId

    def name(self) -> str:
        name = self._generateId(self.displayName())
        return name

    def validateInputCrs(self, parameters, context) -> bool:
        return True  # we accept different crs per default

    def defineCharacteristics(self):
        raise NotImplementedError()

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        raise NotImplementedError()

    def processAlgorithm(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        try:
            result = self.processAlgorithm_(parameters=parameters, context=context, feedback=feedback)
            assert isinstance(result,
                dict), 'return value error, expected a dict as return value, check {}.processAlgorithm_()'.format(
                self.__class__.__name__)
            return result
        except:
            import traceback
            traceback.print_exc()
            for line in traceback.format_exc().split('\n'):
                feedback.reportError(line)
            raise Exception('unexpected error')

    def hasHtmlOutputs(self, *args, **kwargs):
        return False

    def description(self) -> Union['Help', str]:
        return Help('undocumented algorithm')

    def shortHelpString(self):

        if isinstance(self.description(), str):
            text = '<p>' + self.description() + '</p>'
        elif isinstance(self.description(), Help):
            text = '<p>' + self.description().html() + '</p>'
        else:
            assert 0

        if len(self.cookbookRecipes()) > 0:
            text += '<p>Used in the Cookbook Recipes: '
            for i, key in enumerate(self.cookbookRecipes()):
                url = Cookbook.url(key)
                text += '<a href="{}">{}</a>'.format(url, key)
                if i < len(self.cookbookRecipes()) - 1:
                    text += ', '
            text += '</p>\n\n'

        for pd in self.parameterDefinitions():
            assert isinstance(pd, QgsProcessingParameterDefinition)
            text += '<h3>' + pd.description() + '</h3>'
            text += '<p>' + pd.help.html() + '</p>'

        return text

    def helpString(self):
        return self.shortHelpString()

    def helpUrl(self, *args, **kwargs):
        return 'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider/overview'


class Group(Enum):
    ACCURACY_ASSESSMENT = 'Accuracy Assessment'
    Auxilliary = 'Auxilliary'
    CONVOLUTION = 'Convolution, Morphology and Filtering'
    CREATE_RASTER = 'Create Raster'
    CREATE_SAMPLE = 'Create Sample'
    CLASSIFICATION = 'Classification'
    CLUSTERING = 'Clustering'
    IMPORT_DATA = 'Import Data'
    MASKING = 'Masking'
    OPTIONS = 'Options'
    PREPROCESSING = 'Pre-Processing'
    POSTPROCESSING = 'Post-Processing'
    RESAMPLING = 'Resampling and Subsetting'
    RANDOM = 'Random'
    REGRESSION = 'Regression'
    TEST = 'TEST'
    TESTDATA = 'Testdata'
    TRANSFORMATION = 'Transformation'


class Link():
    def __init__(self, url, name):
        self.url = url
        self.name = name


@dataclass
class Help(object):
    text: str = 'undocumented'
    links: List[Link] = field(default_factory=list)

    def __post_init__(self):
        assert isinstance(self.text, str)
        for link in self.links:
            assert isinstance(link, Link)

    def html(self):
        htmlLinks = [r'<a href="{url}">{name}</a>'.format(url=link.url, name=link.name) for link in self.links]
        htmlText = self.text.format(*htmlLinks)
        htmlText = htmlText.replace('\n', '<br>')
        return htmlText

    def rst(self):
        rstLinks = [r'`{name} <{url}>`_'.format(url=link.url, name=link.name) for link in self.links]
        rstText = self.text.format(*rstLinks)
        rstText = rstText.replace('\n', '\n\n')
        return rstText

    def tooltip(self):
        links = [link.name for link in self.links]
        tooltip = self.text.format(*links)
        return tooltip


class Cookbook(object):
    URL = r'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook'
    R_CLASSIFICATION = 'Classification'
    R_REGRESSION = 'Regression'
    R_CLUSTERING = 'Clustering'
    R_TRANSFORMATION = 'Transformation'
    R_FILTERING = 'Filtering'
    R_GRAPHICALMODELER = 'Graphical Modeler'
    R_GENERICFILTER = 'Generic Filter'
    LINK = {R_CLASSIFICATION: 'classification.html',
            R_REGRESSION: 'regression.html',
            R_CLUSTERING: 'clustering.html',
            R_TRANSFORMATION: 'transformation.html',
            R_FILTERING: 'filtering.html',
            R_GRAPHICALMODELER: 'graphical_modeler.html',
            R_GENERICFILTER: 'generic_filter.html'
            }

    @classmethod
    def url(cls, key):
        return '{}/{}'.format(cls.URL, cls.LINK[key])


class EnMAPProcessingParameterMapLayer(QgsProcessingParameterMapLayer):
    def __init__(
            self, name: str, description: str, defaultValue: Any = None, optional: bool = False, help=Help()
    ):
        QgsProcessingParameterMapLayer.__init__(
            self, name=name, description=description, defaultValue=defaultValue, optional=optional
        )
        self.help = help


class EnMAPProcessingParameterRasterLayer(QgsProcessingParameterRasterLayer):
    def __init__(
            self, name: str, description: str, defaultValue: Any = None, optional: bool = False, help=Help()
    ):
        QgsProcessingParameterRasterLayer.__init__(
            self, name=name, description=description, defaultValue=defaultValue, optional=optional
        )
        self.help = help


class EnMAPProcessingParameterBand(QgsProcessingParameterBand):
    def __init__(
            self, name: str, description: str, parentLayerParameterName: str, defaultValue: Any = None,
            optional: bool = False, allowMultiple: bool = False, help=Help()
    ):
        QgsProcessingParameterBand.__init__(
            self, name=name, description=description, defaultValue=defaultValue,
            parentLayerParameterName=parentLayerParameterName, optional=optional, allowMultiple=allowMultiple
        )
        self.help = help


class EnMAPProcessingOutputString(QgsProcessingOutputString):
    def __init__(
            self, name: str, description: str, help=Help()
    ):
        QgsProcessingOutputString.__init__(self, name=name, description=description)
        self.help = help
