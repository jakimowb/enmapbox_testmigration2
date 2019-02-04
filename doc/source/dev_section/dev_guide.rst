Create EnMAP-Box Applications
#############################


Applications for the EnMAP-Box define an ``EnMAPBoxApplication`` instance that describes basic
information like the Application name and how a user can start it. The following examples are taken from the
``examples/minimumexample`` module, which you might copy and modify to implement an EnMAPBox Application.


1. Initialize a new EnMAP-Box Application
=========================================

An EnMAP-Box application inherits from ``EnMAPBoxApplication`` and defines basic information like a
``name`` and ``version``. The variable ``license`` defaults to ``GNU GPL-3``, which is recommended by might be
change to your needs::

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


2. Define an Menu
=================

To become accessible via a menu of the EnMAP-Box, the application needs to implement the ``menu(...)`` function that
returns a QAction or QMenu with multiple QActions. By default, the returned ``QAction`` or ``QMenu`` is added to the EnMAP-Box
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

The ``ExampleEnMAPBoxApp`` uses this mechanism to define an application menu::

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


3. Define QgsProcessingAlgorithms for the EnMAPBoxAlgorithm Provider
====================================================================

Your Application might provide ojne or more ``QgsProcessingAlgorithms`` for the QGIS Processing Framework. This, for example, allow to use your algorithms
within the QGIS Processing Toolbox. To add these QgsProcessingAlgorithms to the EnMAP-Box Algorithm Provider, your ``EnMAPBoxApplication``
might implement the ``geoAlgorithms()``.

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

To add ``ExampleGeoAlgorithm`` to the EnMAPBoxGeoAlgorithmProvider, just define the ``geoAlgorithms()`` like this::

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



4. Create a Graphical User Interface
====================================

The ``startGUI()`` function is used to open the graphical user interface. A very simple GUI could look like this::

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
