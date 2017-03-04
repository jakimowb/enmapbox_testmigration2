from unittest import TestCase
from SignalsManager import SignalsManager

class TestSignalsManager(TestCase):

    def test_connectHTMLCreatedToWebBrowser(self):
        SignalsManager.connectHTMLCreatedToWebBrowser()
