# -*- coding: utf-8 -*-

"""
***************************************************************************
    deploy.py
    Script to build the EnMAP-Box from Repository code
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
import os, sys, re, shutil, zipfile, datetime
import numpy as np
import enmapbox
from enmapbox.gui.utils import DIR_REPO, jp, file_search


#DIR_BUILD = jp(DIR_REPO, 'build')
#DIR_DEPLOY = jp(DIR_REPO, 'deploy')

DIR_BUILD = jp(DIR_REPO, 'build')
DIR_DEPLOY = jp(DIR_REPO, 'deploy')
DIR_DEPLOY = r'E:\_EnMAP\temp\temp_bj\enmapbox_deploys'
DIR_MOST_RECENT = jp(DIR_DEPLOY, 'most_recent_version')
#list of deploy options:
# ZIP - add zipped plugin to DIR_DEPLOY
# UNZIPPED - add the non-zipped plugin to DIR_DEPLOY
DEPLOY_OPTIONS = ['ZIP', 'UNZIPPED']
ADD_TESTDATA = True

#directories below the <enmapbox-repository> folder whose content is to be copied without filtering
PLAIN_COPY_SUBDIRS = ['site-packages']

########## End of config section
timestamp = ''.join(np.datetime64(datetime.datetime.now()).astype(str).split(':')[0:-1])
buildID = '{}.{}'.format(enmapbox.__version__, timestamp)
dirBuildPlugin = jp(DIR_BUILD, 'enmapboxplugin')

def rm(p):
    if os.path.isfile(p):
        os.remove(p)
    elif os.path.isdir(p):
        shutil.rmtree(p)

def cleanDir(d):
    assert os.path.isdir(d)
    for root, dirs, files in os.walk(d):
        for p in dirs + files: rm(jp(root,p))
        break

def mkDir(p, delete=False):
    if delete and os.path.isdir(p):
        shutil.rmtree(p)
    if not os.path.isdir(p):
        os.makedirs(p)



def buildPlugin():
    global buildID, dirBuildPlugin, mkDir



    print('BUILD enmapbox {}...'.format(buildID))


    mkDir(DIR_BUILD, delete=True)
    mkDir(dirBuildPlugin, delete=True)
    SUB_DIRS = ['enmapbox', 'enmapboxgeoalgorithms', 'site-packages']
    if ADD_TESTDATA:
        SUB_DIRS.append('enmapboxtestdata')

    # copy files on top level
    srcFileList = []
    srcFileList.extend(file_search(DIR_REPO, re.compile('\.(py|qrc|png|txt|rst|md)$'), recursive=False))
    for subDir in SUB_DIRS:
        subDirSrc = jp(DIR_REPO, subDir)
        subDirDst = jp(dirBuildPlugin, subDir)

        if subDir in PLAIN_COPY_SUBDIRS:
            srcFileList.extend(file_search(subDirSrc, '*', recursive=True))
        else:
            srcFileList.extend(file_search(subDirSrc, re.compile('\.(py|qrc|ui|ico|png|txt|rst|md)$'), recursive=True))

    ##remove hidden files and
    for p in srcFileList: print(p)
    srcFileList = [f for f in srcFileList if not f.startswith('.')]
    for srcFile in srcFileList:
        dstFile = srcFile.replace(DIR_REPO, dirBuildPlugin)
        mkDir(os.path.dirname(dstFile), delete=False)
        shutil.copyfile(srcFile, dstFile)


#time stamp in local time zone (=computers time)


def deployPlugin():
    print('DEPLOY the build')
    if DIR_MOST_RECENT:
        mkDir(DIR_MOST_RECENT, delete=False)

    if 'UNZIPPED' in DEPLOY_OPTIONS:
        dirDeployUnzipped = jp(DIR_DEPLOY, 'enmapbox.{}'.format(buildID))
        mkDir(dirDeployUnzipped, delete=True)
        dirPlugin = jp(dirDeployUnzipped, 'enmapboxplugin')
        print('Copy files to {}...'.format(dirDeployUnzipped))
        shutil.copytree(dirBuildPlugin, dirPlugin)

        if DIR_MOST_RECENT:
            dirMostRecentPlugin = jp(DIR_MOST_RECENT, 'enmapboxplugin')
            mkDir(dirMostRecentPlugin, delete=False)
            cleanDir(dirMostRecentPlugin)
            for root, dirs, files in os.walk(dirPlugin):
                for d in dirs:
                    shutil.copytree(jp(dirPlugin,d), jp(dirMostRecentPlugin,d))
                for f in files:
                    shutil.copyfile(jp(dirPlugin,f), jp(dirMostRecentPlugin,f))
                break
    if 'ZIP' in DEPLOY_OPTIONS:
        pathDeployZip = jp(DIR_DEPLOY, 'enmapbox.{}'.format(buildID))
        print('Create {}...'.format(pathDeployZip))
        shutil.make_archive(pathDeployZip, 'zip', DIR_BUILD)

        if DIR_MOST_RECENT:
            pathSrc = pathDeployZip + '.zip'
            pathDst = jp(DIR_MOST_RECENT, os.path.basename(pathSrc))
            shutil.copyfile(pathSrc, pathDst)


if __name__ == "__main__":

    import pb_tool
    p = r'D:\Repositories\QGIS_Plugins\enmap-box\pb_tool.cfg'
    pb_tool.deploy()

    buildPlugin()
    deployPlugin()
    print('Finished')
