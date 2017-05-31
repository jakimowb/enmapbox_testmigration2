import os, site, collections
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import DIR_ENMAPBOX


class ApplicationWrapper(QObject):

    def __init__(self):
        pass

class ApplicationRegistry(QObject):

    def __init__(self, enmapBox, parent=None):
        super(ApplicationRegistry, self).__init__(parent)
        self.applicationFolders = []
        self.enmapBox = enmapBox
        self.appList = collections.OrderedDict()

    def addApplicationFolder(self, path):
        if not os.path.isdir(path):
            return False

        site.addsitedir(path)
        for subClass in EnMAPBoxApplication.__subclasses__():
            app = subClass(self.enmapBox)
            appId =  str(type(app))
            assert isinstance(app, EnMAPBoxApplication)
            if appId in self.appList.keys():
                #todo: handle duplicates / re-loads
                pass

            self.loadApplication(app)
        s = ""

    def loadApplication(self, app):
        parentMenu = self.enmapBox.menu('Applications')
        item = app.menu(parentMenu)
        if True:
            if isinstance(item, QMenu):
                #item.setParent(parentMenu)

                #item.setParent(parentMenu)
                #item.menuAction().setParent(parentMenu)
                parentMenu.addMenu(item)

                #parentMenu.addAction(act)
                s = ""
            elif isinstance(item, QAction):
                item.setParent(parentMenu)
                parentMenu.addAction(item)


        geoAlgorithms = app.geoAlgorithms()
        if geoAlgorithms:
            pass
        return True


    def registerApplications(self):
        pass

    def unregisterApplication(self):
        pass

class EnMAPBoxApplication(QObject):

    sigFileCreated = pyqtSignal(str)

    def __init__(self, enmapBox, parent=None):
        super(EnMAPBoxApplication, self).__init__(parent)
        from enmapbox.gui.enmapboxgui import EnMAPBox

        assert isinstance(enmapBox, EnMAPBox)
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
