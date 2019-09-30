import re
from qgis import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from enmapbox.testing import initQgisApplication

from enmapbox.gui.utils import file_search



def remove_shortcutVisibleInContextMenu(rootDir):

    uiFiles = file_search(rootDir, '*.ui', recursive=True)

    regex = re.compile(r'<property name="shortcutVisibleInContextMenu">[^<]*<bool>true</bool>[^<]*</property>', re.MULTILINE)


    for p in uiFiles:
        assert isinstance(p, str)
        assert os.path.isfile(p)

        with open(p, encoding='utf-8') as f:
            xml = f.read()

        if 'shortcutVisibleInContextMenu' in xml:
            print('remove "shortcutVisibleInContextMenu" properties from {}'.format(p))
            xml = regex.sub('', xml)

            with open(p, 'w', encoding='utf-8') as f:
                f.write(xml)


if os.environ['CI']:
    from enmapbox import DIR_REPO
    remove_shortcutVisibleInContextMenu(DIR_REPO)

