from enmapboxapplications.widgets.core import *
from enmapboxapplications.forceapp.core import ForceApp

if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()

    enmapBox = EnMAPBox(None)
    enmapBox.run()
#    enmapBox.openExampleData(mapWindows=1)

    widget = ForceApp()
    widget.show()

    widget.setDB(folder=r'C:\Work\data\FORCE\crete')
    widget.updateDB(folder=r'C:\Work\data\FORCE\crete')

    qgsApp.exec_()
    qgsApp.exitQgis()
