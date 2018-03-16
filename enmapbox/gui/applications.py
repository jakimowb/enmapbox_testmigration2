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

import os, sys, site, collections, re

from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.gui.utils import DIR_ENMAPBOX
from enmapbox.gui.enmapboxgui import EnMAPBox

DEBUG = False #set this on True to not hide external-app errors

class ApplicationWrapper(QObject):
    """
    Stores information on an initialized EnMAPBoxApplication
    """
    def __init__(self, app, parent=None):
        super(ApplicationWrapper, self).__init__(parent)
        assert isinstance(app, EnMAPBoxApplication)
        self.app = app
        self.appId = '{}'.format(app.__class__)
        self.menuItems = []
        self.geoAlgorithms = []


class ApplicationRegistry(QObject):
    """
    Registry to handel EnMAPBox Applications
    """
    def __init__(self, enmapBox, parent=None):
        super(ApplicationRegistry, self).__init__(parent)
        self.appPackageRootFolders = []
        assert isinstance(enmapBox, EnMAPBox)

        self.enmapBox = enmapBox
        self.processingAlgManager = self.enmapBox.processingAlgManager
        self.appList = collections.OrderedDict()

    def addApplicationPackageFile(self, appPkgFile):
        assert os.path.isfile(appPkgFile)

        lines = open(appPkgFile).readlines()
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

        for d, appPackages, _ in os.walk(appPkgRootFolder):
            appPackages = [os.path.abspath(os.path.join(d,p)) for p in appPackages]
            break

        for appPackage in appPackages:
           self.addApplicationPackageSavely(appPackage)
        return self

    def isApplicationPackage(self, appPackagePath):
        """
        Checks if the directory "appPackage" contains an '__init__.py' which defines the funtion
        enmapboxApplicationFactory
        :param appPackage: path to directory
        :return: True, if enmapboxApplicationFactory exists in package definition.
        """

        if not os.path.isdir(appPackagePath):
            return False
        appPkgName = os.path.basename(appPackagePath)
        pkgFile = os.path.join(appPackagePath, '__init__.py')
        appFolder = os.path.dirname(appPackagePath)
        if not os.path.isfile(pkgFile):
            return False

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
                return False

        factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                   if o[0] == 'enmapboxApplicationFactory']
        if len(factory) != 1:
            if added:
                sys.path.remove(appFolder)
            return False

        return True

    def addApplicationPackageSavely(self, appPackagePath):
        """
        Adds an application package with addApplicationPackage but will catch errors.
        :param appPackagePath:
        """
        if DEBUG:
            self.addApplicationPackage(appPackagePath)
        else:
            try:
                if not self.isApplicationPackage(appPackagePath):
                    raise Exception('Invalid EnMAP-Box Application Package: {}'.format(appPackagePath))
                self.addApplicationPackage(appPackagePath)

            except Exception as ex:
                import traceback
                msg = 'Failed to load {}\n Error:"{}"'.format(appPackagePath, '{}'.format(ex))
                msg +='\n Traceback\n ' + repr(traceback.format_stack())
                QgsMessageLog.instance().logMessage(msg, level=QgsMessageLog.CRITICAL)


    def addApplicationPackage(self, appPackagePath):
        """
        Loads an EnMAP-Box application package and adds all its applications
        :param appPackagePath: a path pointing to a directory <application package folder>
        :return:
        """

        if isinstance(appPackagePath, EnMAPBoxApplication):

            assert self.isApplicationPackage(appPackagePath)

            appPkgName = os.path.basename(appPackagePath)
            appFolder = os.path.dirname(appPackagePath)
            pkgFile = os.path.join(appPackagePath, '__init__.py')


            if not os.path.exists(pkgFile):
                raise Exception('Missing __init__.py in {}'.format(appPackagePath))

            if not appFolder in sys.path:
                site.addsitedir(appFolder)


            import imp
            #appModule = imp.load_source('.{}.__init__'.format(appPkgName), pkgFile)
            appModule = __import__(appPkgName)


            factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                       if o[0] == 'enmapboxApplicationFactory']

            if len(factory) == 0:
                raise Exception('Missing enmapboxApplicationFactory() in {}'.format(appPackagePath))
            else:
                factory = factory[0]

            #create the app
            apps = factory(self.enmapBox)
            if apps is None:
                raise Exception(
                    'No EnMAPBoxApplications returned from call to {}.enmapboxApplicationFactory(...)'.format(appPkgName))


            if not isinstance(apps, list):
                apps = [apps]

            for app in apps:
                if not isinstance(app, EnMAPBoxApplication):
                    QgsMessageLog.logMessage('Not an EnMAPBoxApplication instance: {}\n{}'.format(
                        app.__module__, '{}'.format(ex))
                        , level=QgsMessageLog.CRITICAL)
                    continue
                try:
                    self.addApplication(app)
                except Exception as ex:
                    import traceback
                    msg = 'Failed to load app "{} {}"'.format(appPackagePath, '{}'.format(ex))
                    msg += '\n Traceback:\n ' + repr(traceback.format_stack())
                    #QgsMessageLog.instance().logMessage(msg, level=QgsMessageLog.CRITICAL)

                    QgsMessageLog.logMessage('Failed to load {}\n{}'.format(
                        app.__module__, '{}'.format(ex))
                            , level=QgsMessageLog.CRITICAL)

    def addApplications(self, apps):
        """
        Adds a list of EnMAP-Box applications with addApplication
        :param apps: [list-of-EnMAPBoxApplications]
        :return:
        """
        return [self.addApplication(app) for app in apps]

    def addApplication(self, app):
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
        EnMAPBoxApplication.checkRequirements(app)

        if appWrapper.appId in self.appList.keys():
            QgsMessageLog.logMessage('EnMAPBoxApplication {} already loaded.'.format(appWrapper.appId))
            return False

        self.appList[appWrapper.appId] = appWrapper

        #load GUI integration
        if DEBUG:
            print('Load menu items...')

        self.loadMenuItems(appWrapper)

        #load QGIS Processing Framework Integration
        if self.processingAlgManager.isInitialized():
            if DEBUG:
                print('Load GeoAlgorithms...')
            self.loadGeoAlgorithms(appWrapper)

        if DEBUG:
            print('Loading done.')

        return True

    def loadGeoAlgorithms(self, appWrapper):
        assert isinstance(appWrapper, ApplicationWrapper)
        geoAlgorithms = appWrapper.app.geoAlgorithms()
        if DEBUG:
            print('appWrapper.app.geoAlgorithms() returned: {}'.format(geoAlgorithms))

        if not isinstance(geoAlgorithms, list):
            geoAlgorithms = [geoAlgorithms]

        from processing.core.GeoAlgorithm import GeoAlgorithm
        geoAlgorithms = [g for g in geoAlgorithms if isinstance(g, GeoAlgorithm)]

        if len(geoAlgorithms) > 0:
            if DEBUG:
                print('GeoAlgorithms found: {}'.format(geoAlgorithms))
            appWrapper.geoAlgorithms.extend(geoAlgorithms)
            provider = self.processingAlgManager.enmapBoxProvider()
            from enmapbox.algorithmprovider import AlgorithmProvider
            if isinstance(provider, AlgorithmProvider):
                self.processingAlgManager.addAlgorithms(provider, geoAlgorithms)
            else:
                if DEBUG:
                    print('Can not find EnMAPBoxAlgorithmProvider')


    def loadMenuItems(self, appWrapper, parentMenuName = 'Applications'):
        assert isinstance(appWrapper, ApplicationWrapper)
        app = appWrapper.app
        assert isinstance(app, EnMAPBoxApplication)
        parentMenu = self.enmapBox.menu(parentMenuName)
        items = app.menu(parentMenu)

        if items is not None:
            if not isinstance(items, list):
                items = [items]
            appWrapper.menuItems.extend(items)



    def reloadApplication(self, appId):
        assert appId in self.appList.keys()
        self.removeApplication(appId)
        self.addApplication(appId)

    def removeApplication(self, appId):
        appWrapper = self.appList[appId]
        assert isinstance(appWrapper, ApplicationWrapper)

        #remove menu item
        for item in appWrapper.menuItems:
            item.parent().removeChildren(item)

        #todo: remove geo-algorithms
        self.processingAlgManager.removeAlgorithms(appWrapper.geoAlgorithms)



class EnMAPBoxApplication(QObject):
    """
        s = ""
    Base class to describe components of an EnMAPBoxApplication
    and to provide interfaces the main EnMAP-Box
    """

    @staticmethod
    def checkRequirements(enmapBoxApp):
        assert enmapBoxApp.name
        assert enmapBoxApp.version
        assert enmapBoxApp.licence

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

    def geoAlgorithms(self):
        """
        Returns a list of GeoAlgorithms()

        :return:
        """
        return None

