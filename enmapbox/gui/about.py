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


import os, collections, pathlib
from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from enmapbox.gui.utils import loadUi, jp
from enmapbox import DIR_REPO


class AboutDialog(QDialog):
    def __init__(self, *args , **kwds):
        """Constructor."""
        super().__init__(*args , **kwds)
        pathUi
        loadUi()

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
        self.tbContributors.setText(loadTextFile(jp(DIR_REPO, 'CONTRIBUTORS.rst')))
        self.tbChanges.setText(loadTextFile(jp(DIR_REPO, 'CHANGELOG.rst')))
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
