# -*- coding: utf-8 -*-
"""
***************************************************************************
    versioncheck
    ---------------------
    Date                 : November 2017
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
import os

#check the API version of your PyQt sip bindings
import sip
if False:
    from qgis.core import QgsApplication
else:
    from PyQt4.QtGui import QApplication
print('API Version QString: {}'.format(sip.getapi('QString')))
