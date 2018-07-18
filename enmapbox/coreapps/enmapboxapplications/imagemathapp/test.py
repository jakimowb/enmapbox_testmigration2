import os
import tempfile

from qgis._core import QgsProject

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtXml import QDomDocument
from PyQt5 import uic
import enmapboxtestdata
import hubdc.core

from enmapboxapplications.imagemathapp.core import *

#QgsRasterLayer(enmapboxtestdata.enmap, baseName=os.path.basename(enmapboxtestdata.enmap))
#QgsVectorLayer(enmapboxtestdata.landcover, baseName=os.path.basename(enmapboxtestdata.landcover))

def openTestdata():
    filename = r'C:\Work\data\gms\landsat\194\024\LT51940242010189KIS01\LT51940242010189KIS01_sr_band1.img'
    QgsProject.instance().addMapLayers([
        QgsRasterLayer(enmapboxtestdata.enmap, baseName=os.path.basename(enmapboxtestdata.enmap)),
        QgsVectorLayer(enmapboxtestdata.landcover, baseName=os.path.basename(enmapboxtestdata.landcover)),
        QgsRasterLayer(filename, baseName=os.path.basename(filename))])

if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()
#    import enmapboxapplications.ressources
#    enmapboxapplications.ressources.qInitResources()


    openTestdata()
    enmap = QgsRasterLayer(enmapboxtestdata.enmap, baseName=os.path.basename(enmapboxtestdata.enmap))
    landcover = QgsVectorLayer(enmapboxtestdata.landcover, baseName=os.path.basename(enmapboxtestdata.landcover))

    if 1: # default
        # widget = Input()
        widget = Output()
        #widget.setFilename('x.bsq')
        #print(widget.value())

        #widget = RemovableItem(Input); widget.createItem()
        #widget = RemovableItem(Output)
        #widget = ItemList(type=Input)
        #widget = ItemList()
        #widget = Extent()
        #widget = Grid()
        widget = ImageMathApp()
        widget.addInput(name='enmap', layer=enmap)
        widget.addInput(name='mask', layer=landcover)
        widget.addOutput(name='result', filename=r'c:\outputs\result.bsq')

        code = \
'''result = enmap
result[:, mask[0] == 0] = noDataValue(enmap)
setNoDataValue(result, noDataValue(enmap))
setMetadata(result, metadata(enmap))
'''
        #code = 'result = mask'
        widget.setCode(code=code)
#weiter routines einbauen

        #widget.execute()

    if 0:
        widget = Grid()

    widget.show()

    qgsApp.exec_()
    qgsApp.exitQgis()












