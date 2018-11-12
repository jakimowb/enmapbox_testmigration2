import os, sys, re
import qgis
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.Qt import QApplication
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
import qgis.testing


SHOW_GUI = True

def initQgisApplication(*args, **kwds):
    """
    Initializes a QGIS Environment
    :return: QgsApplication instance of local QGIS installation
    """
    if isinstance(QgsApplication.instance(), QgsApplication):
        return QgsApplication.instance()
    else:

        if not 'QGIS_PREFIX_PATH' in os.environ.keys():
            raise Exception('env variable QGIS_PREFIX_PATH not set')


        if sys.platform == 'darwin':
            # search for the QGIS.app
            assert '.app' in qgis.__file__, 'Can not locate path of QGIS.app'
            PATH_QGIS_APP = re.split(r'\.app[\/]', qgis.__file__)[0] + '.app'
            PATH_QGIS = os.path.join(PATH_QGIS_APP, *['Contents', 'MacOS'])


            QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns']))
            QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns', 'qgis']))


        qgsApp = qgis.testing.start_app()

        #initiate a PythonRunner instance if None exists
        if not QgsPythonRunner.isValid():
            r = PythonRunnerImpl()
            QgsPythonRunner.setInstance(r)
        return qgsApp



class PythonRunnerImpl(QgsPythonRunner):
    """
    A Qgs PythonRunner implementation
    """

    def __init__(self):
        super(PythonRunnerImpl, self).__init__()


    def evalCommand(self, cmd:str, result:str):
        try:
            o = compile(cmd)
        except Exception as ex:
            result = str(ex)
            return False
        return True

    def runCommand(self, command, messageOnError=''):
        try:
            o = compile(command, 'fakemodule', 'exec')
            exec(o)
        except Exception as ex:
            messageOnError = str(ex)
            command = ['{}:{}'.format(i+1, l) for i,l in enumerate(command.splitlines())]
            print('\n'.join(command), file=sys.stderr)
            raise ex
            return False
        return True

class QgisMockup(QgisInterface):
    """
    A "fake" QGIS Desktop instance that should provide all the inferfaces a plugin developer might need (and nothing more)
    """

    def pluginManagerInterface(self)->QgsPluginManagerInterface:
        return self.mPluginManager

    @staticmethod
    def create()->QgisInterface:
        """
        Create the QgisMockup and sets the global variables
        :return: QgisInterface
        """

        iface = QgisMockup()

        import qgis.utils
        # import processing
        # p = processing.classFactory(iface)
        if not isinstance(qgis.utils.iface, QgisInterface):

            import processing
            qgis.utils.iface = iface
            processing.Processing.initialize()

            import pkgutil
            prefix = str(processing.__name__ + '.')
            for importer, modname, ispkg in pkgutil.walk_packages(processing.__path__, prefix=prefix):
                try:
                    module = __import__(modname, fromlist="dummy")
                    if hasattr(module, 'iface'):
                        print(modname)
                        module.iface = iface
                except:
                    pass
        #set 'home_plugin_path', which is required from the QGIS Plugin manager
        assert qgis.utils.iface == iface
        qgis.utils.home_plugin_path = os.path.join(QgsApplication.instance().qgisSettingsDirPath(), *['python', 'plugins'])
        return iface

    def __init__(self, *args):
        # QgisInterface.__init__(self)
        super(QgisMockup, self).__init__()

        self.mCanvas = QgsMapCanvas()
        self.mCanvas.blockSignals(False)
        self.mCanvas.setCanvasColor(Qt.black)
        self.mCanvas.extentsChanged.connect(self.testSlot)
        self.mLayerTreeView = QgsLayerTreeView()
        self.mRootNode = QgsLayerTree()
        self.mLayerTreeModel = QgsLayerTreeModel(self.mRootNode)
        self.mLayerTreeView.setModel(self.mLayerTreeModel)
        self.mLayerTreeMapCanvasBridge = QgsLayerTreeMapCanvasBridge(self.mRootNode, self.mCanvas)
        self.mLayerTreeMapCanvasBridge.setAutoSetupOnFirstLayer(True)

        import pyplugin_installer.installer
        PI = pyplugin_installer.instance()
        self.mPluginManager = QgsPluginManagerMockup()

        self.ui = QMainWindow()



        self.mMessageBar = QgsMessageBar()
        mainFrame = QFrame()

        self.ui.setCentralWidget(mainFrame)
        self.ui.setWindowTitle('QGIS Mockup')


        l = QHBoxLayout()
        l.addWidget(self.mLayerTreeView)
        l.addWidget(self.mCanvas)
        v = QVBoxLayout()
        v.addWidget(self.mMessageBar)
        v.addLayout(l)
        mainFrame.setLayout(v)
        self.ui.setCentralWidget(mainFrame)
        self.lyrs = []
        self.createActions()

    def iconSize(self, dockedToolbar=False):
        return QSize(30,30)

    def testSlot(self, *args):
        # print('--canvas changes--')
        s = ""

    def mainWindow(self):
        return self.ui


    def addToolBarIcon(self, action):
        assert isinstance(action, QAction)

    def removeToolBarIcon(self, action):
        assert isinstance(action, QAction)


    def addVectorLayer(self, path, basename=None, providerkey=None):
        if basename is None:
            basename = os.path.basename(path)
        if providerkey is None:
            bn, ext = os.path.splitext(basename)

            providerkey = 'ogr'
        l = QgsVectorLayer(path, basename, providerkey)
        assert l.isValid()
        QgsProject.instance().addMapLayer(l, True)
        self.mRootNode.addLayer(l)
        self.mLayerTreeMapCanvasBridge.setCanvasLayers()
        s = ""

    def legendInterface(self):
        return None

    def addRasterLayer(self, path, baseName=''):
        l = QgsRasterLayer(path, os.path.basename(path))
        self.lyrs.append(l)
        QgsProject.instance().addMapLayer(l, True)
        self.mRootNode.addLayer(l)
        self.mLayerTreeMapCanvasBridge.setCanvasLayers()
        return

        cnt = len(self.canvas.layers())

        self.canvas.setLayerSet([QgsMapCanvasLayer(l)])
        l.dataProvider()
        if cnt == 0:
            self.canvas.mapSettings().setDestinationCrs(l.crs())
            self.canvas.setExtent(l.extent())

            spatialExtent = SpatialExtent.fromMapLayer(l)
            # self.canvas.blockSignals(True)
            self.canvas.setDestinationCrs(spatialExtent.crs())
            self.canvas.setExtent(spatialExtent)
            # self.blockSignals(False)
            self.canvas.refresh()

        self.canvas.refresh()

    def createActions(self):
        m = self.ui.menuBar().addAction('Add Vector')
        m = self.ui.menuBar().addAction('Add Raster')

    def mapCanvas(self):
        return self.mCanvas

    def mapNavToolToolBar(self):
        super().mapNavToolToolBar()

    def messageBar(self, *args, **kwargs):
        return self.mMessageBar

    def rasterMenu(self):
        super().rasterMenu()

    def vectorMenu(self):
        super().vectorMenu()

    def viewMenu(self):
        super().viewMenu()

    def windowMenu(self):
        super().windowMenu()

    def zoomFull(self, *args, **kwargs):
        super().zoomFull(*args, **kwargs)


class TestObjects():
    """
    Class with static rountines to create test objects
    """
    @staticmethod
    def inMemoryClassification(n=3, nl=10, ns=20, nb=1, crs='EPSG:32632'):
        from enmapbox.gui.classification.classificationscheme import ClassificationScheme
        scheme = ClassificationScheme()
        scheme.createClasses(n)

        drv = gdal.GetDriverByName('GTiff')
        assert isinstance(drv, gdal.Driver)
        import uuid
        path = '/vsimem/testClassification.{}.tif'.format(str(uuid.uuid4()))
        ds = drv.Create(path, ns, nl, bands=nb, eType=gdal.GDT_Byte)
        assert isinstance(ds, gdal.Dataset)
        if isinstance(crs, str):
            c = QgsCoordinateReferenceSystem(crs)
            ds.SetProjection(c.toWkt())
        ds.SetGeoTransform([0,1.0,0, \
                            0,0,-1.0])
        step = int(np.ceil(float(nl) / len(scheme)))

        assert isinstance(ds, gdal.Dataset)
        for b in range(1, nb + 1):
            band = ds.GetRasterBand(b)
            array = np.zeros((nl, ns), dtype=np.uint8) - 1
            y0 = 0
            for i, c in enumerate(scheme):
                y1 = min(y0 + step, nl - 1)
                array[y0:y1, :] = c.label()
                y0 += y1 + 1
            band.SetCategoryNames(scheme.classNames())
            band.SetColorTable(scheme.gdalColorTable())
        ds.FlushCache()
        return ds

    @staticmethod
    def createDropEvent(mimeData:QMimeData):
        """Creates a QDropEvent conaining the provided QMimeData"""
        return QDropEvent(QPointF(0, 0), Qt.CopyAction, mimeData, Qt.LeftButton, Qt.NoModifier)


    @staticmethod
    def processingAlgorithm():

        from qgis.core import QgsProcessingAlgorithm

        class TestProcessingAlgorithm(QgsProcessingAlgorithm):

            def __init__(self):
                super(TestProcessingAlgorithm, self).__init__()
                s = ""

            def createInstance(self):
                return TestProcessingAlgorithm()

            def name(self):
                return 'exmaplealg'

            def displayName(self):
                return 'Example Algorithm'

            def groupId(self):
                return 'exampleapp'

            def group(self):
                return 'TEST APPS'

            def initAlgorithm(self, configuration=None):
                self.addParameter(QgsProcessingParameterRasterLayer('pathInput', 'The Input Dataset'))
                self.addParameter(
                    QgsProcessingParameterNumber('value', 'The value', QgsProcessingParameterNumber.Double, 1, False,
                                                 0.00, 999999.99))
                self.addParameter(QgsProcessingParameterRasterDestination('pathOutput', 'The Output Dataset'))

            def processAlgorithm(self, parameters, context, feedback):
                assert isinstance(parameters, dict)
                assert isinstance(context, QgsProcessingContext)
                assert isinstance(feedback, QgsProcessingFeedback)


                outputs = {}
                return outputs

        return TestProcessingAlgorithm()



    @staticmethod
    def enmapBoxApplication():

        from enmapbox.gui.applications import EnMAPBoxApplication
        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapbox = EnMAPBox.instance()

        class TestApp(EnMAPBoxApplication):
            def __init__(self, enmapbox):
                super(TestApp, self).__init__(enmapbox)

                self.name = 'TestApp'
                self.licence = 'GPL-3'
                self.version = '-12345'

            def menu(self, appMenu:QMenu)->QMenu:
                menu = appMenu.addMenu('Test Menu')
                action = menu.addAction('Test Action')
                action.triggered.connect(self.onAction)
                return menu

            def onAction(self):
                print('TestApp action called')

            def processingAlgorithms(self):
                return [TestObjects.processingAlgorithm()]

        return TestApp(enmapbox)
