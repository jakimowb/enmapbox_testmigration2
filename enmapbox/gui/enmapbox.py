
from PyQt4 import QtCore, QtGui, uic

import six, sys, os

DIR = os.path.dirname(__file__)

sys.path.append(DIR)

if six.PY3:
    rc_suffix = '_py3'
else:
    rc_suffix = '_py2'

ENMAPBOX_UI, _ = uic.loadUiType(os.path.join(DIR, 'enmapbox.ui'), resource_suffix=rc_suffix)

class EnMAPBox(QtGui.QMainWindow, ENMAPBOX_UI):
#class EnMAPBoxGUI(QtGUI.QMainwindow, Ui_EnMAPBoxGUIBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(EnMAPBox, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
