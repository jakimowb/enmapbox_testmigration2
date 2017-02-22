from __future__ import print_function
import os
from os.path import join, dirname

DIR = dirname(__file__)
DIR_REPO = dirname(DIR)
DIR_SITE_PACKAGES = join(DIR_REPO, 'site-packages')
DIR_SITE_PACKAGES_OS_SPECIFIC = join(DIR_SITE_PACKAGES, os.sys.platform)
DIR_TESTDATA = join(DIR, 'testdata')
DIR_UI = join(DIR, 'gui','ui')
