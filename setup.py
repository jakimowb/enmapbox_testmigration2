#!/usr/bin/env python
"""
The setup script for EnMAP-Box Testdata.

For using the latest release install the via pip:
    pip install https://bitbucket.org/hu-geomatics/enmap-box-testdata/get/master.tar.gz

For development link the local repo:
    cd <your-local-repo>
    pip install -e .

"""

from distutils.core import setup
import enmapboxtestdata

setup(name='enmapboxtestdata',
    version=enmapboxtestdata.__version__,
    description='EnMAP-Box Testdata',
    author='Andreas Rabe',
    author_email='andreas.rabe@geo.hu-berlin.de',
    packages=['enmapboxtestdata'],
    #license='LICENSE.txt',
    url='https://bitbucket.org/hu-geomatics/enmap-box-testdata'
    )
