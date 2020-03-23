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
import sys, os, collections, shutil, time, re, importlib, typing, subprocess
import pathlib
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtCore import QUrl
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *


# look-up for pip package name and how it gets imported in python
# e.g. 'pip install scikit-learn' installs a package that is imported via 'import sklearn'
# Keys need to be lowercase, as accepted by PIP
PACKAGE_LOOKUP = {'scikit-learn': 'sklearn',
                  'pyopengl': 'OpenGL'
                  }

# just in case a package cannot /should not simply get installed
# calling pip install --user <pip package name>
INSTALLATION_HINT = {
    'enpt_enmapboxapp' : 'git+https://gitext.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp.git'
}

for k in PACKAGE_LOOKUP.keys():
    assert k == k.lower()

class PIPPackage(object):

    def __init__(self, pyPkg:str, pipCmd:str=None):

        assert isinstance(pyPkg, str)
        assert len(pyPkg) > 0

        if pipCmd is None:
            pipCmd = PACKAGE_LOOKUP.get(pyPkg, pyPkg)

        self.pyPkgName:str = pyPkg
        self.pipCmd:str = pipCmd
        self.localLocation:str = ''
        self.stderrMsg:str = ''
        self.stdoutMsg:str = ''

    def __str__(self):
        return '{}'.format(self.pyPkgName)

    def __eq__(self, other):
        if not isinstance(other, PIPPackage):
            return False
        return self.pyPkgName == other.pyPkgName

    def installPackage(self, *args, **kwds):
        args = self.installArgs(*args, **kwds)

        self.stderrMsg = ''
        self.stdoutMsg = ''
        if False:
            try:
                results = subprocess.check_output(args, stderr=subprocess.STDOUT, shell=True)
                self.stderrMsg = ""
                self.stdoutMsg = results.decode()
            except subprocess.CalledProcessError as ex:
                self.stderrMsg = ex.stdout.decode()
                if len(self.stderrMsg) == 0:
                    self.stderrMsg = 'Failed to install {}.\nPlease close QGIS and try "{}" on your CLI.'.format(self.pyPkgName, self.installCommand())
                self.stdoutMsg = ""

            except Exception as otherEx:
                print(otherEx, file=sys.stderr)
        else:
            from contextlib import redirect_stderr, redirect_stdout
            import io
            se = io.StringIO()
            so = io.StringIO()
            with redirect_stderr(se):
                with redirect_stdout(so):
                    try:
                        sys.argv = ["pip"] + args[1:]
                        import pip._internal.cli.main
                        pip._internal.cli.main.main()
                    except Exception as ex:
                        print(ex, file=sys.stderr)
            self.stderrMsg = se.getvalue()
            self.stdoutMsg = so.getvalue()

    def installArgs(self, user:bool = True) -> typing.List[str]:

        # find local pip executable
        import shutil
        args = []
        if shutil.which('pip3'):
            args.append('pip3')
        elif shutil.which('python3'):
            args.append('python3 -m pip')
        elif shutil.which('pip'):
            args.append('pip')
        elif shutil.which('python'):
            args.append('python -m pip')
        else:
            args.append('pip')

        args.append('install')
        if user:
            args.append('--user')
        args.append(self.pipCmd)
        return args

    def installCommand(self, *args, **kwds)->str:
        return ' '.join(self.installArgs(*args, **kwds))

    def isInstalled(self) -> bool:
        """
        Returns True if the package is installed and can be imported in python
        :return:
        :rtype:
        """
        try:
            __import__(self.pyPkgName)
            return True
        except ModuleNotFoundError:
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


def requiredPackages()->typing.List[PIPPackage]:
    """
    Returns a list of pip packages that should be installable according to the `requirements.txt` file
    :return: [list of strings]
    :rtype: list
    """

    # see https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format
    # for details of requirements format

    file = pathlib.Path(__file__).resolve().parents[1] / 'requirements.txt'
    assert file.is_file(), '{} does not exist'.format(file)
    packages = []
    rxPipPkg = re.compile(r'^[a-zA-Z_-][a-zA-Z0-9_-]*')

    with open(file, 'r') as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]

        # A line that begins with # is treated as a comment and ignored.
        lines = [l for l in lines if not l.startswith('#') and len(l) > 0]

        # Whitespace followed by a # causes the # and the remainder of the line to be treated as a comment.
        lines = [l.split(' #')[0] for l in lines]
        for line in lines:
            match = rxPipPkg.search(line)
            if match:
                pipPkg = match.group()
                pyPkg = PACKAGE_LOOKUP.get(pipPkg, pipPkg)
                cmd = INSTALLATION_HINT.get(pipPkg, line)
                pkg = PIPPackage(pyPkg, cmd)
                packages.append(pkg)

    return packages


def missingPackages()->typing.List[PIPPackage]:
    """
    Returns missing packages
    :return: [PIPPackage]
    :rtype:
    """
    return [p for p in requiredPackages() if not p.isInstalled()]

def missingPackageInfo(missing_packages: typing.List[PIPPackage], html=True)->str:
    """
    Converts a list of missing packages into better readable output.
    :param missing_packages: list of uninstalled packages
    :param html: bool, set True (default) to return HTML output string
    :return: str
    """
    assert isinstance(missing_packages, list)
    for p in missing_packages:
        assert isinstance(p, PIPPackage)
    missing_packages = [p for p in missing_packages if isinstance(p, PIPPackage) and not p.isInstalled()]
    n = len(missing_packages)
    if n == 0:
        return None

    from enmapbox import DIR_REPO, URL_INSTALLATION
    info = ['The following {} package(s) are not installed:'.format(n)]
    info.append('<ol>')
    for i, pkg in enumerate(missing_packages):

        assert isinstance(pkg, PIPPackage)
        info.append('\t<li>{} (install by "{}")</li>'.format(pkg.pyPkgName, pkg.installCommand()))

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



class PIPPackageInstallerTableModel(QAbstractTableModel):

    sigStdOutMessage = pyqtSignal(str)
    sigStdErrMessage = pyqtSignal(str)

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.cnPkg = 'Package'
        self.cnStatus = 'Status'
        self.cnCommand = 'Installation Command'
        self.mColumnNames = [self.cnPkg, self.cnStatus, self.cnCommand]
        self.mColumnToolTips = ['Python package name',
                                'Status of python package installation',
                                'Command to install the package from your command line interface']
        self.mPackages = []

        self.mWarned = False

        self.mUser = True

    def setUser(self, b:bool):
        self.mUser = b == True
        self.dataChanged.emit(self.createIndex(0,0), self.createIndex(self.rowCount()-1, self.columnCount()-1))

    def installAll(self):

        if self.showWarning():
            for pkg in [p for p in self if not p.isInstalled()]:
                self.installPackage(pkg)


    def showWarning(self) -> bool:
        """
        Opens the warning to
        :return:
        :rtype:
        """

        if not self.mWarned:
            info = """
            <b>Please try to install the missing package(s) with your local package manager first!</b>
            <p>Common package managers in QGIS environments are:
            <ul>
                <li><a href="https://trac.osgeo.org/osgeo4w/">OSGeo4W (Windows)<a/></li>
                <li><a href="https://docs.conda.io">minconda/anaconda (all platforms)<a/></li>
                <li><a href="https://linux.die.net/man/8/apt-get">apt-get (Linux)</li>
                <li><a href="https://brew.sh">homebrew (macOS)</a></li>
            </ul>
            </p>
            """
            box = QMessageBox(QMessageBox.Warning,
                             'Package Installation',
                             info,
                             QMessageBox.Abort | QMessageBox.Ignore)
            box.setTextFormat(Qt.RichText)
            box.setDefaultButton(QMessageBox.Abort)
            result = box.exec_()

            if result == QMessageBox.Abort:
                return False
            else:
                self.mWarned = True
                return True
        else:
            return True

    def installPackage(self, pkg:PIPPackage):
        assert isinstance(pkg, PIPPackage)
        assert pkg in self.mPackages

        if self.showWarning():

            if pkg.isInstalled():
                self.sigStdOutMessage.emit('{} is already installed'.format(pkg.pyPkgName))
                return
            self.sigStdOutMessage.emit('Install {}\n"{}"'.format(pkg.pyPkgName, pkg.installCommand()))
            QApplication.processEvents()
            idx = self.pkg2index(pkg)
            pkg.installPackage()
            QApplication.processEvents()
            self.dataChanged.emit(idx, self.index(idx.row(), self.columnCount() - 1))
            if len(pkg.stdoutMsg) > 0:
                self.sigStdOutMessage.emit(pkg.stdoutMsg)

            if len(pkg.stderrMsg) > 0:
                self.sigStdErrMessage.emit(pkg.stderrMsg)

    def __len__(self):
        return len(self.mPackages)

    def __iter__(self) -> typing.Iterator[PIPPackage]:
        return iter(self.mPackages)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.mPackages)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.mColumnNames)

    def pkg2index(self, pkg:PIPPackage) -> QModelIndex:
        assert pkg in self.mPackages
        return self.index(self.mPackages.index(pkg), 0)

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.mColumnNames[col]
            if role == Qt.ToolTipRole:
                return self.mColumnToolTips[col]

        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        pkg = self.mPackages[row]
        return self.createIndex(row, column, pkg)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:

        if not index.isValid():
            return None

        pkg = self.mPackages[index.row()]

        assert isinstance(pkg, PIPPackage)
        cn = self.mColumnNames[index.column()]
        if role == Qt.DisplayRole:
            if cn == self.cnPkg:
                return pkg.pyPkgName
            if cn == self.cnStatus:
                if pkg.isInstalled():
                    return 'Installed'
                else:
                    return 'Not installed'
            if cn == self.cnCommand:
                return pkg.installCommand(user=self.mUser)

        if role == Qt.ForegroundRole:
            if cn == self.cnStatus:
                if pkg.isInstalled():
                    return QColor('green')
                else:
                    return QColor('red')

        if role == Qt.ToolTipRole:
            if cn == self.cnPkg:
                return self.mColumnNames[index.column()]

            if cn == self.cnCommand:
                info = 'Command to install {} from your CLI.'.format(pkg.pyPkgName)
                if 'git+' in pkg.installCommand():
                    info += '\nThis command requires having git (https://www.git-scm.com) installed!'
                return info

        if role == Qt.UserRole:
            return pkg




    def addPackages(self, packages:typing.List[PIPPackage]):

        if len(packages) > 0:
            for p in packages:
                assert isinstance(p, PIPPackage)
            n = self.rowCount()
            self.beginInsertRows(QModelIndex(), n, n + len(packages) - 1)
            self.mPackages.extend(packages)
            self.endInsertRows()

    def removePackages(self):
        pass


class PIPPackageInstallerTableView(QTableView):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """
        Opens the context menu
        """
        index = self.indexAt(event.pos())

        if not index.isValid():
            return

        pkg = index.data(Qt.UserRole)
        txt = index.data(Qt.DisplayRole)
        if not isinstance(pkg, PIPPackage):
            return

        model = self.model().sourceModel()
        assert isinstance(model, PIPPackageInstallerTableModel)

        m = QMenu()
        a = m.addAction('Copy')
        a.triggered.connect(lambda *args, v=txt: QApplication.clipboard().setText(v))

        a = m.addAction('Install')
        a.setEnabled(not pkg.isInstalled())
        a.triggered.connect(lambda *args, pm=model, p=pkg: pm.installPackage(p))

        m.exec_(event.globalPos())


class PIPPackageInstaller(QWidget):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        from enmapbox.gui import loadUi
        from enmapbox import DIR_UIFILES
        path = pathlib.Path(DIR_UIFILES) / 'pippackageinstaller.ui'
        loadUi(path, self)

        self.model = PIPPackageInstallerTableModel()
        self.model.sigStdErrMessage.connect(lambda txt: self.addText(txt, QColor('red')))
        self.model.sigStdOutMessage.connect(self.addText)
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.tableView.setModel(self.proxyModel)

        self.cbUser.toggled.connect(self.model.setUser)
        self.cbMissingOnly.toggled.connect(self.showMissingOnly)
        self.showMissingOnly(self.cbMissingOnly.isChecked())

        assert isinstance(self.tableView, PIPPackageInstallerTableView)
        self.tableView.setSortingEnabled(True)
        self.tableView.sortByColumn(1, Qt.DescendingOrder)
        self.buttonBox.button(QDialogButtonBox.YesToAll).clicked.connect(self.model.installAll)
        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(self.close)


    def showMissingOnly(self, b:bool):
        if b:
            self.proxyModel.setFilterRegExp(QRegExp('Not installed', Qt.CaseInsensitive, QRegExp.Wildcard))
        else:
            self.proxyModel.setFilterRegExp(None)

        self.proxyModel.setFilterKeyColumn(1)

    def addText(self, text:str, color:QColor=None):

        c = self.textBrowser.textColor()
        if isinstance(color, QColor):
            self.textBrowser.setTextColor(color)
        self.textBrowser.append('\n'+text)
        self.textBrowser.setTextColor(c)

    def addPackages(self, packages:typing.List[PIPPackage]):
        self.model.addPackages(packages)

