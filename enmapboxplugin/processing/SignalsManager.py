from .Signals import Signals


class SignalsManager(object):

    @classmethod
    def connectHTMLCreatedToWebBrowser(clf):
        Signals.htmlCreated.connect(clf.handleHTMLCreatedInWebBrowser)

    @classmethod
    def disconnectHTMLCreatedToWebBrowser(clf):
        Signals.htmlCreated.disconnect(clf.handleHTMLCreatedInWebBrowser)

    @classmethod
    def emitHTMLCreated(clf, filename):
        Signals.htmlCreated.emit(filename)

    @staticmethod
    def handleHTMLCreatedInWebBrowser(url):
        import webbrowser
        webbrowser.open_new_tab(str(url))
