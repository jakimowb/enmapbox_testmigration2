# -*- coding: utf-8 -*-
"""
***************************************************************************
    dependencychecker

    This module contains functionality to check the calling python environment for required packages and return
    user-friendly warning in case of missing dependencies.

    ---------------------
    Date                 : Januar 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming
import sys, os, collections, shutil, time, re, importlib, typing
import pathlib
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtCore import QUrl
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtWidgets import QMessageBox

PACKAGE_LOOKUP = {'scikit-learn': 'sklearn'}

def checkAndShowMissingDependencies(packageNames)->bool:
    """
    Checks for requirements (python packages, gdal/ogr functionality, ...)

    :param packageNames:
    :type packageNames:
    :return: bool, False in case of any issue, True else.
    :rtype:
    """
    missing = missingPackages(packageNames)
    gdalissues = checkGDALIssues()

    infoText = ''
    if len(missing) > 0:
        infoText += missingPackageInfo(missing)
    if len(gdalissues) > 0:
        infoText += 'GDAL/OGR Problem(s):'
        for i, issue in enumerate(gdalissues):
            infoText += '{}:{}'.format(i+1, issue)
    if infoText == '':
        return True
    else:
        showDialog(infoText)
        return False

def checkGDALIssues()->typing.List[str]:
    """
    Tests for known GDAL issues
    :return: list of errors / known problems
    """
    from osgeo import ogr
    issues = []
    drv = ogr.GetDriverByName('GPKG')

    if not isinstance(drv, ogr.Driver):
        info = 'GDAL/OGR installation does not support the GeoPackage (GPKG) vector driver'
        info += '(https://gdal.org/drivers/vector/gpkg.html).\n'
        issues.append(info)
    return issues


def requiredPackages()->typing.List[str]:
    """
    Returns a list of packages that should be installable according to the `requirements.txt` file
    :return: [list of strings]
    :rtype: list
    """

    file = pathlib.Path(__file__).resolve().parents[1] / 'requirements.txt'
    assert file.is_file(), '{} does not exist'.format(file)
    packages = []
    rx = re.compile(r'^[a-zA-Z_-][a-zA-Z0-9_-]*')
    with open(file, 'r') as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if not l.startswith('#') and len(l) > 0]
        for l in lines:
            match = rx.search(l)
            if match:
                packages.append(match.group())

    return packages

def missingPackages(packageNames: typing.List[str])->typing.List[str]:
    """
    Returns a list of package names that can not be imported
    :param packageNames: list of packages that should be installed
    :type packageNames:
    :return: list of packages that is not installed
    :rtype:
    """
    if not isinstance(packageNames, list):
        packageNames = [packageNames]

    missing = []
    for p in packageNames:
        if importlib.util.find_spec(PACKAGE_LOOKUP.get(p, p)) is None and p not in missing:
            missing.append(p)

    return missing

def missingPackageInfo(missing_packages: typing.List[str], html=True)->str:
    """
    Converts a list of missing packages into better readible output.
    :param missing_packages: list of uninstalled packages
    :param html: bool, set True (default) to return HTML output string
    :return: str
    """
    assert isinstance(missing_packages, list)
    n = len(missing_packages)
    if n == 0:
        return None

    from enmapbox import DIR_REPO, URL_INSTALLATION
    info = ['The following {} package(s) are not installed:'.format(n)]
    info.append('<ol>')
    for i, pkg in enumerate(missing_packages):
        if pkg == 'sklearn':
            pkg = 'scikit-learn'
        info.append('\t<li>{}</li>'.format(pkg))

    pathRequirementsTxt = os.path.join(DIR_REPO, 'requirements.txt')

    info.append('</ol>')
    info.append('<p>Please follow the installation guide <a href="{0}">{0}</a><br/>'.format(URL_INSTALLATION))
    info.append('and install missing packages, e.g. with pip:<br/><br/>')
    info.append('\t<code>$ python3 -m pip install -r {}</code></p><hr>'.format(pathRequirementsTxt))

    info = '\n'.join(info)

    if not html:
        info = re.sub('<br/>', '\n', info)
        info = re.sub('<[^>]*>','', info)
    return  info

def showDialog(info:str):
    """
    Opens a dialog with the text in "info"
    :param info: str, test to show

    :return:
    :rtype:
    """
    from PyQt5.QtCore import QSize
    from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QLabel
    class DependencyInfoWidget(QDialog):

        def __init__(self, parent=None):
            super(DependencyInfoWidget, self).__init__(parent=parent)
            self.setFixedSize(QSize(400, 200))
            self.setModal(True)
            self.setWindowTitle('Missing python packages')
            l = QVBoxLayout()
            self.setLayout(l)
            l.addWidget(QLabel('Missing python packages'))
            self.textEdit = QTextEdit()
            l.addWidget(self.textEdit)

        def setText(self, text):
            self.textEdit.setHtml(text)



    app = QApplication.instance()
    init = not isinstance(app, QApplication)
    if init:
        app = QApplication([])

    w = DependencyInfoWidget()
    w.setText(info)
    w.setModal(True)
    w.exec_()

    if init:
        app.exec_()



def missingTestData()->bool:
    """
    Returns (True, message:str) if testdata can not be loaded,
     (False, None) else
    :return: (bool, str)
    """
    try:
        import enmapboxtestdata
        assert os.path.isfile(enmapboxtestdata.enmap)
        return False
    except Exception as ex:
        print(ex, file=sys.stderr)
        return True


def outdatedTestData()->bool:
    """Returns whether testdata is outdated."""

    try:
        import warnings
        import enmapboxtestdata
        from enmapbox import MIN_VERSION_TESTDATA

        def version_parse(version: str):
            """Return comparable version string"""
            return '.'.join(number.zfill(10) for number in version.split('.'))

        testDataOutdated = version_parse(enmapboxtestdata.__version__) < version_parse(MIN_VERSION_TESTDATA)
        boxOutdated = version_parse(enmapboxtestdata.__version__) > version_parse(MIN_VERSION_TESTDATA)

        if boxOutdated:
            warnings.warn('Testdata version {} required by EnMAP-Box, but installed version {} is newer. '
                          'Installed EnMAP-Box is outdated and may have problems correctly processing the testdata. '
                          'Consider updating the EnMAP-Box.'
                          ''.format(MIN_VERSION_TESTDATA, enmapboxtestdata.__version__))

        return testDataOutdated

    except Exception as ex:
        print(ex, file=sys.stderr)
        return True


def installTestData(overwrite_existing=False, ask=True):
    """
    Downloads and installs the EnMAP-Box Example Data
    """
    if not missingTestData() and not outdatedTestData() and not overwrite_existing:
        print('Testdata already installed and up to date.')
        return

    app = QgsApplication.instance()
    if app is None:
        from enmapbox.testing import initQgisApplication
        app = initQgisApplication()
    from enmapbox import URL_TESTDATA
    from pyplugin_installer.unzip import unzip
    from enmapbox import DIR_TESTDATA
    if ask == True:
        btn = QMessageBox.question(None, 'Testdata is missing or outdated', 'Download testdata from \n{}\n?'.format(URL_TESTDATA))
        if btn != QMessageBox.Yes:
            print('Canceled')
            return

    pathLocalZip = os.path.join(os.path.dirname(DIR_TESTDATA), 'enmapboxtestdata.zip')
    url = QUrl(URL_TESTDATA)
    dialog = QgsFileDownloaderDialog(url, pathLocalZip, 'Download enmapboxtestdata.zip')
    from enmapbox.gui.utils import qgisAppQgisInterface
    qgisMainApp = qgisAppQgisInterface()

    def onCanceled():
        print('Download canceled')
        return

    def onCompleted():
        print('Download completed')
        print('Unzip {}...'.format(pathLocalZip))

        targetDir = DIR_TESTDATA
        os.makedirs(targetDir, exist_ok=True)
        import zipfile
        zf = zipfile.ZipFile(pathLocalZip)


        names = zf.namelist()
        names = [n for n in names if re.search(r'[^/]/enmapboxtestdata/..*', n) and not n.endswith('/')]
        for name in names:
            # create directory if doesn't exist

            pathRel = re.search(r'[^/]+/enmapboxtestdata/(.*)$',name).group(1)
            subDir, baseName = os.path.split(pathRel)
            fullDir = os.path.normpath(os.path.join(targetDir, subDir))
            os.makedirs(fullDir, exist_ok=True)

            if not name.endswith('/'):
                fullPath = os.path.normpath(os.path.join(targetDir, pathRel))
                with open(fullPath, 'wb') as outfile:
                    outfile.write(zf.read(name))
                    outfile.flush()

        zf.close()
        del zf

        print('Testdata installed.')
        spec = importlib.util.spec_from_file_location('enmapboxtestdata', os.path.join(targetDir, '__init__.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules['enmapboxtestdata'] = module


    def onDownloadError(messages):
        raise Exception('\n'.join(messages))

    def deleteFileDownloadedFile():

        pass
        # dirty patch for Issue #167
        #
        #print('Remove {}...'.format(pathLocalZip))
        #os.remove(pathLocalZip)

    def onDownLoadExited():

        from qgis.PyQt.QtCore import QTimer
        QTimer.singleShot(5000, deleteFileDownloadedFile)



    def onDownloadProgress(received, total):
        if not qgisMainApp and total > 0:
            print('\r{:0.2f} %'.format(100.*received/total), end=' ', flush=True)
            time.sleep(0.1)

    dialog.downloadCanceled.connect(onCanceled)
    dialog.downloadCompleted.connect(onCompleted)
    dialog.downloadError.connect(onDownloadError)
    dialog.downloadExited.connect(onDownLoadExited)
    dialog.downloadProgress.connect(onDownloadProgress)

    dialog.open()
    dialog.exec_()

