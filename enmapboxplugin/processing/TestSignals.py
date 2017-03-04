from unittest import TestCase
from .Signals import Signals

class TestSignals(TestCase):

    def test_connectDummyHandlerAndEmit(self):

        def dummy_handler(url):
            raise NotImplementedError

        Signals.htmlCreated.connect(dummy_handler)
        Signals.htmlCreated.emit('my.html')
        self.assertRaises(NotImplementedError)
