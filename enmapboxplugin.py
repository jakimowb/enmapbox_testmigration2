from __future__ import absolute_import
import inspect
import os
import six
import traceback
import sys
import importlib
import re
import site

import qgis.gui
from PyQt4.QtCore import *
from PyQt4.QtGui import *



jp = os.path.join
DIR_REPO = os.path.normpath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
DIR_SITE_PACKAGES = jp(DIR_REPO, 'site-packages')

DEPENDENCIES_MANDATORY = ['numpy','scipy','sklearn','matplotlib']
DEPENDENCIES_OPTIONAL = ['foobar','astrolib']


class EnMAPBoxPlugin:
    _enmapBoxInstance = None

    def enmapBoxInstance(self):
        return self._enmapBoxInstance
    # initialize and unload all the stuff that comes under the umbrella of the EnMAP-Box:
    # main gui, maybe smaller GUIs and QGIS extensions, processing routines....

    def __init__(self, iface):
        self.iface = iface


        #open QGIS python console. this is required to allow for print() statements in the source code.
        if isinstance(self.iface, qgis.gui.QgisInterface):
            import console
            c = console.show_console()
            c.setVisible(True)

    def has_processing_framework(self):
        try:
            from processing.core import Processing
            return True
        except:
            return False


    def initGui(self):
        # add toolbar actions
        self.toolbarActions = []

        #1. EnMAP-Box main window

        syspaths = [os.path.normpath(p) for p in sys.path]
        if DIR_REPO not in syspaths: sys.path.append(DIR_REPO)
        site.addsitedir(DIR_SITE_PACKAGES)

        import enmapbox.main
        import enmapbox.utils
        from enmapbox.main import EnMAPBox
        dprint = enmapbox.main.dprint
        dprint('INIT ENMAPBOX-GUI')

        for p in DEPENDENCIES_MANDATORY:
            enmapbox.utils.check_package(p, stop_on_error=True)
        for p in DEPENDENCIES_OPTIONAL:
            failed = []
            if not enmapbox.utils.check_package(p):
                failed.append(p)
            if len(failed) > 0:
                dprint('Unable to load the following optional packages : {}'.format(', '.join(failed)))


        self.enmapbox = EnMAPBox(self.iface)
        EnMAPBoxPlugin._enmapBoxInstance = self.enmapbox

        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.enmapbox.run)
        self.toolbarActions.append(action)

        dprint('INIT ENMAPBOX QGIS TOOLBAR ACTION(S)')
        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)


        # init processing provider
        dprint('INIT ENMAPBOX PROCESSING PROVIDER(S)')
        self.processingProviders = []
        if self.has_processing_framework():
            # add example app
            try:
                from processing.core.Processing import Processing
                from enmapbox.apps.core import EnMAPBoxProvider

                #self.processingProviders.append(EnMAPBoxProvider())

                #todo: add other providers here

                #add providers to processing framework
                for provider in self.processingProviders:
                    Processing.addProvider(provider)

            except Exception, e:
                tb = traceback.format_exc()
                six.print_('ERROR occurred while loading EnMAPBoxProvider for processing frame work:', file=sys.stderr)
                six.print_(str(e))
                six.print_(tb)
            dprint('Processing framework initialization done')
        else:
            dprint('Unable to fine processing framework')
        dprint('EnMAP-Box initialization done')

    def unload(self):
        for action in self.toolbarActions:
            print(action)
            self.iface.removeToolBarIcon(action)

        if self.has_processing_framework():
            from processing.core.Processing import Processing
            for provider in self.processingProviders:
                Processing.removeProvider(provider)
        self.enmapbox = None
        from enmapbox.main import EnMAPBox
        EnMAPBox._instance = None

    def openGUI(self):
        pass


    def tr(self, message):
        return QCoreApplication.translate('EnMAPBoxPlugin', message)


if __name__ == '__main__':

    #start a QGIS instance
    if True:
        if sys.platform == 'darwin':
            PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
        else:
            PATH_QGS = os.environ['QGIS_PREFIX_PATH']
        assert os.path.exists(PATH_QGS)
        qgsApp = qgis.core.QgsApplication([], True)
        qgsApp.setPrefixPath(PATH_QGS, True)
        qgsApp.initQgis()

        import enmapbox.main

        w = QMainWindow()
        w.setWindowTitle('QgsMapCanvas Example')
        w.show()
        EB = enmapbox.main.EnMAPBox(w)
        EB.run()
        qgsApp.exec_()
        qgsApp.exitQgis()

        # qgsApp.exitQgis()
        # app.exec_()
        pass

        #load the plugin
    print('Done')
