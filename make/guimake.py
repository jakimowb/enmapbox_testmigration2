import os, sys, fnmatch, six, subprocess, re

ROOT = os.path.dirname(os.path.dirname(__file__))

from enmapbox import DIR_REPO
from qps.make.make import compileResourceFile, compileQGISResourceFiles
from qps.utils import file_search



def compileResourceFiles():

    dir1 = os.path.join(DIR_REPO, 'enmapbox')
    dir2 = os.path.join(DIR_REPO, 'site-packages')

    qrcFiles = []
    for pathDir in [dir1, dir2]:
        qrcFiles += file_search(pathDir, '*.qrc', recursive=True)

    for file in qrcFiles:
        print('Compile {}...'.format(file))
        compileResourceFile(file)
