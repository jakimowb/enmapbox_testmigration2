
from osgeo import gdal, ogr, osr, gdal_array

import sys, os, re

try:
    from qgis.gui import *
    from qgis.core import *
    import qgis
    import qgis_add_ins

    qgis_available = True
except:
    qgis_available = False

print('QGIS?:{}'.format(qgis_available))

import numpy as np
import tsv_widgets
import six
import multiprocessing


jp = os.path.join


path = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
if os.path.exists(path):
    multiprocessing.set_executable(path)
    sys.argv = [ None ]

pluginDir = os.path.dirname(__file__)
sys.path.append(pluginDir)
sys.path.append(os.path.join(pluginDir, 'libs'))
sys.path.append(os.path.join(pluginDir, *['libs','pyqtgraph']))

import pyqtgraph as pg

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def basic_3d_example():
    ## build a QApplication before building other widgets
    app = pg.mkQApp()


    ## make a widget for displaying 3D objects
    import pyqtgraph.opengl as gl
    view = gl.GLViewWidget()
    view.show()

    ## create three grids, add each to the view
    xgrid = gl.GLGridItem()
    ygrid = gl.GLGridItem()
    zgrid = gl.GLGridItem()
    view.addItem(xgrid)
    view.addItem(ygrid)
    view.addItem(zgrid)

    ## rotate x and y grids to face the correct direction
    xgrid.rotate(90, 0, 1, 0)
    ygrid.rotate(90, 1, 0, 0)

    ## scale each grid differently
    xgrid.scale(0.2, 0.1, 0.1)
    ygrid.scale(0.2, 0.1, 0.1)
    zgrid.scale(0.1, 0.2, 0.1)

    app.exec_()

PATH_EXAMPLE_IMG = jp(os.path.dirname(__file__), *['examples', 'Hymap_Berlin-A_Image'])
PATH_QGS = r'/Applications/QGIS.2.12.1.app/Contents/MacOS'


def multiview_example():

    cube = gdal_array.LoadFile(PATH_EXAMPLE_IMG)

    app = pg.mkQApp()
    w = pg.GraphicsLayoutWidget(border=True)
    w.show()

    xl = ['{}'.format(n+1) for n in range(5)]
    yl = ['A','B','C']

    for c, l in enumerate(xl):
        r = w.addLabel(l, row=0, col=c+1)

    for r, l in enumerate(yl):
        w.addLabel(l, row=r+1, col=0)

    refView = None
    for col in range(1, len(xl)+1):
        print(col)
        for r, l in enumerate(yl):
            row = r+1
            RGB = cube[[26, 73, 15],:,:]
            nb, nl, ns = RGB.shape
            RGB = RGB.transpose((2,1,0))
            name = '{}{}'.format(col, l)
            viewBox = pg.ViewBox(invertY=True, lockAspect=True, name=name)
            #viewBox.autoRange(padding=100,)
            viewBox.setXRange(0,ns)
            viewBox.setYRange(0,nl)
            imgItem = pg.ImageItem()
            imgItem.setImage(RGB)
            viewBox.addItem(imgItem)

            if refView is None:
                refView = viewBox
            else:
                viewBox.setXLink(refView)
                viewBox.setYLink(refView)

            w.addItem(viewBox, row=row, col=col)


    print('exec')
    app.exec_()

def qgis_map_canvas():
    app = pg.mkQApp()
    QgsApplication.setPrefixPath(PATH_QGS, True)
    QgsApplication.initQgis()

    w = QMainWindow()
    c = QgsMapCanvas()
    c.setCanvasColor(Qt.black)
    c.enableAntiAliasing(True)

    reg = QgsMapLayerRegistry.instance()
    w.setCentralWidget(c)
    w.show()


    lyr =  QgsRasterLayer(PATH_EXAMPLE_IMG)
    reg.addMapLayer(lyr, True)

    c.setExtent(lyr.extent())
    c.setLayerSet([QgsMapCanvasLayer(lyr)])

    app.exec_()
    pass

def main():

    #basic_3d_example()
    #multiview_example()
    qgis_map_canvas()

    pass

if __name__ == '__main__':
    main()
    print('Done')