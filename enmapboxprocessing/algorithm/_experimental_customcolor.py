from typing import Dict, Any, List, Tuple

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from processing.gui.wrappers import WidgetWrapper, DIALOG_MODELER, DIALOG_BATCH
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingParameterString)

from enmapbox.externals.qps.classification.classificationscheme import ClassificationSchemeWidget
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import Category
from typeguard import typechecked


class ColorWidget(QWidget):

    def __init__(self, *args, **kwargs):
        print(*args, **kwargs)
        QWidget.__init__(self, *args, **kwargs)
        layout = QVBoxLayout()
        self.mClassificationSchemeWidget = ClassificationSchemeWidget()
        layout.addWidget(self.mClassificationSchemeWidget)
        self.setLayout(layout)

    def setToolTip(self, *args, **kwargs):
        pass

    def value(self):
        scheme = self.mClassificationSchemeWidget.classificationScheme()
        categories = list()
        for v, n, c in zip(scheme.classLabels(), scheme.classNames(), scheme.classColors()):
            categories.append(Category(v, str(n), str(c.name())))
        return str(categories)


class ColorWidgetWrapper(WidgetWrapper):
    # adopted from C:\source\QGIS3-master\python\plugins\processing\algs\gdal\ui\RasterOptionsWidget.py

    widget: ColorWidget

    def createWidget(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return ColorWidget()

    def setValue(self, value):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            raise NotImplementedError()

    def value(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return self.widget.value()


@typechecked
class ExperimentalCustomColor(EnMAPProcessingAlgorithm):
    P_COLOR, _COLOR = 'color', 'Color'

    @classmethod
    def displayName(cls) -> str:
        return 'Custom Color'

    def shortDescription(self) -> str:
        return 'Custom color widget'

    def group(self):
        return Group.Test.value + Group.Experimental.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        options_param = QgsProcessingParameterString(self.P_COLOR, 'Color')
        options_param.setMetadata({'widget_wrapper': {'class': ColorWidgetWrapper}})
        self.addParameter(options_param)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        color = self.parameterAsString(parameters, self.P_COLOR, context)
        print(color)
        return {}
