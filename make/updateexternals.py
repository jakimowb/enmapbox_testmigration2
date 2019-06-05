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

import os, sys, re, shutil, zipfile, datetime
from enmapbox import DIR_REPO
from enmapbox.qps.make import updateexternals
from ..externals.qpsmake.updateexternals import RemoteInfo

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
                  remoteBranch='master')


RemoteInfo.create(r'https://bitbucket.org/ecstagriculture/enmap-box-lmu-vegetation-apps.git',
                  prefixLocal=r'enmapbox/apps/lmuvegetationapps',
                  prefixRemote=r'lmuvegetationapps',
                  remoteBranch='master')

RemoteInfo.create(r'https://bitbucket.org/jakimowb/virtual-raster-builder.git',
                  prefixLocal=r'site-packages/vrtbuilder',
                  prefixRemote=r'vrtbuilder',
                  remoteBranch='master')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
                  key='enmapboxapplications',
                  prefixLocal=r'enmapbox/coreapps/enmapboxapplications',
                  prefixRemote=r'enmapboxapplications',
                  excluded=['ressources.py'],
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
                  key='enmapboxgeoalgorithms',
                  prefixLocal='site-packages/enmapboxgeoalgorithms',
                  prefixRemote=r'enmapboxgeoalgorithms',
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-datacube.git',
                  prefixLocal=r'site-packages/hubdc',
                  prefixRemote=r'hubdc',
                  excluded=['gis','testdata'],
                  remoteBranch='develop')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-workflow.git',
                  prefixLocal=r'site-packages/hubflow',
                  prefixRemote=r'hubflow',
                  remoteBranch='develop')


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
    import qps.make.updateexternals
    if isinstance(remoteLocations, str):
        remoteLocations = [remoteLocations]
    qps.make.updateexternals.updateRemoteLocations(remoteLocations)

if __name__ == "__main__":

    # update remotes
    to_update = [#'hub-datacube'
                 #,'hub-workflow'
                 #,'enmapboxapplications'
                 #,'enmapboxgeoalgorithms'
                 #,'enmap-box-lmu-vegetation-apps'
                 #'virtual-raster-builder',
                 #'enmapboxgeoalgorithmsdoc'
                 #'enpt_enmapboxapp'
                 'qps', 'vrtbuilder'
                ]
    updateRemotes(to_update)
    exit(0)