import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from enmapbox.testing import EnMAPBoxTestCase

import unittest

class Test(EnMAPBoxTestCase):

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
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)



