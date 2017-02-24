from unittest import TestCase
from SitePackageAppender import SitePackageAppender

class TestSitePackageAppender(TestCase):

    def test_appendThirdPartyPackages(self):
        SitePackageAppender().appendAll()
        import HTML
        import markup
        import tabulate
        import rios
        import sklearn
        import yaml
