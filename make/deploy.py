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
*   (at your option) any later version.
                 *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming

import os, sys, re, shutil, zipfile, datetime
import qgis.utils
from qgis.PyQt.QtCore import *
import numpy as np
from pb_tool import pb_tool

import enmapbox
from enmapbox.gui.utils import jp, file_search
from enmapbox import DIR_REPO
import git


CHECK_COMMITS = False

########## End of config section
REPO = git.Repo(DIR_REPO)
currentBranch = REPO.active_branch.name
timestamp = ''.join(np.datetime64(datetime.datetime.now()).astype(str).split(':')[0:-1]).replace('-','')
buildID = '{}.{}.{}'.format(enmapbox.__version__, timestamp, re.sub(r'[\\/]','_', currentBranch))


def rm(p):
    """
    Remove files or directory 'p'
    :param p: path of file or directory to be removed.
    """
    if os.path.isfile(p):
        os.remove(p)
    elif os.path.isdir(p):
        shutil.rmtree(p)


def cleanDir(d):
    """
    Remove content from directory 'd'
    :param d: directory to be cleaned.
    """
    assert os.path.isdir(d)
    for root, dirs, files in os.walk(d):
        for p in dirs + files: rm(jp(root, p))
        break


def mkDir(d, delete=False):
    """
    Make directory.
    :param d: path of directory to be created
    :param delete: set on True to delete the directory contents, in case the directory already existed.
    """
    if delete and os.path.isdir(d):
        cleanDir(d)
    if not os.path.isdir(d):
        os.makedirs(d)


def build():
    # the directory to build the "enmapboxplugin" folder
    DIR_DEPLOY = jp(DIR_REPO, 'deploy')
    # DIR_DEPLOY = r'E:\_EnMAP\temp\temp_bj\enmapbox_deploys\most_recent_version'

    # local pb_tool configuration file.
    pathCfg = jp(DIR_REPO, 'pb_tool.cfg')
    cfg = pb_tool.get_config(pathCfg)
    cdir = os.path.dirname(pathCfg)
    pluginname = cfg.get('plugin', 'name')
    dirPlugin = jp(DIR_DEPLOY, pluginname)
    os.chdir(cdir)

    mkDir(DIR_DEPLOY)

    if os.path.isdir(dirPlugin):
        print('Remove old build folder...')
        shutil.rmtree(dirPlugin, ignore_errors=True)

    if True:  # update metadata
        pathMetadata = jp(DIR_REPO, 'metadata.txt')
        # update version number in metadata
        f = open(pathMetadata)
        lines = f.readlines()
        f.close()
        lines = re.sub('version=.*\n', 'version={}\n'.format(buildID), ''.join(lines))
        f = open(pathMetadata, 'w')
        f.write(lines)
        f.flush()
        f.close()

    # required to choose andy DIR_DEPLOY of choice
    # issue tracker: https://github.com/g-sherman/plugin_build_tool/issues/4

    if True:
        # 1. clean an existing directory = the enmapboxplugin folder
        pb_tool.clean_deployment(ask_first=False)



        if currentBranch not in ["develop", "master"]:
            print('Skipped automatic version update because current branch is not "develop" or "master". ')
        else:
            # 2. set the version to all relevant files
            # r = REPO.git.execute(['git','diff', '--exit-code']).split()
            diffs = [r for r in REPO.index.diff(None) if 'deploy.py' not in str(r)]
            if CHECK_COMMITS and len(diffs) > 0:
                # there are diffs. we need to commit them first.
                # This should not be done automatically, as each commit should contain a proper commit message
                raise Exception('Please commit all changes first.')

        # 2. Compile. Basically call pyrcc to create the resources.rc file
        # I don't know how to call this from pure python
        pb_tool.compile_files(cfg)

        # 3. Deploy = write the data to the new enmapboxplugin folder
        pb_tool.deploy_files(pathCfg, DIR_DEPLOY, quick=True, confirm=False)

        # 4. As long as we can not specify in the pb_tool.cfg which file types are not to deploy,
        # we need to remove them afterwards.
        # issue: https://github.com/g-sherman/plugin_build_tool/issues/5
        print('Remove files...')

        if True:
            # delete help folder
            shutil.rmtree(os.path.join(dirPlugin, *['help']), ignore_errors=True)
        for f in file_search(DIR_DEPLOY, re.compile('(svg|pyc)$'), recursive=True):
            os.remove(f)

    # 5. create a zip
    print('Create zipfile...')
    from enmapbox.gui.utils import zipdir

    pluginname = cfg.get('plugin', 'name')
    pathZip = jp(DIR_DEPLOY, '{}.{}.snapshot.zip'.format(pluginname, buildID))
    dirPlugin = jp(DIR_DEPLOY, pluginname)
    zipdir(dirPlugin, pathZip)
    # os.chdir(dirPlugin)
    # shutil.make_archive(pathZip, 'zip', '..', dirPlugin)

    # 6. install the zip file into the local QGIS instance. You will need to restart QGIS!
    if True:
        print('\n### To update/install the EnMAP-Box, run this command on your QGIS Python shell:\n')
        print('from pyplugin_installer.installer import pluginInstaller')
        print('pluginInstaller.installFromZipFile(r"{}")'.format(pathZip))
        print('#### Close (and restart manually)\n')
        #print('iface.mainWindow().close()\n')
        print('QProcess.startDetached(QgsApplication.arguments()[0], [])')
        print('QgsApplication.quit()\n')


    print('Finished')


if __name__ == "__main__":

    build()

