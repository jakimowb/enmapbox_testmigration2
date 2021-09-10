from unittest import TestCase

from enmapboxprocessing.glossary import injectGlossaryLinks


class TestUtils(TestCase):

    def test_LinearSVC_issue(self):
        text = 'Training dataset pickle file used for fitting the classifier. If not specified, an unfitted classifier is created.'
        print(text)
        print()
        lead = injectGlossaryLinks(text)
        print(lead)
        # self.assertEqual(gold, lead)

        # self.assertEqual(white, Utils.parseColor('255, 255, 255'))
