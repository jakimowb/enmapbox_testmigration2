import unittest
import xmlrunner
import typing
from urlchecker.core.check import UrlChecker, UrlCheckResult
from urlchecker.core.urlproc import UrlCheckResult
import pathlib

DIR_REPO = pathlib.Path(__file__).parents[1]

DIR_DOCS = DIR_REPO / 'doc'
DIR_CODE = DIR_REPO / 'enmapbox'


class TestRepository(unittest.TestCase):

    def test_project_urls(self):
        urls = ['https://www.enmap.org/',
                'https://enmap-box.readthedocs.io',
                'https://bitbucket.org/hu-geomatics/enmap-box']

        checker = UrlCheckResult()
        checker.check_urls(urls)
        failed = "\n".join(checker.failed)
        self.assertTrue(len(checker.failed) == 0,
                        msg=f'Failed to connect to: {failed}\nService down?')



if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
