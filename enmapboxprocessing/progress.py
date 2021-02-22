from qgis._core import QgsProcessingFeedback
from typeguard import typechecked


@typechecked
class SilentFeedback(QgsProcessingFeedback):

    def __init__(self, feedback: QgsProcessingFeedback, pushInfo=False, setProgress=False):
        super().__init__()
        self.feedback = feedback
        self._pushInfo = pushInfo
        self._setProgress = setProgress

    def pushInfo(self, info):
        if self._pushInfo:
            self.feedback.pushInfo(info)

    def setProgress(self, progress):
        if self._setProgress:
            self.feedback.setProgress(progress)
