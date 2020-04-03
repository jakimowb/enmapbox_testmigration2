# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    applications.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
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

import os, sys, site, collections, re, inspect, traceback, typing, warnings

from qgis.core import *
from qgis.core import Qgis
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.gui.utils import *
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.algorithmprovider import EnMAPBoxProcessingProvider
from enmapbox import messageLog, DIR_REPO as ROOT

DEBUG = False #set this on True to not hide external-app errors



class EnMAPBoxApplication(QObject):
    """
    Base class to describe components of an EnMAPBoxApplication
    and to provide interfaces the main EnMAP-Box
    """
    @staticmethod
    def checkRequirements(enmapBoxApp) -> (bool, str):
        """
        Tests if the EnMAPBoxApplication defines all required information.
        :param enmapBoxApp: EnMAPBoxApplication
        :return: (True|False, [list-of-errors])
        """
        infos = []
        if not isinstance(enmapBoxApp, EnMAPBoxApplication):
            infos.append('Not an EnMAPBoxApplication "{}"'.format(str(enmapBoxApp)))
        else:
            if not isinstance(enmapBoxApp.name, str) or len(enmapBoxApp.name.strip()) == 0:
                infos.append('Application name is undefined')
            if not isinstance(enmapBoxApp.version, str) or len(enmapBoxApp.version.strip()) == 0:
                infos.append('Application version is undefined')
            if not isinstance(enmapBoxApp.licence, str) or len(enmapBoxApp.licence.strip()) == 0:
                infos.append('Application licence is undefined')
        return len(infos) == 0, infos

    """
        This signal will tell the EnMAPBox that the EnMAPBoxApplication has created a file, e.g. a new raster image.
        E.g. call self.sigFileCreated.emit("filepath.txt") to inform the EnMAPBox 
    """
    sigFileCreated = pyqtSignal(str)


    def __init__(self, enmapBox, parent=None):
        super(EnMAPBoxApplication, self).__init__(parent)
        self.enmapbox = enmapBox
        self.qgis = enmapBox.iface

        #required attributes. Must be different to None
        self.name = None
        self.version = None
        self.licence = 'GNU GPL-3'

        #optional attributes, can be None
        self.projectWebsite = None
        self.description = None

    def removeApplication(self):
        """
        Overwrite to remove components of your application when this app is disabled.
        """
        return None

    def icon(self) -> QIcon:
        """
        Overwrite to return a QIcon
        http://doc.qt.io/qt-5/qicon.html
        :return:
        """
        return None

    def menu(self, appMenu):
        """
        :param appMenu: the EnMAP-Box' Application QMenu
        :return: None (default), the QMenu or QAction that is to be added to the QMenu "appMenu".
        """
        return None

    def geoAlgorithms(self) -> list:
        """
        Deprecated. Use processingAlgorithms() to return a list of QgsProcessingAlgorithms
        """
        raise Exception('Use "processingAlgorithms" instead.')


    def processingAlgorithms(self) -> list:

        return []


class ApplicationWrapper(QObject):
    """
    Stores information about an initialized EnMAPBoxApplication
    """
    def __init__(self, app:EnMAPBoxApplication, parent=None):
        super(ApplicationWrapper, self).__init__(parent)
        assert isinstance(app, EnMAPBoxApplication)
        self.app = app
        self.appId = '{}.{}'.format(app.__class__,app.name)
        self.menuItems = []
        self.processingAlgorithms = []

class ApplicationRegistry(QObject):
    """
    Registry to load and remove EnMAPBox Applications
    """
    def __init__(self, enmapBox, parent=None):
        super(ApplicationRegistry, self).__init__(parent)
        self.appPackageRootFolders = []
        assert isinstance(enmapBox, EnMAPBox)

        self.mEnMAPBox = enmapBox
        self.mAppWrapper = collections.OrderedDict()

        self.mAppInitializationMessages = collections.OrderedDict()

    def __len__(self):
        return len(self.mAppWrapper)

    def __iter__(self):
        return iter(self.mAppWrapper.values())

    def applications(self) -> list:
        """
        Returns the EnMAPBoxApplications
        :return: [list-of-EnMAPBoxApplications]
        """
        return [w.app for w in self.applicationWrapper()]

    def applicationWrapper(self, nameOrApp=None) -> list:
        """
        Returns the EnMAPBoxApplicationWrappers.
        :param nameOrApp: str | EnMAPBoxApplication to return the ApplicationWrapper for
        :return: [list-of-EnMAPBoxApplicationWrappers]
        """
        wrappers = [w for w in self.mAppWrapper.values()]
        if nameOrApp is not None:
            wrappers = [w for w in wrappers if isinstance(w, ApplicationWrapper) and nameOrApp in [w.appId, w.app.name, w.app]]
        return wrappers

    def addApplicationListing(self, appPkgFile:str):
        """
        Loads EnMAPBoxApplications from locations defined in a text file
        :param appPkgFile: str, filepath to file with locations of EnMAPBoxApplications
        """
        if isinstance(appPkgFile, pathlib.Path):
            appPkgFile = str(appPkgFile)
        assert isinstance(appPkgFile, str)
        assert os.path.isfile(appPkgFile)
        pkgFileDir = os.path.dirname(appPkgFile)
        f = open(appPkgFile)
        lines = f.readlines()
        f.close()

        lines = [l.strip() for l in lines]
        lines = [l for l in lines if len(l) > 0 and not l.startswith('#')]

        appFolders = []
        for line in lines:
            assert isinstance(line, str)
            if os.path.isabs(line):
                appFolders.append(line)
            else:
                path = os.path.join(pkgFileDir, line)
                path = os.path.normpath(path)
                appFolders.append(path)
        appFolders = [p for p in appFolders if os.path.isdir(p)]
        for appPath in appFolders:
            self.addApplicationFolder(appPath)


    def isApplicationFolder(self, appPackagePath:str) -> bool:
        """
        Checks if the directory "appPackage" contains an '__init__.py' with an enmapboxApplicationFactory
        :param appPackage: path to directory
        :return: True | False
        """

        if not os.path.isdir(appPackagePath):
            return False

        pkgFile = os.path.join(appPackagePath, '__init__.py')
        if not os.path.isfile(pkgFile):
            return False

        fileStats = os.stat(pkgFile)
        if fileStats.st_size > 1 *1024**2: #assumes that files larger 1 MByte are not source code any more
            return False

        f = open(pkgFile)
        text = f.read()
        f.close()

        return re.search(r'def\s+enmapboxApplicationFactory\(.+\)\s*(->[^:]+)?:', text) is not None


    def findApplicationFolders(self, rootDir):
        """
        Searches for folders that contain an EnMAPBoxApplications
        :param rootDir: str, root path directory
        :return: [list-of-str]
        """
        results = []
        if os.path.isdir(rootDir):
            for file in file_search(rootDir, '__init__.py', recursive=True):
                p = os.path.dirname(file)
                if self.isApplicationFolder(p):
                    results.append(p)
        return results


    def addApplicationFolder(self, appPackagePath:str, isRootFolder=False) -> bool:
        """
        Loads an EnMAP-Box application from its root folder.
        :param appPackagePath: directory with an __init__.py which defines a .enmapboxApplicationFactory() or
                               directory without any __init__.py which contains EnMAPBoxApplication folders
        :return: bool, True if any EnMAPBoxApplication was added
        """
        if isinstance(appPackagePath, pathlib.Path):
            appPackagePath = str(appPackagePath)

        if isRootFolder:
            assert (isinstance(appPackagePath, str) and os.path.isdir(appPackagePath))
            subDirs = []
            for n in os.listdir(appPackagePath):
                p = os.path.join(appPackagePath, n)
                if self.isApplicationFolder(p):
                    subDirs.append(p)
            results = [self.addApplicationFolder(p, isRootFolder=False) for p in subDirs]
            return any(results)
        else:
            basename = os.path.basename(appPackagePath)
            try:
                if not (isinstance(appPackagePath, str) and os.path.isdir(appPackagePath)):
                    raise Exception('Not a directory: "{}"'.format(appPackagePath))

                appPkgName = os.path.basename(appPackagePath)
                appPkgRoot = os.path.dirname(appPackagePath)
                pkgFile = os.path.join(appPackagePath, '__init__.py')

                blacklist = os.environ.get('EMB_APP_BLACKLIST', '').split(',')
                if appPkgName in blacklist:
                    raise Exception('Skipped loading EnMAPBoxApplication "{}"'.format(appPkgName))

                print('Load EnMAPBoxApplication(s) from "{}"'.format(appPkgName))

                if not os.path.isfile(pkgFile):
                    raise Exception('File does not exist: "{}"'.format(pkgFile))

                if not appPkgRoot in sys.path:
                    site.addsitedir(appPkgRoot)

                # do not use __import__
                # appModule = __import__(appPkgName)
                appModule = importlib.import_module(appPkgName)

                factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                            if o[0] == 'enmapboxApplicationFactory']

                if len(factory) == 0:
                    raise Exception('Missing definition of enmapboxApplicationFactory() in {}'.format(pkgFile))

                factory = factory[0]

                # create the app
                apps = factory(self.mEnMAPBox)
                if not isinstance(apps, list):
                    apps = [apps]

                foundValidApps = False

                for app in apps:
                    if not isinstance(app, EnMAPBoxApplication):
                        raise Exception('Not an EnMAPBoxApplication instance: {}'.format(app.__module__))
                    else:
                        result = self.addApplication(app)
                        foundValidApps = True

                if foundValidApps:
                    # return True if app  factory returned a valid EnMAPBoxApplication
                    self.mAppInitializationMessages[basename] = True
                else:
                    # return False if app factory did not return any EnMAPBoxApplication
                    self.mAppInitializationMessages[basename] = False
                return foundValidApps

            except Exception as ex:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tbLines = traceback.format_tb(exc_traceback)
                tbLines = ''.join(tbLines)
                info = '{}:{}\nTraceback:\n{}'.format(ex.__class__.__name__, ex, tbLines)
                # return Error with Traceback
                self.mAppInitializationMessages[basename] = info
                print(info, file=sys.stderr)
                return False

    def addApplications(self, apps) -> list:
        """
        Adds a list of EnMAP-Box applications with addApplication
        :param apps: [list-of-EnMAPBoxApplications]
        :return:
        """
        return [self.addApplication(app) for app in apps]

    def addApplication(self, app:EnMAPBoxApplication) -> bool:
        """
        Adds a single EnMAP-Box application, i.a. a class that implemented the EnMAPBoxApplication Interface
        :param app: EnMAPBoxApplication
        """
        if DEBUG:
            print('addApplication({})'.format(str(app)))
        assert isinstance(app, EnMAPBoxApplication)

        appWrapper = ApplicationWrapper(app)
        if DEBUG:
            print('Check requirements...')
        isOk, errorMessages = EnMAPBoxApplication.checkRequirements(app)
        if not isOk:
            raise Exception('Unable to load EnMAPBoxApplication "{}"\n{}.'.format(appWrapper.appId, '\n\t'.join(errorMessages)))

        if appWrapper.appId in self.mAppWrapper.keys():
            messageLog('EnMAPBoxApplication {} already loaded. Reload'.format(appWrapper.appId))
            self.removeApplication(appWrapper.appId)

        self.mAppWrapper[appWrapper.appId] = appWrapper

        #load GUI integration
        if DEBUG:
            print('Load menu items...')

        self.loadMenuItems(appWrapper)

        # load QGIS Processing Framework Integration
        import enmapbox.algorithmprovider
        if isinstance(enmapbox.algorithmprovider.instance(), enmapbox.algorithmprovider.EnMAPBoxProcessingProvider):
            self.loadProcessingAlgorithms(appWrapper)

        if DEBUG:
            print('Loading done.')

        return True

    def loadProcessingAlgorithms(self, appWrapper:ApplicationWrapper):

        assert isinstance(appWrapper, ApplicationWrapper)
        processingAlgorithms = appWrapper.app.processingAlgorithms()
        if DEBUG:
            print('appWrapper.app.geoAlgorithms() returned: {}'.format(processingAlgorithms))

        if not isinstance(processingAlgorithms, list):
            processingAlgorithms = [processingAlgorithms]

        processingAlgorithms = [g for g in processingAlgorithms if isinstance(g, QgsProcessingAlgorithm)]

        if len(processingAlgorithms) > 0:
            processingAlgorithms = [alg.createInstance() for alg in processingAlgorithms]
            if DEBUG:
                print('QgsProcessingAlgorithms found: {}'.format(processingAlgorithms))
            appWrapper.processingAlgorithms.extend(processingAlgorithms)
            import enmapbox.algorithmprovider
            provider = enmapbox.algorithmprovider.instance()

            if isinstance(provider, EnMAPBoxProcessingProvider):
                provider.addAlgorithms(processingAlgorithms)
            else:
                print('Can not find EnMAPBoxAlgorithmProvider')


    def loadMenuItems(self, appWrapper:ApplicationWrapper, parentMenuName = 'Applications'):
        """
        Adds an EnMAPBoxApplication QMenu to its parent QMenu
        :param appWrapper:
        :param parentMenuName:
        :return:
        """
        assert isinstance(appWrapper, ApplicationWrapper)
        app = appWrapper.app
        assert isinstance(app, EnMAPBoxApplication)
        parentMenu = self.mEnMAPBox.menu(parentMenuName)
        items = app.menu(parentMenu)

        if items is not None:
            if not isinstance(items, list):
                items = [items]
            appWrapper.menuItems.extend(items)



    def reloadApplication(self, appId:str):
        """
        Reloads an EnMAP-Box Application
        :param appId: str
        """
        assert appId in self.mAppWrapper.keys()
        self.removeApplication(appId)
        self.addApplication(appId)

    def removeApplication(self, appId):
        """
        Removes the EnMAPBoxApplication
        :param appId: str
        """
        if isinstance(appId, EnMAPBoxApplication):
            appId = ApplicationWrapper(appId).appId

        appWrapper = self.mAppWrapper.pop(appId)
        assert isinstance(appWrapper, ApplicationWrapper)

        #remove menu item
        for item in appWrapper.menuItems:

            parent = item.parent()
            if isinstance(parent, QMenu):
                if isinstance(item, QMenu):
                    parent.removeAction(item.menuAction())
                else:
                    s = ""

        import enmapbox.algorithmprovider
        provider = enmapbox.algorithmprovider.instance()
        assert isinstance(provider, EnMAPBoxProcessingProvider)
        provider.removeAlgorithms(appWrapper.processingAlgorithms)


