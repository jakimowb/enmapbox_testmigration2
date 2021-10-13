import re
import typing

from enmapbox.externals.qps.utils import loadUi, file_search
from enmapbox.testing import TestCase
from enmapbox import DIR_REPO


class TestUIFiles(TestCase):

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
