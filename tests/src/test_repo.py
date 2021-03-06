import unittest
import warnings

import xmlrunner
import re
import typing
from urlchecker.core.check import UrlChecker, UrlCheckResult
from urlchecker.core.urlproc import UrlCheckResult
import pathlib
from enmapbox.testing import TestCase
from enmapbox.externals.qps.utils import file_search, loadUi

DIR_REPO = pathlib.Path(__file__).parents[1]

DIR_DOCS = DIR_REPO / 'doc'
DIR_CODE = DIR_REPO / 'enmapbox'


class TestRepository(TestCase):

    def test_project_urls(self):
        urls = ['https://www.enmap.org/',
                'https://enmap-box.readthedocs.io',
                'https://bitbucket.org/hu-geomatics/enmap-box']

        checker = UrlCheckResult()
        checker.check_urls(urls)
        failed = "\n".join(checker.failed)
        self.assertTrue(len(checker.failed) == 0,
                        msg=f'Failed to connect to: {failed}\nService down?')

    @unittest.skipIf(TestCase.runsInCI(), 'not that important')
    def test_qgis_api_imports(self):
        from enmapbox import DIR_REPO
        from enmapbox.gui.utils import file_search

        re1 = re.compile(r'^\w*import qgis._')
        re2 = re.compile(r'^\w*from qgis._')

        affected_files: typing.Dict[str, typing.List[int]] = dict()
        for path in file_search(DIR_REPO, '*.py', recursive=True):
            with open(path, encoding='utf-8') as f:
                affected_lines = []
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if re1.search(line) or re2.search(line):
                        affected_lines.append(i + 1)

                if len(affected_lines) > 0:
                    affected_files[path] = affected_lines

        if len(affected_files) > 0:
            msg = ['Shadowed imports of "qgs._" instead "qgis."']
            for path, lines in affected_files.items():
                msg.append(f'{path}: lines: {lines}')
            msg = '\n'.join(msg)
            warnings.warn(msg)
            # self.se(False, msg=msg)

    def test_ui_files(self):

        rx = re.compile(r'.*\.ui$')
        ERRORS: typing.Dict[str, Exception] = dict()
        for uifile in file_search(DIR_REPO, rx, recursive=True):
            try:
                fmt = loadUi(uifile)
            except Exception as ex:
                ERRORS[uifile] = ex
        messages = []
        for path, ex in ERRORS.items():
            ex: Exception
            messages.append(f'\t{path}: {ex}')
        messages = '\n'.join(messages)
        self.assertTrue(len(ERRORS) == 0, msg=f'Unable to loads {len(ERRORS)} *.ui files:\n\t{messages}')


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
