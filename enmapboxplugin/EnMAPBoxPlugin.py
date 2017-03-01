from ProcessingPlugin import ProcessingPlugin
from GUIPlugin import GUIPlugin


class EnMAPBoxPlugin:

    def __init__(self, iface):

        self.iface = iface
        self.processingPlugin = self._tryPlugin(ProcessingPlugin)
        self.viewerPlugin = self._tryPlugin(GUIPlugin)

    def initGui(self):

        self.processingPlugin.initGui()
        self.viewerPlugin.initGui()

    def unload(self):

        self.processingPlugin.unload()
        self.viewerPlugin.unload()

    def _tryPlugin(self, Plugin):

        try:
            return Plugin(self.iface)
        except:
            self._initConsole()
            self._printTraceback()
            return DefectPluginHandler()

    def _initConsole(self):

        from console.console import _console, PythonConsole
        from PyQt4.QtCore import QTimer
        if _console is None:
            _console = PythonConsole(self.iface.mainWindow())
            QTimer.singleShot(0, _console.activate)

    def _printTraceback(self):

        import traceback, sys
        traceback.print_exc(file=sys.stdout)


class DefectPluginHandler(object):

    def initGui(self):
        pass

    def unload(self):
        pass
