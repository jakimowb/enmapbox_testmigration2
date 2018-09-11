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
    widget = SynthmixApp()
    widget.show()

    qgsApp.exec_()
    qgsApp.exitQgis()
