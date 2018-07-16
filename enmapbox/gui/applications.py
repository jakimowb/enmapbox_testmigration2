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

import os, sys, site, collections, re, inspect

from qgis.core import *
from qgis.core import Qgis
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.gui.utils import *
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
from enmapbox import messageLog
DEBUG = False #set this on True to not hide external-app errors



class EnMAPBoxApplication(QObject):
    """
        s = ""
    Base class to describe components of an EnMAPBoxApplication
    and to provide interfaces the main EnMAP-Box
    """

    @staticmethod
    def checkRequirements(enmapBoxApp)->(bool,str):

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
        call self.sigFileCreated.emit("filepath.txt") to let the EnMAP-Box know that you created "filepath.txt".
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

        :return:
        """
        return None

    def icon(self):
        """
        Overwrite to return a QIcon
        http://doc.qt.io/qt-5/qicon.html
        :return:
        """
        return None

    def menu(self, appMenu):
        """
        :param appMenu: the EnMAP-Box' Application QMenu
        :return: None (default), the QMenu or QAction that is added to the QMenu "appMenu".
        """
        return None

    def geoAlgorithms(self)->list:
        """
        Returns a list of GeoAlgorithms()

        :return:
        """
        messageLog('Deprecated method "geoAlgorithms". Use "processingAlgorithms" instead.')
        return []

    def processingAlgorithms(self)->list:

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
    Registry to handel EnMAPBox Applications
    """
    def __init__(self, enmapBox, parent=None):
        super(ApplicationRegistry, self).__init__(parent)
        self.appPackageRootFolders = []
        assert isinstance(enmapBox, EnMAPBox)

        self.mEnMAPBox = enmapBox
        self.mProcessingAlgManager = self.mEnMAPBox.processingAlgManager
        self.mAppInfos = collections.OrderedDict()


    def __len__(self):
        return len(self.mAppInfos)

    def __iter__(self):
        return iter(self.mAppInfos.values())

    def applications(self)->list:
        """
        Returns the EnMAPBoxApplications
        :return: [list-of-EnMAPBoxApplications]
        """
        return [w.app for w in self.applicationWrapper()]

    def applicationWrapper(self, nameOrApp=None)->list:
        """
        Returns the EnMAPBoxApplicationWrappers.
        :param nameOrApp: str | EnMAPBoxApplication to return the ApplicationWrapper for
        :return: [list-of-EnMAPBoxApplicationWrappers]
        """
        wrappers = [w for w in self.mAppInfos.values()]
        if nameOrApp is not None:
            wrappers = [w for w in wrappers if isinstance(w, ApplicationWrapper) and nameOrApp in [w.appId, w.app.name, w.app]]
        return wrappers

    def addApplicationPackageFile(self, appPkgFile):
        assert os.path.isfile(appPkgFile)

        f = open(appPkgFile)
        lines = f.readlines()
        f.close()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if len(l) > 0 and not l.startswith('#')]
        from enmapbox.gui.utils import DIR_REPO as ROOT
        lines = [(l if os.path.isabs(l) else os.path.join(ROOT, l)) for l in lines]
        lines = [l for l in lines if os.path.isdir(l)]
        for appPath in lines:
            appDir = os.path.normpath(os.path.dirname(appPath))
            if not appDir in sys.path:
                sys.path.append(appDir)

            self.addApplicationPackageSavely(appPath)

    def addApplicationPackageRootFolder(self, appPkgRootFolder):
        """
        Searches and loads the EnMAP-Box application packages located in appDir
        :param appPkgRootFolder: Directory with EnMAP-Box application packages
        :return: self
        """
        if not os.path.isdir(appPkgRootFolder):
            return False

        if not appPkgRootFolder in sys.path:
            sys.path.append(appPkgRootFolder)

        for d, subs, _ in os.walk(appPkgRootFolder):
            appPackages = [os.path.abspath(os.path.join(d,p)) for p in subs]
            s = ""
            break

        for appPackage in appPackages:
           self.addApplicationPackageSavely(appPackage)
        return self

    def isApplicationPackage(self, appPackagePath)->bool:
        """
        Checks if the directory "appPackage" contains an '__init__.py' which defines the function
        enmapboxApplicationFactory
        :param appPackage: path to directory
        :return: (True, None) if enmapboxApplicationFactory exists in package definition.
                (False, Exception) if enmapboxApplicationFactory does not exists in package definition.
        """

        if not os.path.isdir(appPackagePath):
            return (False, Exception('not a directory: '.find(appPackagePath)))
        appPkgName = os.path.basename(appPackagePath)
        pkgFile = os.path.join(appPackagePath, '__init__.py')
        appFolder = os.path.dirname(appPackagePath)
        if not os.path.isfile(pkgFile):
            return (False, Exception('Could not find '+pkgFile))

        added = False
        if not appFolder in sys.path:

            sys.path.append(appFolder)
            added = True
        #import imp
        #appModule = imp.load_source('.{}.__init__'.format(appPkgName), pkgFile)
        try:
            appModule = __import__(appPkgName)
        except Exception as ex:
            if added:
                sys.path.remove(appFolder)
            return (False, ex)

        factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                   if o[0] == 'enmapboxApplicationFactory']
        if len(factory) != 1:
            if added:
                sys.path.remove(appFolder)
            return (False, Exception('Could not find enmapboxApplicationFactory in {}'.find(appModule)))

        return (True, None)


    def addApplicationPackageSavely(self, appPackagePath):
        """
        Adds an application package with addApplicationPackage but will catch errors.
        :param appPackagePath:
        """
        if DEBUG:
            self.addApplicationPackage(appPackagePath)
        else:
            try:
                isPkg, ex = self.isApplicationPackage(appPackagePath)
                if not isPkg:
                    raise Exception('Invalid EnMAP-Box Application Package: {}\n{}'.format(appPackagePath), str(ex) )
                self.addApplicationPackage(appPackagePath)

            except Exception as ex:
                import traceback
                msg = 'Failed to load {}\n\tError:"{}"'.format(appPackagePath, '{}'.format(ex))
                msg +='\n\tTraceback:\n' + ''.join(traceback.format_stack())
                print(msg)
                #messageLog(msg, level=Qgis.Critical)


    def addApplicationPackage(self, appPackagePath:str):
        """
        Loads an EnMAP-Box application package and adds all its applications
        :param appPackagePath: a path pointing to a directory <application package folder>
        :return:
        """
        assert isinstance(appPackagePath, str)
        if isinstance(appPackagePath, str):
            isPkg, ex = self.isApplicationPackage(appPackagePath)
            assert isPkg, str(ex)

            appPkgName = os.path.basename(appPackagePath)
            appFolder = os.path.dirname(appPackagePath)
            pkgFile = os.path.join(appPackagePath, '__init__.py')

            print('import EnMAPBoxApplication package"{}"'.format(appPkgName))
            if not os.path.exists(pkgFile):
                raise Exception('Missing __init__.py in {}'.format(appPackagePath))

            if not appFolder in sys.path:
                site.addsitedir(appFolder)


            import importlib

            #appModule = imp.load_source('.{}.__init__'.format(appPkgName), pkgFile)
            appModule = __import__(appPkgName)


            factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                       if o[0] == 'enmapboxApplicationFactory']

            if len(factory) == 0:
                raise Exception('Missing enmapboxApplicationFactory() in {}'.format(appPackagePath))
            else:
                factory = factory[0]

            #create the app
            apps = factory(self.mEnMAPBox)
            if apps is None:
                raise Exception(
                    'No EnMAPBoxApplications returned from call to {}.enmapboxApplicationFactory(...)'.format(appPkgName))


            if not isinstance(apps, list):
                apps = [apps]

            for app in apps:
                if not isinstance(app, EnMAPBoxApplication):
                    messageLog('Not an EnMAPBoxApplication instance: {}\n{}'.format(app.__module__, '{}'.format(ex)), level=Qgis.Critical)
                    continue
                try:
                    self.addApplication(app)
                except Exception as ex:
                    import traceback
                    msg = 'Failed to load app "{} {}"'.format(appPackagePath, '{}'.format(ex))
                    msg += '\n Traceback:\n ' + repr(traceback.format_stack())
                    #QgsMessageLog.instance().logMessage(msg, level=QgsMessageLog.CRITICAL)

                    messageLog('Failed to load {}\n{}'.format(app.__module__, '{}'.format(ex)) , level=Qgis.Critical)

    def addApplications(self, apps)->list:
        """
        Adds a list of EnMAP-Box applications with addApplication
        :param apps: [list-of-EnMAPBoxApplications]
        :return:
        """
        return [self.addApplication(app) for app in apps]

    def addApplication(self, app:EnMAPBoxApplication)->bool:
        """
        Adds a single EnMAP-Box application, i.a. a class that implemented the EnMAPBoxApplication Interface
        :param app:
        """
        if DEBUG:
            print('addApplication({})'.format(str(app)))
        assert isinstance(app, EnMAPBoxApplication)

        appWrapper = ApplicationWrapper(app)
        if DEBUG:
            print('Check requirements...')
        isOk, errorMessages = EnMAPBoxApplication.checkRequirements(app)
        if not isOk:
            messageLog('Unable to load EnMAPBoxApplication "{}"\n{}.'.format(appWrapper.appId, '\n\t'.join(errorMessages)))
            return False
        if appWrapper.appId in self.mAppInfos.keys():
            messageLog('EnMAPBoxApplication {} already loaded. Reload'.format(appWrapper.appId))
            self.removeApplication(appWrapper.appId)

        self.mAppInfos[appWrapper.appId] = appWrapper

        #load GUI integration
        if DEBUG:
            print('Load menu items...')

        self.loadMenuItems(appWrapper)

        #load QGIS Processing Framework Integration
        if self.mProcessingAlgManager.isInitialized():
            if DEBUG:
                print('Load GeoAlgorithms...')
            self.loadProcessingAlgorithms(appWrapper)

        if DEBUG:
            print('Loading done.')

        return True

    def loadProcessingAlgorithms(self, appWrapper):
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
            provider = self.mProcessingAlgManager.enmapBoxProvider()
            if isinstance(provider, EnMAPBoxAlgorithmProvider):
                provider.addAlgorithms(processingAlgorithms)
            else:
                if DEBUG:
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
        assert appId in self.mAppInfos.keys()
        self.removeApplication(appId)
        self.addApplication(appId)

    def removeApplication(self, appId):
        """
        Removes the EnMAPBoxApplication
        :param appId: str
        """
        if isinstance(appId, EnMAPBoxApplication):
            appId = ApplicationWrapper(appId).appId

        appWrapper = self.mAppInfos.pop(appId)
        assert isinstance(appWrapper, ApplicationWrapper)

        #remove menu item
        for item in appWrapper.menuItems:

            parent = item.parent()
            if isinstance(parent, QMenu):
                if isinstance(item, QMenu):
                    parent.removeAction(item.menuAction())
                else:
                    s = ""

        #todo: remove geo-algorithms
        PAM = self.mProcessingAlgManager
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsManager
        from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
        assert isinstance(PAM, ProcessingAlgorithmsManager)

        provider = PAM.enmapBoxProvider()
        assert isinstance(provider, EnMAPBoxAlgorithmProvider)
        provider.removeAlgorithms(appWrapper.processingAlgorithms)
        s = ""

