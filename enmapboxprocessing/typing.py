from dataclasses import dataclass
from typing import Union, List, Dict, Optional

import numpy as np
from osgeo import gdal
from qgis._core import QgsRasterDataProvider, QgsRasterLayer
from sklearn.base import ClassifierMixin, RegressorMixin
from sklearn.pipeline import Pipeline

from typeguard import typechecked

GdalDataType = int
GdalResamplingAlgorithm = int
NumpyDataType = Union[type, np.dtype]
QgisDataType = int
Number = Union[int, float]
Array1d = np.ndarray
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
@dataclass
class Category(object):
    value: Union[int, str]
    name: str
    color: HexColor


Categories = List[Category]
SampleX = np.array
SampleY = np.array

Classifier = ClassifierMixin
Regressor = RegressorMixin


@typechecked
@dataclass
class ClassifierDump(object):
    categories: Optional[Categories]
    features: Optional[List[str]]
    X: Optional[SampleX]
    y: Optional[SampleY]
    classifier: Optional[Union[Classifier, Pipeline]] = None

    def withCategories(self, categories):
        asdict = self.__dict__.copy()
        asdict['categories'] = categories
        return ClassifierDump(**asdict)

    def withFeatures(self, features):
        asdict = self.__dict__.copy()
        asdict['features'] = features
        return ClassifierDump(**asdict)

    def withClassifier(self, classifier):
        asdict = self.__dict__.copy()
        asdict['classifier'] = classifier
        return ClassifierDump(**asdict)

    def withSample(self, X, y):
        asdict = self.__dict__.copy()
        asdict['X'] = X
        asdict['y'] = y
        return ClassifierDump(**asdict)


@typechecked
@dataclass
class RegressionDump(object):
    targets: List[str]
    features: List[str]
    X: SampleX
    y: SampleY
    regressor: Optional[Regressor] = None

    def withRegressor(self, regressor):
        asdict = self.__dict__.copy()
        asdict['regressor'] = regressor
        return RegressionDump(**asdict)

    def withSample(self, X, y):
        asdict = self.__dict__.copy()
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
