from typing import Union, List, Dict, Optional, Tuple

import numpy as np
from PyQt5.QtGui import QColor
from osgeo import gdal
from qgis._core import Qgis, QgsRasterDataProvider, QgsRasterLayer
from typeguard import typechecked

GdalDataType = int
GdalResamplingAlgorithm = int
NumpyDataType = np.dtype
QgisDataType = Qgis.DataType
Array2d = np.ndarray
Array3d = Union[np.ndarray, List[Array2d]]
MetadataScalarValue = Optional[Union[str, int, float]]
MetadataListValue = List[MetadataScalarValue]
MetadataValue = Union[MetadataScalarValue, MetadataListValue]
MetadataDomain = Dict[str, MetadataValue]
Metadata = Dict[str, MetadataDomain]
RasterSource = Union[str, QgsRasterLayer, QgsRasterDataProvider, gdal.Dataset]
CreationOptions = List[str]
Category = Tuple[Union[int, str], str, QColor]
Categories = List[Category]
SampleX = Array2d
SampleY = Array2d


@typechecked
def checkSampleShape(X: SampleX, y: SampleY) -> bool:
    return (X.ndim == y.ndim == 2) and (X.shape[0] == y.shape)
