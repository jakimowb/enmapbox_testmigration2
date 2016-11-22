from __future__ import absolute_import
import six, sys, os, gc, re, collections, site
import itertools
import numpy as np
from qgis.core import *
from qgis.gui import *

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyqtgraph.graphicsItems import *
from enmapbox.utils import *
from enmapbox.main import DIR_UI

"""
class RasterLayerProperties(QgsOptionsDialogBase):
    def __init__(self, lyr, canvas, parent, fl=Qt.Widget):
        super(RasterLayerProperties, self).__init__("RasterLayerProperties", parent, fl)
        # self.setupUi(self)
        self.initOptionsBase(False)
        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)
"""

class RasterLayerProperties(QgsOptionsDialogBase,
        loadUIFormClass(os.path.normpath(jp(DIR_UI, 'rasterlayerpropertiesdialog.ui')),
                                   )):
    def __init__(self, lyr, canvas, parent=None):
        """Constructor."""
        title = 'RasterLayerProperties'
        super(RasterLayerProperties, self).__init__(title, parent, Qt.Dialog, settings=QSettings())
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use auto connect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initOptionsBase(False, title)
        #self.restoreOptionsBaseUi('TITLE')
        self.rasterLayer = lyr
        self.canvas = canvas

        self.oldStyle = self.rasterLayer.styleManager().style(self.rasterLayer.styleManager().currentStyle())

        self.accepted.connect(self.apply)
        self.rejected.connect(self.onCancel)
        pass

    def onCancel(self):
        #restore style
        if self.oldStyle.xmlData() != self.rasterLayer.styleManager().style(
                self.rasterLayer.styleManager().currentStyle()
        ).xmlData():

            s = ""

    def apply(self):
        #apply settings
        s = ""

    def sync(self):
        # fill widgets with layer values here

        s  =""

    def syncToLayer(self):
        renderer = self.rasterLayer.renderer()
        if renderer:
            self.setRendererWidget(renderer.type())

        self.sync()
        self.rasterLayer.triggerRepaint()

    def setRendererWidget(self, rendererName):

        s = ""

class VectorLayerProperties(QgsOptionsDialogBase):

    def __init__(self, lyr, canvas, parent, fl=Qt.Widget):
        super(RasterLayerProperties, self).__init__("VectorLayerProperties", parent, fl)
        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)

def showLayerPropertiesDialog(layer, canvas, parent):
    d = None
    if isinstance(layer, QgsRasterLayer):
        d = RasterLayerProperties(layer, canvas, parent)
        d.setSettings(QSettings())
    elif isinstance(layer, QgsVectorLayer):
        d = VectorLayerProperties(layer, canvas, parent)
    else:
        assert NotImplementedError()
    d.exec_()



