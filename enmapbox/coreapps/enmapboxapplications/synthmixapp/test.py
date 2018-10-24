from enmapboxapplications.widgets.core import *
from enmapboxapplications.synthmixapp.core import SynthmixApp
from enmapboxtestdata import *

if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    #import qgisresources.images
    #qgisresources.images.qInitResources()


    enmapBox = EnMAPBox(None)
    enmapBox.run()
    #enmapBox.openExampleData(mapWindows=1)

    for source in [enmap, hires, landcover_polygons, landcover_points, library]:
        enmapBox.addSource(source=source)

    try:
        widget = SynthmixApp()
        widget.show()

        qgsApp.exec_()
        qgsApp.exitQgis()
    except:
        import traceback
        traceback.print_exc()

