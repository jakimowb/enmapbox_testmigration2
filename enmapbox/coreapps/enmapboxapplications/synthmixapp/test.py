from enmapbox.testing import initQgisApplication
from enmapboxapplications.widgets.core import *
from enmapboxapplications.synthmixapp.core import SynthmixApp


if __name__ == '__main__':

    qgsApp = initQgisApplication()

    import qgisresources.images
    qgisresources.images.qInitResources()


    enmapBox = EnMAPBox(None)
    enmapBox.run()
    enmapBox.openExampleData(mapWindows=0)

    try:
        widget = SynthmixApp()
        widget.show()

        qgsApp.exec_()
        qgsApp.exitQgis()
    except:
        import traceback
        traceback.print_exc()

