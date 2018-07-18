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
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os, sys, re, shutil, zipfile, datetime
import numpy as np
import enmapbox
from enmapbox.gui.utils import DIR_REPO, jp, file_search
import git

REPO = git.Repo(DIR_REPO)

REMOTEINFOS = dict()


class RemoteInfo(object):
    @staticmethod
    def create(*args, **kwds):
        info = RemoteInfo(*args, **kwds)
        if not info.key in REMOTEINFOS.keys():
            REMOTEINFOS[info.key] = []
        REMOTEINFOS[info.key].append(info)

    def __init__(self, uri, key=None, prefixLocal=None, prefixRemote=None, remoteBranch='master', excluded=[],
                 postupdatehook=None):
        """
        Describes how a remote repository is connected to this repository
        :param uri: uri of remote repository. Needs to end with  '.git'
        :param key: name under which the remote repo will be knows.
            Defaults to remote-repo if uri is like ..remote-repo.git
        :param prefixLocal: local location. Defaults to <this-repo>/<key>
        :param prefixRemote: remote location behind <remoteBranch>,
            e.g. "subfolder" to get "<remoteBranch>:subfolder" only.
            Defaults to root of remote repository
        :param remoteBranch: the remote branch. Defaults to "master"
        """
        assert uri.endswith('.git')
        self.uri = uri
        self.key = key if key is not None else os.path.splitext(os.path.basename(self.uri))[0]
        assert prefixLocal is not ''
        assert prefixRemote is not ''
        self.prefixLocal = self.key if prefixLocal is None else prefixLocal
        self.prefixRemote = prefixRemote
        self.remoteBranch = remoteBranch
        self.excluded = excluded
        self.postupdatehook = None

    def remotePath(self):
        if self.prefixRemote is None or len(self.prefixRemote) == 0:
            return self.remoteBranch
        else:
            return self.remoteBranch + ':' + self.prefixRemote


# specify remote branches
RemoteInfo.create(r'https://github.com/pyqtgraph/pyqtgraph.git',
                  prefixLocal=r'site-packages/pyqtgraph')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-testdata.git',
                  prefixLocal=r'enmapboxtestdata',
                  prefixRemote=r'enmapboxtestdata',
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
                  remoteBranch='master')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
                  key='enmapboxgeoalgorithms',
                  prefixLocal='enmapboxgeoalgorithms',
                  prefixRemote=r'enmapboxgeoalgorithms',
                  remoteBranch='master')


#RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git',
#                  prefixLocal=r'doc/source/geoalgorithms',
#                  prefixRemote=r'doc/source',
#                  excluded=['conf.py','index.rst'],
#                  remoteBranch='master')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-datacube.git',
                  prefixLocal=r'site-packages/hubdc',
                  prefixRemote=r'hubdc',
                  excluded=['gis','testdata'],
                  remoteBranch='master')

RemoteInfo.create(r'https://bitbucket.org/hu-geomatics/hub-workflow.git',
                  prefixLocal=r'site-packages/hubflow',
                  prefixRemote=r'hubflow',
                  remoteBranch='master')


def updateRemote(remoteInfo):
    if isinstance(remoteInfo, str):
        remoteInfos = REMOTEINFOS[remoteInfo]

    # see https://stackoverflow.com/questions/23937436/add-subdirectory-of-remote-repo-with-git-subtree
    # see https://blisqu.wordpress.com/2012/09/08/merge-subdirectory-from-another-git-repository/
    for remoteInfo in remoteInfos:
        assert isinstance(remoteInfo, RemoteInfo)
        remote = REPO.remote(remoteInfo.key)
        print('Fetch {}...'.format(remoteInfo.remotePath()))
        remote.fetch(remoteInfo.remotePath())
        files = REPO.git.execute(
            ['git', 'ls-tree', '--name-only', '-r', 'HEAD', remoteInfo.prefixLocal]).split()
        if len(files) > 0:

            p = os.path.join(DIR_REPO, remoteInfo.prefixLocal)
            if os.path.exists(p):
                info = ''.join([i for i in REPO.git.rm(remoteInfo.prefixLocal, r=True, f=True)])
                print(info)


        info = ''.join([i for i in REPO.git.read_tree(prefix=remoteInfo.prefixLocal, u='{key}/{path}'.format(
            key=remoteInfo.key, path=remoteInfo.remotePath()
        ))])
        print(info)

        # remove excluded files
        for e in remoteInfo.excluded:
            info = ''.join([i for i in REPO.git.rm(remoteInfo.prefixLocal + '/' + e, r=True, f=True)])
            print(info)

        print('Update {} done'.format(remoteInfo.key))


def addRemote(remoteInfo):
    assert isinstance(remoteInfo, RemoteInfo)
    """
    :param name: Desired name of the remote
    :param url: URL which corresponds to the remote's name
    :param kwargs: Additional arguments to be passed to the git-remote add command
    :return: New Remote instance
    :raise GitCommandError: in case an origin with that name already exists
    """
    newRemote = REPO.create_remote(remoteInfo.key, remoteInfo.uri)
    newRemote.fetch(remoteInfo.remoteBranch)


if __name__ == "__main__":

    # check existing remotes
    print('Remotes:')
    existingRemoteNames = [r.name for r in REPO.remotes if r.name != 'origin']
    for rn in existingRemoteNames:
        if rn not in REMOTEINFOS.keys():
            print('Not described in RemoteInfos: {}'.format(rn))

    for rn in REMOTEINFOS.keys():
        if rn not in existingRemoteNames:
            print('Need to add {}'.format(rn))
            for info in REMOTEINFOS[rn]:
                addRemote(info)

    # update remotes
    to_update = ['hub-datacube',
                'hub-workflow',
                 # 'enmap-box-testdata',
                'enmapboxapplications',
                'enmapboxgeoalgorithms'
                #'enmap-box-lmu-vegetation-apps',
                 #'virtual-raster-builder',
                 # 'enmapboxgeoalgorithmsdoc'
                ]

    for p in to_update:
        updateRemote(p)

    print('Finished')
