#!/usr/bin/env python
"""
The setup script for HUB-Datacubew (HUBDC).

For development it is link the local repo into your python:
    cd <your-local-repo>
    pip install -e .

"""

from distutils.core import setup

import hubdc

setup(name='hubdc',
    version=hubdc.HUBDC_VERSION,
    description='HUB-Datacube',
    author='Andreas Rabe',
    author_email='andreas.rabe@geo.hu-berlin.de',
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/hub-datacube'
    )
