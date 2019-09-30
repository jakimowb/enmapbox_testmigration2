import re, os, pathlib, sys

p = str(pathlib.Path(__file__).parents[1].absolute())
if p not in sys.path:
    sys.path.append(p)

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


if os.environ.get('CI'):
    from enmapbox import DIR_REPO
    remove_shortcutVisibleInContextMenu(DIR_REPO)

