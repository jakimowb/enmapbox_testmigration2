
from PyQt4 import QtCore, QtGui, uic

import six, sys, os

jp = os.path.join

DIR = os.path.dirname(__file__)
import gui
DIR_GUI = os.path.dirname(gui.__file__)

if six.PY3:
    rc_suffix = '_py3'
else:
    rc_suffix = '_py2'

ENMAPBOX_GUI_UI, _ = uic.loadUiType(jp(DIR_GUI, 'enmapbox_gui.ui'), resource_suffix=rc_suffix)

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
    return QtGui.QIcon(self.getIcon())

def getIcon():
    p = jp(DIR_GUI, *['icons', 'enmapbox.png'])
    assert os.path.exists(p)
    return p

class EnMAPBox:
    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        self.iface = iface
        self.gui = EnMAPBox_GUI(iface.mainWindow())
        pass


    def run(self):
        self.gui.show()
        pass
