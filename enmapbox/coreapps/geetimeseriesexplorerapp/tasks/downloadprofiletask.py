from math import nan
from os.path import exists
from typing import Optional, List

from qgis._core import QgsTask, QgsMessageLog, Qgis

from enmapboxprocessing.utils import Utils
from typeguard import typechecked

try:
    import ee
except:
    pass

@typechecked
class DownloadProfileTask(QgsTask):

    def __init__(
            self, filename: Optional[str], eePoint: 'ee.Geometry', eeCollection: 'ee.ImageCollection', scale: float,
            offsets: List[float], scales: List[float]
    ):
        QgsTask.__init__(self, 'Download profile task', QgsTask.CanCancel)
        self.filename = filename
        self.eePoint = eePoint
        self.eeCollection = eeCollection
        self.scale = scale
        self.offsets = offsets
        self.scales = scales
        self.data_: Optional[List] = None
        self.exception: Optional[Exception] = None

    def run(self):
        try:

            if self.filename is not None:
                self.alreadyExists = exists(self.filename)
            else:
                self.alreadyExists = False

            if self.alreadyExists:
                return True

            if self.filename is not None and exists(self.filename):  # if file already exists,
                return True  # we do nothing

            self.data_ = self.eeCollection.getRegion(self.eePoint, scale=self.scale).getInfo()

            # scale data
            for i, (offset, scale) in enumerate(zip(self.offsets, self.scales), 4):
                if offset != 0 and scale != 1:
                    for values in self.data_[1:]:
                        value = values[i]
                        if value is None:
                            value = nan
                        else:
                            value = value * scale + offset
                        values[i] = value

            if self.filename is not None:
                Utils.jsonDump(self.data_, self.filename)

        except Exception as e:
            self.exception = e
            return False

        return True

    def finished(self, result):
        if self.isCanceled():
            return
        elif not result:
            raise self.exception

        if self.filename is not None:
            if self.alreadyExists:
                QgsMessageLog.logMessage(
                    f'already exists: {self.filename}', tag="GEE Time Series Explorer", level=Qgis.Success
                )
            else:
                QgsMessageLog.logMessage(
                    f'downloaded: {self.filename}', tag="GEE Time Series Explorer", level=Qgis.Success
                )


    def data(self) -> Optional[List]:
        if self.data_ is None:
            self.data_ = Utils.jsonLoad(self.filename)  # use cached version
        return self.data_
