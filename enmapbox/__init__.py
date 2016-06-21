
__name__ = 'enmapbox'


import sys, os

def add_to_sys_path(path):
    assert os.path.isdir(path)
    if path not in sys.path:
        sys.path.append(path)

jp = os.path.join

DIR = os.path.dirname(__file__)
import gui
DIR_GUI = jp(DIR,'gui')
add_to_sys_path(DIR_GUI)
add_to_sys_path(jp(DIR, 'libs'))

