#!/usr/bin/env python
"""
The setup script for HUB-Datacube (HUBDC).

Setting up a Python environment with conda:

    conda create -n hubdc python=2  gdal dask pandas


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
    packages=['hubdc'],
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/hub-datacube'
    )
