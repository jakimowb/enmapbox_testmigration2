#!/usr/bin/env python
"""
The setup script for HUB-Workflow (HUBFLOW).

For using the latest release install via pip:
    pip install https://bitbucket.org/hu-geomatics/hub-workflow/get/master.tar.gz

For development link the local repo:
    cd <your-local-repo>
    pip install -e .

"""

from distutils.core import setup

import hubflow

setup(name='hubflow',
    version=hubflow.__version__,
    description='HUB-Workflow',
    author='Andreas Rabe',
    author_email='andreas.rabe@geo.hu-berlin.de',
    packages=['hubflow'],
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/hub-workflow'
    )
