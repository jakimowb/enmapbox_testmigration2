from PyQt5.QtWidgets import QDoubleSpinBox, QWidget

from qgis.PyQt import uic
from typeguard import typechecked


@typechecked
class WavebandLocatorPercentilesWidget(QWidget):
    mP1: QDoubleSpinBox
    mP2: QDoubleSpinBox

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)