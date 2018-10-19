# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    __init__.py
    speclib module definition
    -------------------------
    Date                 : Okt 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This file is part of the EnMAP-Box.                                   *
*                                                                         *
*   The EnMAP-Box is free software; you can redistribute it and/or modify *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   The EnMAP-Box is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with the EnMAP-Box. If not, see <http://www.gnu.org/licenses/>. *
*                                                                         *
***************************************************************************
"""

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *

from enmapbox.gui.plotstyling import PlotStyleEditorWidgetFactory
#register Editor widgets, if not done before
reg = QgsGui.editorWidgetRegistry()
if len(reg.factories()) == 0:
    reg.initEditors()

if not 'PlotSettings' in reg.factories().keys():
    plotStyleEditorWidgetFactory = PlotStyleEditorWidgetFactory('PlotSettings')
    reg.registerWidget('PlotSettings', plotStyleEditorWidgetFactory)
else:
    plotStyleEditorWidgetFactory = reg.factories()['PlotSettings']

from .qgsfunctions import registerQgsExpressionFunctions
registerQgsExpressionFunctions()