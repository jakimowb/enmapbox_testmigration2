from PyQt4.QtCore import QObject, pyqtSignal

class Signals(object):

    class QObjectBinder(QObject):
        imageCreated = pyqtSignal(str)
        pickleCreated = pyqtSignal(str)
        htmlCreated = pyqtSignal(str)

    signals = QObjectBinder()
    imageCreated = signals.imageCreated
    pickleCreated = signals.pickleCreated
    htmlCreated = signals.htmlCreated
