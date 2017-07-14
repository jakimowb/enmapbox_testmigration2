# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/tests.py

    Some unit tests
    ---------------------
    Date                 : Juli 2017
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

from unittest import TestCase


class TestNdvi(TestCase):
    def test_ndvi(self):
        from enmapbox.testdata.HymapBerlinB import HymapBerlinB_image
        from .algorithms import ndvi
        from tempfile import tempdir
        from os.path import join
        ndvi(infile=HymapBerlinB_image,
             outfile=join(tempdir(), 'ndvi.img'))
