Create an EnMAP-Box Application
===============================

EnMAP-Box Applications are normal python programs that can be called

* directly from EnMAP-Box GUI, e.g. via special tool buttons or context menues, or
* the QGIS Processing Framework as a GeoAlgorithm of the EnMAPBoxAlgorithmProvider

EnMAP-Box applications can interact with a running EnMAP-Box instance via the EnMAP-Box API, and, for example,
open new raster images in an EnMAP-Box map canvas or read the list of data sources.

The following tutorial refers to the example Application in ``examples/exampleapp``.
You might copy, rename and modify this to fit to your own needs and create your own EnMAP-Box Application.


1. The EnMAPBoxApplication Interface
------------------------------------

Initialize an new EnMAPBoxApplication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An EnMAP-Box Application derives from the `EnMAPBoxApplication` class and sets the class variables
`name` and `version`. The variable `license` defaults to `GNU GPL-3`` but might be change to the needs of your application::

    class ExampleEnMAPBoxApp(EnMAPBoxApplication):
        """
        This class implements an EnMAPBoxApplication Interface.

        """
        def __init__(self, enmapBox, parent=None):

            #First, call the constructor of the EnMAPBoxApplication superclass
            super(ExampleEnMAPBoxApp, self).__init__(enmapBox, parent=parent)

            #specify the name of this app
            self.name = 'My EnMAPBox App'

            #specify a version string
            self.version = '0.8.15'

            #specify a licence under which you distribute this application
            self.licence = 'BSD-3'


Define an Application Menu
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

        menu = appMenu.addMenu('Example App')
        menu.setIcon(self.icon())

        #add a QAction that starts a process of your application.
        #In this case it will open your GUI.
        a = menu.addAction('Show ExampleApp GUI')
        a.triggered.connect(self.startGUI)

        appMenu.addMenu(menu)

        return menu


Define GeoAlgorithms for the EnMAPBoxAlgorithm Provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your Application might provide a multiple `GeoAlgorithms` for the QGIS Processing, which allow your algorithms to be used, for example,
within the QGIS Processing Toolbox. To add these GeoAlgorithms to the EnMAP-Box GeoAlgorithmProvider your `EnMAPBoxApplication`
might implement the `geoAlgorithms()` function which returns a list of Geoalgorithms.

For the sake of simplicity, let's have an function that just prints its input arguments::

    def myAlgorithm(infile, outfile):
        """
        An algorithm that just prints the file paths
        """
        print('Infile: {}'.format(infile)
        print('Outfile: {}'.format(outfile)

The QGIS GeoAlgorithm to call it might look like this::

    from processing.core.GeoAlgorithm import GeoAlgorithm
    from processing.core.parameters import ParameterRaster
    from processing.core.outputs import OutputRaster
    class MyGeoAlgorithm(GeoAlgorithm):

        def defineCharacteristics(self):
            self.name = 'Example Algorithm'
            self.group = My EnMAPBox App
            self.addParameter(ParameterRaster('infile', 'Example Input Image'))
            self.addOutput(OutputRaster('outfile', 'Example Output Image'))

        def processAlgorithm(self, progress):

            #map processing framework parameters to that of you algorithm
            infile = self.getParameterValue('infile')
            outfile = self.getOutputValue('outfile')

            #run your algorithm
            myAlgorithm(infile, outfile)


        def help(self):
            return True, 'Shows how to implement an GeoAlgorithm'

To add `MyGeoAlgorithm` to the EnMAPBoxGeoAlgorithmProvider, just define the `geoAlgorithms()` like this::

    def geoAlgorithms(self):
        """
        This function returns the QGIS Processing Framework GeoAlgorithms specified by your application
        :return: [list-of-GeoAlgorithms]
        """

        return [MyGeoAlgorithm()]



2. Create a Graphical User Interface
------------------------------------

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

A GUI quickly becomes too complex to be programmed line-by-line.
In this case it is preferred to use the QDesigner and to "draw" the GUI. The GUI definition is
save as *.ui XML file, which that can be translated into PyQt code automatically::


    pyqt
