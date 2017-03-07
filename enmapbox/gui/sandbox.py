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
    qgsApp = initQgs()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    #do something here

    qgsApp.exec_()
    qgsApp.exitQgis()

def sandboxPFReport():
    qgsApp = initQgs()
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
    qgsApp = initQgs()
    import enmapbox.gui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = False
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()
    from enmapbox.testdata import HymapBerlinB, HymapBerlinA
    if False:
        for k in HymapBerlinB.__dict__.keys():
            if k.startswith('Hymap'):
                EB.addSource(getattr(HymapBerlinB, k))

    EB.createDock('MAP', initSrc=HymapBerlinA.HymapBerlinA_image)
    EB.createDock('MAP', initSrc=HymapBerlinA.HymapBerlinA_mask)
    #do something here

    qgsApp.exec_()
    qgsApp.exitQgis()


def sandboxDragDrop():
    qgsApp = initQgs()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    # do something here

    qgsApp.exec_()
    qgsApp.exitQgis()


def sandboxGUI():
    qgsApp = initQgs()


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



def initQgs():
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
        s = ""

    else:
        # assume OSGeo4W startup
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    os.environ['QGIS_DEBUG'] = '1'
    assert os.path.exists(PATH_QGS)



    qgsApp = QgsApplication([], True)
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns')
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns/qgis')
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()
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




if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py


    #run tests
    if True: sandboxPureGui()
    if False: sandboxPFReport()
    if False: sandboxDragDrop()
    if False: sandboxGUI()
    if False: sandboxDialog()