
__name__ = 'enmapbox'

__all__ = ['enmapbox', 'datasources','gui']
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)


DEBUG = True

import six
def dprint(text, file=None):
    if DEBUG:
        six._print('DEBUG::{}'.format(text), file=file)

#DIR = os.path.dirname(__file__)
#import gui
#DIR_GUI = jp(DIR,'gui')
#add_to_sys_path(DIR_GUI)
#add_to_sys_path(jp(DIR, 'libs'))
