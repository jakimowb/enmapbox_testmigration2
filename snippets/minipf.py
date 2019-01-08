# -*- coding: utf-8 -*-

"""
***************************************************************************
    minipf
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
import qgis


from enmapbox.testing import initQgisApplication
qapp = initQgisApplication()

from processing.gui.ProcessingToolbox import ProcessingToolbox
from processing.core.Processing import Processing
from processing.core.alglist import algList
Processing.initialize()
from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
Processing.addProvider(EnMAPBoxAlgorithmProvider())

for a in algList.algs: print(a)
s  = ""
