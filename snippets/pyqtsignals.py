from PyQt5.QtCore import *

class Signals(QObject):
    sigImageCreated = pyqtSignal(str)
    sigPickleCreated = pyqtSignal(str)
    sigHtmlCreated = pyqtSignal(str)

Signals = Signals()

def onSignalReceived(result):
    print(('Signal received:',result))

if __name__ == '__main__':
    qApp = QCoreApplication([])
    #add site-packages to sys.path as done by enmapboxplugin.py
    Signals.sigImageCreated.connect(onSignalReceived)

    #test
    Signals.sigImageCreated.emit('path to image')
    Signals.sigPickleCreated.emit('non received signal')
    qApp.exec_()