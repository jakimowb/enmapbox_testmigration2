from enmapboxapplications.widgets.core import *
from enmapboxapplications.imagestatistics.core import *
import enmapboxtestdata


if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()

    enmapBox = EnMAPBox(None)
    enmapBox.run()
    enmapBox.loadExampleData()

    try:
        widget = ImageStatisticsApp()
        widget.show()
        #widget.execute()
    except:
        import traceback
        traceback.print_exc()

    qgsApp.exec_()
    qgsApp.exitQgis()
