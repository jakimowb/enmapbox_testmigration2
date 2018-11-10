from os.path import join, dirname, basename
from PyQt5.Qt import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from enmapboxapplications.imagemathapp.core import ImageMathApp
from enmapboxapplications.imagestatistics.core import ImageStatisticsApp
from enmapboxapplications.scatterplotapp.core import ScatterPlotApp
from enmapboxapplications.synthmixapp.core import SynthmixApp
from enmapboxapplications.forceapp.core import ForceApp
from enmapboxapplications.classificationapp.core import ClassificationWorkflowApp

def enmapboxApplicationFactory(enmapBox):
    return [EnMAPBoxImageMathApp(enmapBox),
            EnMAPBoxImageStatisticsApp(enmapBox),
            EnMAPBoxScatterPlotApp(enmapBox),
            EnMAPBoxSynthmixApp(enmapBox),
            #EnMAPBoxForceMosaikBuilderApp(enmapBox),
            EnMAPBoxClassificationWorkflowApp(enmapBox)
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
        a = appMenu.addAction('ImageStatistics')
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
        a = appMenu.addAction('Scatterplot')
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

        self.name = 'SynthmixRegressionMapper'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Synthmix Regression Mapper')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = SynthmixApp(parent=self.enmapbox.ui)
        w.show()


class EnMAPBoxClassificationWorkflowApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'ClassificationWorkflowApp'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Classification Workflow')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ClassificationWorkflowApp(parent=self.enmapbox.ui)
        w.show()


class EnMAPBoxForceMosaikBuilderApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)
        self.name = 'ForceMosaikBuilder'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        appMenu = self.enmapbox.menu('Tools')
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Force Mosaik Builder')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ForceApp(parent=self.enmapbox.ui)
        w.show()

if __name__ == '__main__':

    from enmapbox.gui.utils import initQgisApplication
    from enmapbox.gui.enmapboxgui import EnMAPBox

    qgsApp = initQgisApplication()

    import qgisresources.images
    qgisresources.images.qInitResources()

    if True:

        #widget = ImageMathApp()
        #widget = ImageStatisticsApp()
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