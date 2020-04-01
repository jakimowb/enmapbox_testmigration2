import unittest
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import QTimer
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox.gui.enmapboxgui import EnMAPBoxSplashScreen
class TestEnMAPBoxSplashScreen(EnMAPBoxTestCase):

    def test_splashScreen(self):

        import time
        import enmapbox
        w = QWidget()

        splash = EnMAPBoxSplashScreen(parent=w)
        self.assertIsInstance(splash, EnMAPBoxSplashScreen)
        i = 0
        splash.showMessage('Message {} {}'.format(i, str(time.time())))
        def onTimeOut(*args):
            nonlocal i
            splash.showMessage('Message {} {}'.format(i, str(time.time())))
            i += 1
        self.assertFalse(splash.size().isNull())

        timer = QTimer()
        timer.startTimer(2)
        timer.timeout.connect(onTimeOut)

        self.showGui([w, splash])

if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
