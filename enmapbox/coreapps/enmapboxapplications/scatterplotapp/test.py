from enmapboxapplications.widgets.core import *
from enmapboxapplications.scatterplotapp.core import ScatterPlotApp


if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()

    enmapBox = EnMAPBox(None)
    enmapBox.run()
    enmapBox.openExampleData(mapWindows=0)

    try:
        widget = ScatterPlotApp()
        widget.show()
    except:
        import traceback
        traceback.print_exc()

    qgsApp.exec_()
    qgsApp.exitQgis()

