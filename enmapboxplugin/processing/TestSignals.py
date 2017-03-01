from unittest import TestCase
from Signals import Signals

class TestSignals(TestCase):

    def test_emitURL(self):
        Signals.emitHTMLCreated(r'https://google.de')
