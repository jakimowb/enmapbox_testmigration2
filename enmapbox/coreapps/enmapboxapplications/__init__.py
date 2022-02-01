from os.path import join, dirname

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from enmapbox.gui.applications import EnMAPBoxApplication
from enmapboxapplications.imagemathapp.core import ImageMathApp
from enmapboxapplications.regressionapp.core import RegressionWorkflowApp
from enmapboxapplications.synthmixapp.core import SynthmixApp
from hubdsm.processing.classificationstatistics import ClassificationStatistics


def enmapboxApplicationFactory(enmapBox):
    return [
        EnMAPBoxImageMathApp(enmapBox),
        EnMAPBoxSynthmixApp(enmapBox),
        EnMAPBoxRegressionWorkflowApp(enmapBox),
    ]


class EnMAPBoxImageMathApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'ImageMath'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        filename = join(dirname(__file__), 'imagemathapp', 'icons', 'numpy.png')
        return QIcon(filename)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('ImageMath')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ImageMathApp(parent=self.enmapbox.ui)
        w.addInput()
        w.show()

class EnMAPBoxSynthmixApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'Regression-based unmixing (synthMix)'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Regression-based unmixing (synthMix)')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = SynthmixApp(parent=self.enmapbox.ui)
        w.show()


class EnMAPBoxRegressionWorkflowApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'RegressionWorkflowApp'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Regression Workflow')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = RegressionWorkflowApp(parent=self.enmapbox.ui)
        w.show()


if __name__ == '__main__':

    from enmapbox.gui.utils import initQgisApplication

    qgsApp = initQgisApplication()

    import qgisresources.images

    qgisresources.images.qInitResources()

    if True:

        # widget = ImageMathApp()
        # widget = ImageStatisticsApp()
        # widget = ScatterPlotApp()
        widget = SynthmixApp()
        widget.show()

    else:

        enmapBox = EnMAPBox(None)
        enmapBox.run()
        enmapBox.openExampleData(mapWindows=1)

        for app in enmapboxApplicationFactory(enmapBox):
            enmapBox.addApplication(app)

    qgsApp.exec_()
