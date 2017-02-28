from unittest import TestCase

IMAGE_RECEIVED = None

class TestSignals(TestCase):

    def test_connectDummyHandlerAndEmitSignal(self):

        from Signals import Signals

        def handleImageCreated(filename):
            global IMAGE_RECEIVED
            IMAGE_RECEIVED = True

        signals = Signals()
        signals.imageCreated.connect(handleImageCreated)
        signals.imageCreated.emit('c:\image.img')

        self.assertTrue(IMAGE_RECEIVED)
