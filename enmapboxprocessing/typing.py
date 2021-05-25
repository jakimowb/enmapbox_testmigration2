from typing import Union, List, Dict, Optional, NamedTuple

import numpy as np
from osgeo import gdal
from qgis._core import QgsRasterDataProvider, QgsRasterLayer
from sklearn.base import ClassifierMixin, RegressorMixin
from sklearn.pipeline import Pipeline

from typeguard import typechecked

GdalDataType = int
GdalResamplingAlgorithm = int
NumpyDataType = np.dtype
QgisDataType = int
Array2d = np.ndarray
Array3d = Union[np.ndarray, List[Array2d]]
MetadataScalarValue = Optional[Union[str, int, float]]
MetadataListValue = List[MetadataScalarValue]
MetadataValue = Union[MetadataScalarValue, MetadataListValue]
MetadataDomain = Dict[str, MetadataValue]
Metadata = Dict[str, MetadataDomain]
RasterSource = Union[str, QgsRasterLayer, QgsRasterDataProvider, gdal.Dataset]
CreationOptions = List[str]
HexColor = str


@typechecked
class Category(NamedTuple):
    value: Union[int, str]
    name: str
    color: HexColor


Categories = List[Category]
SampleX = Array2d
SampleY = Array2d

Classifier = ClassifierMixin
Regressor = RegressorMixin


@typechecked
class ClassifierDump(NamedTuple):
    categories: Optional[Categories]
    features: Optional[List[str]]
    X: Optional[SampleX]
    y: Optional[SampleY]
    classifier: Optional[Union[Classifier, Pipeline]] = None

    def withCategories(self, categories):
        asdict = self._asdict()
        asdict['categories'] = categories
        return ClassifierDump(**asdict)

    def withFeatures(self, features):
        asdict = self._asdict()
        asdict['features'] = features
        return ClassifierDump(**asdict)

    def withClassifier(self, classifier):
        asdict = self._asdict()
        asdict['classifier'] = classifier
        return ClassifierDump(**asdict)

    def withSample(self, X, y):
        asdict = self._asdict()
        asdict['X'] = X
        asdict['y'] = y
        return ClassifierDump(**asdict)


@typechecked
class RegressionDump(NamedTuple):
    targets: List[str]
    features: List[str]
    X: SampleX
    y: SampleY
    regressor: Optional[Regressor] = None

    def withRegressor(self, regressor):
        asdict = self._asdict()
        asdict['regressor'] = regressor
        return RegressionDump(**asdict)

    def withSample(self, X, y):
        asdict = self._asdict()
        asdict['X'] = X
        asdict['y'] = y
        return RegressionDump(**asdict)


@typechecked
def checkSampleShape(X: SampleX, y: SampleY, raise_=False) -> bool:
    if not (X.ndim == y.ndim == 2) and (X.shape[0] == y.shape[0]):
        if raise_:
            raise ValueError(f'X{list(X.shape)} and y{list(y.shape)} data not matching')
        return False
    return True