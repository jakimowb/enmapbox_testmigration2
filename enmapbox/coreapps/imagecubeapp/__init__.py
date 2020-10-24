import os
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from enmapbox import EnMAPBoxApplication, EnMAPBox

NAME = 'Image Cube'
VERSION = '0.2'
APP_DIR = os.path.dirname(__file__)


class ImageCubeApplication(EnMAPBoxApplication):

    def __init__(self, enmapBox: EnMAPBox, parent=None):

        super(ImageCubeApplication, self).__init__(enmapBox, parent=parent)

        self.name = NAME
        self.version = VERSION
        self.licence = 'GNU GPL-3'
        self.mErrorMessage = None
        #self.mImageCubeWidget: QWidget = None
        self.mIcon = enmapBox.icon()
        self.mActionStartGUI = QAction(self.name)
        self.mActionStartGUI.setIcon(self.icon())
        self.mActionStartGUI.triggered.connect(self.startGUI)

    def icon(self):
        return self.mIcon

    def openglAvailable(self) -> bool:
        try:
            import OpenGL
            import PyQt5.QtOpenGL
            self.mErrorMessage = None
            return True
        except Exception as ex:
            self.mErrorMessage = ex
            return False

    def menu(self, appMenu):
        appMenu = self.enmapbox.menu('Tools')
        assert isinstance(appMenu, QMenu)
        appMenu.addAction(self.mActionStartGUI)

        return None

    def startGUI(self, *args):

        if self.openglAvailable():
            from imagecubeapp.imagecube import ImageCubeWidget
            #if not isinstance(self.mImageCubeWidget, ImageCubeWidget):
            mImageCubeWidget = ImageCubeWidget()
            mImageCubeWidget.setWindowTitle(self.name)
            mImageCubeWidget.setWindowIcon(self.icon())
            mImageCubeWidget.show()
        else:
            text = ['Unable to start ' + NAME]
            text.append('OpenGL / PyQt5.QtOpenGL not available')
            if isinstance(self.mErrorMessage, Exception):
                text.append(str(self.mErrorMessage))
            text = '\n'.join(text)
            QMessageBox.information(None, 'Missing Package', text)


def enmapboxApplicationFactory(enmapBox: EnMAPBox) -> list:
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: [list-of-EnMAPBoxApplications]
    """
    return [ImageCubeApplication(enmapBox)]
