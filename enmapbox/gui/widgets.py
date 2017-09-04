
import os, collections
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.utils import loadUI

class OpenFileWidget(QWidget, loadUI('openfilewidget.ui')):

    def __init__(self, title='<#>', parent=None):
        super(OpenFileWidget, self).__init__(parent)
        self.setupUi(self)

    def setFileType(self, type):

        pass



