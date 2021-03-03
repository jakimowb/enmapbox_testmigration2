from typing import Union, List, Dict, Optional, NamedTuple

import numpy as np
from osgeo import gdal
from qgis._core import QgsRasterDataProvider, QgsRasterLayer
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


@typechecked
def checkSampleShape(X: SampleX, y: SampleY) -> bool:
    return (X.ndim == y.ndim == 2) and (X.shape[0] == y.shape)
