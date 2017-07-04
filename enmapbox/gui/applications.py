import os, sys, site, collections, inspect, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import DIR_ENMAPBOX
from enmapbox.gui.enmapboxgui import EnMAPBox


class ApplicationWrapper(QObject):
    """
    Stores information on an initialized EnMAPBoxApplication
    """
    def __init__(self, app):
        assert isinstance(app, EnMAPBoxApplication)
        self.app = app
        self.menuItem = []
        self.geoAlgorithms = []


class ApplicationRegistry(QObject):
    """
    Registry to handel EnMAPBox Applications
    """
    def __init__(self, enmapBox, parent=None):
        super(ApplicationRegistry, self).__init__(parent)
        self.applicationFolders = []
        assert isinstance(enmapBox, EnMAPBox)

        self.enmapBox = enmapBox
        self.PFMgr = self.enmapBox.processingAlgManager
        self.appList = collections.OrderedDict()

    def addApplicationFolder(self, appDir):
        """

        :param appDir:
        :return:
        """
        if not os.path.isdir(appDir):
            return False


        for d, appPackages, _ in os.walk(appDir):
            appPackages = [os.path.abspath(os.path.join(d,p)) for p in appPackages]
            break


        for appPackage in appPackages:
            self.addApplication(appPackage)

    def addApplication(self, appPackagePath):
        """

        :param appPackagePath:
        :return:
        """


        #todo: catch error, keep system stable
        import imp
        appPkgName = os.path.basename(appPackagePath)
        appFolder = os.path.dirname(appPackagePath)
        pkgFile = os.path.join(appPackagePath, '__init__.py')

        if not os.path.exists(pkgFile):
            logging.info('Missing __init__.py in {}'.format(appPackagePath))
            return
        if not appFolder in sys.path:
            site.addsitedir(appFolder)

        appModule = None

        try:
            appModule = __import__(appPkgName)
        except:
            sys.path_importer_cache.clear()
            appModule = __import__(appPkgName)

        if appModule is None:
            logging.error('Unable to load module "{}"'.format(appPkgName))
            return False

        factory = [o[1] for o in inspect.getmembers(appModule, inspect.isfunction) \
                   if o[0] == 'enmapboxApplicationFactory']
        if len(factory) == 0:
            logging.info('Missing enmapboxApplicationFactory() in {}'.format(appPackagePath))
            return False
        else:
            factory = factory[0]

        #create the app
        apps = factory(self.enmapBox)
        for app in apps:

            if not isinstance(app, EnMAPBoxApplication):
                logger.error('Not an EnMAPBoxApplication {}'.format(str(app)))
                continue

            appId = str(app.__class__)
            if appId in self.appList.keys():
                #todo: handle duplicates (signal?)
                pass

            #check app
            EnMAPBoxApplication.checkRequirements(app)

            #register this app
            appWrapper = ApplicationWrapper(app)
            self.appList[appId] = appWrapper
            self.loadApplication(appId)



    def loadGeoAlgorithms(self, appWrapper):
        geoAlgorithms = appWrapper.app.geoAlgorithms()
        appWrapper.geoAlgorithms.extend(geoAlgorithms)
        self.PFMgr.addAlgorithms(self.PFMgr.enmapBoxProvider(), geoAlgorithms)


    def loadMenuItems(self, appWrapper, parentMenuName = 'Applications'):
        assert isinstance(appWrapper, ApplicationWrapper)
        app = appWrapper.app
        assert isinstance(app, EnMAPBoxApplication)
        parentMenu = self.enmapBox.menu(parentMenuName)
        item = app.menu(parentMenu)
        if item is None:
            print('no menu items defined')
            pass
        else:
            if isinstance(item, QMenu):
                parentMenu.addMenu(item)

            elif isinstance(item, QAction):
                item.setParent(parentMenu)
                parentMenu.addAction(item)
                appWrapper.menuItem.append(item)


    def loadApplication(self, appId):
        assert appId in self.appList.keys()
        #include into GUI
        appWrapper = self.appList[appId]
        self.loadMenuItems(appWrapper)

        # include into PF
        if self.PFMgr.isInitialized():
            self.loadGeoAlgorithms(appWrapper)

    def reloadApplication(self, appId):
        assert appId in self.appList.keys()
        self.removeApplication(appId)
        self.loadApplication(appId)

    def removeApplication(self, appId):
        appWrapper = self.appList[appId]
        assert isinstance(appWrapper, ApplicationWrapper)

        #remove menu item
        for item in appWrapper.menuItem:
            item.parent().removeChildren(item)

        #todo: remove geo-algorithms
        self.PFMgr.removeAlgorithms(appWrapper.geoAlgorithms)
        self.appList.re


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
        self.licence = None

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