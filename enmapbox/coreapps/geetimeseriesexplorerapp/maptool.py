from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, pyqtSignal
from qgis._gui import QgsMapTool, QgsMapMouseEvent, QgsMapCanvas

debug = not True


class MapTool(QgsMapTool):
    sigClicked = pyqtSignal(QgsMapMouseEvent)

    def __init__(self, canvas: QgsMapCanvas):
        QgsMapTool.__init__(self, canvas)

    def activate(self):
        QgsMapTool.activate(self)
        self.canvas().setCursor(QCursor(Qt.CrossCursor))

    def deactivate(self):
        QgsMapTool.deactivate(self)

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        event.accept()
        if debug:
            print('MapTool.canvasReleaseEvent')

        self.sigClicked.emit(event)
