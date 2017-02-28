import traceback
from ProcessingPlugin import ProcessingPlugin
from ViewerPlugin import ViewerPlugin


class EnMAPBoxPlugin:

    def __init__(self, iface):
        try:
            self.processingPlugin = ProcessingPlugin(iface)
        except Exception as error:
            self.processingPlugin = DefectPluginHandler(iface, error)

        try:
            self.viewerPlugin = ViewerPlugin(iface)
        except Exception as error:
            self.viewerPlugin = DefectPluginHandler(iface, error)

    def initGui(self):

        self.processingPlugin.initGui()
        self.viewerPlugin.initGui()

    def unload(self):
        self.processingPlugin.unload()
        self.viewerPlugin.unload()

class DefectPluginHandler(object):

    def __init__(self, iface, error):
        self.iface = iface
        self.error = error

    def initGui(self):
        pass

    def unload(self):
        pass