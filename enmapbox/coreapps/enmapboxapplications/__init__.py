from os.path import join, dirname, basename
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction
from qgis._core import QgsRasterLayer

from enmapbox.gui.applications import EnMAPBoxApplication
from enmapbox.gui.dataviews.docks import DockTypes, MapDock
from enmapboxapplications.imagemathapp.core import ImageMathApp
from enmapboxapplications.imagestatistics.core import ImageStatisticsApp
from enmapboxapplications.scatterplotapp.core import ScatterPlotApp
from enmapboxapplications.synthmixapp.core import SynthmixApp
from enmapboxapplications.regressionapp.core import RegressionWorkflowApp
from hubdsm.processing.classificationstatistics import ClassificationStatistics


def enmapboxApplicationFactory(enmapBox):
    return [
        EnMAPBoxImageMathApp(enmapBox),
        EnMAPBoxImageStatisticsApp(enmapBox),
        EnMAPBoxScatterPlotApp(enmapBox),
        EnMAPBoxSynthmixApp(enmapBox),
        EnMAPBoxRegressionWorkflowApp(enmapBox),
        MenuEntries(enmapBox)
    ]


class MenuEntries(EnMAPBoxApplication):
    A_CLASSIFICATION_STATISTICS = 'Classification Statistics'

    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'Menu Entries'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def menu(self, appMenu):
        toolsMenu = self.enmapbox.menu('Tools')
        a = toolsMenu.addAction(self.A_CLASSIFICATION_STATISTICS)
        a.triggered.connect(self.actionTriggered)
        return toolsMenu

    def geoAlgorithms(self):
        return []

    def actionTriggered(self, *args):
        name = self.sender().text()
        if name == self.A_CLASSIFICATION_STATISTICS:
            self.enmapbox.showProcessingAlgorithmDialog(ClassificationStatistics())
        else:
            raise ValueError(name)



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


class EnMAPBoxImageStatisticsApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'Image Statistics'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        appMenu = self.enmapbox.menu('Tools')
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Image Statistics')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ImageStatisticsApp(parent=self.enmapbox.ui)
        w.show()


class EnMAPBoxScatterPlotApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'ScatterPlot'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        appMenu = self.enmapbox.menu('Tools')
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Scatter plot')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ScatterPlotApp(parent=self.enmapbox.ui)
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
    from enmapbox.gui.enmapboxgui import EnMAPBox

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
