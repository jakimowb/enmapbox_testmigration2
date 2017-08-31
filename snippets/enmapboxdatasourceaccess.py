
# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapboxdatasourceaccess.py

    Examples how to access data sources listed in the EnMAP-Box
    ---------------------
    Date                 : August 2017
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
from __future__ import absolute_import
import os, collections
from qgis import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.utils import loadUI
from enmapbox.gui.enmapboxgui import EnMAPBox


def comboboxExample(isEditable):

    w = QWidget()
    w.setMaximumWidth(250)

    #Combobox to show file names
    cb = QComboBox(w)

    #Model to handle EnMAP-Box DataSources of all kinds
    from enmapbox.gui.datasources import DataSourceListModel

    model = DataSourceListModel()
    model.setSourceType('RASTER') #restrict on Raster Files
    cb.setModel(model)

    #a button to open and add new files
    btn = QPushButton(w)
    btn.setText('...')
    btn.clicked.connect(lambda: model.addSource(QFileDialog.getOpenFileName(w, 'Select source')))

    #
    l = QHBoxLayout()
    l.addWidget(cb)
    l.addWidget(btn)
    w.setLayout(l)

    #
    # allow to copy & paste file pathss
    #
    if isEditable:
        cb.setEditable(True)

        #a slot to handle manual edited paths
        def onComboboxEditTextChanged(text):
            dataSource = model.addSource(text)
            from enmapbox.gui.datasources import DataSource
            if isinstance(dataSource, DataSource):
                index = model.uri2index(dataSource)
                if index is not None:
                    cb.setCurrentIndex(index.row())
                    cb.setStyleSheet('QComboBox {color:black}')
                    return

            cb.setStyleSheet('QComboBox {color:red}')

        cb.editTextChanged.connect(onComboboxEditTextChanged)

    w.show()

if __name__ == '__main__':
    from enmapbox.gui.utils import initQgisApplication
    app = initQgisApplication()

    #start the EnMAP-Box
    import enmapbox.gui.enmapboxgui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = False

    emb = EnMAPBox(None)
    emb.run()
    emb.openExampleData(1) #show test data

    #Show datasources in QComboBox
    if True: comboboxExample(False)

    # Show datasources in editable QComboBox
    if True: comboboxExample(True)

    app.exec_()
