#!/usr/bin/env python
"""
The setup script for HUB-Workflow (HUBFLOW).
"""

from distutils.core import setup

import hubflow

setup(name='hubflow',
    version=hubflow.HUBFLOW_VERSION,
    description='HUB-Workflow',
    author='Andreas Rabe',
    author_email='andreas.rabe@geo.hu-berlin.de',
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/hub-workflow'
    )
