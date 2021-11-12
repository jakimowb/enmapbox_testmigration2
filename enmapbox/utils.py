from typing import Union, Optional

from qgis._core import QgsRasterLayer

from enmapboxprocessing.algorithm.awesomespectralindicesalgorithm import AwesomeSpectralIndicesAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
def findBroadBand(raster: QgsRasterLayer, name: str, strict=False) -> Optional[int]:
    """
    Return raster band that best matches the given broad-band.
    If strict is True, return None, if matched band is outside the FWHM range.
    """

    return AwesomeSpectralIndicesAlgorithm.findBroadBand(raster, name, strict)
