from enmapboxapplications.widgets.core import *
from enmapboxapplications.classificationapp.core import ClassificationWorkflowApp


if __name__ == '__main__':

    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()

    import qgisresources.images
    qgisresources.images.qInitResources()

    enmapBox = EnMAPBox(None)
    enmapBox.run()
    enmapBox.openExampleData(mapWindows=0)
    #enmapBox.addSource(source=r'C:\Users\janzandr\AppData\Local\Temp\classifier.pkl')


    try:

        widget = ClassificationWorkflowApp()
        widget.show()

    except:
        import traceback
        traceback.print_exc()

    qgsApp.exec_()
    qgsApp.exitQgis()

