# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.gui.utils import initQgisApplication
QGIS_APP = initQgisApplication()
from enmapboxtestdata import enmap, hymap, speclib
from enmapbox.gui.mimedata import *



class MimeDataTests(unittest.TestCase):

    def test_conversions(self):
        for t1 in ['normalstring', b'bytestring', r'rawstring']:

            ba = toByteArray(t1)
            self.assertIsInstance(ba, QByteArray)
            t2 = fromByteArray(ba)
            self.assertIsInstance(t2, str)
            self.assertEqual(len(t1), len(t2))
            if isinstance(t1, bytes):
                self.assertEqual(t1.decode(), t2)
            else:
                self.assertEqual(t1, t2)



if __name__ == "__main__":

    #exampleMapLinking()
    unittest.main()



