from PyQt4.QtCore import QObject, pyqtSignal

class Signals(object):

    class QObjectBinder(QObject):
        imageCreated = pyqtSignal(str)
        pickleCreated = pyqtSignal(str)
        htmlCreated = pyqtSignal(str)
    signals = QObjectBinder()

    @classmethod
    def connectHTMLCreatedToWebBrowser(clf):
        clf.signals.htmlCreated.connect(clf.handleHTMLCreatedInWebBrowser)

    @classmethod
    def disconnectHTMLCreatedToWebBrowser(clf):
        clf.signals.htmlCreated.disconnect(clf.handleHTMLCreatedInWebBrowser)

    @classmethod
    def emitHTMLCreated(clf, filename):
        clf.signals.htmlCreated.emit(filename)

    @staticmethod
    def handleHTMLCreatedInWebBrowser(url):
        import webbrowser
        webbrowser.open_new_tab(str(url))

Signals.connectHTMLCreatedToWebBrowser()
