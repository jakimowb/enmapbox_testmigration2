from __future__ import absolute_import

import os
from qgis.core import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import *

LORE_IPSUM = r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."

"""
def printLogMessage(message, tag, level):
    if level == 1:
        m = message.split('\n')
        if '' in message.split('\n'):
            m = m[0:m.index('')]
        m = '\n'.join(m)
        if not re.search('enmapbox', m):
            return
        print('{}: {}'.format(tag, m))
    elif level == 2:
        print('{}({}): {}'.format( tag, level, message ) )
    s= ""
#from qgis.core import QgsMessageLog
#QgsMessageLog.instance().messageReceived.connect(printLogMessage)
"""

def _sandboxTemplate():
    qgsApp = initQgisEnvironment()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    #do something here

    qgsApp.exec_()
    qgsApp.exitQgis()

def sandboxPFReport():
    qgsApp = initQgisEnvironment()
    import enmapbox.gui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = True
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    #create a report in Processing Framework?
    from enmapbox.testdata import RandomForestModel
    from enmapboxplugin.processing.Signals import Signals
    from enmapbox.testdata import HymapBerlinB
    #EB.createDock('MAP', initSrc=HymapBerlinB.HymapBerlinB_image)

    Signals.pickleCreated.emit(RandomForestModel)
    from enmapbox.gui.utils import DIR_REPO
    Signals.htmlCreated.emit(jp(DIR_REPO,r'documentation/build/html/hub.gdal.html'))

    qgsApp.exec_()
    qgsApp.exitQgis()

def sandboxPureGui(dataSources=None, loadProcessingFramework=False, loadExampleData=False):
    qgsApp = initQgisEnvironment()


    import enmapbox.gui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = loadProcessingFramework
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    if loadExampleData:
        EB.openExampleData(mapWindows=2)

    qgsApp.exec_()
    qgsApp.exitQgis()


def sandboxDragDrop():
    qgsApp = initQgisEnvironment()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    # do something here

    qgsApp.exec_()
    qgsApp.exitQgis()


def sandboxGUI():
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.openExampleData(mapWindows=2)



#for backward compatibility
initQgisEnvironment = initQgisApplication


def sandboxDialog():
    qgsApp = initQgisEnvironment()
    w = QDialog()
    w.setWindowTitle('Sandbox')
    w.setFixedSize(QSize(300,400))
    l = QHBoxLayout()

    canvas = QgsMapCanvas(w, 'Canvas')
    l.addWidget(canvas)
    canvas.setAutoFillBackground(True)
    canvas.setCanvasColor(Qt.black)
    canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

    w.setLayout(l)
    qgsApp.setActiveWindow(w)
    w.show()

    qgsApp.exec_()
    qgsApp.exitQgis()



def sandboxTreeNodes():
    from enmapbox.gui.dockmanager import DockManager, DockPanelUI
    from enmapbox.gui.docks import DockArea

    dm = DockManager()
    ui = DockPanelUI()
    ui.connectDockManager(dm)
    rootNode = ui.model.rootNode
    from enmapbox.testdata.HymapBerlinA import HymapBerlinA_image
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode

    if True:
        n1 = TreeNode(rootNode, 'Group Node without value. Column span')
        n2 = TreeNode(n1, 'SubNode', value='SubNode Value')
        n3 = TreeNode(n1, 'Subnode, no value')
        crs = QgsCoordinateReferenceSystem('EPSG:4362')
        nCrs = CRSTreeNode(n1, crs)
        n2 = TreeNode(n1, 'SubGroup', value='SubGroup value')
        n3 = TreeNode(n1, 'SubSubNode, no value')
        n1.removeChildNode(n2)
    else:
        da = DockArea()
        dm.connectDockArea(da)
        dm.createDock('MAP', initSrc=HymapBerlinA_image)

    ui.show()


def sandboxDockManager():


    from enmapbox.gui.dockmanager import DockManager, DockPanelUI
    from enmapbox.gui.docks import DockArea

    dm = DockManager()
    ui = DockPanelUI()
    ui.connectDockManager(dm)
    rootNode = ui.model.rootNode
    from enmapbox.testdata.UrbanGradient import EnMAP
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode

    da = DockArea()
    dm.connectDockArea(da)
    dm.createDock('MAP', initSrc=EnMAP)

    ui.show()



def sandboxDataSourceManager():
    from enmapbox.gui.datasourcemanager import DataSourceManager, DataSourcePanelUI
    from enmapbox.gui.docks import DockArea

    dm = DataSourceManager()
    d = QDialog()
    d.setWindowTitle('TestDialog')
    d.setLayout(QVBoxLayout())
    ui = DataSourcePanelUI()
    ui.connectDataSourceManager(dm)
    d.layout().addWidget(ui)
    from enmapbox.testdata.UrbanGradient import EnMAP, LandCover
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode

    dm.addSource(EnMAP)
    dm.addSource(LandCover)
    d.show()
    s = ""


def howToStartEnMAPBoxInPython():

    # 2. start EnMAP-Box GUI
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()



if __name__ == '__main__':
    import site, sys, os
    if False:
        howToStartEnMAPBoxInPython()
        exit(0)
    else:
        qgsApp = initQgisEnvironment()

        #p = r'D:\Repositories\QGIS_Plugins'
        #pluginPath = [os.environ.get('QGIS_PLUGINPATH', '')]+[p]
        #os.environ['QGIS_PLUGINPATH'] = ';'.join(pluginPath)


        if False: sandboxTreeNodes()
        if False: sandboxDataSourceManager()
        if False: sandboxDockManager()
        if False: sandboxPureGui(loadProcessingFramework=True)
        if False: sandboxPFReport()
        if False: sandboxDragDrop()
        if True: sandboxGUI()
        if False: sandboxDialog()

        qgsApp.exec_()
        qgsApp.quit()