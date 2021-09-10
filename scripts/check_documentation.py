# noinspection PyPep8Naming
import warnings
import argparse
import datetime
import os
import pathlib
import re
import shutil
import sys
import typing
import site
import io
from os.path import join
from warnings import warn

site.addsitedir(pathlib.Path(__file__).parents[1])
import enmapbox
from enmapbox.gui.utils import file_search
from enmapbox import DIR_REPO, __version__

def ensure_lowercase_file_extensions():
    DIR_DOCS = pathlib.Path(DIR_REPO) / 'doc' / 'source'
    rxUpercase = re.compile(r'\.(?P<ext>(PNG|JPEG))$')
    for path in file_search(DIR_DOCS, rxUpercase, recursive=True):
        p, ext = os.path.splitext(path)
        new_path = p + ext.lower()
        print(f'rename: {path}')
        os.rename(path, new_path)
        s = ""




if __name__ == "__main__":
    ensure_lowercase_file_extensions()
    exit(0)