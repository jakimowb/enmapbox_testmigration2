from enmapbox import EnMAPBox, initAll
from enmapbox.testing import start_app
from geetimeseriesexplorerapp import GeeTimeseriesExplorerApp


#import pyqtgraph.examples
#pyqtgraph.examples.run()
#exit(0)
qgsApp = start_app()
initAll()
enmapBox = EnMAPBox(None)

app = GeeTimeseriesExplorerApp.instance()

# init GUI
app.actionToggleMainDock.trigger()
app.actionToggleProfileDock.trigger()


# create a composite
app.mainDock.mLANDSAT_LC08_C02_T1_L2.clicked.emit()
#app.dockWidget.mCompositeDateStart.setDate(QDate(2020, 8, 1))
#app.dockWidget.mCompositeDateEnd.setDate(QDate(2020, 8, 2))
#app.dockWidget.mCreateComposite.clicked.emit()
qgsApp.exec_()

# for i in range(w.colorRamp().count()): print(i, w.colorRamp().color(i/(w.colorRamp().count() - 1)).name())


# todo var qaMask = image.select('QA_PIXEL').rightShift(8).bitwiseAnd(3).neq(3)



