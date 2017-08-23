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
        for p in dirs + files: rm(jp(root,p))
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

if __name__ == "__main__":

    import pb_tool

    #the directory to build the "enmapboxplugin" folder
    DIR_DEPLOY = jp(DIR_REPO, 'deploy')
    DIR_DEPLOY = r'E:\_EnMAP\temp\temp_bj\enmapbox_deploys\most_recent_version'

    #local pb_tool configuration file.
    pathCfg = jp(DIR_REPO, 'pb_tool.cfg')
    mkDir(DIR_DEPLOY)

    #required to choose andy DIR_DEPLOY of choice
    pb_tool.get_plugin_directory = lambda : DIR_DEPLOY

    #1. clean an existing directory = the enmapboxplugin folder
    pb_tool.clean_deployment(ask_first=False, config=pathCfg)

    #2. Compile. Basically call pyrcc to create the resources.rc file
    #I don't know how to call this from pure python
    if True:
        import subprocess
        os.chdir(DIR_REPO)
        subprocess.call(['pb_tool', 'compile'])
    else:
        cfgParser = pb_tool.get_config(config=pathCfg)
        pb_tool.compile_files(cfgParser)

    #3. Deploy = write the data to the new enmapboxplugin folder
    pb_tool.deploy_files(pathCfg, confirm=False)

    #4. As long as we can not specify in the pb_tool.cfg which file types are not to deploy,
    # we need to remove them afterwards.
    print('Remove files...')
    for f in file_search(jp(DIR_DEPLOY, 'enmapboxplugin'), re.compile('(svg|pyc)$'), recursive=True):
        os.remove(f)



    print('Finished')
