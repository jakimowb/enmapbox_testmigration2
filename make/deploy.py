# -*- coding: utf-8 -*-

"""
***************************************************************************
    deploy
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from __future__ import absolute_import
import os, sys, re, shutil, zipfile
from enmapbox.gui.utils import *

FLAG_TESTDATA = True

DIR_DEPLOY = jp(DIR_REPO, 'deploy')
DIR_BUILD = jp(DIR_REPO, 'build')


def mkDir(p, delete=False):
    if delete and os.path.isdir(p):
        shutil.rmtree(p)
    if not os.path.isdir(p):
        os.makedirs(p)



PLUGINBUILDDIR = jp(DIR_BUILD, 'enmap-box')


SUB_DIRS = ['enmapbox', 'enmapboxgeoalgorithms', 'site-packages']
if FLAG_TESTDATA:
    SUB_DIRS.append('enmapboxtestdata')

mkDir(DIR_DEPLOY)


mkDir(PLUGINBUILDDIR, delete=True)



for subDir in SUB_DIRS:
    subDirSrc = jp(DIR_REPO, subDir)
    subDirDst = jp(PLUGINBUILDDIR, subDir)

    if subDir in ['site-packages']:
        srcFiles = file_search(subDirSrc, '*', recursive=True)
    else:
        srcFiles = file_search(subDirSrc, re.compile('\.(py|qrc|png|txt|rst|md)$'), recursive=True)

    srcFiles = [f for f in srcFiles if not f.startswith('.')]

    for srcFile in srcFiles:
        dstFile = srcFile.replace(subDirSrc, subDirDst)
        mkDir(os.path.dirname(dstFile))
        shutil.copyfile(srcFile, dstFile)
    s = ""

#zip it
pathZip = jp(DIR_DEPLOY, 'enmapboxplugin')
shutil.make_archive(pathZip, 'zip', PLUGINBUILDDIR)

print('Finished')
