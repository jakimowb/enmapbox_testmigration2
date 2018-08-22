###############
Developer Guide
###############

.. todo:: Potentially some adjustment necessary to fit "new" structure:

          Developer Guide

            * Create new EnMAP-Box Application
                * Setup
                * QtApp
                * GeoAlgo
            * Managing EnMAP-Box (aktuell API - Quick Start)


EnMAP-Box Applications are normal python programs that can be called

* directly from EnMAP-Box GUI, e.g. via special tool buttons or context menues, or
* the QGIS Processing Framework as a QgsProcessingAlgorithm of the EnMAPBoxAlgorithmProvider

EnMAP-Box applications can interact with a running EnMAP-Box instance via the EnMAP-Box API, and, for example,
open new raster images in an EnMAP-Box map canvas or read the list of data sources.

The following tutorial refers to the example Application in ``examples/exampleapp``.
You might copy, rename and modify this to fit to your own needs and create your own EnMAP-Box Application.



Initialize a new EnMAP-Box Application
######################################

An EnMAP-Box Application derives from the `EnMAPBoxApplication` class and sets the class variables
`name` and `version`. The variable `license` defaults to `GNU GPL-3`` but might be change to the needs of your application::

    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import QMenu, QAction, QWidget, QHBoxLayout, QLabel, QPushButton
    from enmapbox.gui.applications import EnMAPBoxApplication
    from qgis.core import *


    VERSION = '0.0.1'
    LICENSE = 'GNU GPL-3'
    APP_DIR = os.path.dirname(__file__)

    APP_NAME = 'My First EnMAPBox App'

    class ExampleEnMAPBoxApp(EnMAPBoxApplication):
        """
        This Class inherits from an EnMAPBoxApplication
        """
        def __init__(self, enmapBox, parent=None):
            super(ExampleEnMAPBoxApp, self).__init__(enmapBox, parent=parent)

            #specify the name of this app
            self.name = APP_NAME

            #specify a version string

            self.version = VERSION

            #specify a licence under which you distribute this application
            self.licence = LICENSE


Define an Application Menu
==========================

To become accessible via a menu of the EnMAP-Box, the application needs to implement the `menu()` function that
returns a QAction or QMenu with multiple QActions. By default, the returned `QAction` or `QMenu` is added to the EnMAP-Box
"Application" menu where a user can click on to start the Application or to run different parts of your application


The connection between a single QAction and other parts of your code is realized using the Qt Signal-Slot concept, as in
this minimum example that you can run in a single python script::


    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

    if __name__ == '__main__':


        app = QApplication([])

        def myFunction(*args):
            print('Function called with arguments: {}'.format(args))

        menu = QMenu()
        a = menu.addAction('Without arguments')
        a.triggered.connect(myFunction)

        a = menu.addAction('With arguments')
        a.triggered.connect(lambda : myFunction(0,8,15))

        menu.show()
        app.exec_()

The `ExampleEnMAPBoxApp` uses this mechanism to define an application menu::

    def menu(self, appMenu):
        """
        Returns a QMenu that will be added to the parent `appMenu`
        :param appMenu:
        :return: QMenu
        """
        assert isinstance(appMenu, QMenu)
        """
        Specify menu, submenus and actions that become accessible from the EnMAP-Box GUI
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """

        # this way you can add your QMenu/QAction to an other menu entry, e.g. 'Tools'
        # appMenu = self.enmapbox.menu('Tools')

        menu = appMenu.addMenu('My Example App')
        menu.setIcon(self.icon())

        #add a QAction that starts a process of your application.
        #In this case it will open your GUI.
        a = menu.addAction('Show ExampleApp GUI')
        assert isinstance(a, QAction)
        a.triggered.connect(self.startGUI)
        appMenu.addMenu(menu)

        return menu


Define QgsProcessingAlgorithms for the EnMAPBoxAlgorithm Provider
=================================================================

Your Application might provide ojne or more ``QgsProcessingAlgorithms`` for the QGIS Processing Framework. This, for example, allow to use your algorithms
within the QGIS Processing Toolbox. To add these QgsProcessingAlgorithms to the EnMAP-Box Algorithm Provider, your ``EnMAPBoxApplication``
might implement the `geoAlgorithms()`.

For the sake of simplicity, let's have an function that just prints a dictionary of input arguments::

    def printDictionary(parameters):
        """
        An algorithm that just prints the provided parameter dictionary
        """
        print('Parameters:')
        for key, parameter in parameters.items():
            print('{} = {}'.format(key, parameter))


A ``QgsProcessingAlgorithm`` to call it might look like this::

    class ExampleGeoAlgorithm(QgsProcessingAlgorithm):

        def __init__(self):

            super(ExampleGeoAlgorithm, self).__init__()
            s = ""

        def createInstance(self):
            return ExampleGeoAlgorithm()

        def name(self):
            return 'exmaplealg'

        def displayName(self):
            return 'Example Algorithm'

        def groupId(self):

            return 'exampleapp'

        def group(self):
            return APP_NAME

        def initAlgorithm(self, configuration=None):
            self.addParameter(QgsProcessingParameterRasterLayer('pathInput', 'The Input Dataset'))
            self.addParameter(QgsProcessingParameterNumber('value','The value', QgsProcessingParameterNumber.Double, 1, False, 0.00, 999999.99))
            self.addParameter(QgsProcessingParameterRasterDestination('pathOutput', 'The Output Dataset'))

        def processAlgorithm(self, parameters, context, feedback):

            assert isinstance(parameters, dict)
            assert isinstance(context, QgsProcessingContext)
            assert isinstance(feedback, QgsProcessingFeedback)

            myAlgorithm(parameters)
            outputs = {}
            return outputs

To add `ExampleGeoAlgorithm` to the EnMAPBoxGeoAlgorithmProvider, just define the `geoAlgorithms()` like this::

    def geoAlgorithms(self):
        """
        This function returns the QGIS Processing Framework GeoAlgorithms specified by your application
        :return: [list-of-GeoAlgorithms]
        """

        return [ExampleGeoAlgorithm()]


Calling the ExampleGeoAlgorithm from the QGIS Processing Toolbox should create a printout on the IDE / QGIS python console like this::

    Parameters:
    pathInput = <qgis._core.QgsRasterLayer object at 0x0000018AA3C47A68>
    pathOutput = <QgsProcessingOutputLayerDefinition {'sink':C:/Users/ivan_ivanowitch/AppData/Local/Temp/processing_cb76d9820fc64087aa8264f0f8505334/642d8e0abb764557881346399dda9c68/pathOutput.bsq, 'createOptions': {'fileEncoding': 'System'}}>
    value = 1.0



Create a Graphical User Interface
=================================

The `startGUI()` function is used to open the graphical user interface. A very simple GUI could look like this::

    def onButtonClicked():
        print('Button was pressed')

    w = QWidget()
    w.setLayout(QVBoxLayout())
    w.layout().addWidget(QLabel('Hello World'))
    btn = QPushButton()
    btn.setText('click me')
    btn.clicked.connect(onButtonClicked)
    w.layout().addWidget(btn)
    w.show()



A GUI quickly becomes too complex to be programmed line-by-line. In this case it is preferred to use the QDesigner and to *draw* the GUI.
The GUI definition is saved in an ``*.ui`` XML file, which that can be translated into PyQt code automatically.






Managing EnMAP-Box (API Quick Start)
####################################



Access the EnMAP-Box
====================

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
===================

Add a new data sources
----------------------

To add a new data source to the EnMAP-Box just support its file-path or,
more generally spoken, its unified resource identifier (uri)::

    enmapBox = EnMAPBox.instance()
    enmapBox.addSource('filepath')


List existing data sources
--------------------------

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
-------------------

Use the data source path to remove it from the EnMAP-Box::

    enmapBox = EnMAPBox.instance()
    enmapBox.removeSource('path_to_source')

    #or remove multiple sources
    enmapBox.removeSources(['list-of-sources'])


Manage Windows
==============

The EnMAP-Box provides different windows to visualize different data sources.
You can create a new windows with::

    enmapBox = EnMAP-Box.instance()
    enmapBox.createDock('MAP')  # a spatial map
    enmapBox.createDock('SPECLIB') # a spectral library
    enmapBox.createDock('TEXT') # a text editor
    enmapBox.createDock('WEBVIEW') # a browser
    enmapBox.createDock('MIME') # a window to drop mime data



Interact with the EnMAP-Box
===========================

This example shows how the `Qt Signal-Slot system <http://doc.qt.io/archives/qt-4.8/signalsandslots.html>`_ can be used to react on EnMAP-Box events::


    class ExampleDialog(QDialog):
        def __init__(self, parent=None):
            super(ExampleDialog, self).__init__(parent=parent)

            # self.setParent(enmapBox.ui)
            self.btn = QPushButton('Clear')
            self.label = QLabel('This Box will shows data sources newly added to the EnMAP-Box.')
            self.tb = QPlainTextEdit()
            self.tb.setLineWrapMode(QPlainTextEdit.NoWrap)
            self.tb.setPlainText('Click "Project" > "Add example data"\n or add any other data source to the EnMAP-Box')
            l = QVBoxLayout()
            self.setLayout(l)
            l.addWidget(self.label)
            l.addWidget(self.tb)
            l.addWidget(self.btn)

            self.btn.clicked.connect(self.tb.clear)

        def onSignal(self, src):
            import datetime
            t = datetime.datetime.now()
            text = self.tb.toPlainText()
            text = '{}\n{} : {}'.format(text, t.time(), src)
            self.tb.setPlainText(text)

    enmapBox = EnMAPBox.instance()
    d = ExampleDialog(parent=enmapBox.ui)
    d.setFixedSize(QSize(600, 300))

    #connect different signals to a slot
    enmapBox.sigDataSourceAdded.connect(d.onSignal)
    enmapBox.sigCurrentLocationChanged.connect(d.onSignal)

    d.show()




Create EnMAP-Box Applications
=============================

Applications for the EnMAP-Box are python programs that can be called from

* the EnMAP-Box GUI directly and might provide its own GUI
* the QGIS Processing Framework. In this case they implement the GeoAlgorithm interface and are added to the EnMAPBoxAlgorithmProvider



The ``examples/exampleapp`` shows how this can be done. Copy, rename and modify it to your needs to get
your code interacting with the EnMAP-Box.



List of environmental variables
===============================

The following environmental variables can be set to change the starting behaviour of the EnMAP-Box.

====================  ====================  ================================================================================
Name                  Values, * = Default   Description
====================  ====================  ================================================================================
EMB_LOAD_PF           TRUE*/FALSE           Load QGIS processing framework.
EMB_LOAD_EA           TRUE*/FALSE           Loads external applications.
EMB_DEBUG             TRUE/FALSE*           Enable additional debug printouts.
EMB_SPLASHSCREEN      TRUE*/FALSE           Splashscreen on EnMAP-Box start.
EMB_MESSAGE_TIMEOUT   integer               Timeout in seconds for popup messages in the message bar.
EMB_APPLICATION_PATH  string                list of directories (separated by ';' or ':') to load EnMAPBoxApplications from.
====================  ====================  ================================================================================

Further links and sources
=========================

* https://docs.python.org/devguide

Git for Beginners
-----------------

* http://rogerdudler.github.io/git-guide/
* http://rogerdudler.github.io/git-guide/files/git_cheat_sheet.pdf


PyQGIS
------

* https://www.qgis.org/api/
* https://webgeodatavore.github.io/pyqgis-samples/
* http://plugins.qgis.org/planet/
* https://www.qgis.org/en/site/getinvolved/development/qgisdevelopersguide.html


Python Code Documentation
-------------------------

* http://www.sphinx-doc.org/en/stable/tutorial.html
* https://docs.python.org/devguide/documenting.html
* http://docutils.sourceforge.net/rst.html
* https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html
