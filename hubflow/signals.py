from PyQt4.QtCore import QObject, pyqtSignal

class Signals(object):
    class QObjectBinder(QObject):
        fileCreated = pyqtSignal(str)
    signals = QObjectBinder()
signals = Signals.signals

if __name__ == '__main__':

    def handler(filename):
        print(filename)

    signals.fileCreated.connect(handler)
    signals.fileCreated.emit('my.img')
