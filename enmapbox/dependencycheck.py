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
import sys, os, collections

LAST_MISSED_PACKAGES = None
LAST_MISSED_INFO = ''

def checkAndShowMissingDependencies(packageNames):
    missing = missingPackages(packageNames)

    if len(missing) == 0:
        return True
    else:
        info = missingPackageInfo(missing)
        showDialog(info)
        return False




def missingPackages(packageNames):
    if not isinstance(packageNames, list):
        packageNames = [packageNames]

    missing = collections.OrderedDict()
    for p in packageNames:
        try:
            __import__(p)

        except Exception as ex:
            missing[p] = str(ex)
    LAST_MISSED_PACKAGES = list(missing.keys())
    return missing

def missingPackageInfo(missingPackages):

    assert isinstance(missingPackages, collections.OrderedDict)
    n = len(missingPackages)
    info = ['Unable to import the following {} package(s):'.format(n)]
    for pkg, ex in missingPackages.items():
        info.append(pkg)

    info.append('\nSystem info:')
    info.append('Python executable: {}'.format(sys.executable))
    info.append('Python prefix: {}'.format(sys.exec_prefix))
    info.append('PYTHONPATH:')
    for p in sorted(sys.path):
        info.append('{}'.format(p))
    info.append('\nOS ENVIRONMENT:')
    for k,v in os.environ.items():
        info.append('{}={}'.format(k,v))

    info = '\n'.join(info)

    LAST_MISSED_INFO = info
    return  info

def showDialog(info):
    from PyQt5.QtCore import QSize
    from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QLabel
    class DependencyInfoWidget(QDialog):

        def __init__(self, parent=None):
            super(DependencyInfoWidget, self).__init__(parent=parent)
            self.setFixedSize(QSize(400, 200))
            self.setModal(True)
            self.setWindowTitle('Missing python packages')
            l = QVBoxLayout()
            self.setLayout(l)
            l.addWidget(QLabel('Missing python packages'))
            self.textEdit = QTextEdit()
            l.addWidget(self.textEdit)

        def setText(self, text):
            self.textEdit.setText(text)

    from PyQt5.QtGui import QApplication

    app = QApplication.instance()
    init = not isinstance(app, QApplication)
    if init:
        app = QApplication([])

    w = DependencyInfoWidget()
    w.setText(info)
    w.setModal(True)
    w.exec_()

    if init:
        app.exec_()



def main():

    required = ['numpy','dash', 'sklearn', 'matplotlib', 'pyqtgraph']
    result = checkAndShowMissingDependencies(required)
    print(result)

if __name__ == '__main__':
    main()

