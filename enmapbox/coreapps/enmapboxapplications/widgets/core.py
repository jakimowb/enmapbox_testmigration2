from os.path import join, dirname, basename, splitext, exists, isabs, abspath
from os import remove
import tempfile
from osgeo import gdal
import numpy
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from enmapbox.gui.utils import loadUIFormClass
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.datasources import DataSourceSpectralLibrary
from hubflow.core import *

pathUi = join(dirname(__file__), 'ui')

class UiLibrary(QComboBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enmapBox = EnMAPBox.instance()
        assert isinstance(self.enmapBox, EnMAPBox)
        self.enmapBox.sigDataSourceAdded.connect(self.setLibraries)

        self.names = list()
        self.filenames = list()
        self.setLibraries()
#        self.setCurrentIndex(0)

    def setLibraries(self, *args, **kwargs):

        for source in self.enmapBox.dataSourceManager.mSources:
            if isinstance(source, DataSourceSpectralLibrary):
                if source.mUri not in self.filenames:
                    self.names.append(source.mName)
                    self.filenames.append(source.mUri)
                    self.addItem(self.names[-1])

    def currentLibrary(self):
        if self.currentIndex() >= 0 and self.currentIndex() < len(self.filenames):
            return ENVISpectralLibrary(filename=self.filenames[self.currentIndex()])
        else:
            return None

class UiLabeledLibrary(QWidget, loadUIFormClass(pathUi=join(pathUi, 'labeledLibary.ui'))):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.uiLibrary().currentIndexChanged.connect(self.setFields)
        self.setFields(0)

    def uiLibrary(self):
        assert isinstance(self.uiLibrary_, UiLibrary)
        return self.uiLibrary_

    def uiField(self):
        assert isinstance(self.uiField_, QComboBox)
        return self.uiField_

    def setFields(self, index):
        for i in range(self.uiField().count()):
            self.uiField().removeItem(0)
        library = self.uiLibrary().currentLibrary()
        if library is not None:
            fields = library.attributeDefinitions()
            self.uiField().addItems(fields)

    def currentLibrary(self):
        return self.uiLibrary().currentLibrary()

    def currentField(self):
        text = self.uiField().currentText()
        if text is '':
            return None
        else:
            return text
