Getting Started
###############

The following examples show how interacte with the EnMAP-Box GUI application.
All examples can be found as unittest TestCases in examples/api_examples.py

Example 1: Start the EnMAP-Box
==============================

For simplicity, we like to import some QGIS and Qt libraries which we use for the following examples globally::

    from qgis.core import *
    from qgis.gui import *
    from qgis.PyQt.QtWidgets import *
    from qgis.PyQt.QtGui import *
    from qgis.PyQt.QtCore import *


The Qt and QGIS widgets and objects need a QApplication or QgsApplication, respectively instance. This application
provides the main GUI Thread and keeps a GUI application alive. As we like to use the following examples from inside a
IDE like PyCharm, we need to emulate the QGIS Desktop Application, which else provides the QgsApplication instance::

    from enmapbox.testing import initQgisApplication
    qgsApp = initQgisApplication()


Now we can start the EnMAP-Box and open the example data::

    from enmapbox import EnMAPBox
    enmapBox = EnMAPBox(None)


    qgsApp.exec_()


The EnMAPBox object is a singleton, which means that there exist only one EnMAPBox instance. If there is already an existing EnMAP-Box instance, you can connect to like this::

    from enmapbox import EnMAPBox
    enmapBox = EnMAPBox.instance()
    print(enmapBox)

Load the EnMAP-Box test data::

    enmapBox.openExampleData()

Finally, shut down the EnMAP-Box instance::

    enmapBox = EnMAPBox.instance()
    enmapBox.close()



Manage Data Sources
###################

Add data sources
================

The EnMAP-Box differentiates between Raster, Vector, Spectral Libraries and other data sources. To add new data sources
just provide the file-paths or unified resource identifier (uri) via `enmapBox.addSource(r'uri')` ::

    enmapBox = EnMAPBox.instance()

    # add some data sources
    from enmapboxtestdata import enmap as pathRasterSource
    from enmapboxtestdata import landcover_polygons as pathVectorSource
    from enmapboxtestdata import library as pathSpectralLibrary

    #add a single source
    enmapBox.addSource(pathRasterSource)

    #add a list of sources
    enmapBox.addSources([pathVectorSource, pathSpectralLibrary])


The EnMAP-Box uses the QGIS API to visualize spatial data and allows to show OpenGIS Web Services (OWS)
like Web Map Services (WMS) and Web Feature Services (WFS)::

    wmsUri = 'referer=OpenStreetMap%20contributors,%20under%20ODbL&type=xyz&url=http://tiles.wmflabs.org/hikebike/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=17&zmin=1'
    wfsUri = r'restrictToRequestBBOX=''1'' srsname=''EPSG:25833'' typename=''fis:re_postleit'' url=''http://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_postleit'' version=''auto'''
    enmapBox.addSource(wmsUri, name="Open Street Map")
    enmapBox.addSource(wfsUri, name='Berlin PLZ')


  .. figure:: img/gstart_datasources.png
     :width: 100%

     Output example: Input raster (left), vector geometry for clipping (middle) and resulting output (right)

List existing data sources
==========================

You can iterate over all data sources::

    for source in enmapBox.dataSources():
        print(source)

... or specific ones only, using the ::

    for source in enmapBox.dataSources('RASTER'):
        print(source)




Remove data sources
===================

Use the data source path to remove it from the EnMAP-Box::

    enmapBox = EnMAPBox.instance()
    enmapBox.removeSource('source_path')

    #or remove multiple sources
    enmapBox.removeSources(['list-of-source_path'])


Manage Windows
##############

The EnMAP-Box provides different specialized windows called `Docks` to visualize spatial data and spectral libraries.
You can create new windows with::

    enmapBox = EnMAP-Box.instance()
    enmapBox.createDock('MAP')  # a spatial map
    enmapBox.createDock('SPECLIB') # a spectral library
    enmapBox.createDock('TEXT') # a text editor
    enmapBox.createDock('WEBVIEW') # a browser
    enmapBox.createDock('MIME') # a window to drop mime data (for developers)


Create a simple EnMAP-Box Application
#####################################

Applications for the EnMAP-Box are python programs that provide an `EnMAPBoxApplication` instance which is added to the EnMAPBox instance.
The `EnMAPBoxApplication` instance is used to provide:

* a `QMenu` which is added to the EnMAP-Box GUI menu and allows to start your applications by mouse click
* `QgsProcessingAlgorithms` which appear in the `EnMAPBoxAlgorithmProvider and allow to run your algorithms as part of
  the QGIS Processing Framework.


The ``examples/minimumexample`` module give an exmaple how to implement an EnMAPBoxApplication. Copy, rename and modify it to your needs to get
your code interacting with the EnMAP-Box.





