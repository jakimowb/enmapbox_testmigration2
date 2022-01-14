import unittest
import xmlrunner
from qgis.PyQt.QtWidgets import QPushButton, QGroupBox

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QVBoxLayout, QWidget, QGridLayout
from qps.testing import TestObjects, TestCase
from qgis.gui import QgsSpinBox

from qps.simplewidgets import SliderSpinBox, DoubleSliderSpinBox, FlowLayout

class SimpleWidgetTests(TestCase):

    def test_FlowLayout(self):


        w = QGroupBox()
        l = FlowLayout()
        l.setSpacing(0)
        l.setContentsMargins(0, 0, 0, 0)
        for i in range(10):
            btn = QPushButton(f'Button {i+1}')
            l.addWidget(btn)
        w.setLayout(l)
        self.assertIsInstance(w.layout(), FlowLayout)
        s = ""
        self.showGui(w)

    def test_SliderSpinBox(self):

        sb = SliderSpinBox()
        sbl = DoubleSliderSpinBox()

        l = QGridLayout()
        for row, a in enumerate([Qt.AlignLeft, Qt.AlignRight, Qt.AlignTop, Qt.AlignBottom]):
            for col, sb in enumerate([SliderSpinBox(spinbox=QgsSpinBox(), spinbox_position=a),
                                      SliderSpinBox(spinbox_position=a),
                                      DoubleSliderSpinBox(spinbox_position=a)]):
                sb.setValue(10)
                sb.setMinimum(-10)
                sb.setMaximum(100)
                l.addWidget(sb, row, col)



        w = QWidget()
        w.setLayout(l)
        self.showGui(w)


if __name__ == '__main__':

    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)