from PyQt5.QtCore import QSizeF
from qgis._core import QgsRectangle

from enmapboxprocessing.extentwalker import ExtentWalker
from enmapboxprocessing.test.testcase import TestCase


class TestExtentWalker(TestCase):

    def test_walkExtent_with_2x3_blocks_ofSize_4x5(self):
        nx = 2
        ny = 3
        sizex = 4
        sizey = 5
        extent = QgsRectangle(0, 0, nx * sizex, ny * sizey)
        blockSize = QSizeF(4, 5)
        extentWalker = ExtentWalker(extent, blockSize)
        self.assertEqual(extentWalker.nBlocksX(), nx)
        self.assertEqual(extentWalker.nBlocksY(), ny)
        gold = '[(0, 0, <QgsRectangle: 0 10, 4 15>), (0, 1, <QgsRectangle: 0 5, 4 10>), (0, 2, <QgsRectangle: 0 0, 4 5>), (1, 0, <QgsRectangle: 4 10, 8 15>), (1, 1, <QgsRectangle: 4 5, 8 10>), (1, 2, <QgsRectangle: 4 0, 8 5>)]'
        self.assertEqual(str(list(extentWalker)), gold)

    def test_walkExtent_with_blockSize_thatDoesNotMatch(self):
        extent = QgsRectangle(0, 0, 3, 3)
        blockSize = QSizeF(2, 2)
        for x, y, blockExtent in ExtentWalker(extent, blockSize):
            print(x, y, blockExtent.width(), blockExtent.height())
            if x == 1:
                self.assertEqual(1, blockExtent.width())
            else:
                self.assertEqual(2, blockExtent.width())
            if y == 1:
                self.assertEqual(1, blockExtent.height())
            else:
                self.assertEqual(2, blockExtent.height())
