# -*- coding: utf-8 -*-
"""
***************************************************************************
    test
    ---------------------
    Date                 : Dezember 2017
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
# noinspection PyPep8Naming
from __future__ import unicode_literals, absolute_import

import qgis.core
from PyQt4.QtCore import *
from PyQt4.QtGui import *




class MyWidget(QWidget):

    sigMySignal = pyqtSignal(str, int)

    def __init__(self):
        super(MyWidget, self).__init__(None)


        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel('Hello World'))
        self.myButton = QPushButton('Press me')
        self.myButton.clicked.connect(self.onClicked)

        assert isinstance(self.myButton, QPushButton)

        self.layout().addWidget(self.myButton)

    def onClicked(self, b):

        print('Hello? {}'.format(b))
        self.sigMySignal.emit("Hello 2? {}".format(b), 1)

from PyQt4 import uic
pathUiFile = 'D:\Repositories\QGIS_Plugins\enmap-box\snippets\example.ui'
from enmapbox.gui.utils import loadUIFormClass
#FORM_CLASS, _ = uic.loadUi(pathUiFile)
FORM_CLASS = loadUIFormClass(pathUiFile)

class MyDesignerWidget(QFrame, FORM_CLASS):

    def __init__(self):
        super(MyDesignerWidget, self).__init__(None)
        self.setupUi(self)
        self.myGroupBox



if __name__ == '__main__':

    app = QApplication([])

    if False:
        w = MyWidget()
        w.show()
        w.sigMySignal.connect(lambda s,b: w.setWindowTitle(s))
    if True:
        w = MyDesignerWidget()
        w.show()
    app.exec_()









