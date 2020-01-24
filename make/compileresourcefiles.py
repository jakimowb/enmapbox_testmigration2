import os, sys, fnmatch, six, subprocess, re, pathlib, typing
import qgis.testing
app = qgis.testing.start_app()

from PyQt5.QtCore import QResource, QFile
from PyQt5.QtGui import QIcon
ROOT = os.path.dirname(os.path.dirname(__file__))

from enmapbox import DIR_REPO
#from enmapbox.externals.qps.make.make import compileResourceFile, compileQGISResourceFiles
from enmapbox.externals.qps.utils import file_search

def scantree(path, ending='.qrc')->pathlib.Path:
    """Recursively returns file paths in directory"""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            if entry.path.endswith(ending):
                yield pathlib.Path(entry.path)

def compileResourceFiles(dirRCC=None, inputDirs=None):
    """
    Converts Qt *.qrc files into binary *.rcc
    :param dirRCC:
    :type dirRCC:
    :return:
    :rtype:
    """

    if isinstance(dirRCC, str):
        dirRCC = pathlib.Path(dirRCC)
    if dirRCC:
        assert dirRCC.is_dir()

    if inputDirs is None:
        dir1 = os.path.join(DIR_REPO, 'enmapbox')
        dir2 = os.path.join(DIR_REPO, 'site-packages')
        inputDirs = [dir1, dir2]

    qrcFiles = []
    for pathDir in inputDirs:
        #qrcFiles += list(file_search(pathDir, '*.qrc', recursive=True))
        qrcFiles += list(scantree(pathDir))

    for pathQrc in qrcFiles:
        assert isinstance(pathQrc, pathlib.Path)
        print('Compile {}...'.format(pathQrc))
        assert pathQrc

        if dirRCC:
            d = dirRCC
        else:
            d = pathQrc.parent

        pathRcc = d / re.sub(r'\.qrc$', '.rcc', pathQrc.name)
        cmd = 'rcc --binary {} --output {}'.format(pathQrc.as_posix(), pathRcc.as_posix())

        print(cmd)
        os.system(cmd)

        if True:
            MAPPING = dict()
            cmdMapping = 'rcc --list-mapping {}'.format(pathQrc.as_posix())

            with os.popen(cmdMapping) as f:

                for line in f.read().split('\n'):
                    if '\t' in line:
                        key, path = line.split('\t')
                        MAPPING[key] = path
            #compileResourceFile(file)
            canLoadResource = os.path.exists(pathRcc.as_posix()) and QResource.registerResource(pathRcc.as_posix())
            if canLoadResource:
                print('Loaded: {}'.format(pathRcc.as_posix()))
                print('Loaded keys:')
                for key in MAPPING.keys():
                    icon = QIcon(key)
                    assert icon.isNull() == False
                    print(key)




def showIcons(dirIcon):

    scantree(dirIcon, ending='rcc')

if __name__ == "__main__":

    if False:
        dirRCC = None
        if False:
            dirRCC = pathlib.Path(ROOT) /'enmapbox' /'resources'
            os.makedirs(dirRCC, exist_ok=True)
        compileResourceFiles(outDir=dirRCC)


    if True:
        dirQRC = pathlib.Path(r'C:\Users\geo_beja\Repositories\QGIS')
        dirRCC = pathlib.Path(DIR_REPO) / 'qgisresources'
        compileResourceFiles(dirRCC=dirRCC, inputDirs=[dirQRC])