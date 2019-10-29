#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***************************************************************************
    about
    ---------------------
    Date                 : September 2017
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

#
   Copyright (c) 2019. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
   Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
   Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
   Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
   Vestibulum commodo. Ut rhoncus gravida arcu.


import os, collections
from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from enmapbox.gui.utils import loadUI, jp
from enmapbox import DIR_REPO


class AboutDialog(QDialog, loadUI('aboutdialog.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(AboutDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.mTitle = self.windowTitle()
        self.listWidget.currentItemChanged.connect(lambda: self.setAboutTitle())
        from enmapbox import __version__
        self.labelVersion.setText('Version {}'.format(__version__))
        self.setAboutTitle()

        import codecs
        #loadTextFile = lambda p: (open(p, 'r','UTF-8').read())

        def loadTextFile(p):
            if not os.path.isfile(p):
                return 'File not found "{}"'.format(p)

            f = open(p, 'r', encoding='utf-8')
            lines = f.read()
            f.close()
            return lines

        self.tbLicense.setText(loadTextFile(jp(DIR_REPO, 'LICENSE.txt')))
        self.tbContributors.setText(loadTextFile(jp(DIR_REPO, 'CONTRIBUTORS.md')))
        self.tbChanges.setText(loadTextFile(jp(DIR_REPO, 'CHANGES.txt')))
    def setAboutTitle(self, suffix=None):
        item = self.listWidget.currentItem()

        if item:
            title = '{} | {}'.format(self.mTitle, item.text())
        else:
            title = self.mTitle
        if suffix:
            title += ' ' + suffix
        self.setWindowTitle(title)



if __name__ == '__main__':

    from enmapbox.testing import initQgisApplication
    app = initQgisApplication()
    d = AboutDialog()
    d.show()
    app.exec_()
