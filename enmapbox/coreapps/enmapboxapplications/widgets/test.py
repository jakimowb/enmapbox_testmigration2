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

from enmapboxapplications.widgets.core import *
from enmapboxapplications.synthmixapp.core import SynthmixApp

if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()

    enmapBox = EnMAPBox(None)
    enmapBox.run()
    enmapBox.openExampleData(mapWindows=1)
#    enmapBox.addSource(r'C:\Work\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\speclib\EndmemberSpeclib')
#    enmapBox.addSource(enmapboxtestdata.speclib)

#    widget = UiLibrary()
    #widget = UiLabeledLibrary()
    widget = SynthmixApp()
    widget.show()

    qgsApp.exec_()
    qgsApp.exitQgis()
