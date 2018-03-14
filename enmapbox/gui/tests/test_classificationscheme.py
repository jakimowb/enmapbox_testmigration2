# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from enmapbox.gui.sandbox import initQgisEnvironment
from enmapbox.gui.utils import *
from enmapbox.gui.classificationscheme import *
QGIS_APP = initQgisEnvironment()


from unittest import TestCase
class TestReclassify(TestCase):

    def testClassInfo(self):
        name = 'TestName'
        label = 2
        color = QColor('green')
        c = ClassInfo(name=name, label=label, color=color)
        self.assertEqual(c.name(), name)
        self.assertEqual(c.label(), label)
        self.assertEqual(c.color(), color)

        name2 = 'TestName2'
        label2 = 3
        color2 = QColor('red')
        c.setLabel(label2)
        c.setColor(color2)
        c.setName(name2)
        self.assertEqual(c.name(), name2)
        self.assertEqual(c.label(), label2)
        self.assertEqual(c.color(), color2)


    def testClassificationScheme(self):
        cs = ClassificationScheme.createClasses(3)

        self.assertIsInstance(cs, ClassificationScheme)
        self.assertEqual(cs[0].color(), DEFAULT_UNCLASSIFIEDCOLOR)
        self.assertEqual(cs[1].color(), DEFAULT_CLASSCOLORS[0])
        self.assertEqual(cs[2].color(), DEFAULT_CLASSCOLORS[1])
        c = ClassInfo(label=1, name='New Class', color=QColor('red'))
        cs.addClass(c)
        self.assertEqual(cs[3], c)
        cs.resetLabels()
        self.assertEqual(cs[3].label(), 3)



if __name__ == "__main__":

    unittest.main()



