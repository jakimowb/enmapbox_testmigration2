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
import sys, os, collections, shutil, time, re, importlib
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtCore import QUrl
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtWidgets import QMessageBox

URL_REQUIREMENTS = r'https://bitbucket.org/hu-geomatics/enmap-box/src/develop/requirements.txt'
LAST_MISSED_PACKAGES = None
LAST_MISSED_INFO = ''

def checkAndShowMissingDependencies(packageNames):
    missing = missingPackages(packageNames)

    if len(missing) == 0:
        return True
    else:
        info = missingPackageInfo(missing)
        showDialog(info)
        return False




def missingPackages(packageNames):
    if not isinstance(packageNames, list):
        packageNames = [packageNames]

    missing = collections.OrderedDict()
    for p in packageNames:
        spec = importlib.util.find_spec(p)
        if spec is None:
            missing[p] = 'Can not import python package ""'.format(p)
    LAST_MISSED_PACKAGES = list(missing.keys())
    return missing

def missingPackageInfo(missingPackages):

    assert isinstance(missingPackages, collections.OrderedDict)
    n = len(missingPackages)
    info = ['Unable to import the following {} package(s):'.format(n)]
    for pkg, ex in missingPackages.items():
        info.append(pkg)

    info.append('You can install from you shell with pip:')
    DIR_REPO = os.path.dirname(os.path.dirname(__file__))
    info.append('$python3 -m pip install -r {}\n'.format(URL_REQUIREMENTS))
    info.append('use option --force-reinstall to update packages to required minimum versions')

    info.append('\nSystem info:')
    info.append('Python executable: {}'.format(sys.executable))
    info.append('Python prefix: {}'.format(sys.exec_prefix))
    info.append('PYTHONPATH:')
    for p in sorted(sys.path):
        info.append('{}'.format(p))
    info.append('\nOS ENVIRONMENT:')
    for k,v in os.environ.items():
        info.append('{}={}'.format(k,v))

    info = '\n'.join(info)

    LAST_MISSED_INFO = info
    return  info

def showDialog(info):
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
            self.textEdit.setText(text)



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



def missingTestdata()->bool:
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


def outdatedTestdata()->bool:
    """Returns whether testdata is outdated."""

    try:
        import warnings
        import enmapboxtestdata
        from enmapbox import MIN_VERSION_TESTDATA

        testDataOutdated = float(enmapboxtestdata.__version__) < float(MIN_VERSION_TESTDATA)
        boxOutdated = float(enmapboxtestdata.__version__) > float(MIN_VERSION_TESTDATA)

        if boxOutdated:
            warnings.warn('Testdata version {} required by EnMAP-Box, but installed version {} is newer. '
                          'Installed EnMAP-Box is outdated and may have problems correctly processing the testdata. '
                          'Consider updating the EnMAP-Box.'
                          ''.format(MIN_VERSION_TESTDATA, enmapboxtestdata.__version__))

        return testDataOutdated

    except Exception as ex:
        print(ex, file=sys.stderr)
        return True


def installTestdata(overwrite_existing=False):
    """
    Downloads and installs the EnMAP-Box Example Data
    """
    if not missingTestdata() and not outdatedTestdata() and not overwrite_existing:
        print('Testdata already installed and up to date.')
        return

    app = QgsApplication.instance()
    if app is None:
        from enmapbox.gui.utils import initQgisApplication
        app = initQgisApplication()
    from enmapbox import URL_TESTDATA
    from pyplugin_installer.unzip import unzip
    from enmapbox import DIR_TESTDATA
    btn = QMessageBox.question(None, 'Testdata is missing or outdated', 'Download testdata from \n{}\n?'.format(URL_TESTDATA))
    if btn != QMessageBox.Yes:
        print('Canceled')
        return

    pathLocalZip = os.path.join(os.path.dirname(DIR_TESTDATA), 'enmapboxtestdata.zip')
    url = QUrl(URL_TESTDATA)
    dialog = QgsFileDownloaderDialog(url, pathLocalZip, 'Download {}'.format(os.path.basename(URL_TESTDATA)))
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

