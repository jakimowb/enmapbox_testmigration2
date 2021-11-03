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
import subprocess
import warnings

import qgis
import site
from qgis.gui import QgisInterface, QgsMapLayerConfigWidgetFactory
from qgis.core import Qgis, QgsApplication, QgsProcessingRegistry, QgsProcessingProvider, QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QSettings, QResource
from qgis.PyQt.QtGui import QIcon
from osgeo import gdal
import traceback

# try to find and add the QGIS internal processing folder
try:
    import processing
except ModuleNotFoundError as ex:
    qgis_dir = pathlib.Path(qgis.__file__).parent
    print(f'Try to find processing framework relative to {qgis_dir}')
    potential_paths = []
    pkg = None
    if not isinstance(QgsApplication.instance(), QgsApplication):
        rxPackagePath = re.compile('PKGDATAPATH=(?P<path>[^\r\n]*)')
        info_script = pathlib.Path(__file__).parent / 'qgisinfo.py'
        assert info_script.is_file()
        commands = [
            ['python3', str(info_script)],
            ['python', str(info_script)]
        ]
        new_env = os.environ.copy()
        new_env['QT_QPA_PLATFORM'] = 'offscreen'
        for cmd in commands:
            try:
                result = subprocess.check_output(cmd, env=new_env).decode()
                match = rxPackagePath.search(result)
                pkg = pathlib.Path(match.group('path'))
                if pkg.is_dir():
                    break
            except:
                pass
    else:
        pkg = pathlib.Path(QgsApplication.pkgDataPath())
    if isinstance(pkg, pathlib.Path):
        potential_paths.append(pkg / 'python' / 'plugins')
        potential_paths.append(pkg / 'share' / 'qgis' / 'python' / 'plugins')
        for p in potential_paths:
            if (p / 'processing').is_dir():
                print(f'## Add plugin directory to python path: {p}')
                site.addsitedir(p)
                break

        try:
            import processing

            print(f'## Success {p}')
        except Exception as ex:
            traceback.print_exc()

            print(ex)

__version__ = '3.10'  # subsub-version information is added during build process
__version_exampledata__ = '3.9'  # still use 3.9 data; note that the exampledata folder is part of the repo, but will be removed from the plugin ZIP

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
ISSUE_TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
CREATE_ISSUE = 'https://bitbucket.org/hu-geomatics/enmap-box/issues/new'
DEPENDENCIES = ['numpy', 'scipy', 'osgeo.gdal', 'PyQt5', 'sklearn', 'matplotlib']
DOCUMENTATION = 'https://enmap-box.readthedocs.io/'
URL_TESTDATA = fr'https://bitbucket.org/hu-geomatics/enmap-box/downloads/exampledata.{__version_exampledata__}.zip'
URL_INSTALLATION = r'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html#install-required-python-packages'
URL_QGIS_RESOURCES = r'https://bitbucket.org/jakimowb/qgispluginsupport/downloads/qgisresources.zip'
MIN_VERSION_QGIS = '3.18'

PLUGIN_DEPENDENCIES = ['vrtbuilderplugin>=0.9']
ABOUT = """
<p align="center">
The EnMAP-Box is a QGIS plug-in to visualize and process remote sensing data, and particularly developed to handle EnMAP products. 
It was particularly developed to handle imaging spectroscopy data from the upcoming EnMAP sensor
</p>

<p align="center">Project Website<br/>
<a href="https://enmap-box.readthedocs.io"><span style=" text-decoration: underline; color:#0000ff;">
https://enmap-box.readthedocs.io</span></a></p>

<p align="center">Licenced under the GNU General Public Licence<br/>
<a href="http://www.gnu.org/licenses/"><span style=" text-decoration: underline; color:#0000ff;">
http://www.gnu.org/licenses/</span></a></p>

<p align="center">Environmental Mapping and Analysis Program (EnMAP)<br/>
<a href="http://www.enmap.org"><span style=" text-decoration: underline; color:#0000ff;">
http://www.enmap.org</span></a></p>

<p align="center">
The EnMAP-Box is developed at Humboldt-Universität zu Berlin under contract by the Helmholtz Centre 
Potsdam GFZ and is part of the EnMAP Core Science Team activities. 
It is funded by the German Aerospace Centre (DLR) - Project Management Agency, 
granted by the Federal Ministry of Economic Affairs and Energy (BMWi; grant no. 50EE1529). 
</p>
"""

DIR_ENMAPBOX = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])
DIR_EXAMPLEDATA = (pathlib.Path(DIR_REPO) / 'enmapbox' / 'exampledata').as_posix()

DIR_UNITTESTS = os.path.join(DIR_REPO, 'enmapboxtesting')

ENMAP_BOX_KEY = 'EnMAP-Box'

_ENMAPBOX_PROCESSING_PROVIDER: QgsProcessingProvider = None
_ENMAPBOX_MAPLAYER_CONFIG_WIDGET_FACTORIES: typing.List[QgsMapLayerConfigWidgetFactory] = []

gdal.SetConfigOption('GDAL_VRT_ENABLE_PYTHON', 'YES')


def enmapboxSettings() -> QSettings:
    """
    Returns the QSettings object for EnMAP-Box Settings
    :return: QSettings
    """
    return QSettings('HU-Berlin', ENMAP_BOX_KEY)


settings = enmapboxSettings()
DEBUG = str(os.environ.get('DEBUG', False)).lower() in ['1', 'true']
site.addsitedir(DIR_SITEPACKAGES)

# test if PyQtGraph is available
try:
    import pyqtgraph
except:
    # use PyQtGraph brought by QPS
    pSrc = pathlib.Path(DIR_ENMAPBOX) / 'externals' / 'qps' / 'externals'
    assert pSrc.is_dir()
    site.addsitedir(pSrc)
    # import pyqtgraph


def icon() -> QIcon:
    """
    Returns the EnMAP icon.
    (Requires that the EnMAP resources have been loaded before)
    :return: QIcon
    """
    return QIcon(':/enmapbox/gui/ui/icons/enmapbox.svg')


def debugLog(msg: str):
    if str(os.environ.get('DEBUG', False)).lower() in ['1', 'true']:
        print('DEBUG:' + msg, flush=True)


def messageLog(msg, level=Qgis.Info, notifyUser: bool = True):
    """
    Writes a log message to the QGIS EnMAP-Box Log
    :param msg: log message string
    :param level: Qgis.MessageLevel=[Qgis.Info|Qgis.Warning|Qgis.Critical|Qgis.Success|Qgis.NONE]
    """
    if not isinstance(msg, str):
        msg = str(msg)
    app = QgsApplication.instance()
    if isinstance(app, QgsApplication):
        app.messageLog().logMessage(msg, 'EnMAP-Box',
                                    level=level,
                                    notifyUser=notifyUser)
        from qgis.utils import iface
        if isinstance(iface, QgisInterface) and level == Qgis.Critical:
            iface.openMessageLog()
            title = msg.split('\n')[0]
            iface.messageBar().pushMessage(title, msg, msg, level=level)
    else:
        if level == Qgis.Critical:
            print(msg, file=sys.stderr)
        elif level == Qgis.Warning:
            warnings.warn(msg, stacklevel=2)
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


def initPythonPaths():
    """
    Adds EnMAP-Box internal paths to PYTHONPATH
    Can be used e.g. in unit-tests to ensure that sub-packages are imported right
    """
    ROOT = pathlib.Path(__file__).parent
    site.addsitedir(ROOT / 'site-packages')
    site.addsitedir(ROOT / 'apps')
    site.addsitedir(ROOT / 'coreapps')


def initEnMAPBoxResources():
    """
    Loads (or reloads) all Qt resource files
    """
    debugLog('started initEnMAPBoxResources')
    from .externals.qps.resources import initQtResources, initResourceFile
    initQtResources(DIR_ENMAPBOX)
    debugLog('finished initEnMAPBoxResources')


def registerEditorWidgets():
    """
    Initialises QgsEditorWidgets
    """
    debugLog('started initEditorWidgets')

    from .externals.qps import registerEditorWidgets
    registerEditorWidgets()

    debugLog('finished initEditorWidgets')


def unregisterEditorWidgets():
    """
    just for convenience. So far editor widgets can not be unregistered
    :return:
    :rtype:
    """
    pass


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
                messageLog(str(ex2), Qgis.Warning)
    except Exception as ex:
        traceback.print_exc()
        info = 'Unable to load enmapboxgeoalgorithms.algorithms'
        info += '\n' + str(ex)
        messageLog(info, Qgis.Critical)
    return algs


def registerEnMAPBoxProcessingProvider():
    """
    Initializes the EnMAPBoxProcessingProvider
    """
    debugLog('started initEnMAPBoxProcessingProvider')
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
        info = ['EnMAP-Box: Failed to load enmapboxgeoalgorithms.algorithms.ALGORITHMS.\n{}'.format(str(ex)),
                'PYTHONPATH:']
        for p in sorted(sys.path):
            info.append(p)
        messageLog(info, Qgis.Warning)
        print('\n'.join(info), file=sys.stderr)

    debugLog('started initEnMAPBoxProcessingProvider')


def unregisterEnMAPBoxProcessingProvider():
    """Removes the EnMAPBoxProcessingProvider"""
    from enmapbox.algorithmprovider import EnMAPBoxProcessingProvider, ID
    registry = QgsApplication.instance().processingRegistry()
    provider = registry.providerById(ID)

    if isinstance(provider, EnMAPBoxProcessingProvider):
        global _ENMAPBOX_PROCESSING_PROVIDER
        _ENMAPBOX_PROCESSING_PROVIDER = None
        # this deletes the C++ object
        registry.removeProvider(ID)


def registerMapLayerConfigWidgetFactories():
    """
    Registers widgets to be shown into the QGIS layer properties dialog
    """
    debugLog('started initMapLayerConfigWidgetFactories')
    global _ENMAPBOX_MAPLAYER_CONFIG_WIDGET_FACTORIES
    from .externals.qps import mapLayerConfigWidgetFactories, registerMapLayerConfigWidgetFactory

    from .externals.qps.layerconfigwidgets.rasterbands import RasterBandConfigWidgetFactory
    from .externals.qps.layerconfigwidgets.gdalmetadata import GDALMetadataConfigWidgetFactory
    for factory in [RasterBandConfigWidgetFactory(),
                    GDALMetadataConfigWidgetFactory()]:

        registered = registerMapLayerConfigWidgetFactory(factory)
        if isinstance(registered, QgsMapLayerConfigWidgetFactory):
            _ENMAPBOX_MAPLAYER_CONFIG_WIDGET_FACTORIES.append(registered)

    debugLog('finished initMapLayerConfigWidgetFactories')


def unregisterMapLayerConfigWidgetFactories():
    """
    Removes MapLayerConfigWidgetFactories which had been registered with the EnMAP-Box
    """
    from .externals.qps import unregisterMapLayerConfigWidgetFactory
    for factory in _ENMAPBOX_MAPLAYER_CONFIG_WIDGET_FACTORIES:
        unregisterMapLayerConfigWidgetFactory(factory)


def registerExpressionFunctions():
    """
    Adds Expression functions for the QGIS expression editor
    """
    from .externals.qps.qgsfunctions import registerQgsExpressionFunctions
    registerQgsExpressionFunctions()


def unregisterExpressionFunctions():
    """
    Removes added expression functions
    """
    from .externals.qps.qgsfunctions import unregisterQgsExpressionFunctions
    unregisterQgsExpressionFunctions()


def initAll():
    """
    Calls other init routines required to run the EnMAP-Box properly
    """
    initEnMAPBoxResources()
    registerEditorWidgets()
    registerExpressionFunctions()
    registerEnMAPBoxProcessingProvider()
    registerMapLayerConfigWidgetFactories()

    from .externals.qps import registerSpectralLibraryIOs
    registerSpectralLibraryIOs()

    from .externals.qps import registerSpectralProfileSamplingModes
    registerSpectralProfileSamplingModes()


def unloadAll():
    """
    Reomves all registered factories etc.
    """
    unregisterEditorWidgets()
    unregisterExpressionFunctions()
    unregisterMapLayerConfigWidgetFactories()
    unregisterEnMAPBoxProcessingProvider()


EnMAPBox = None
EnMAPBoxApplication = None


def tr(text: str) -> str:
    """
    to be implemented: string translation
    :param text:
    :return: str
    """
    return text


def run():
    """
    Call to start the EnMAP-Box
    :return:
    """
    import enmapbox.__main__
    enmapbox.__main__.run()


# skip imports when QGIS is not properly setup.
# this is the case e.g. in an Read-the-docs environment, when the source code needs just to be there,
# but not its dependencies
# https://docs.readthedocs.io/en/stable/builds.html
# print(f'QGIS_PREFIX_PATH={QgsApplication.prefixPath()}')
if not os.environ.get('READTHEDOCS', False) in [True, 'True']:
    from enmapbox import initEnMAPBoxResources

    initEnMAPBoxResources()

    from enmapbox.gui.enmapboxgui import EnMAPBox

    EnMAPBox = EnMAPBox

    from enmapbox.gui.applications import EnMAPBoxApplication

    EnMAPBoxApplication = EnMAPBoxApplication
