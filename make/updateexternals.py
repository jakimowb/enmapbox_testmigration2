# -*- coding: utf-8 -*-

"""
***************************************************************************
    updateexternals.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os, sys, re, shutil, zipfile, datetime, pathlib
os.environ['READTHEDOCS'] = 'True'

DIR_ENMAPBOX_REPO = pathlib.Path(__file__).parents[1].as_posix()
if not DIR_ENMAPBOX_REPO in sys.path:
    sys.path.append(DIR_ENMAPBOX_REPO)

from enmapbox import DIR_REPO
from enmapbox.externals.qps.make import updateexternals
from enmapbox.externals.qps.make.updateexternals import RemoteInfo

import git # install with: pip install gitpython

updateexternals.setProjectRepository(DIR_REPO)

#not required any more
#RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-testdata.git',
#                  prefixLocal=r'enmapboxtestdata',
#                  prefixRemote=r'enmapboxtestdata',
#                  remoteBranch='master')

RemoteInfo.create(r'https://bitbucket.org/jakimowb/qgispluginsupport.git',
                  key='qps',
                  prefixLocal='enmapbox/externals/qps',
                  prefixRemote=r'qps',
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/ecstagriculture/enmap-box-lmu-vegetation-apps.git',
                  prefixLocal=r'enmapbox/apps/lmuvegetationapps',
                  prefixRemote=r'lmuvegetationapps',
                  remoteBranch='master')

## enmap-box-geoalgorithmsprovider.git

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
                  key='enmapboxgeoalgorithms',
                  prefixLocal=r'doc/source/usr_section/usr_manual/processing_algorithms',
                  prefixRemote=r'doc/source/processing_algorithms',
                  remoteBranch='develop')


RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
                  key='enmapboxgeoalgorithms',
                  prefixLocal=r'enmapbox/coreapps/enmapboxapplications',
                  prefixRemote=r'enmapboxapplications',
                  excluded=['ressources.py'],
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
                  key='enmapboxgeoalgorithms',
                  prefixLocal=r'site-packages/enmapboxgeoalgorithms',
                  prefixRemote=r'enmapboxgeoalgorithms',
                  remoteBranch='develop')

## hub-datacube.git

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-datacube.git',
                  prefixLocal=r'site-packages/hubdc',
                  prefixRemote=r'hubdc',
                  excluded=['gis','testdata'],
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-datacube.git',
                  prefixLocal=r'doc/source/dev_section/dev_cookbook/hubdc',
                  prefixRemote=r'doc/source',
                  excluded=['conf.py', 'index.rst'],
                  remoteBranch='develop')


## hub-workflow.git

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-workflow.git',
                  prefixLocal=r'site-packages/hubflow',
                  prefixRemote=r'hubflow',
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-workflow.git',
                  prefixLocal=r'doc/source/dev_section/dev_cookbook/hubflow',
                  prefixRemote=r'doc/source',
                  excluded=['conf.py', 'index.rst'],
                  remoteBranch='develop')

## GFZ

RemoteInfo.create(r'https://gitext.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp.git',
                  prefixLocal=r'enmapbox/apps/enpt_enmapboxapp',
                  prefixRemote=r'enpt_enmapboxapp',
                  #remoteBranch='master'
                  remoteBranch='master'
                  )

def updateRemotes(remoteLocations):
    """
    Shortcut to update from terminal
    :param remoteLocations: str or list of str with remote location keys to update.
    """
    import enmapbox.externals.qps.make.updateexternals as updateexternals
    if isinstance(remoteLocations, str):
        remoteLocations = [remoteLocations]
    updateexternals.updateRemoteLocations(remoteLocations)

if __name__ == "__main__":

    import getopt

    try:
        print(sys.argv)
        opts, to_update = getopt.getopt(sys.argv[1:], "")
    except getopt.GetoptError as err:
        print(err)

    if len(to_update) == 0:
        to_update = ['qps',
                     'hub-datacube',
                     'hub-workflow',
                     'enmapboxgeoalgorithms',
                     'enmap-box-lmu-vegetation-apps',
                    ]
    updateRemotes(to_update)
    exit(0)