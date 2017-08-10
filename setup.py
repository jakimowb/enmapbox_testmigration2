#!/usr/bin/env python
"""
The setup script for HUB-Datacube (HUBDC).

For using the latest release install via pip:
    pip install https://bitbucket.org/hu-geomatics/hub-datacube/get/master.tar.gz

For development link the local repo:
    cd <your-local-repo>
    pip install -e .

"""

from distutils.core import setup

import hubdc

setup(name='hubdc',
    version=hubdc.__version__,
    description='HUB-Datacube',
    author='Andreas Rabe',
    author_email='andreas.rabe@geo.hu-berlin.de',
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/hub-datacube'
    )
