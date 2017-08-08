#!/usr/bin/env python
"""
The setup script for the EnMAP-Box GeoAlgorithmsProvider Test-Plugin.

For isolated testing without the EnMAP-Box checkout the repo into the QGISPluginFolder via git:
    cd <your-QGISPluginFolder>
    git clone https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git

For using the latest release install the via pip:
    pip install https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider/get/master.tar.gz

For development link the local repo:
    cd <your-local-repo>
    pip install -e .

"""

from distutils.core import setup
import enmapboxgeoalgorithms

setup(name='enmapboxgeoalgorithms',
    version=enmapboxgeoalgorithms.ENMAPBOXGEOALGORITHMS_VERSION,
    description='EnMAP-Box GeoAlgorithmsProvider',
    author='Andreas Rabe',
    author_email='andreas.rabe@geo.hu-berlin.de',
    packages=['enmapboxgeoalgorithms'],
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider'
    )
