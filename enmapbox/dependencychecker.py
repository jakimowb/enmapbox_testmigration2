# -*- coding: utf-8 -*-
"""
***************************************************************************
    dependencychecker

    This module contains functionality to check the calling python environment for required packages and return
    user-friendly warning in case of missing dependencies.

    ---------------------
    Date                 : Januar 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
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
# noinspection PyPep8Naming
from __future__ import unicode_literals, absolute_import
import sys, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *

def checkDependency(packageName):

    pass

def checkDependencies(packageNames):

    pass


class DependencyInfoWidget(QDialog):

    def __init__(self, missing,  parent=None):
        super(DependencyInfoWidget, self).__init__(parent=parent)

        self.setWindowTitle('Missing python packages')
        l = QVBoxLayout()
        self.setLayout(l)
        l.addWidget(QLabel('Please install these packages'))
        self.lw = QListWidget()
        self.lw.itemClicked.connect(self.onItemClicked)
        l.addWidget(QLabel('Please install these packages to '))
        l.addWidget(self.lw)


    def setMissingPackages(self, missing):
        self.lw.clear()
        for m in missing:
            item = QListWidgetItem()
            item.setText(str(m))

            self.lw.addItem(item)

    def onItemClicked(self, item):

        if isinstance(item, QListWidgetItem):
            pkg = item.text()
            cb = QApplication.clipboard()
            assert isinstance(cb, QClipboard)
            cb.setText(pkg)






if __name__ == '__main__':

    required = ['numpy','dash', 'sklearn', 'matplotlib', 'pyqtgraph']


