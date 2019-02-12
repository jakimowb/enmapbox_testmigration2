
Installation (Dev)
##################


Background
==========


If you like to develop an EnMAP-Box application (or more general: a Qt or QGIS application), you really should
use the comfort of an up-to-date Integrated Development Environment (IDE), and because the EnMAP-Box 3 is a QGIS plugin,
this IDE should run in the same environment as your local QGIS desktop application does.

In the following we describe how to run and debug the EnMAP-Box from an IDE *without* the need to start the QGIS desktop application.
We tested it for the `PyCharm <https://www.jetbrains.com/pycharm/>`_ IDE, but in principle the approach should work with other IDEs like `PyDev <http://www.pydev.org/>`_ as well.

To setup your IDE for developing EnMAP-Box Applications, you need to:

    1. Start your IDE using the same environmental settings as QGIS and create a new project ("your EnMAP-Box application")

    2. Set the QGIS python as python interpreter of your project

    3. Ensure that all python packages your application depends on are accessible in your QGIS python and
       your IDE (:ref:`install-python-packages`):

        * gdal, numpy, scipy, scikit-learn

        * pyqtgraph, matplotlib

        * sphinx and the sphinx-rtd-theme fro documentation

    4. Link the EnMAP-Box source code into your IDE project

    5. Start the EnMAP-Box from your IDE (:ref:`dev_start_enmapbox_from_ide`)

The more you get into the details of EnMAP-Box/QGIS/Qt Application Development, you might want to explore the respective APIs.
For this is is helpful to use the Qt documentation files (instead of slow online webpages). See XXX for more details



Windows
=======


The following description is based on http://spatialgalaxy.net/2018/02/13/quick-guide-to-getting-started-with-pyqgis3-on-windows/

QGIS for Windows (OSGeo4W) uses a set of cascading batch (``*.bat``) files to setup up the QGIS environment.
We recommend to use similar approaches to start the IDE and other application that require to operate in the same environment as the desktop QGIS does.

First, we need to know the root folder of our QGIS3/OSGeo4W installation, hereafter refered as ``OSGEO4W_ROOT``, e.g. ````OSGEO4W_ROOT=C:\Program Files\QGIS 3.0\`` or ````OSGEO4W_ROOT=C:\Program Files\OSGeo4W\``

OSGeo4W Shell
-------------

The following script shows how to setup and start the QGIS shell with a Python 3 and Qt 5 environment:

.. code-block:: bat

    ::STARTUP Script to start a IDE like PyCharm under the same environment as QGIS
    ::OSGeo4W/QGIS installation folder
    set OSGEO4W_ROOT="C:\Program Files\QGIS 3.4"

    ::set defaults, clean path, load OSGeo4W modules (incrementally)
    call %OSGEO4W_ROOT%\bin\o4w_env.bat
    call qt5_env.bat
    call py3_env.bat


Now you can type ``python`` to start a python 3 shell. Please note that without calling ```py3_env.bat`` before, the QGIS shell would start a python 2 shell instead.

Commands available in the QGIS shell can be listed with ``o-help``. E.g. calling ``qgis`` will start the QGIS desktop and ``setup`` the graphical OSGeo Installer.
Some of the most important for developen QGIS or EnMAP-Box applications might be:

=====================     ============================================================================
Command                   Description
=====================     ============================================================================
``qgis``                  QGIS desktop application
``setup``                 OSGeo4W graphical installer
``designer``              Qt Designer to draw graphical user interfaces
``qgis-designer``         Qt Designer + additional QGIS widgets
``assistant``             Qt Assistant to browse Qt + QGIS API reference
``python``                python shell. call ``py3_env.bat`` before to activate python 3
``pip``                   python package installer (similar to ``python -m pip``)
=====================     ============================================================================


Depending on previous setup steps some of these commands might not be installed by default.
The Qt Designer and Qt Assistant, for example, require to have the ``qt5-doc`` and ``qt5-devel`` packages installed.


IDE Start script
----------------

1. Create a ``start_IDE_with_QGIS.bat`` to start your IDE in the same environment as the QGIS desktop application:

.. code-block:: bat

    ::STARTUP Script to start a IDE like PyCharm under the same environment as QGIS
    ::OSGeo4W or QQGIS installation folder
    set OSGEO4W_ROOT="C:\Program Files\QGIS 3.4"

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

1. Ensure that the `QGIS_PREFIX_PATH` is available to the macOS shell. If not, edit the users `.bash_profile`:

    PATH="/Library/Frameworks/Python.framework/Versions/3.6/bin:${PATH}"
    export PATH
    QGIS_PREFIX_PATH="/Applications/QGIS3.app/Contents/MacOS"
    export QGIS_PREFIX_PATH

2. Start your IDE and ensure that following paths are available to your python project:

    /Applications/QGIS3.app/Contents/Resources/python
    /Applications/QGIS3.app/Contents/Resources/python/plugins

3.


.. todo:: macOS descriptions


Linux
=====

.. todo:: Linux descriptions



Setup the project
=================
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

Building the EnMAP-Box requires additional python packages, e.g. Sphinx for building the documentation etc. You can install these requirements with:

.. code-block:: batch

    pip install -r https://bitbucket.org/hu-geomatics/enmap-box/raw/requirements_developer.txt



The EnMAP-Box repositories `make` folder contains some helper scripts required to build (parts) of the EnMAP-Box Plugin:

make/deploy.py - create the EnMAP-Box Plugin ZIP file
make/guimake.py - routines to handle PyQt5 issues, e.g. to create the Qt resource files
make/iconselect.py - a widget to show Qt internal QIcons and to copy its resource path to the clipboard
make/updateexternals.py - update parts of the EnMAP-Box code which are hosted in external repositories


If you like to build and install the EnMAP-Box Plugin from repository code you need to
run the `build()` function in `deploy.py`.

Applications to develop with Qt & QGIS
======================================

The Qt company provides several tools to create Qt C++ applications. Although these focus primarily on
C++ developers, they are helpful also for developer which make use of the Qt and QGIS python API.

Qt Assistant
------------

The Qt Assistant allows you to browse fast and offline through Qt help files (`*.qch`). These files exists for
all Qt classes and the QGIS API. They can be generated event with Sphinx, which allows you to provide your
own source-code documentation as `.qch` file as well.

The QGIS API help file `qgis.qch` can be downloaded from https://qgis.org/api/

The Qt help files are usually installed with your local Qt installation.
Windows users can find it in a folder similar to `C:\Program Files\QGIS 3.4\apps\Qt5\doc`.


Qt Designer
-----------

The Qt Designer is a powerful tool to create the frontend of graphically user interfaces.
A new GUI frontend can be drawed an saved in a XML file with file ending `*.ui`.These form files can be called from
python code, in which the entire backend might be implemented.


.. figure:: img/qt_designer_example.png

     :width: 100%

     Qt Designer showing the metadataeditor.ui for the Metadata editor.


Qt Creator
----------

Qt Creator is the one-in-all IDE to develop Qt C++ applications. It includes the functionality covered by Qt Assistant
(here called Help) and Qt Designer (here called form designer) and helps to browse C++ code. If you like to
explore the QGIS source code to better understand what it does behind the QGIS python API interfaces, this is the IDE
you should go for.


.. figure:: img/qt_creator_example_ui.png

     :width: 100%

     Qt Creator with opened metadataeditor.ui.







Explore the Qt and QGIS API
===========================

API references can be found at:

* https://qgis.org/api/ (C++ API)

* https://qgis.org/pyqgis/master/ (autogenerated Python API)

* http://doc.qt.io/qt-5/ (Qt5 API)

However, it is recommended to use Qt help files (*.qch), which can be used offline and allow for much faster browsing and searching.

1. Download or locate the help *.qch files

* QGIS API https://qgis.org/api/qgis.qch
* Qt API

    * `C:\Program Files\QGIS 3.4\apps\Qt5\doc` (Windows)
    * `~/Qt/Docs/Qt-5.11.2/` (macOS)

2. Open the Qt Assistant / Qt Creator settings and add the required *.qch files, in particular ``qgis.qch``, ``qtcore.qch``, ``qtwidgets.qch`` and ``qtgui.qch``.
















