
import random
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.gui import *
from qgis.core import *
from enmapbox.testing import initQgisApplication, TestObjects
from osgeo import gdal, osr

def createRandomRaster()->gdal.Dataset:
    """
    Create a random example
    :return:
    """

    path = r'F:\Temp\randomdataset.bsq'
    path = r'/vsimem/randomdataset.tiff'
    ns = random.choice(list(range(10,1000,10)))
    nl = random.choice(list(range(10,1000,10)))
    nb = random.choice([1,6,12,256])
    hasClasses = random.choice([True, False])

    if hasClasses:
        dt = gdal.GDT_Byte
        nc = random.choice(list(range(1,256)))
    else:
        nc = None
        dt = random.choice([gdal.GDT_Byte, gdal.GDT_Int16, gdal.GDT_Float32])
    print('{}x{}x{} tp {}'.format(nb, nl, ns, path))
    ds = TestObjects.createRasterDataset(nl=nl, ns=ns, nb=nb, eType=dt, nc=nc, path=path)

    return ds




APP = initQgisApplication()

ds = createRandomRaster()
lyr = QgsRasterLayer(ds.GetFileList()[0])
QgsProject.instance().addMapLayer(lyr)
def onModifyRasterSource():
    global ds, lyr
    print('Change source raster data!')
    nb0 = lyr.bandCount()
    ns0 =lyr.width()
    nl0 = lyr.height()

    ds = createRandomRaster()
    nb1, nl1, ns1 = ds.RasterCount, ds.RasterYSize, ds.RasterXSize
    lyr2 = QgsRasterLayer(ds.GetFileList()[0])
    print('Old: {}x{}x{}'.format(nb0, nl0, ns0))
    print('New: {}x{}x{}'.format(nb1, nl1, ns1))
    assert lyr2.bandCount() == nb1
    assert lyr2.width() == ns1
    assert lyr2.height() == nl1
    lyr.dataProvider().dataChanged.emit()
    lyr.dataProvider().updateExtents()
    #lyr.dataProvider().setInput(lyr2.dataProvider())
    lyr.dataProvider().copyBaseSettings(lyr2.dataProvider())
    lyr.dataProvider().reload()
    lyr.dataProvider().reloadData()
    lyr.triggerRepaint()
    lyr.reload()

    QApplication.instance().processEvents()


    assert lyr.bandCount() == lyr2.bandCount()
    assert lyr.width() == lyr2.width()
    assert lyr.heigth() == lyr2.height()



canvas = QgsMapCanvas()
canvas.setDestinationCrs(lyr.crs())
canvas.setExtent(lyr.extent())
canvas.setLayers([lyr])

btn = QPushButton()
btn.setText('Change data!')
btn.clicked.connect(onModifyRasterSource)
w = QWidget()
w.setLayout(QVBoxLayout())
w.layout().addWidget(canvas)
w.layout().addWidget(btn)
w.show()

APP.exec_()