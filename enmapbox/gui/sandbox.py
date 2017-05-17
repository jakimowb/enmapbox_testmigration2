from __future__ import absolute_import

import os
from qgis.core import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import *

LORE_IPSUM = r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."


def writelogmessage(message, tag, level):
    print('{}({}): {}'.format( tag, level, message ) )
from qgis.core import QgsMessageLog
QgsMessageLog.instance().messageReceived.connect(writelogmessage)


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

def sandboxPureGui():
    qgsApp = initQgisEnvironment()
    import enmapbox.gui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = True
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    #load urban gradient dataset
    #add relevant files
    baseDir = r'E:\_EnMAP\Project_EnMAP-Box\SampleData\urbangradient_data'
    files = []
    files += file_search(baseDir, '*.bsq', recursive=True)
    files += file_search(baseDir, '*.shp', recursive=True)
    import enmapbox.testdata
    files += [enmapbox.testdata.RandomForestModel]
    for file in files:
        EB.addSource(file)

    bp = r'EnMAP01_Berlin_Urban_Gradient_2009.bsq'
    baseDir = r'E:\_EnMAP\Project_EnMAP-Box\SampleData\urbangradient_data\BerlinUrbGrad2009_01_image_products\01_image_products'
    baseShp = r'E:\_EnMAP\Project_EnMAP-Box\SampleData\urbangradient_data\BerlinUrbGrad2009_02_additional_data\02_additional_data\land_cover'
    path1 = jp(baseDir, 'EnMAP01_Berlin_Urban_Gradient_2009.bsq')
    path2 = jp(baseDir, 'EnMAP02_Berlin_Urban_Gradient_2009.bsq')

    EB.createDock('MAP', initSrc=path1)
    EB.createDock('MAP', initSrc=path2)
    #do something here
    from qgis import utils as qgsUtils
    qgsUtils.iface.messageBar().pushMessage('STARTED', QgsMessageBar.SUCCESS)
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
    qgsApp = initQgisEnvironment()


    # EB = EnMAPBox(w)

    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)

    if False:
        if True:
            from enmapbox.testdata import UrbanGradient
            EB.createDock('MAP', name='MapDock 1', initSrc=UrbanGradient.EnMAP01_Berlin_Urban_Gradient_2009_bsq)
            EB.createDock('MAP', name='MapDock 2', initSrc=UrbanGradient.LandCov_Class_Berlin_Urban_Gradient_2009_bsq)
            EB.createDock('MAP', name='MapDock 2', initSrc=UrbanGradient.LandCov_Vec_Berlin_Urban_Gradient_2009_shp)
            EB.createDock('CURSORLOCATIONVALUE')
        if False: EB.createDock('MIME')

        if False:
            EB.createDock('TEXT',html=LORE_IPSUM)
            EB.createDock('TEXT', html=LORE_IPSUM)

        if False:
            # register new model
            import enmapbox.processing
            enmapbox.processing.registerModel(path, 'MyModel')
            # IconProvider.test()
            # exit()

    # md1.linkWithMapDock(md2, linktype='center')
    # EB.show()
    # EB.addSource(r'C:\Users\geo_beja\Repositories\enmap-box_svn\trunk\enmapProject\enmapBox\resource\testData\image\AF_Mask')
    # EB.addSource(r'C:\Users\geo_beja\Repositories\enmap-box_svn\trunk\enmapProject\enmapBox\resource\testData\image\AF_LAI')
    # EB.addSource(
    #   r'C:\Users\geo_beja\Repositories\enmap-box_svn\trunk\enmapProject\enmapBox\resource\testData\image\AF_LC')
    EB.run()
    from enmapbox.testdata import UrbanGradient
    if False:
        EB.addSource(UrbanGradient.LandCov_Class_Berlin_Urban_Gradient_2009_bsq)

    if True:

        EB.createDock('MAP', name='EnMAP 01', initSrc=UrbanGradient.EnMAP01_Berlin_Urban_Gradient_2009_bsq)
        EB.createDock('MAP', name='HyMap 01', initSrc=UrbanGradient.HyMap01_Berlin_Urban_Gradient_2009_bsq)
        #EB.createDock('MAP', name='LandCov Level1', initSrc=UrbanGradient.LandCov_Layer_Level1_Berlin_Urban_Gradient_2009_bsq)
        #EB.createDock('MAP', name='LandCov Level2', initSrc=UrbanGradient.LandCov_Layer_Level2_Berlin_Urban_Gradient_2009_bsq)
        #EB.createDock('MAP', name='Shapefile', initSrc=UrbanGradient.LandCov_Vec_polygons_Berlin_Urban_Gradient_2009_shp)
        #EB.createDock('CURSORLOCATIONVALUE')

    qgsApp.exec_()

    qgsApp.exitQgis()

    # qgsApp.exitQgis()
    # app.exec_()
    pass

    # load the plugin
    print('Done')



def initQgisEnvironment():
    import site

    # start a QGIS instance
    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
        os.environ['GDAL_DATA'] = r'/usr/local/Cellar/gdal/1.11.3_1/share'

        #rios?
        from enmapbox.gui.utils import DIR_SITEPACKAGES
        #add win32 package, at least try to

        pathDarwin = jp(DIR_SITEPACKAGES, *['darwin'])
        site.addsitedir(pathDarwin)
        QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns')
        QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns/qgis')
        s = ""

    else:
        # assume OSGeo4W startup
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    os.environ['QGIS_DEBUG'] = '1'

    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()
    import enmapbox.gui
    enmapbox.gui.DEBUG = True
    return qgsApp


def sandboxDialog():

    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
        os.environ['GDAL_DATA'] = r'/usr/local/Cellar/gdal/1.11.3_1/share'
    else:
        # assume OSGeo4W startup
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    os.environ['QGIS_DEBUG'] = '1'


    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns')
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns/qgis')
    #QT_PLUGIN_PATH = % OSGEO4W_ROOT %\apps\qgis\qtplugins;
    # % OSGEO4W_ROOT %\apps\qt4\plugins

    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()

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





    from enmapbox.gui.layerproperties import showLayerPropertiesDialog
    from enmapbox.gui.main import TestData


    lyr = QgsRasterLayer(TestData.AF_Image)
    QgsMapLayerRegistry.instance().addMapLayer(lyr)
    canvas.setLayers([QgsMapCanvasLayer(lyr)])
    canvas.setExtent(lyr.extent())


    result = showLayerPropertiesDialog(lyr, canvas, modal=False)
    print('Results {}'.format(result))

    #qgsApp.exec_()
    qgsApp.exitQgis()



def sandboxTreeNodes():

    qgisApp = initQgisEnvironment()

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
    qgisApp.exec_()


def sandboxDockManager():

    qgisApp = initQgisEnvironment()

    from enmapbox.gui.dockmanager import DockManager, DockPanelUI
    from enmapbox.gui.docks import DockArea

    dm = DockManager()
    ui = DockPanelUI()
    ui.connectDockManager(dm)
    rootNode = ui.model.rootNode
    from enmapbox.testdata.HymapBerlinA import HymapBerlinA_image
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode

    da = DockArea()
    dm.connectDockArea(da)
    dm.createDock('MAP', initSrc=HymapBerlinA_image)

    ui.show()
    qgisApp.exec_()


def sandboxDataSourceManager():

    qgisApp = initQgisEnvironment()

    from enmapbox.gui.datasourcemanager import DataSourceManager, DataSourcePanelUI
    from enmapbox.gui.docks import DockArea

    dm = DataSourceManager()
    ui = DataSourcePanelUI()
    ui.connectDataSourceManager(dm)
    rootNode = ui.model.rootNode
    from enmapbox.testdata.HymapBerlinA import HymapBerlinA_image
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode

    dm.addSource(HymapBerlinA_image)
    ui.show()
    qgisApp.exec_()

def howToStartEnMAPBoxInPython():
    import os
    # 1. initialize QGIS Environment
    PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()

    # 2. start EnMAP-Box GUI
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    qgsApp.exec_()


if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py


    #run tests
    if True:
        howToStartEnMAPBoxInPython()
        exit(0)
    if False: sandboxTreeNodes()
    if False: sandboxDataSourceManager()
    if False: sandboxDockManager()
    if True: sandboxPureGui()
    if False: sandboxPFReport()
    if False: sandboxDragDrop()
    if False: sandboxGUI()
    if False: sandboxDialog()