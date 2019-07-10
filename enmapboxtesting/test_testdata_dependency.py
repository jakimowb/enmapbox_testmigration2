from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

app = QApplication([])
import unittest

class Test(unittest.TestCase):

    def test_version(self):

        from enmapbox.dependencycheck import outdatedTestData
        self.assertFalse(outdatedTestData())

    def test_signals(self):

        def myslot():
            print('signaled')

        class MyObject(QObject):
            sig = pyqtSignal()

            def __init__(self):

                super(MyObject, self).__init__()


        O = MyObject()
        O.sig.connect(myslot)
        O.sig.connect(myslot)

        O.sig.emit()

        QApplication.processEvents()

        s = ""
if __name__ == "__main__":
    unittest.main()



