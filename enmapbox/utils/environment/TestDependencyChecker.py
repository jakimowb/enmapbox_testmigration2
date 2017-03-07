from unittest import TestCase
from .DependencyChecker import DependencyChecker
from .SitePackageAppender import SitePackageAppender

class TestDependencyChecker(TestCase):

    def test_isImportable(self):
        self.assertTrue(DependencyChecker.isImportable('enmapbox'))

    def test_isNotImportable(self):
        self.assertFalse(DependencyChecker.isImportable('this_is_a_missing_package'))

    def test_requiredDependencies(self):

        SitePackageAppender.appendAll()
        modules = ['matplotlib']#, 'sklearn']
        modules.extend(['html', 'HTML', 'pyqtgraph', 'markup', 'rios', 'tabulate', 'unipath', 'units', 'yaml'])
        DependencyChecker.importAllDependencies(modules)
