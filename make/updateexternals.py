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

from __future__ import absolute_import
import os, sys, re, shutil, zipfile, datetime
import numpy as np
import enmapbox
from enmapbox.gui.utils import DIR_REPO, jp, file_search
import git

REMOTEINFO = {
    'pyqtgraph-core':'',
    'hub-datacube':'',
    'hub-workflow':'',
    'enmapboxgeoalgorithms':'enmapboxgeoalgorithms'


}

def update(remoteKey):
    pass

if __name__ == "__main__":
    repo = git.Repo(DIR_REPO)
    print('Remotes:')
    for r in repo.remotes:
        print('\t{}'.format(str(r)))

    remote = repo.remote('hub-datacube')
    s = ""