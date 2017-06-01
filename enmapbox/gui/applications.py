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
        self.PFM = self.enmapBox.processingAlgManager
        self.appList = collections.OrderedDict()

    def addApplicationFolder(self, appDir):
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
            #load app
            appWrapper = ApplicationWrapper(app)
            self.loadApplication(appWrapper)

    def loadGeoAlgorithms(self, appWrapper):
        app = appWrapper.app

        geoAlgorithms = app.geoAlgorithms()
        if geoAlgorithms is not None:
            enmapBoxProvider = self.PFM.enmapBoxProvider()
            from enmapboxplugin.processing.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider
            assert isinstance(enmapBoxProvider, EnMAPBoxAlgorithmProvider)
            import processing.core.Processing as Processing
            from processing.core.GeoAlgorithm import GeoAlgorithm
            """
            def addAlgorithm(self, providerName, alg):
                for p in self.providers:
                    if p.getName() == providerName:
                        p.loadAlgorithms()
                        self.algs[p.getName()] = {a.commandLineName(): a for a in p.algs}
                        self.providerUpdated.emit(p.getName())
                        break
            """
            for ga in geoAlgorithms:
                assert isinstance(ga, GeoAlgorithm)
                ga.provider = enmapBoxProvider
                #todo: handle duplicates
                enmapBoxProvider.dynamicallyAddedAlgs.append(ga)
            self.PFM.algList.reloadProvider(enmapBoxProvider.getName())
            s = ""
            pass

            appWrapper.geoAlgorithms.extend(geoAlgorithms)

    def loadMenuItems(self, appWrapper):
        app = appWrapper.app

        parentMenu = self.enmapBox.menu('Applications')
        #try:
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

        #except:
        #    print "Unexpected error:", sys.exc_info()[0]

    def loadApplication(self, appWrapper):
        #        except:
        # print "Unexpected error:", sys.exc_info()[0]

        self.loadMenuItems(appWrapper)
        if self.PFM.isInitialized():
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
        Returns a list of GeoAlgorithms()

        :return:
        """
        return None

if __name__ == '__main__':
    #mini test
    pass