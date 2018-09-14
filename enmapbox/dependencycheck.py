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
import sys, os, collections, shutil, time, re
from qgis.PyQt.Qt import QApplication, QUrl
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtWidgets import QMessageBox

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
        try:
            __import__(p)

        except Exception as ex:
            missing[p] = str(ex)
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
    info.append('$python -m pip install -r {}\n'.format(os.path.join(DIR_REPO, 'requirements.txt')))
    info.append('use option --force-reinstall to update packages to required minimum version')

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
        assert os.path.isfile(enmapboxtestdata.hymap)
        assert os.path.isfile(enmapboxtestdata.landcover)
        assert os.path.isfile(enmapboxtestdata.speclib)
        return False
    except Exception as ex:
        print(ex, file=sys.stderr)
        return True

def installTestdata(overwrite_existing=False):
    """
    Downloads and installs the EnMAP-Box Example Data
    """
    if not missingTestdata() and not overwrite_existing:
        print('Testdata already installed.')
        return

    from enmapbox import URL_TESTDATA
    from pyplugin_installer.unzip import unzip
    from enmapbox import DIR_TESTDATA
    btn = QMessageBox.question(None, 'Testdata is missing', 'Download testdata from \n{}\n?'.format(URL_TESTDATA))
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
                outfile = open(fullPath, 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()

        print('Remove {}...'.format(pathLocalZip))
        os.remove(pathLocalZip)
        print('Testdata installed.')

    def onDownloadError(messages):
        raise Exception('\n'.join(messages))

    def onDownLoadExited():
        pass

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

