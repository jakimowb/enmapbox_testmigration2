# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : March 2016
    Copyright            : (C) 2014 by Victor Olaya
    Email                : benjamin.jakimow at geo dot hu-berlin dot de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Benjamin Jakimow'
__date__ = 'March 2016'
__copyright__ = '(C) 2016, Benjamin Jakimow'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

def classFactory(iface):
    from EnMAPBoxPlugin import EnMAPBoxPlugin
    return EnMAPBoxPlugin(iface)