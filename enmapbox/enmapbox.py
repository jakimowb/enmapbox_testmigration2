
from PyQt4 import QtCore, QtGui, uic

import six, sys, os

jp = os.path.join

DIR = os.path.dirname(__file__)
import gui
DIR_GUI = os.path.dirname(gui.__file__)
if DIR_GUI not in sys.path:
    sys.path.append(DIR_GUI)

if six.PY3:
    rc_suffix = '_py3'
    import gui.resources_py3
else:
    rc_suffix = '_py2'
    import gui.resources_py2

from qgis.gui import *
from qgis.core import *

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
        self.setWindowIcon(QtGui.QIcon(getIcon()))


def getQIcon():
    return QtGui.QIcon(getIcon())

def getIcon():
    p = jp(DIR_GUI, *['icons', 'enmapbox.png'])
    assert os.path.exists(p)
    return p



class EnMAPBox:
    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        self.iface = iface
        self.gui = EnMAPBox_GUI()
        self.gui.setWindowTitle('EnMAP-Box ' + VERSION)

        self.ViewManager = EnMAPBoxViewManager(self.gui.centralWidget())
        self.DataSourceManager = EnMAPBoxDataSourceManager()
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




class EnMAPBoxViewManager(QtCore.QObject):

    def __init__(self, centralwidget):
        self.views = dict()
        self.centralwidget = centralwidget
        pass

    def addView(self, view):
        assert isinstance(view, EnMAPBoxView)

    def removeView(self, view_name):
        if view_name in self.views.keys():
            self.views.pop(view_name)
        else:
            print("view does not exist:"+view_name)

    def getView(self, name):
        return self.views[name]



class EnMAPBoxView(QtGui.QFrame):

    def __init__(self):
        pass

    def close(self):
        pass

    def detach(self):
        pass
        w = QtGui.QWidget()
        #add GUI to detached widget

    def attach(self, viewManager):
        assert isinstance(viewManager, EnMAPBoxViewManager)




