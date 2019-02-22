# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    enmapbox/__init__.py
    Package definition with global settings and initialization routines
    ---------------------
    Date                 : Oct 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This file is part of the EnMAP-Box.                                   *
*                                                                         *
*   The EnMAP-Box is free software; you can redistribute it and/or modify *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   The EnMAP-Box is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with the EnMAP-Box. If not, see <http://www.gnu.org/licenses/>. *
*                                                                         *
***************************************************************************
"""

import sys, os, site, re

import qgis
from qgis.core import Qgis, QgsApplication, QgsProcessingRegistry, QgsProcessingProvider
from qgis.PyQt.QtCore import QSettings


__version__ = '3.3' #subsub-version information is added during build process

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
ISSUE_TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
CREATE_ISSUE = 'https://bitbucket.org/hu-geomatics/enmap-box/issues/new'
DEPENDENCIES = ['numpy','scipy','osgeo', 'PyQt5', 'sklearn','pyqtgraph','matplotlib']
DOCUMENTATION = 'https://enmap-box.readthedocs.io/'
URL_TESTDATA = r'https://bitbucket.org/hu-geomatics/enmap-box-testdata/get/master.zip'
MIN_VERSION_TESTDATA = '0.10'

DIR_ENMAPBOX = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])
DIR_TESTDATA = os.path.join(DIR_REPO, 'enmapboxtestdata')

ENMAP_BOX_KEY = 'EnMAP-Box'


def enmapboxSettings()->QSettings:
    """
    Returns the QSettings object for EnMAP-Box Settings
    :return: QSettings
    """
    return QSettings('HU-Berlin', ENMAP_BOX_KEY)

settings = enmapboxSettings()

DEBUG = settings.value('EMB_DEBUG', False)
LOAD_PROCESSING_FRAMEWORK = settings.value('EMB_LOAD_PF', True)
LOAD_EXTERNAL_APPS = settings.value('EMB_LOAD_EA', True)
LOAD_INTERNAL_APPS = settings.value('EMB_LOAD_IA', True)

site.addsitedir(DIR_SITEPACKAGES)


# make the EnMAP-Box resources available

try:
    from qps import resourcemockup
    if not 'images' in sys.modules.keys():
        sys.modules['images'] = resourcemockup

except:
    pass




def messageLog(msg, level=Qgis.Info):
    """
    Writes a log message to the QGIS EnMAP-Box Log
    :param msg: log message string
    :param level: Qgis.MessageLevel=[Qgis.Info |  Qgis.Warning| Qgis.Critical| Qgis.Success | Qgis.NONE]
    """

    if not isinstance(msg, str):
        msg = str(msg)
    QgsApplication.instance().messageLog().logMessage(msg, 'EnMAP-Box', level)


def initEnMAPBoxResources():
    """
    Loads (or reloads) EnMAP-Box Resources
    """

    try:
        import enmapbox.resources
        enmapbox.resources.qInitResources()
    except Exception as ex:
        print('Unable to import enmapbox.resources', file=sys.stderr)

    try:
        import qps.qpsresources
        qps.qpsresources.qInitResources()
    except Exception as ex:
        print('Unable to import qps.resources', file=sys.stderr)



def initEditorWidgets():
    """
    Initialises QgsEditorWidgets
    """
    import qps
    qps.registerEditorWidgets()


_enmapboxProvider = None
def initEnMAPBoxProcessingProvider():
    """Initializes the EnMAPBoxProcessingProvider"""
    from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider, ID

    registry = QgsApplication.instance().processingRegistry()
    assert isinstance(registry, QgsProcessingRegistry)
    global _enmapboxProvider
    prov = registry.providerById(ID)
    if not isinstance(prov, QgsProcessingProvider):
        _enmapboxProvider = EnMAPBoxAlgorithmProvider()
        assert isinstance(_enmapboxProvider, EnMAPBoxAlgorithmProvider)
        registry.addProvider(_enmapboxProvider)

        assert registry.providerById(ID) == _enmapboxProvider

    try:
        import enmapboxgeoalgorithms.algorithms
        existingAlgNames = [a.name() for a in registry.algorithms() if a.groupId() == _enmapboxProvider.id()]
        missingAlgs = [a for a in enmapboxgeoalgorithms.algorithms.ALGORITHMS if a.name() not in existingAlgNames]
        _enmapboxProvider.addAlgorithms(missingAlgs)


    except Exception as ex:
        info = ['Failed to load QgsProcessingAlgorithms.\n{}'.format(str(ex))]
        info.append('PYTHONPATH:')
        for p in sorted(sys.path):
            info.append(p)
        print('\n'.join(info), file=sys.stderr)


def initAll():
    """
    Calls other init routines required to run the EnMAP-Box properly
    """
    initEnMAPBoxResources()
    initEditorWidgets()
    initEnMAPBoxProcessingProvider()




EnMAPBox = None
EnMAPBoxApplication = None

# skip imports when on RTD, as we can not install the full QGIS environment as required
# https://docs.readthedocs.io/en/stable/builds.html
if not os.environ.get('READTHEDOCS') in ['True', 'TRUE', True]:

    from enmapbox.gui.enmapboxgui import EnMAPBox
    EnMAPBox = EnMAPBox

    from enmapbox.gui.applications import EnMAPBoxApplication
    EnMAPBoxApplication = EnMAPBoxApplication



def run():
    """
    Call to start the EnMAP-Box
    :return:
    """
    import enmapbox.__main__
    enmapbox.__main__.run()

