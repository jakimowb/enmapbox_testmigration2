from __future__ import absolute_import
import inspect
import os
import six
import traceback
import sys
import importlib
import re
import site

from qgis.gui import *
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *



jp = os.path.join
DIR_REPO = os.path.normpath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
DIR_SITE_PACKAGES = jp(DIR_REPO, 'site-packages')

DEPENDENCIES_MANDATORY = ['numpy','scipy','sklearn','matplotlib']
DEPENDENCIES_OPTIONAL = ['foobar','astrolib']


class ViewerPlugin:
    def __init__(self, iface):
        self.iface = iface

        ##########################################
        # Viewer integration is currently broken #
        return

        #activate python console. this is required to redirect all printouts done to stdout / stderr
        import console.console as CONSOLE
        if CONSOLE._console is None:
            CONSOLE._console = CONSOLE.PythonConsole(iface.mainWindow())
            QTimer.singleShot(0, CONSOLE._console.activate)


    def has_processing_framework(self):
        try:
            from processing.core import Processing
            return True
        except:
            return False


    def initGui(self):

        ##########################################
        # Viewer integration is currently broken #
        return


        self.toolbarActions = []
        self.pluginLayerTypes = dict()
        self.processingProviders = []
        self.enmapbox = None

        syspaths = [os.path.normpath(p) for p in sys.path]
        if DIR_REPO not in syspaths: sys.path.append(DIR_REPO)

        #add platform independent site-packages
        site.addsitedir(DIR_SITE_PACKAGES)

        #add platform specific site-packages
        site.addsitedir(jp(DIR_SITE_PACKAGES, os.sys.platform))

        from enmapbox.main import EnMAPBox
        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.run)
        self.toolbarActions.append(action)
        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)



        import enmapbox.utils
        dprint = enmapbox.main.dprint
        dprint('INIT ENMAPBOX-GUI')

        for p in DEPENDENCIES_MANDATORY:
            enmapbox.utils.check_package(p, stop_on_error=True)
        for p in DEPENDENCIES_OPTIONAL:
            failed = []
            if not enmapbox.utils.check_package(p):
                failed.append(p)
            if len(failed) > 0:
                dprint('Unable to load the following optional packages : {}'.format(', '.join(failed)))


        dprint('REGISTER ENMAPBOX PLUGIN LAYER(S)')
        self.pluginLayerTypes[WatermarkPluginLayer.LAYER_TYPE] = WatermarkPluginLayerType()
        for key, plugin in self.pluginLayerTypes.items():
            dprint('add '+key)
            QgsPluginLayerRegistry.instance().addPluginLayerType(plugin)

        # init processing provider
        dprint('INIT ENMAPBOX PROCESSING PROVIDER(S)')
        if self.has_processing_framework():
            # add example app
            try:
                from processing.core.Processing import Processing
                from enmapbox.apps.core import EnMAPBoxProvider
                self.processingProviders.append(EnMAPBoxProvider())
                #add providers to processing framework

                for provider in self.processingProviders:
                    Processing.addProvider(provider)

            except Exception, e:
                tb = traceback.format_exc()
                six.print_('ERROR occurred while loading EnMAPBoxProvider for processing frame work:', file=sys.stderr)
                six.print_(str(e))
                six.print_(tb)

            dprint('Processing framework initialization done')
        else:
            dprint('Unable to fine processing framework')
        dprint('EnMAP-Box initialization done')

    def run(self):
        from enmapbox.main import EnMAPBox

        self.enmapbox = EnMAPBox.instance()
        if not self.enmapbox:
            self.enmapbox = EnMAPBox(self.iface)
        self.enmapbox.run()

    def unload(self):

        ##########################################
        # Viewer integration is currently broken #
        return

        import enmapbox.main
        dprint = enmapbox.main.dprint

        for action in self.toolbarActions:
            print(action)
            self.iface.removeToolBarIcon(action)

        for key, plugin in self.pluginLayerTypes.items():
            QgsPluginLayerRegistry.instance().removePluginLayerType(key)

        if self.has_processing_framework():
            from processing.core.Processing import Processing
            for provider in self.processingProviders:
                Processing.removeProvider(provider)

        dprint('UNLOAD ENMAPBOX INSTANCE')
        from enmapbox.main import EnMAPBox
        if isinstance(self.enmapbox, EnMAPBox):
            self.enmapbox.gui.close()
            self.enmapbox = None
            EnMAPBox._instance = None





    def tr(self, message):
        return QCoreApplication.translate('EnMAPBoxPlugin', message)


class WatermarkPluginLayer(QgsPluginLayer):

    LAYER_TYPE="watermark"

    def __init__(self):
        QgsPluginLayer.__init__(self, WatermarkPluginLayer.LAYER_TYPE, "Watermark plugin layer")
        self.setValid(True)

        self.image_path = "."
        self.image = None

    def draw(self, rendererContext):
        if self.image != None:
            painter = rendererContext.painter()
            extent = rendererContext.extent()
            mapToPixel = rendererContext.mapToPixel()
            rasterScaleFactor = rendererContext.rasterScaleFactor()
            invRasterScaleFactor = 1.0/rasterScaleFactor

            # get dimensions of painter area (so it is also correctly scaled in print composer)
            # Note: watermark is not correctly scaled in print preview
            topleft = mapToPixel.transform(extent.xMinimum(), extent.yMaximum())
            bottomright = mapToPixel.transform(extent.xMaximum(), extent.yMinimum())
            width = (bottomright.x() - topleft.x()) * rasterScaleFactor
            height = (bottomright.y() - topleft.y()) * rasterScaleFactor


            # setup painter
            painter.save()
            painter.scale(invRasterScaleFactor, invRasterScaleFactor)

            # render watermark image in lower left corner
            painter.setOpacity(0.5)
            y = height - 32 - self.image.height()
            painter.drawImage(32, y, self.image)

            painter.restore()

        return True

    def readXml(self, node):
        # custom properties
        self.readImage( node.toElement().attribute("image_path", ".") )
        return True

    def writeXml(self, node, doc):
        element = node.toElement();
        # write plugin layer type to project  (essential to be read from project)
        element.setAttribute("type", "plugin")
        element.setAttribute("name", WatermarkPluginLayer.LAYER_TYPE);
        # custom properties
        element.setAttribute("image_path", str(self.image_path))
        return True

    def readImage(self, image_path):
        self.image_path = image_path
        self.image = QImage(self.image_path)

    def showImageDialog(self):
        filename = QFileDialog.getOpenFileName(None, "Select watermark image", self.image_path, "Image Files (*.png *.jpg *.bmp)")
        if filename != "":
            self.readImage(filename)

        # trigger repaint
        self.setCacheImage(None)
        self.emit(SIGNAL("repaintRequested()"))


class WatermarkPluginLayerType(QgsPluginLayerType):

    def __init__(self):
        QgsPluginLayerType.__init__(self, WatermarkPluginLayer.LAYER_TYPE)

    def createLayer(self):
        return WatermarkPluginLayer()

    def showLayerProperties(self, layer):
        layer.showImageDialog()

        # indicate that we have shown the properties dialog
        return True


