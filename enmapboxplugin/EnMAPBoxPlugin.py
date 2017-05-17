import traceback
from qgis.gui import QgsMessageBar, QgsMessageBarItem
from qgis.core import QgsMessageLog, QgsMessageLogConsole
from ProcessingPlugin import ProcessingPlugin
from GUIPlugin import GUIPlugin


class EnMAPBoxPlugin:

    def __init__(self, iface):
        # make all existing site-packages available
        self.iface = iface
        self.messageBar = self.iface.messageBar()
        assert isinstance(self.messageBar, QgsMessageBar)
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



            msg = 'Failed to load part of EnMAP-Box: {}'.format(str(Plugin))
            tb = traceback.format_exc()
            tag = 'EnMAP-Box'
            logMsg = '{}\n{}'.format(msg, tb)
            if True:
                from qgis import utils as qgsUtils
                import sys
                qgsUtils.showException(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], msg, messagebar=True)
            else:

                msgBarItem = self.iface.messageBar().createMessage(msg)
                assert isinstance(msgBarItem, QgsMessageBarItem)
                #button = QPushButton(msgBarItem)
                #button.setText('Show stack trace')
                #msgBarItem.layout().addWidget(button)
                self.iface.messageBar().pushWidget(msgBarItem, QgsMessageBar.CRITICAL)

                QgsMessageLog.logMessage(logMsg, tag, QgsMessageLog.CRITICAL)
                self.iface.openMessageLog()

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
