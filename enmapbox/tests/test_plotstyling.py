# -*- coding: utf-8 -*-

"""
***************************************************************************

    ---------------------
    Date                 :
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin jakimow at geo dot hu-berlin dot de
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
import unittest, json, pickle
from enmapbox.gui.plotstyling import *
import numpy as np
from osgeo import gdal




class TestInit(unittest.TestCase):

    def setUp(self):
        pass

    def test_json(self):


        pen = QPen()
        encoded = pen2tuple(pen)
        self.assertIsInstance(encoded, tuple)
        pen2 = tuple2pen(encoded)
        self.assertIsInstance(pen2, QPen)
        self.assertEqual(pen, pen2)

        plotStyle = PlotStyle()
        plotStyle.markerPen.setColor(QColor('green'))



        jsonStr = plotStyle.json()
        self.assertIsInstance(jsonStr, str)
        plotStyle2 = PlotStyle.fromJSON(jsonStr)

        self.assertIsInstance(plotStyle2, PlotStyle)
        self.assertTrue(plotStyle == plotStyle2)







if __name__ == '__main__':

    import json

    txt = json.dumps([0,1,2])

    unittest.main()
