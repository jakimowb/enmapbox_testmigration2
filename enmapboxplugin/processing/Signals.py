from PyQt4.QtCore import QObject, pyqtSignal

class Signals(QObject):
    imageCreated = pyqtSignal(str)
    pickleCreated = pyqtSignal(str)
    htmlCreated = pyqtSignal(str)
