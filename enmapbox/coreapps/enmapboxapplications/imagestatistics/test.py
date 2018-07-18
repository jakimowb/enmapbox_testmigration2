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

from enmapboxapplications.imagestatistics.core import *

def openTestdata():
    QgsProject.instance().addMapLayers([
        QgsRasterLayer(enmapboxtestdata.enmap, baseName=os.path.basename(enmapboxtestdata.enmap)),
        QgsRasterLayer(enmapboxtestdata.hymap, baseName=os.path.basename(enmapboxtestdata.hymap)),
        QgsVectorLayer(enmapboxtestdata.landcover, baseName=os.path.basename(enmapboxtestdata.landcover))])

if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()

    openTestdata()
    enmap = QgsRasterLayer(enmapboxtestdata.enmap, baseName=os.path.basename(enmapboxtestdata.enmap))
    landcover = QgsVectorLayer(enmapboxtestdata.landcover, baseName=os.path.basename(enmapboxtestdata.landcover))

    try:
        widget = ImageStatisticsApp()
        widget.uiRaster().setCurrentIndex(1)
        widget.uiMask().setCurrentIndex(3)
        widget.show()
        #widget.execute()
    except:
        import traceback
        traceback.print_exc()

    qgsApp.exec_()
    qgsApp.exitQgis()
