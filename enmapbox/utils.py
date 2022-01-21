from typing import Optional

from qgis.core import QgsRasterLayer

from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from typeguard import typechecked


@typechecked
def findBroadBand(raster: QgsRasterLayer, name: str, strict=False) -> Optional[int]:
    """
    Return raster band that best matches the given broad-band.
    If strict is True, return None, if matched band is outside the FWHM range.
    """

    return CreateSpectralIndicesAlgorithm.findBroadBand(raster, name, strict)
