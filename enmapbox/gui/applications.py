import os, sys, site, collections, inspect, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
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
        self.appId = str(app.__class__)
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
        self.PFMgr = self.enmapBox.processingAlgManager
        self.appList = collections.OrderedDict()

    def addApplicationPackageRootFolder(self, appPkgRootFolder):
        """
        Searches and loads the EnMAP-Box application packages located in appDir
        :param appPkgRootFolder: Directory with EnMAP-Box application packages
        :return: self
        """
        if not os.path.isdir(appPkgRootFolder):
            return False


        for d, appPackages, _ in os.walk(appPkgRootFolder):
            appPackages = [os.path.abspath(os.path.join(d,p)) for p in appPackages]
            break


        for appPackage in appPackages:
            if DEBUG:
                self.addApplicationPackage(appPackage)
            else:
                try:
                    self.addApplicationPackage(appPackage)
                except Exception as ex:
                    QgsMessageLog.instance().logMessage('Failed to load {} {}'.format(appPackage, str(ex))
                                                        , level=QgsMessageLog.CRITICAL)
        return self


    def addApplicationPackage(self, appPackagePath):
        """
        Loads an EnMAP-Box application package and adds all its applications
        :param appPackagePath: a path pointing to a directory <application package folde
        :return:
        """
        #todo: catch error, keep system stable

        appPkgName = os.path.basename(appPackagePath)
        appFolder = os.path.dirname(appPackagePath)
        pkgFile = os.path.join(appPackagePath, '__init__.py')

        if not os.path.exists(pkgFile):
            raise Exception('Missing __init__.py in {}'.format(appPackagePath))

        if not appFolder in sys.path:
            site.addsitedir(appFolder)


        import importlib, imp
        appModule = imp.load_source('__init__', pkgFile)
       # appModule = importlib.import_module('__init__', pkgFile)

        factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                   if o[0] == 'enmapboxApplicationFactory']

        if len(factory) == 0:
            raise Exception('Missing enmapboxApplicationFactory() in {}'.format(appPackagePath))

        factory = factory[0]

        #create the app
        apps = factory(self.enmapBox)
        if len(apps) == 0:
            raise Exception('No EnMAPBoxApplications returned from call to {}.enmapboxApplicationFactory(...)'.format(appPkgName))

        for app in apps:
            if DEBUG:
                self.addApplication(app)
            else:
                try:
                    self.addApplication(app)
                except Exception as ex:

                    QgsMessageLog.instance().logMessage('Failed to load {}\n{}'.format(app.__module__, ex.message)
                                                        , level=QgsMessageLog.CRITICAL)

    def addApplication(self, app):
        """
        Adds a single EnMAP-Box application, i.a. a class that implemented the EnMAPBoxApplication Interface
        :param app:
        """

        assert isinstance(app, EnMAPBoxApplication)

        appWrapper = ApplicationWrapper(app)
        EnMAPBoxApplication.checkRequirements(app)

        if appWrapper.appId in self.appList.keys():
            # todo: handle duplicates (signal?)
            s = ""
        self.appList[appWrapper.appId] = appWrapper

        #load GUI integration
        self.loadMenuItems(appWrapper)

        #load QGIS Processing Framework Integration
        if self.PFMgr.isInitialized():
            self.loadGeoAlgorithms(appWrapper)

    def loadGeoAlgorithms(self, appWrapper):
        geoAlgorithms = appWrapper.app.geoAlgorithms()
        if geoAlgorithms is not None:
            if not isinstance(geoAlgorithms, list):
                geoAlgorithms = [geoAlgorithms]
            from processing.core.GeoAlgorithm import GeoAlgorithm
            geoAlgorithms = [g for g in geoAlgorithms if isinstance(g, GeoAlgorithm)]
            appWrapper.geoAlgorithms.extend(geoAlgorithms)
            self.PFMgr.addAlgorithms(self.PFMgr.enmapBoxProvider(), geoAlgorithms)


    def loadMenuItems(self, appWrapper, parentMenuName = 'Applications'):
        assert isinstance(appWrapper, ApplicationWrapper)
        app = appWrapper.app
        assert isinstance(app, EnMAPBoxApplication)
        parentMenu = self.enmapBox.menu(parentMenuName)

        items = app.menu(parentMenu)
        if not isinstance(items, list):
            items = [items]

        for item in items:
            if isinstance(item, QMenu):

                parentMenu = item.parent()
                if item not in parentMenu.children():
                    parentMenu.addMenu(item)
                appWrapper.menuItems.append(item)

            elif isinstance(item, QAction):
                parentMenu = item.parent().parent()
                item.setParent(parentMenu)
                if item not in parentMenu.children():
                    parentMenu.addAction(item)
                appWrapper.menuItems.append(item)




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
        self.PFMgr.removeAlgorithms(appWrapper.geoAlgorithms)



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
        :return: None (default), QMenu or QAction that will be added to the EnMAP-Box menu bar
        """
        return None

    def geoAlgorithms(self):
        """
        Returns a list of GeoAlgorithms()

        :return:
        """
        return None

if __name__ == '__main__':
    #mini test
    pass