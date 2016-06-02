
from PyQt4 import QtCore, QtGui, uic

import six, sys, os

def add_to_sys_path(path):
    if path not in sys.path:
        sys.path.append(path)

jp = os.path.join

DIR = os.path.dirname(__file__)
import gui
DIR_GUI = os.path.dirname(gui.__file__)
add_to_sys_path(DIR_GUI)

try:
    import pyqtgraph as pg
except:
    add_to_sys_path(jp(DIR, 'libs'))
    import pyqtgraph as pg


if six.PY3:
    rc_suffix = '_py3'
    import gui.resources_py3
else:
    rc_suffix = '_py2'
    import gui.resources_py2

#todo: reduce imports to minimum
from qgis.gui import *
from qgis.core import *
import qgis.core
import qgis.gui
from PyQt4.Qt import *

VERSION = '2016-0.beta'
ENMAPBOX_GUI_UI, _ = uic.loadUiType(jp(DIR_GUI, 'enmapbox_gui.ui'), from_imports=False, resource_suffix=rc_suffix)

class EnMAPBox_GUI(QtGui.QMainWindow, ENMAPBOX_GUI_UI):
    def __init__(self, parent=None):
        """Constructor."""
        super(EnMAPBox_GUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowIcon(getQIcon())

        pass

def getQIcon():
    return QtGui.QIcon(getIcon())

def getIcon():
    p = jp(DIR_GUI, *['icons', 'enmapbox.png'])
    assert os.path.exists(p)
    return p



class EnMAPBox:
    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        print(iface)
        self.iface = iface
        self.gui = EnMAPBox_GUI()
        self.gui.setWindowTitle('EnMAP-Box ' + VERSION)
        self.layerregistry = qgis.core.QgsMapLayerRegistry.instance()
        self.dockarea = EnMAPBoxDockArea()
        self.gui.centralWidget().layout().addWidget(self.dockarea)
        #self.gui.centralWidget().addWidget(self.dockarea)
        self.DataSourceManager = EnMAPBoxDataSourceManager()



        #link action objects to action behaviour
        self.gui.actionAddView.triggered.connect(lambda: self.dockarea.addView(EnMAPBoxDock(self)))
        self.gui.actionAddMapView.triggered.connect(lambda : self.dockarea.addView(EnMAPBoxMapDock(self)))
        self.gui.actionAddTextView.triggered.connect(lambda: self.dockarea.addView(EnMAPBoxTextDock(self)))


    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, qgis.gui.QgisInterface)


    def addFile(self):
        s = ""
        pass

    @staticmethod
    def getIcon():
        return getQIcon()

    def run(self):
        self.gui.show()
        pass

    def addImage(self, path):
        pass

    def addView(self, path):
        pass


class EnMAPBoxDataSourceManager(QtCore.QObject):

    def __init__(self):
        pass

    def addSource(self, source):

        #switch to differentiate between sources
        if isinstance(source, str):
            #handle strings

            pass
        elif isinstance(source, qgis.core):
            pass
        pass

    def removeSource(self, source):
        pass

    pass

class TestData():

    prefix = jp(DIR, 'testdata')
    def __init__(self):
        pass


    @staticmethod
    def Image():
        return os.path.join(TestData.prefix, 'SF_20x20.tif')


    @staticmethod
    def AF_Image():
        return os.path.join(TestData.prefix, 'AF_Image')

    @staticmethod
    def Landsat_Image():
        return os.path.join(TestData.prefix, 'xyz.img')
    pass


from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.dockarea.Dock import Dock, DockLabel
from pyqtgraph.dockarea.DockDrop import *
class EnMAPBoxDock(Dock):
    '''
    Handle style sheets etc., basic stuff that differs from pyqtgraph dockarea
    '''
    def __init__(self, enmapbox, name='view', closable=True, *args, **kwds):
        super(EnMAPBoxDock, self).__init__(name=name, closable=False, *args, **kwds)
        self.enmapbox = enmapbox
        self.title = name
        self.setStyleSheet('background:#FFF')
        #change the enmapbox-like things
        self.topLayout.removeWidget(self.label)
        del self.label


        self.label = self._getLabel()
        self.topLayout.addWidget(self.label, 0, 1)

        if closable:
            self.label.sigCloseClicked.connect(self.close)

        self.raiseOverlay()


        self.hStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top-width: 0px;
        }
        """
        self.vStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-left-width: 0px;
        }
        """
        self.nStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
        }"""
        self.dragStyle = """
        EnMAPBoxDock > QWidget {
            border: 4px solid #00F;
            border-radius: 5px;
        }"""

        self.widgetArea.setStyleSheet(self.hStyle)
        self.topLayout.update()

    def _getLabel(self):
        """
        This functions returns the Label that is used to style the Dock
        :return:
        """
        return EnMAPBoxDockLabel(self)

    def append_hv_style(self, stylestr):
        obj_name = type(self).__name__
        style = ' \n{} {{\n{}\n}} '.format(obj_name, stylestr)
        self.hStyle += style
        self.vStyle += style

from pyqtgraph.widgets.VerticalLabel import VerticalLabel
class EnMAPBoxDockLabel(VerticalLabel):
    sigClicked = QtCore.Signal(object, object)
    sigCloseClicked = QtCore.Signal()
    sigNormalClicked = QtCore.Signal()

    def __init__(self, dock):
        assert isinstance(dock, EnMAPBoxDock)
        self.dim = False
        self.fixedWidth = False
        self.dock = dock
        VerticalLabel.__init__(self, self.dock.title, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.updateStyle()
        self.setAutoFillBackground(False)
        self.startedDrag = False
        self.buttons = list() #think from right to left
        self.pressPos = QtCore.QPoint()

        closeButton = QtGui.QToolButton(self)
        closeButton.setToolTip('Close window')
        closeButton.clicked.connect(self.sigCloseClicked)
        closeButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarCloseButton))
        self.buttons.append(closeButton)

        if True:
            floatButton = QtGui.QToolButton(self)
            #testButton.clicked.connect(self.sigNormalClicked)
            floatButton.setToolTip('Float this window')
            floatButton.clicked.connect(lambda : self.dock.float())
            floatButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarNormalButton))
            self.buttons.append(floatButton)

    def updateStyle(self):
        r = '3px'
        if self.dim:
            fg = '#aaa'
            bg = '#44a'
            border = '#339'
        else:
            fg = '#fff'
            bg = '#66c'
            border = '#55B'

        if self.orientation == 'vertical':
            self.vStyle = """EnMAPBoxDockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """EnMAPBoxDockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.hStyle)

    def setDim(self, d):
        if self.dim != d:
            self.dim = d
            self.updateStyle()

    def setOrientation(self, o):
        VerticalLabel.setOrientation(self, o)
        self.updateStyle()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pressPos = ev.pos()
            self.startedDrag = False
            ev.accept()

    def mouseMoveEvent(self, ev):
        if not self.startedDrag and (
            ev.pos() - self.pressPos).manhattanLength() > QtGui.QApplication.startDragDistance():
            self.dock.startDrag()
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if not self.startedDrag:
            self.sigClicked.emit(self, ev)
        ev.accept()

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dock.float()

    def resizeEvent(self, ev):
        if self.orientation == 'vertical':
            size = ev.size().width()
        else:
            size = ev.size().height()

        for i, btn in enumerate([b for b in self.buttons if not b.isHidden()]):
            if self.orientation == 'vertical':
                pos = QtCore.QPoint(0, i * size)
            else:
                pos = QtCore.QPoint(ev.size().width() - (i+1)*size, 0)
            btn.setFixedSize(QtCore.QSize(size, size))
            btn.move(pos)

        super(EnMAPBoxDockLabel, self).resizeEvent(ev)

class EnMAPBoxMapDockLabel(EnMAPBoxDockLabel):

    def __init__(self, *args, **kwds):

        super(EnMAPBoxMapDockLabel, self).__init__(*args, **kwds)

        linkButton = QtGui.QToolButton(self)
        # testButton.clicked.connect(self.sigNormalClicked)
        linkButton.setToolTip('Link map window with other map windows')
        linkButton.clicked.connect(lambda: self.dock.linkWithMapDock())
        linkButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink))
        self.buttons.append(linkButton)


class EnMAPBoxMapDock(EnMAPBoxDock):
    """
    A dock to visualize geodata that can be mapped
    """
    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)


        super(EnMAPBoxMapDock, self).__init__(*args, **kwds)

        self.canvas = qgis.gui.QgsMapCanvas(self)
        settings = QSettings()
        assert isinstance(self.canvas, qgis.gui.QgsMapCanvas)
        self.canvas.setCanvasColor(Qt.green)
        self.canvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        self.canvas.useImageToRender(settings.value('/qgis/use_image_to_render', False, type=bool))
        self.layout.addWidget(self.canvas)

        #link canvas to map tools
        g = self.enmapbox.gui
        g.actionAddView.triggered.connect(lambda: self.dockarea.addView(EnMAPBoxDock(self)))
        g.actionAddMapView.triggered.connect(lambda : self.dockarea.addView(EnMAPBoxMapDock(self)))
        g.actionAddTextView.triggered.connect(lambda: self.dockarea.addView(EnMAPBoxTextDock(self)))

        # create the map tools and linke them to the toolbar actions
        self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)
        self.toolPan.setAction(g.actionPan)
        self.toolPan.action().triggered.connect(lambda: self.canvas.setMapTool(self.toolPan))

        self.toolZoomIn = qgis.gui.QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(g.actionZoomIn)
        self.toolZoomIn.action().triggered.connect(lambda: self.canvas.setMapTool(self.toolZoomIn))

        self.toolZoomOut = qgis.gui.QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(g.actionZoomOut)
        self.toolZoomOut.action().triggered.connect(lambda: self.canvas.setMapTool(self.toolZoomOut))

        #todo: add pixel inspect

        #set default map tool
        self.canvas.setMapTool(self.toolPan)

        #todo: context menu

        if initSrc:
            self.addLayer(initSrc)

    def _getLabel(self):
        return EnMAPBoxMapDockLabel(self)

    def linkWithMapDock(self, mapDock):
        assert isinstance(mapDock, EnMAPBoxMapDock)




    def addLayer(self, layerSrc):

        #todo: handle input src
        lyr = None
        if type(layerSrc) is str:
            if os.path.exists(layerSrc):
                lyr = qgis.core.QgsRasterLayer(layerSrc)

        if lyr is not None:
            self.enmapbox.layerregistry.addMapLayer(lyr, True)
            self.canvas.setExtent(lyr.extent())
            #todo: handle multiple layers
            canvasLayers = self.canvas.layers()
            canvasLayers.append(qgis.gui.QgsMapCanvasLayer(lyr))
            self.canvas.setLayerSet(canvasLayers)

        pass


class EnMAPBoxTextDock(EnMAPBoxDock):

    """
    A dock to visualize textural data
    """
    def __init__(self, *args, **kwds):
        html = kwds.pop('html', None)
        plainTxt = kwds.pop('plainTxt', None)

        super(EnMAPBoxTextDock, self).__init__(*args, **kwds)

        self.edit = QtGui.QTextEdit(self)

        if html:
            self.edit.insertHtml(html)
        elif plainTxt:
            self.edit.insertPlainText(plainTxt)
        self.layout.addWidget(self.edit)



class EnMAPBoxDockArea(DockArea):

    def __init__(self, *args, **kwds):
        super(EnMAPBoxDockArea, self).__init__(*args, **kwds)


    def addView(self, enmapboxdock, **kwds):
        assert isinstance(enmapboxdock, EnMAPBoxDock)
        self.addDock(dock=enmapboxdock, **kwds)




def create_qgis_instance():
    pass


if __name__ == '__main__':

    #start a QGIS instance

    from qgis.gui import *
    from qgis.core import *
    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
    else:
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()


#    w = QMainWindow()
#    w.setWindowTitle('QgsMapCanvas Example')
#    w.show()
   # EB = EnMAPBox(w)
    EB = EnMAPBox(None)
    EB.dockarea.addView(EnMAPBoxDock(EB, name='view1 Default'))
    EB.dockarea.addView(EnMAPBoxMapDock(EB, name='view2: a map', initSrc=TestData.Image()))
    EB.dockarea.addView(EnMAPBoxTextDock(EB,
                                         name='view3: a text/info window',
                                         html='Lore <i>ipsum</i> tralalla<br/> '
                                              '<a href="http://www.enmap.org">www.enmap.org</a>'))
    EB.dockarea.addView(EnMAPBoxMapDock(EB, name='view4: another map', initSrc=TestData.Image()))
    #EB.show()
    EB.run()


    qgsApp.exec_()

    qgsApp.exitQgis()

    # qgsApp.exitQgis()
    # app.exec_()
    pass

    #load the plugin
    print('Done')

