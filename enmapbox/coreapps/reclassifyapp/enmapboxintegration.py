# -*- coding: utf-8 -*-

"""
***************************************************************************
    hubreclassify/enmapboxintegration.py

    This file shows how to integrate your own algorithms and user interfaces into the EnMAP-Box.
    ---------------------
    Date                 : Juli 2017
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

import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from reclassifyapp import APP_DIR
class ReclassifyTool(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(ReclassifyTool, self).__init__(enmapBox, parent=parent)
        self.name = 'Reclassify Tool'
        self.version = 'Version 0.1'
        self.licence = 'GPL-3'

    def icon(self):
        pathIcon = os.path.join(APP_DIR, 'icon.png')
        return QIcon(pathIcon)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """
        appMenu = self.enmapbox.menu('Tools')

        #add a QAction that starts your GUI
        a = appMenu.addAction('Reclassify')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return a


    def startGUI(self, *args):
        from reclassifyapp import reclassifydialog as ui
        uiDialog = ui.ReclassifyDialog(self.enmapbox.ui)
        uiDialog.show()

        uiDialog.accepted.connect(lambda : self.runReclassification(**uiDialog.reclassificationSettings()))

    def runReclassification(self, **settings):
        #return {'pathSrc': pathSrc, 'pathDst': pathDst, 'LUT': LUT,
        #        'classNames': dstScheme.classNames(), 'classColors': dstScheme.classColors()}
        if len(settings) > 0 :
            from reclassifyapp import reclassify
            reclassify.reclassify(settings['pathSrc'],
                                  settings['pathDst'],
                                  settings['dstClassScheme'],
                                  settings['labelLookup'])