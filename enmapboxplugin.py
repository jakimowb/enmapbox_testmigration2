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
site.addsitedir(jp(DIR_REPO, 'site-packages'))

DEPENDENCIES = ['numpy','foobar']




def check_package(name, package=None, verbose=True, stop_on_error=False):
    try:
        importlib.import_module(name, package)
        if verbose:
            print('Import {} successful'.format(name))
    except Exception, e:
        error_text = 'Unable to import {}'.format(name)
        if stop_on_error:
            raise Exception(error_text)
        else:
            six.print_(error_text, file=sys.stderr)
            return False
    return True





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
            from processing.core.Processing import Processing
            return True
        except:
            return False


    def initGui(self):
        # add toolbar actions
        self.toolbarActions = []

        #1. EnMAP-Box main window


        site_packages = jp(DIR_REPO, 'site-packages')
        to_add = [site_packages]

        #for name in os.listdir(site_packages):
        #    path = jp(site_packages, name)
        #    if os.path.isdir(path):
        #        print(path)
        #        to_add.append(path)
        if DIR_REPO not in sys.path:
            sys.path.append(DIR_REPO)
        from enmapbox.utils import add_to_sys_path
        add_to_sys_path(to_add)

        print('INIT ENMAPBOX-GUI')
        for p in sys.path: print(p)

        from enmapbox.main import EnMAPBox
        self.enmapbox = EnMAPBox(self.iface)
        EnMAPBoxPlugin._enmapBoxInstance = self.enmapbox

        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.enmapbox.run)
        self.toolbarActions.append(action)

        #2. tbd...
        for action in self.toolbarActions:
            print('ADD::{}'.format(action))
            self.iface.addToolBarIcon(action)


        # init processing provider

        self.processingProviders = []
        if True and self.has_processing_framework():
            # add example app
            try:
                from processing.core.Processing import Processing
                from enmapbox.apps.core import EnMAPBoxProvider


                p = EnMAPBoxProvider()

                self.processingProviders.append(EnMAPBoxProvider())

                #todo: add other providers here

                #add providers to processing framework
                for provider in self.processingProviders:
                    Processing.addProvider(provider)

            except Exception, e:
                tb = traceback.format_exc()
                six.print_('ERROR occurred while loading EnMAPBoxProvider for processing frame work:', file=sys.stderr)
                six.print_(str(e))
                six.print_(tb)
            print('Processing Framework initialization done')
        print('EnMAP-Box initialization done')

    def unload(self):
        for action in self.toolbarActions:
            print(action)
            self.iface.removeToolBarIcon(action)

        if self.has_processing_framework():
            from processing.core.Processing import Processing
            for provider in self.processingProviders:
                Processing.removeProvider(provider)

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
