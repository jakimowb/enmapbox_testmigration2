# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    enmapbox/__init__.py
    EnMAP-Box package definition
    -----------------------------------------------------------------------
    begin                : Jan 2016
    copyright            : (C) 2016 by Benjamin Jakimow
    email                : benjamin.jakimow@geo.hu-berlin.de

***************************************************************************
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
                                                                                                                                                 *
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this software. If not, see <http://www.gnu.org/licenses/>.
***************************************************************************
"""

import sys
import os
import site
import re
import pathlib
import traceback
import typing
import qgis
from qgis.gui import QgisInterface
from qgis.core import Qgis, QgsApplication, QgsProcessingRegistry, QgsProcessingProvider, QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QSettings, QResource
from qgis.PyQt.QtGui import QIcon


__version__ = '3.6' #subsub-version information is added during build process

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
ISSUE_TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
CREATE_ISSUE = 'https://bitbucket.org/hu-geomatics/enmap-box/issues/new'
DEPENDENCIES = ['numpy', 'scipy', 'osgeo.gdal', 'PyQt5', 'sklearn', 'matplotlib']
DOCUMENTATION = 'https://enmap-box.readthedocs.io/'
URL_TESTDATA = r'https://bitbucket.org/hu-geomatics/enmap-box-testdata/get/master.zip'
URL_INSTALLATION = r'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html#install-required-python-packages'

MIN_VERSION_TESTDATA = '0.11'

DIR_ENMAPBOX = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])
DIR_TESTDATA = os.path.join(DIR_REPO, 'enmapboxtestdata')

DIR_UNITTESTS = os.path.join(DIR_REPO, 'enmapboxtesting')

ENMAP_BOX_KEY = 'EnMAP-Box'

_ENMAPBOX_PROCESSING_PROVIDER : QgsProcessingProvider = None


def enmapboxSettings() -> QSettings:
    """
    Returns the QSettings object for EnMAP-Box Settings
    :return: QSettings
    """
    return QSettings('HU-Berlin', ENMAP_BOX_KEY)

settings = enmapboxSettings()
DEBUG = settings.value('EMB_DEBUG', False)
site.addsitedir(DIR_SITEPACKAGES)

# test PyQtGraph
try:
    import pyqtgraph
except:
    pSrc = pathlib.Path(DIR_ENMAPBOX) / 'externals' / 'qps' / 'externals'
    assert pSrc.is_dir()
    site.addsitedir(pSrc)
    import pyqtgraph

def icon() -> QIcon:
    """
    Returns the EnMAP icon.
    (Requires that the EnMAP resources have been loaded before)
    :return: QIcon
    """
    return QIcon(':/enmapbox/gui/ui/icons/enmapbox.svg')


def messageLog(msg, level=Qgis.Info):
    """
    Writes a log message to the QGIS EnMAP-Box Log
    :param msg: log message string
    :param level: Qgis.MessageLevel=[Qgis.Info|Qgis.Warning|Qgis.Critical|Qgis.Success|Qgis.NONE]
    """
    if not isinstance(msg, str):
        msg = str(msg)
    app = QgsApplication.instance()
    if isinstance(app, QgsApplication):
        app.messageLog().logMessage(msg, 'EnMAP-Box', level)
    else:
        if level == Qgis.Critical:
            print(msg, file=sys.stderr)
        else:
            print(msg)


def scantree(path, ending: str = '') -> pathlib.Path:
    """Recursively returns file paths in directory"""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path, ending=ending)
        else:
            if entry.path.endswith(ending):
                yield pathlib.Path(entry.path)


def initEnMAPBoxResources():
    """
    Loads (or reloads) all Qt resource files
    """
    if DEBUG:
        print('started initEnMAPBoxResources', flush=True)
    from .externals.qps.resources import initQtResources, initResourceFile
    initQtResources(DIR_ENMAPBOX)
    if DEBUG:
        print('finished initEnMAPBoxResources', flush=True)


def initEditorWidgets():
    """
    Initialises QgsEditorWidgets
    """
    if DEBUG:
        print('started initEditorWidgets', flush=True)

    from .externals.qps import registerEditorWidgets
    registerEditorWidgets()

    if DEBUG:
        print('finished initEditorWidgets', flush=True)
        
def collectEnMAPBoxAlgorithms() -> typing.List[QgsProcessingAlgorithm]:
    """
    Safely collects all QgsProcessingalgorithms from enmapboxgeoalgorithms.algorithms
    Missing dependencies or import errors will not stop the EnMAP-Box from being loaded
    :return: [QgsProcessingAlgorithms]
    :rtype: list
    """
    algs = []
    try:
        import enmapboxgeoalgorithms.algorithms
        for a in enmapboxgeoalgorithms.algorithms.ALGORITHMS:
            try:
                algs.append(a.create())
            except Exception as ex2:
                traceback.print_stack()
                print(ex2)
    except Exception as ex:
        traceback.print_stack()
        info = 'Unable to load enmapboxgeoalgorithms.algorithms'
        info += '\n'+str(ex)
        print(info, file=sys.stderr)

    return algs

def initEnMAPBoxProcessingProvider():
    """
    Initializes the EnMAPBoxProcessingProvider
    """
    if DEBUG:
        print('started initEnMAPBoxProcessingProvider', flush=True)
    from enmapbox.algorithmprovider import EnMAPBoxProcessingProvider, ID

    registry = QgsApplication.instance().processingRegistry()
    assert isinstance(registry, QgsProcessingRegistry)
    provider = registry.providerById(ID)
    if not isinstance(provider, QgsProcessingProvider):
        provider = EnMAPBoxProcessingProvider()
        registry.addProvider(provider)

    assert isinstance(provider, EnMAPBoxProcessingProvider)
    assert id(registry.providerById(ID)) == id(provider)
    global _ENMAPBOX_PROCESSING_PROVIDER
    _ENMAPBOX_PROCESSING_PROVIDER = provider

    try:
        existingAlgNames = [a.name() for a in registry.algorithms() if a.groupId() == provider.id()]
        missingAlgs = [a for a in collectEnMAPBoxAlgorithms() if a.name() not in existingAlgNames]
        provider.addAlgorithms(missingAlgs)
    except Exception as ex:
        traceback.print_exc()
        info = ['EnMAP-Box: Failed to load enmapboxgeoalgorithms.algorithms.ALGORITHMS.\n{}'.format(str(ex))]
        info.append('PYTHONPATH:')
        for p in sorted(sys.path):
            info.append(p)
        messageLog(info, Qgis.Warning)
        print('\n'.join(info), file=sys.stderr)
    
    if DEBUG:
        print('started initEnMAPBoxProcessingProvider', flush=True)


def removeEnMAPBoxProcessingProvider():
    """Removes the EnMAPBoxProcessingProvider"""
    from enmapbox.algorithmprovider import EnMAPBoxProcessingProvider, ID
    registry = QgsApplication.instance().processingRegistry()
    provider = registry.providerById(ID)

    if isinstance(provider, EnMAPBoxProcessingProvider):
        global _ENMAPBOX_PROCESSING_PROVIDER
        _ENMAPBOX_PROCESSING_PROVIDER = None
        # this deletes the C++ object
        registry.removeProvider(ID)


def initMapLayerConfigWidgetFactories():
    if DEBUG:
        print('started initMapLayerConfigWidgetFactories', flush=True)

    from .externals.qps import registerMapLayerConfigWidgetFactories, mapLayerConfigWidgetFactories
    registerMapLayerConfigWidgetFactories()
    for factory in mapLayerConfigWidgetFactories():
        qgis.utils.iface.registerMapLayerConfigWidgetFactory(factory)

    if DEBUG:
        print('finished initMapLayerConfigWidgetFactories', flush=True)


def initAll():
    """
    Calls other init routines required to run the EnMAP-Box properly
    """
    initEnMAPBoxResources()
    initEditorWidgets()
    initEnMAPBoxProcessingProvider()
    initMapLayerConfigWidgetFactories()



EnMAPBox = None
EnMAPBoxApplication = None

# skip imports when on RTD, as we can not install the full QGIS environment as required
# https://docs.readthedocs.io/en/stable/builds.html
if not os.environ.get('READTHEDOCS') in ['True', 'TRUE', True]:

    from enmapbox.gui.enmapboxgui import EnMAPBox
    EnMAPBox = EnMAPBox

    from enmapbox.gui.applications import EnMAPBoxApplication
    EnMAPBoxApplication = EnMAPBoxApplication


def tr(text: str) -> str:
    """
    to be implemented: string translation
    :param text:
    :return: str
    """
    return text

class Qgis(object):
    """Collection of some static methodes to programmatically interact with QGIS inside the QGIS console."""

    @classmethod
    def activeRaster(cls):
        try:
            from hubdc.core import openRasterDataset
            return openRasterDataset(qgis.utils.iface.activeLayer().source())
        except:
            return None

    @classmethod
    def activeVector(cls):
        try:
            from hubdc.core import openVectorDataset
            return openVectorDataset(qgis.utils.iface.activeLayer().source())
        except:
            return None

    @classmethod
    def activeDataset(cls):
        dataset = cls.activeRaster()
        if dataset is None:
            dataset = cls.activeVector()
        return dataset

    @classmethod
    def activeBand(cls, index):
        dataset = cls.activeRaster()
        if dataset is not None:
            try:
                return dataset.band(index=index)
            except:
                return None
        else:
            return None

    @classmethod
    def activeData(cls, index=None):

        from hubdc.core import RasterDataset, VectorDataset

        dataset = cls.activeDataset()
        if isinstance(dataset, RasterDataset):
            if index is None:
                return cls.activeRaster().readAsArray()
            else:
                return cls.activeBand(index=index).readAsArray()
        elif isinstance(dataset, VectorDataset):
            return dataset.attributeTable()
        elif dataset is None:
            return None
        else:
            raise TypeError()

def run():
    """
    Call to start the EnMAP-Box
    :return:
    """
    import enmapbox.__main__
    enmapbox.__main__.run()

