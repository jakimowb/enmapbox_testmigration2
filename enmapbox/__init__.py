
__name__ = 'enmapbox'

__all__ = ['enmapbox', 'datasources','gui']
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import os

jp = os.path.join

DIR = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR)
DIR_SITE_PACKAGES = jp(DIR_REPO, 'site-packages')
DIR_UI = jp(DIR, *['gui','ui'])

DEBUG = False

import six
def dprint(text, file=None):
    if DEBUG:
        six._print('DEBUG::{}'.format(text), file=file)


#DIR = os.path.dirname(__file__)
#import gui
#DIR_GUI = jp(DIR,'gui')
#add_to_sys_path(DIR_GUI)
#add_to_sys_path(jp(DIR, 'libs'))

