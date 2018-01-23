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
# noinspection PyPep8Naming

from __future__ import absolute_import
from distutils.version import LooseVersion
import os, sys, re, shutil, zipfile, datetime
import numpy as np
import enmapbox
from enmapbox.gui.utils import DIR_REPO, jp, file_search
import git

CREATE_TAG = True
CHECK_COMMITS = True
########## End of config section
REPO = git.Repo(DIR_REPO)
timestamp = ''.join(np.datetime64(datetime.datetime.now()).astype(str).split(':')[0:-1])
timestamp = timestamp.replace('-', '')
version = timestamp



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


if __name__ == "__main__":

    import pb_tool

    # the directory to build the "enmapboxplugin" folder
    DIR_DEPLOY = jp(DIR_REPO, 'deploy')
    # DIR_DEPLOY = r'E:\_EnMAP\temp\temp_bj\enmapbox_deploys\most_recent_version'

    # local pb_tool configuration file.
    pathCfg = jp(DIR_REPO, 'pb_tool.cfg')

    mkDir(DIR_DEPLOY)

    # required to choose andy DIR_DEPLOY of choice
    # issue tracker: https://github.com/g-sherman/plugin_build_tool/issues/4
    pb_tool.get_plugin_directory = lambda: DIR_DEPLOY
    cfg = pb_tool.get_config(config=pathCfg)

    if True:
        # 1. clean an existing directory = the enmapboxplugin folder
        pb_tool.clean_deployment(ask_first=False, config=pathCfg)

        currentBranch = REPO.active_branch.name

        if currentBranch not in ["develop", "master"]:
            print('Skipped automatic version update because current branch is not "develop" or "master". ')
        else:
            #2. set the version to all relevant files
            #r = REPO.git.execute(['git','diff', '--exit-code']).split()
            diffs = [r for r in REPO.index.diff(None) if 'deploy.py' not in str(r)]
            if CHECK_COMMITS and len(diffs) > 0:
                # there are diffs. we need to commit them first.
                # This should not be done automatically, as each commit should contain a proper commit message
                raise Exception('Please commit all changes first.')

            pathMetadata = jp(DIR_REPO, 'metadata.txt')

            #update version number in metadata
            lines = open(pathMetadata).readlines()
            lines = re.sub('version=.*\n', 'version={}\n'.format(version), ''.join(lines))
            f = open(pathMetadata, 'w')
            f.write(lines)
            f.flush()
            f.close()

            pathPkgInit = jp(DIR_REPO, *['enmapbox', '__init__.py'])
            lines = open(pathPkgInit).readlines()
            lines = re.sub('__version__ = .*\n', "__version__ = '{}'\n".format(version), ''.join(lines))
            f = open(pathPkgInit, 'w')
            f.write(lines)
            f.flush()
            f.close()


        # 2. Compile. Basically call pyrcc to create the resources.rc file
        # I don't know how to call this from pure python
        if True:
            import subprocess
            import guimake
            from enmapbox.gui.utils import DIR_UIFILES

            os.chdir(DIR_REPO)
            subprocess.call(['pb_tool', 'compile'])
            guimake.compile_rc_files(DIR_UIFILES)
            # replace the annoying time stamp by a version number?

            from enmapbox.gui.ui import resources
            pathRC = resources.__file__
            lines = open(pathRC).readlines()
            lines = re.sub('# Created: .*\n', "".format(version), ''.join(lines))
            f = open(pathRC, 'w')
            f.write(lines)
            f.flush()
            f.close()



        else:
            cfgParser = pb_tool.get_config(config=pathCfg)
            pb_tool.compile_files(cfgParser)

        # create a tag
        if CREATE_TAG:
            index = REPO.index
            index.add([pathPkgInit, pathMetadata])
            index.commit('updated metadata for version: "{}"'.format(version))

            REPO.create_tag('v.' + version)

        # 3. Deploy = write the data to the new enmapboxplugin folder
        pb_tool.deploy_files(pathCfg, confirm=False)

        # 4. As long as we can not specify in the pb_tool.cfg which file types are not to deploy,
        # we need to remove them afterwards.
        # issue: https://github.com/g-sherman/plugin_build_tool/issues/5
        print('Remove files...')

        for f in file_search(DIR_DEPLOY, re.compile('(svg|pyc)$'), recursive=True):
            os.remove(f)

    # 5. create a zip
    print('Create zipfile...')
    from enmapbox.gui.utils import zipdir

    pluginname = cfg.get('plugin', 'name')
    pathZip = jp(DIR_DEPLOY, '{}.{}.zip'.format(pluginname, timestamp))
    dirPlugin = jp(DIR_DEPLOY, pluginname)
    zipdir(dirPlugin, pathZip)
    # os.chdir(dirPlugin)
    # shutil.make_archive(pathZip, 'zip', '..', dirPlugin)

    # 6. copy to local QGIS user DIR
    if True:
        import shutil

        from os.path import expanduser

        pathQGIS = os.path.join(expanduser("~"), *['.qgis2', 'python', 'plugins'])

        assert os.path.isdir(pathQGIS)
        pathDst = os.path.join(pathQGIS, os.path.basename(dirPlugin))
        rm(pathDst)
        shutil.copytree(dirPlugin, pathDst)
        s = ""

    print('Finished')
