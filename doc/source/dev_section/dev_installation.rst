
Installation (Dev)
##################


Background
==========

The EnMAP-Box 3 is a QGIS plugin and therefore uses the Python distribution that is delivered with or linked into QGIS.
If you like to use an Integrated Development Environment (IDE) to develop and debug python applications for the EnMAP-Box,
or in general QGIS, we recommend that your IDE runs under the same environmental settings as your QGIS does.

The following sections describe which settings are needed to run and debug the EnMAP-Box from
inside an IDE *without* the need to start a heavy QGIS instance.

We mainly tested in for the `PyCharm <https://www.jetbrains.com/pycharm/>`_ IDE and it worked well on `PyDev <http://www.pydev.org/>`_, too.

To setup your IDE for developing EnMAP-Box Applications, you need to:

    1. Clone the EnMAP-Box git repository and add it to your project sources

    2. Start your IDE using the same environmental settings as QGIS

    3. Set the QGIS python as python interpreter of your project

    4. Ensure that all python packages your application depends on are accessible in your QGIS python and
       your IDE (:ref:`install-python-packages`):

        * gdal, numpy, scipy, scikit-learn

        * pyqtgraph, matplotlib


        * sphinx and the sphinx-rtd-theme fro documentation

    5. Start the EnMAP-Box from your IDE (:ref:`dev_start_enmapbox_from_ide`)


Windows
=======

The following description is based on http://spatialgalaxy.net/2018/02/13/quick-guide-to-getting-started-with-pyqgis3-on-windows/

QGIS for Windows is based on an OSGeo4W installation that uses a set of cascading batch (``*.bat``) files to setup the QGIS environment. We use a similar approach to start the IDE.

1. First, locate the root folder of your QGIS3/OSGeo4W installation, e.g. ``C:\Program Files\QGIS 3.0\`` or ``C:\Program Files\OSGeo4W\``

2. Create a ``start_IDE_with_QGIS.bat`` to start your IDE in the same QGIS environment:

.. code-block:: bat

    ::STARTUP Script to start a IDE like PyCharm under the same environment as QGIS
    ::OSGeo4W or QQGIS installation folder
    set OSGEO4W_ROOT="C:\Program Files\QGIS 3.0"

    ::Executable of your IDE
    set IDE="C:\Program Files\JetBrains\PyCharm 2017.3.4\bin\pycharm64.exe"

    ::set defaults, clean path, load OSGeo4W modules (incrementally)
    call %OSGEO4W_ROOT%\bin\o4w_env.bat
    call qt5_env.bat
    call py3_env.bat

    ::lines taken from python-qgis.bat
    set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis
    set PATH=%QGIS_PREFIX_PATH%\bin;%PATH%

    ::make git and git-lfs accessible
    set PATH=%PATH%;C:\Users\geo_beja\AppData\Local\Programs\Git\bin
    set PATH=%PATH%;C:\Users\geo_beja\AppData\Local\Programs\Git LFS

    ::make PyQGIS packages available to Python
    set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python;%PYTHONPATH%

    :: GDAL Configuration (https://trac.osgeo.org/gdal/wiki/ConfigOptions)
    :: Set VSI cache to be used as buffer, see #6448 and
    set GDAL_FILENAME_IS_UTF8=YES
    set VSI_CACHE=TRUE
    set VSI_CACHE_SIZE=1000000
    set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins

    ::
    set QGIS_DEBUG=1

    start "Start your IDE aware of QGIS" /B %IDE% %*

    ::uncomment the following lines to start the Qt Designer, Assistent or QGIS 3 as well
    ::start "Start Qt Designer" /B designer
    ::start "Start Qt Assistant" /B assistant
    ::start "Start QGIS" /B "%OSGEO4W_ROOT%\bin\qgis-bin.exe" %*

    ::uncomment the following lines to open the OSGeo4W Shell
    ::@echo on
    ::@if [%1]==[] (echo run o-help for a list of available commands & cmd.exe /k) else (cmd /c "%*")

Note the lines to extend ``PATH`` by locations of local Git executables. This might be required to enable your IDE to access the git and git-lfs executables.

.. code-block:: bat

    set PATH=%PATH%;C:\Users\geo_beja\AppData\Local\Programs\Git\bin
    set PATH=%PATH%;C:\Users\geo_beja\AppData\Local\Programs\Git LFS


You can start Qt development tools with:

.. code-block:: bat

    start "Start Qt Designer" /B designer
    start "Start Qt Assistant" /B assistant
    start "Start QGIS" /B "%OSGEO4W_ROOT%\bin\qgis-bin.exe" %*


3. Call ``start_IDE_with_QGIS.bat`` to start your IDE and create a new project.

   Open the project settings and select the ``C:\Program Files\QGIS 3.0\bin\python3.exe`` as project interpreter.




4. Finally add the following locations to your project:

=================================================== ======================
Path                                                Notes
=================================================== ======================
``C:\YourRepositories\enmapbox``                    EnMAP-Box Source Code
``C:\Program Files\QGIS 3.0\apps\qgis\python``      QGIS and Qt Python API
``C:\Program Files\QGIS 3.0\apps\Python36\Scripts`` other helpful scripts
=================================================== ======================




macOS
=====

.. todo:: macOS descriptions


Linux
=====

.. todo:: Linux descriptions


.. _dev_start_enmapbox_from_ide:

Start the EnMAP-Box
===================

If everything is set up correctly, you should be able to start the EnMAP-Box using this Python script:

.. code-block:: python

    if __name__ == '__main__':

        from enmapbox.gui.utils import initQgisApplication
        from enmapbox.gui.enmapboxgui import EnMAPBox

        qgsApp = initQgisApplication()
        enmapBox = EnMAPBox(None)
        enmapBox.openExampleData(mapWindows=1)

        qgsApp.exec_()
        qgsApp.quit()


Build the EnMAP-Box Plugin for QGIS
===================================


The `make` folder contains some helper scripts required to build (parts) of the EnMAP-Box Plugin:

make/deploy.py - create the EnMAP-Box Plugin ZIP file
make/guimake.py - routines to handle PyQt5 issues, e.g. to create the Qt resource files
make/iconselect.py - a widget to show Qt internal QIcons and to copy its resource path to the clipboard
make/updateexternals.py - update parts of the EnMAP-Box code which are hosted in external repositories


If you like to build and install the EnMAP-Box Plugin from repository code you need to
run the `build()` function in `deploy.py`.





