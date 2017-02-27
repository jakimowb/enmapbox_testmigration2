from __future__ import absolute_import

import site

import qgis.core
import qgis.gui
from enmapbox import DIR, DIR_SITE_PACKAGES

VERSION = '2016-0.beta'


#DIR = os.path.dirname(__file__)
#DIR_REPO = os.path.dirname(DIR)
#DIR_SITE_PACKAGES = jp(DIR_REPO, 'site-packages')
#DIR_UI = jp(DIR, *['gui','ui'])
site.addsitedir(DIR_SITE_PACKAGES)

from enmapbox.gui.treeviews import *
from enmapbox.gui.docks import *



#todo: reduce imports to minimum
#import PyQt4
#import pyqtgraph
#import pyqtgraph.dockarea.DockArea


from PyQt4 import QtGui

from enmapbox.gui.datasources import *

RC_SUFFIX =  '_py3' if six.PY3 else '_py2'


"""
add_and_remove = DIR_GUI not in sys.path
if add_and_remove: sys.path.append(DIR_GUI)

ENMAPBOX_GUI_UI, qt_base_class = uic.loadUiType(os.path.normpath(jp(DIR_GUI, 'enmapbox_gui.ui')),
                                    from_imports=False, resource_suffix=RC_SUFFIX)
if add_and_remove: sys.path.remove(DIR_GUI)
del add_and_remove, RC_SUFFIX
"""


class EnMAPBox_GUI(QtGui.QMainWindow,
                   loadUIFormClass(os.path.normpath(jp(DIR_UI, 'enmapbox_gui.ui')),
                                   )):
    def __init__(self, parent=None):
        """Constructor."""
        super(EnMAPBox_GUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowIcon(getIcon())

        pass




def getIcon(name=IconProvider.EnMAP_Logo):
    return QtGui.QIcon(name)



class EnMAPBox():

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):

        assert EnMAPBox._instance is None
        EnMAPBox._instance = self
        self.iface = iface

        self.gui = EnMAPBox_GUI()
        self.gui.showMaximized()
        self.gui.setAcceptDrops(True)
        self.gui.setWindowTitle('EnMAP-Box ' + VERSION)

        self.dockarea = DockArea()
        self.gui.centralWidget().layout().addWidget(self.dockarea)


        self.dataSourceManager = DataSourceManager()
        self.dockManager = DockManager(self)

        def replaceView(view_old, view_new):
            assert isinstance(view_old, QTreeView)
            w = view_old.parentWidget()
            w.layout().removeWidget(view_old)
            name = view_old.objectName()
            view_new.setObjectName(name)
            w.layout().addWidget(view_new)
            view_new.setSizePolicy(view_old.sizePolicy())
            view_new.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # view.setMaximumSize(view_old.maximumSize())
            view_new.setMinimumSize(view_old.minimumSize())
            view_new.viewport().setAcceptDrops(True)
            view_new.setDragEnabled(True)
            view_new.setAcceptDrops(True)
            view_new.viewport().setAcceptDrops(True)
            view_new.setDropIndicatorShown(True)

            del view_old

        view = TreeView(None)
        view.setModel(DataSourceManagerTreeModel(view, self))
        view.setMenuProvider(TreeViewMenuProvider(view))

        self.gui.dataSourceTreeView = replaceView(self.gui.dataSourceTreeView,view)
        #workaround to get QgsLayerTreeView
        view = TreeView(None)
        view.setModel(DockManagerTreeModel(view, self))
        view.setMenuProvider(TreeViewMenuProvider(view))


        self.gui.dockTreeView = replaceView(self.gui.dockTreeView, view)

        #link action objects to action behaviour
        #self.gui.actionAddView.triggered.connect(lambda: self.dockarea.addDock(EnMAPBoxDock(self)))
        self.gui.actionAddMapView.triggered.connect(lambda : self.dockManager.createDock('MAP'))
        self.gui.actionAddTextView.triggered.connect(lambda: self.dockManager.createDock('TEXT'))
        self.gui.actionAddDataSource.triggered.connect(lambda: self.addSource(str(QFileDialog.getOpenFileName(self.gui, "Open a data source"))))
        self.gui.actionAddMimeView.triggered.connect(lambda : self.dockManager.createDock('MIME'))
        self.gui.actionCursor_Location_Values.triggered.connect(lambda : self.dockManager.createDock('CURSORLOCATIONVALUE'))
        self.gui.actionSave_Settings.triggered.connect(self.saveProject)
        s = ""


    def saveProject(self):
        proj = QgsProject.instance()
        proj.dumpObjectInfo()
        proj.dumpObjectTree()
        proj.dumpProperties()
        s = ""

    def restoreProject(self):
        s = ""


    def createDock(self, *args, **kwds):
        self.dockManager.createDock(*args, **kwds)

    def removeDock(self, *args, **kwds):
        self.dockManager.removeDock(*args, **kwds)

    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, qgis.gui.QgisInterface)

    def addSource(self, source, name=None):
        return self.dataSourceManager.addSource(source, name=name)



    def getURIList(self, *args, **kwds):
        return self.dataSourceManager.getURIList(*args, **kwds)

    @staticmethod
    def getIcon():
        return getIcon()

    def run(self):
        self.gui.show()
        pass


    def onDataSourceTreeViewCustomContextMenu(self, point):
        tv = self.gui.dataSourceTreeView
        assert isinstance(tv, QTreeView)
        index = tv.indexAt(point)


        model = tv.model()
        if index.isValid():
            treeItem = model.data(index, 'TreeItem')
            itemData = model.data(index, Qt.UserRole)

            if itemData or len(treeItem.actions) > 0:
                menu = QMenu()
                #append dynamic parts reactive to opened docks etc
                if isinstance(itemData, DataSource):
                    if isinstance(itemData, DataSourceSpatial):
                        mapDocks = [d for d in self.DOCKS if isinstance(d, MapDock)]
                        mapDocks = sorted(mapDocks, key=lambda d:d.name())
                        if len(mapDocks) > 0:
                            subMenu = QMenu()
                            subMenu.setTitle('Add to Map...')
                            for mapDock in mapDocks:
                                action = QAction('"{}"'.format(mapDock.name()), menu)
                                action.triggered.connect(lambda : mapDock.addLayer(itemData.getMapLayer()))
                                subMenu.addAction(action)
                            menu.addMenu(subMenu)
                        action = QAction('Add to new map', menu)
                        action.triggered.connect(lambda : self.createDock('MAP', initSrc=itemData))
                        menu.addAction(action)
                    action = QAction('Remove', menu)
                    action.triggered.connect(lambda : self.dataSourceManager.removeSource(itemData))
                else:
                    action = QAction('Copy', menu)
                    action.triggered.connect(lambda: QApplication.clipboard().setText(str(itemData)))
                #append item specific menue
                if len(treeItem.actions) > 0:
                    for action in treeItem.actions:
                        #action.setParent(menu)
                        menu.addAction(action)

                menu.exec_(tv.viewport().mapToGlobal(point))




        s = ""





class TestData():

    prefix = jp(os.path.normpath(DIR), *['testdata'])
    assert os.path.exists(prefix)
    RFC_Model = jp(prefix, 'rfc.model')

    prefix = jp(os.path.normpath(DIR), *['testdata', 'AlpineForeland'])
    assert os.path.exists(prefix)
    #assert os.path.isdir(prefix)

    AF_Image = jp(prefix, 'AF_Image.bip')
    AF_LAI = jp(prefix, r'AF_LAI.bsq')
    AF_LC = jp(prefix, r'AF_LC.bsq')
    AF_Mask = jp(prefix, r'AF_Mask.bsq')
    AF_MaskVegetation = jp(prefix, r'AF_MaskVegetation.bsq')






