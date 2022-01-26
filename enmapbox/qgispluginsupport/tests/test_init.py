# coding=utf-8
"""Resources test.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest
import pathlib
import re
import xmlrunner
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsApplication
from qgis.gui import QgsEditorWidgetFactory


class testClassTesting(unittest.TestCase):

    @unittest.skipIf(True or isinstance(QgsApplication.instance(), QgsApplication), 'QgsApplication already started')
    def test_init(self):

        from qps.testing import start_app
        from qps.utils import scanResources
        import qps
        app = start_app()
        self.assertIsInstance(app, QgsApplication)

        qps.initResources()

        paths = [p for p in scanResources() if p.startswith(':/qps/')]
        self.assertTrue(len(paths) > 0)
        for p in paths:
            icon = QIcon(p)
            self.assertFalse((icon.isNull()))

        import qps
        qps.registerEditorWidgets()

        import qps.speclib.core.spectrallibrary
        self.assertIsInstance(qps.speclib.gui.spectralprofileeditor.SPECTRAL_PROFILE_EDITOR_WIDGET_FACTORY,
                              QgsEditorWidgetFactory)

        import qps.plotstyling.plotstyling
        self.assertIsInstance(qps.plotstyling.plotstyling.PLOTSTYLE_EDITOR_WIDGET_FACTORY,
                              QgsEditorWidgetFactory)

        import qps.classification.classificationscheme
        self.assertIsInstance(qps.classification.classificationscheme.CLASS_SCHEME_EDITOR_WIDGET_FACTORY,
                              QgsEditorWidgetFactory)

    def test_relative_imports(self):

        root = pathlib.Path(__file__).parents[1]

        from qps.utils import file_search

        re1 = re.compile(r'^\w*import qps')
        re2 = re.compile(r'^\w*from qps')
        for path in file_search(root / 'qps', '*.py', recursive=True):
            with open(path, encoding='utf-8') as f:
                lines = f.read()
                self.assertTrue(re1.search(lines) is None, msg='non-relative "import qps" in {}'.format(path))
                self.assertTrue(re2.search(lines) is None, msg='non-relative "from qps" in {}'.format(path))


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
