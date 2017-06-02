import os, sys, site, collections
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import DIR_ENMAPBOX
from enmapbox.gui.enmapboxgui import EnMAPBox

class ApplicationWrapper(QObject):
    """
    Stores some information on EnMAPBoxApplications
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
            appPackages = [os.path.join(d,p) for p in appPackages]
            break
        for appPackage in appPackages:
            self.addApplication(appPackage)

    def addApplication(self, appPackagePath):


        #todo: catch error, keep system stable
        import imp
        appName = os.path.basename(appPackagePath)
        pkgFile = os.path.join(appPackagePath, '__init__.py')
        if not os.path.exists(pkgFile):
            print('Missing package definition in {}'.format(appPackagePath))
            return
        mod = imp.load_source(appName, pkgFile)

        for subClass in EnMAPBoxApplication.__subclasses__():
            #check class
            appId = str(str(subClass))
            if appId in self.appList.keys():
                #todo: handle duplicates (signal?)
                pass

            #initialize App interface
            app = subClass(self.enmapBox)

            #check app
            EnMAPBoxApplication.checkRequirements(app)

            #load app
            appWrapper = ApplicationWrapper(app)
            self.loadApplication(appWrapper)

    def loadGeoAlgorithms(self, appWrapper):
        geoAlgorithms = appWrapper.app.geoAlgorithms()
        appWrapper.geoAlgorithms.extend(geoAlgorithms)
        self.PFMgr.addAlgorithms(self.PFMgr.enmapBoxProvider(), geoAlgorithms)


    def loadMenuItems(self, appWrapper, parentMenuName = 'Applications'):
        app = appWrapper.app
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


    def loadApplication(self, appWrapper):

        self.loadMenuItems(appWrapper)
        if self.PFMgr.isInitialized():
            self.loadGeoAlgorithms(appWrapper)

    def reloadApplication(self, appWrapper):
        self.removeApplication(appWrapper)
        self.loadApplication(appWrapper)

    def removeApplication(self, appWrapper):
        assert isinstance(appWrapper, ApplicationWrapper)

        #remove menu item
        for item in appWrapper.menuItem:
            item.parent().removeChildren(item)

        #todo: remove geo-algorithms
        self.PFMgr.removeAlgorithms(appWrapper.geoAlgorithms)
        self.appList.re


class EnMAPBoxApplication(QObject):
    """
    Base class to describe components of an EnMAPBoxApplication
    and to provide interfaces the main EnMAP-Box
    """

    @staticmethod
    def checkRequirements(enmapBoxApp):
        assert enmapBoxApp.name
        assert enmapBoxApp.version
        assert enmapBoxApp.licence


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