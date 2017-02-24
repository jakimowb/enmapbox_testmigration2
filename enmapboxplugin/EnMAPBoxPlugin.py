import traceback
from ProcessingPlugin import ProcessingPlugin
from ViewerPlugin import ViewerPlugin


class EnMAPBoxPlugin:

    def __init__(self, iface):
        self.processingPlugin = ProcessingPlugin(iface)
        self.viewerPlugin = ViewerPlugin(iface)

    def initGui(self):

        self.processingPlugin.initGui()
        self.viewerPlugin.initGui()

    def unload(self):
        self.processingPlugin.unload()
        self.viewerPlugin.unload()

