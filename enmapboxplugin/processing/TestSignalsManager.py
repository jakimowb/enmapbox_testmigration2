from unittest import TestCase

from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
SitePackageAppender.appendAll()

from .SignalsManager import SignalsManager
from enmapbox.processing.types import unpickle
from enmapbox.testdata import HymapBerlinA

class TestSignalsManager(TestCase):

    def test_connectHTMLCreatedToWebBrowserAndEmitRFCReport(self):

        rfc = unpickle(HymapBerlinA.RandomForestClassifier)
        html = rfc.report().saveHTML().filename

        SignalsManager.connectHTMLCreatedToWebBrowser()
        SignalsManager.emitHTMLCreated(html)
