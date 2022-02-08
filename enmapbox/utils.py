from typing import Optional

from PyQt5.QtCore import QObject

from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from qgis.core import QgsRasterLayer
from typeguard import typechecked


@typechecked
def findBroadBand(raster: QgsRasterLayer, name: str, strict=False) -> Optional[int]:
    """
    Return raster band that best matches the given broad-band.
    If strict is True, return None, if matched band is outside the FWHM range.
    """

    return CreateSpectralIndicesAlgorithm.findBroadBand(raster, name, strict)


@typechecked
class BlockSignals(object):
    """Context manager for blocking QObject signals."""

    def __init__(self, *objects: QObject):
        self.objects = objects

    def __enter__(self):
        self.signalsBlocked = [obj.signalsBlocked() for obj in self.objects]
        for object in self.objects:
            object.blockSignals(True)

    def __exit__(self, exc_type, exc_value, tb):
        for object, signalsBlocked in zip(self.objects, self.signalsBlocked):
            object.blockSignals(signalsBlocked)
