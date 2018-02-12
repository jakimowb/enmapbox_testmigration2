Installation for Developers
===========================

Background
----------

The EnMAP-Box 3 is a QGIS plugin and therefore uses the Python distribution that is delivered with or linked into QGIS.
If you like to use an Integrated Development Environment (IDE) to develop and debug python applications for the EnMAP-Box,
or in general QGIS, we recommend that your IDE runs under the same environmental settings as your QGIS does.

The following sections describe which settings are needed to run and debug the EnMAP-Box from
inside an IDE *without* starting the heavy QGIS Application.

We mainly tested in for the `PyCharm <https://www.jetbrains.com/pycharm/>`_ IDE and it worked well on `PyDev <http://www.pydev.org/>`_ too.

Overview
--------


To setup your IDE for developing EnMAP-Box Applications, you need to:


    1. Clone the EnMAP-Box git repository and add it to your project sources

    2. Set the QGIS python as your project interpreter

    3. Ensure that your environmental settings are similar to that used by QGIS (:ref:`env_variables`)

    4. Ensure that all required python packages are accessible in your QGIS python and will be found
       by your IDE (:ref:`python_packages`):

        * gdal, numpy

        * scioy, scikit-learn

        * pyqtgraph

        * matplotlib

        * spy

        * gdal

    5. Start the EnMAP-Box from your IDE (:ref:`minimal_startup`)




.. _env_variables:

Python Interpreter
------------------

It is likely that your system has multiple python environments installed.
To find out which of them is used in your QGIS, open the QGIS Python shell and call::

    import sys
    print(sys.executable)

This Python should be the one used by your IDE. In PyCharm this can be done via ``Preferences > Project > Project Interpreter``.


Environmental Variables
-----------------------

To find out which environmental variables are used by your local QGIS, open the QGIS Python shell and call::

    import os
    for k in sorted(os.environ.keys()): print((k, os.environ[k]))


To our best knowledge at least the following need to be set:

    * ``PATH`` point to all the directories where QGIS and other Frameworks find its executables and libraries.

    * ``GDAL_DATA`` points to the directory where GDAL stores coordinate system definitions,
      e.g. the ``gcs.csv``, ``pcs.cvs`` and ``epsg.wkt``

    * ``QGIS_PLUGINPATH`` points to directories in which QGIS will searches for QGIS Plugins


.. _python_packages:

Python Packages
---------------


During startup QGIS loads some standard locations into the ``PYTHONPATH`` to make python packages available,
e.g. the PyQt and PyQGIS APIs.To find out which are required by the core QIS, open the QGIS Python shell an call::

    import sys
    for p in sorted(sys.path): print(p)

To ensure that your IDE provides syntax support for other package, you might need to add some more source paths to your
IDE project, for example:


    * the QGIS Python site-package folder, e.g. ``<OSGeo4W>\apps\Python27\lib\site-packages``


    * the QGIS internal python plugin folder, e.g. ``<OSGeo4W>/apps/qgis/./python/plugins``, to inspect the QGIS Processing Plugin code


    * the QGIS user plugin folder, e.g. ``<HOME>\.qgis2\python\plugins``





.. _minimal_startup:

EnMAP-Box Start Script
----------------------

If your IDE is set up correctly, you should be able to start the EnMAP-Box using this Python script::


    if __name__ == '__main__':

        from enmapbox.gui.utils import initQgisApplication
        from enmapbox.gui.enmapboxgui import EnMAPBox

        qgsApp = initQgisApplication()
        enmapBox = EnMAPBox(None)
        enmapBox.openExampleData(mapWindows=1)

        qgsApp.exec_()
        qgsApp.quit()


Platform specific hints
-----------------------


Windows (OSGeo4W)
.................

QGIS for windows is maintained by the OSGeo4W package installer. The ``qgis.exe`` is located in a folder system
like ``<OSGeo4WRoot>/bin``. An easy way to ensure that your IDE operates under the same environment as QGIS does, is to use the following startup script in a
batch file ``.bat`` file::

    ::OSGeo4W installation
    set OSGEO4W_ROOT=D:\\Programs\OSGeo4W

    ::PyCharm executable
    set IDE="C:\Program Files (x86)\JetBrains\PyCharm 2016.3\bin\pycharm.exe"

    ::ensure a clean python path to use modules from OSGeo4W python only
    set PYTHONPATH=

    ::set defaults, clean path, load OSGeo4W modules (incrementally)
    CALL %OSGEO4W_ROOT%\bin\o4w_env.bat

    ::lines taken from python-qgis.bat
    set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis
    set PATH=%QGIS_PREFIX_PATH%\bin;%PATH%

    ::append git and git-lfs to PATH
    set PATH=%PATH%;C:\Program Files\Git\bin
    set PATH=%PATH%;C:\Program Files\Git LFS

    :: GDAL Configuration (https://trac.osgeo.org/gdal/wiki/ConfigOptions)
    :: Set VSI cache to be used as buffer, see #6448 and
    set GDAL_FILENAME_IS_UTF8=YES
    set VSI_CACHE=TRUE
    set VSI_CACHE_SIZE=1000000
    set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt4\plugins
    set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python;%PYTHONPATH%

    start "IDE aware of QGIS" /B %'IDE% %*


Please note that the line ``CALL %OSGEO4W_ROOT%\bin\o4w_env.bat``` is responsible for an incremental call of other batch files which setup
the new environment. After this you might specify others variables, like we do here by expanding ``PATH`` by locations of ``git.exe`` and ``git-lfs.exe``.

If you plan to develop your own GUI based on Qt, you might install the related packages in the OSGeo4W installer
(see :ref:`install_qgis_windows`):

    * Qt4: pyqt4m qt4.devel, qt4.doc qt4-libs (Libs, includes the QDesigner)
    * pyqt4



macOS (standard installation)
.............................

The QGIS.app for macOS can be downloaded from `<http://www.kyngchaos.com/software/qgis>`_. It is installed to
``/Applications`` and linked against the standard macOS python.

    * Python Interpreter ``/usr/bin/python`` (Standard macOS python)

    * Content Root ``/Applications/QGIS.app/Contents/MacOS/../Resources/python``

    * Content Root ``/Applications/QGIS.app/Contents/Resources/python/plugins`` to access python code of QGIS default plugins, in particular the
      `QGIS Processing Framework <https://docs.qgis.org/2.18/en/docs/user_manual/processing/index.html>`_

    * Content Root ``~/.qgis2/python/plugins``, if you like to access python plugins installed from the
      `QGIS Python Plugins Repository <https://plugins.qgis.org/plugins/>`_.



macOS (OSGeo4Mac)
.................

The `Homebrew <https://brew.sh/>`_ package installer can be used to download and install QGIS as well. Please see
`OSGeo4Mac QGIS <https://github.com/OSGeo/homebrew-osgeo4mac>`_ for details.

In this case the locations of required packages might vary. Start the OSGeo4Mac QGIS, open the Python shell and check
the package locations as used by QGIS::

    import os
    import <package>
    print(os.path.dirname(<package>.__file__))

e.g. for scipy ::

    import os
    import scipy
    print(os.path.dirname(scipy.__file__))

Add the returned directories  or its parent site-package folders to as contet root to your IDE project e.g:

    * ``/usr/local/opt/qgis2/libexec/python2.7/site-packages``

    * ``/usr/local/lib/qt-4/python2.7/site-packages``

    * ``/usr/local/lib/python2.7/site-packages``



Linux (Ubuntu)
..............

    * tbd.

    *

