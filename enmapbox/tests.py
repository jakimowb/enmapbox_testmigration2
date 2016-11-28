from __future__ import absolute_import
import six, sys, os, gc, re, collections, site, inspect
from osgeo import gdal, ogr

from qgis import *
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
from PyQt.QtCore import *
import enmapbox
enmapbox.DEBUG = True
dprint = enmapbox.dprint
jp = os.path.join

LORE_IPSUM = r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."


def writelogmessage(message, tag, level):
    print('{}({}): {}'.format( tag, level, message ) )
from qgis.core import QgsMessageLog
QgsMessageLog.instance().messageReceived.connect( writelogmessage)


def test_GUI():
    # start a QGIS instance
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

    import enmapbox.processing

    if False:
        # register new model
        path = r'C:\foo\bar.model'

        enmapbox.processing.registerModel(path, 'MyModel')
        # IconProvider.test()
        # exit()

    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()

    if False:
        w = QMainWindow()
        w.setWindowTitle('QgsMapCanvas Example')

        w.setLayout(QGridLayout())
        from enmapbox.gui.docks import CanvasLinkTargetWidget
        w.layout().addWidget(CanvasLinkTargetWidget(None, None, parent=w))
        w.show()

    # add example images





    # EB = EnMAPBox(w)

    from enmapbox.main import EnMAPBox, TestData
    EB = EnMAPBox(None)
    # EB.dockarea.addDock(EnMAPBoxDock(EB, name='Dock (unspecialized)'))
    if True:
        if True:
            EB.createDock('MAP', name='MapDock 1', initSrc=TestData.AF_LAI)
            EB.createDock('MAP', name='MapDock 2', initSrc=TestData.AF_Image)
            EB.createDock('CURSORLOCATIONVALUE')
        if True: EB.createDock('MIME')

        if False:
            EB.createDock('TEXT',html=LORE_IPSUM)
            EB.createDock('TEXT', html=LORE_IPSUM)

        if True:
            # register new model
            path = TestData.RFC_Model
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

    #how to get loaded data sources
    from enmapbox.datasources import DataSourceRaster
    rasterSources = [src for src in EnMAPBox.instance().dataSourceManager.sources if isinstance(src, DataSourceRaster)]
    for src in rasterSources:
        print(src.uri)

    qgsApp.exec_()

    qgsApp.exitQgis()

    # qgsApp.exitQgis()
    # app.exec_()
    pass

    # load the plugin
    print('Done')

def test_dialog():

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
    from enmapbox.main import TestData


    lyr = QgsRasterLayer(TestData.AF_Image)
    QgsMapLayerRegistry.instance().addMapLayer(lyr)
    canvas.setLayerSet([QgsMapCanvasLayer(lyr)])
    canvas.setExtent(lyr.extent())


    result = showLayerPropertiesDialog(lyr, canvas, modal=False)
    print('Results {}'.format(result))

    #qgsApp.exec_()
    qgsApp.exitQgis()




if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py

    from enmapbox import DIR_SITE_PACKAGES
    site.addsitedir(DIR_SITE_PACKAGES)

    #run tests
    if True: test_GUI()
    if False: test_dialog()