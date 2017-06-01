import os, sys, site, collections
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import DIR_ENMAPBOX
from enmapbox.gui.enmapboxgui import EnMAPBox

class ApplicationWrapper(QObject):

    def __init__(self, app):
        assert isinstance(app, EnMAPBoxApplication)
        self.app = app
        self.menuItem = []
        self.geoAlgorithms = []


class ApplicationRegistry(QObject):

    def __init__(self, enmapBox, parent=None):
        super(ApplicationRegistry, self).__init__(parent)
        self.applicationFolders = []
        assert isinstance(enmapBox, EnMAPBox)

        self.enmapBox = enmapBox
        self.appList = collections.OrderedDict()

    def addApplicationFolder(self, appDir):
        if not os.path.isdir(appDir):
            return False

        #add all sub-directories to python path
        # extend system path by appDir
        oldSys = sys.path
        # sys.path.extend(appDir)
        site.addsitedir(appDir)

        for _, appPackages, _ in os.walk(appDir):
            break
        for appPackage in appPackages:
            self.addApplication(appPackage)

    def addApplication(self, appPackageName):


        #todo: catch error, keep system stable
        import importlib
        appPackage = importlib.import_module('__init__', appPackageName)
        for subClass in EnMAPBoxApplication.__subclasses__():
            #check class
            appId = str(str(subClass))
            if appId in self.appList.keys():
                #todo: handle duplicates (signal?)
                pass

            #initialize App interface
            app = subClass(self.enmapBox)
            #load app
            appWrapper = ApplicationWrapper(app)
            self.loadApplication(appWrapper)

    def loadGeoAlgorithms(self, appWrapper):
        app = appWrapper.app
        try:
            geoAlgorithms = app.geoAlgorithms()
            if geoAlgorithms:
                pass

                appWrapper.geoAlgorithms.extend(geoAlgorithms)
        except:
            print "Unexpected error:", sys.exc_info()[0]

    def loadMenuItems(self, appWrapper):
        app = appWrapper.app

        parentMenu = self.enmapBox.menu('Applications')
        try:
            item = app.menu(parentMenu)
            if item is None:
                print('no menu items defined')
                pass
            else:
                if isinstance(item, QMenu):
                    # item.setParent(parentMenu)

                    # item.setParent(parentMenu)
                    # item.menuAction().setParent(parentMenu)
                    parentMenu.addMenu(item)

                    # parentMenu.addAction(act)
                    s = ""
                elif isinstance(item, QAction):
                    item.setParent(parentMenu)
                    parentMenu.addAction(item)
                appWrapper.menuItem.append(item)

        except:
            print "Unexpected error:", sys.exc_info()[0]

    def loadApplication(self, appWrapper):
        self.loadMenuItems(appWrapper)
        self.loadGeoAlgorithms(appWrapper)

    def reloadApplication(self, appWrapper):
        self.removeApplication(appWrapper)
        self.loadApplication(appWrapper)

    def removeApplication(appWrapper):
        assert isinstance(appWrapper, ApplicationWrapper)

        #remove menu item
        for item in appWrapper.menuItem:
            item.parent().removeChildren(item)

        #remove geo-algorithms


class EnMAPBoxApplication(QObject):

    sigFileCreated = pyqtSignal(str)

    def __init__(self, enmapBox, parent=None):
        super(EnMAPBoxApplication, self).__init__(parent)
        self.enmapbox = enmapBox
        self.qgis = enmapBox.iface
        self.name = 'My App'
        self.version = '0.42'
        self.licence = 'GPL-3'

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
        Returns a list of GeoAlgorithms

        :return:
        """
        return None

if __name__ == '__main__':
    #mini test
    pass