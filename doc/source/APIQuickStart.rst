API - Quick Start
=================



Access the EnMAP-Box
--------------------

Start the EnMAP-Box from scratch::

    from enmapbox.gui.enmapboxgui import EnMAPBox
    from enmapbox.gui.utils import initQgisApplication

    qgsApp = initQgisApplication()
    enmapBox = EnMAPBox(None)
    enmapBox.openExampleData(mapWindows=1)

    qgsApp.exec_()
    qgsApp.quit()


The EnMAPBox object is designed as singleton, i.e. only one EnMAPBox instance
can exist per thread. If there is already an existing EnMAP-Box instance, you can connect to like this::

    from enmapbox.gui.enmapboxgui import EnMAPBox
    enmapBox = EnMAPBox.instance()


Finally, shut down the EnMAP-Box instance::

    enmapBox = EnMAPBox.instance()
    enmapBox.close()



Manage Data Sources
-------------------

Add a new data sources
......................

To add a new data source to the EnMAP-Box just support its file-path or,
more generally spoken, its unified resource identifier (uri)::

    enmapBox = EnMAPBox.instance()
    enmapBox.addSource('filepath')


List existing data sources
..........................

The EnMAP-Box differentiates between Raster, Vector, SpectraLibraries and HUB-DataCube
and other files-based data sources. The data sources known to the EnMAP-Box can be listed like this::

    enmapBox = EnMAPBox.instance()

    # print all sources
    for source in enmapBox.dataSources():
        print(source)

    # print raster sources only
    for source in enmapBox.dataSources('RASTER'):
        print(source)



Remove data sources
....................

Use the data source path to remove it from the EnMAP-Box::

    enmapBox = EnMAPBox.instance()
    enmapBox.removeSource('path_to_source')

    #or remove multiple sources
    enmapBox.removeSources(['list-of-sources'])


Manage EnMAP-Box Windows
------------------------

The EnMAP-Box provides different windows to visualize different data sources.
You can create a new windows with::

    enmapBox = EnMAP-Box.instance()
    enmapBox.createDock('MAP')  # a spatial map
    enmapBox.createDock('SPECLIB') # a spectral library
    enmapBox.createDock('TEXT') # a text editor
    enmapBox.createDock('WEBVIEW') # a browser
    enmapBox.createDock('MIME') # a window to drop mime data




Create EnMAP-Box Applications
-------------------------------

Applications for the EnMAP-Box are normal python programs that might be called from the (i) EnMAP-Box GUI or the QGIS Processing Framework,
where they appear in the (ii) EnMAPBoxAlgorithmProvider.

The ``enmapbox/apps/exampleapp`` shows how this can be done. Copy, rename and modify it to your needs to get
your code interacting with the EnMAP-Box.


