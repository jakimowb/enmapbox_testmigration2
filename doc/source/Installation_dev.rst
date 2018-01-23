Installation for Developers
===========================

Background
----------

The EnMAP-Box 3 is a QGIS plugin and therefore uses the Python distribution that is delivered with or linked into QGIS.
If you like to use an Integrated Development Environment (IDE) to develop and debug python applications for the EnMAP-Box,
or in general QGIS, we recommend that your IDE runs under the same environmental settings as your QGIS does.

The following sections describe - to our experience - which settings are required to run and debug the EnMAP-Box from
inside the `PyCharm <https://www.jetbrains.com/pycharm/>`_ IDE *without starting the heavy QGIS Application*.
Not tested yet, we assume that similar settings are required for other IDEs, e.g. `PyDev <http://www.pydev.org/>`_, as well.

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
e.g. the PyQt and PyQGIS APIs.To find out which are required by the core QIS, open the QGIS Python shell an call:

    import sys
    for p in sorted(sys.path): print(p)

To ensure that your IDE's Syntax help / Intellisense can find it, you should add the most important paths
as source paths to your IDE project, for example:


    * the QGIS Python site-package folder, e.g.


    * the QGIS internal python plugin folder, e.g. to access the QGIS Processing Plugin code


    * the QGIS PyQt4 packages




Example Windows (OSGeo4W)
-------------------------

QGIS for windows is installed by the OSGeo4W package installer. This means that the qgis.exe is located in a folder system
``<OSGeo4WRoot>/bin``, with <OSGeo4WRoot> being a directory like ...``QGIS


The easiest way to ensure that your IDE operates under the same environment as QGIS is to use the same
startup script in ``.bat`` files::



    tbd.


Settings for the IDE are than:

    * Python Interpreter

    * Content Root ``tbd.``

    * Content Root ``tbd.``





Examples for macOS (standard installation)
------------------------------------------

The QGIS.app for macOS can be downloaded from `<http://www.kyngchaos.com/software/qgis>`_. It is installed to
``/Applications`` and linked against the standard macOS python.

    * Python Interpreter ``/usr/bin/python`` (Standard macOS python)

    * Content Root ``/Applications/QGIS.app/Contents/MacOS/../Resources/python``

    * Content Root ``/Applications/QGIS.app/Contents/Resources/python/plugins``, if you like to access QGIS default Plugins
      like the QGIS Processing Framwork.

    * Content Root ``~/.qgis2/python/plugins``, if you like to access python plugins installed from the
      `QGIS Python Plugins Repository <https://plugins.qgis.org/plugins/>`_.



Examples for macOS (OSGeo4Mac)
------------------------------

The `Homebrew <https://brew.sh/>`_ package installer can be used to download and install QGIS too, as described in
`OSGeo4Mac QGIS <https://github.com/OSGeo/homebrew-osgeo4mac>`_ . In this case the locations of required packages might vary.
Start the OSGeo4Mac QGIS, open the Python shell and step for step, check the locations of required packages and add
them to your IDE as content root.

    * Python Interpreter

    * Python Path:
        ``export PYTHONPATH=/usr/local/opt/qgis2/libexec/python2.7/site-packages:/usr/local/lib/qt-4/python2.7/site-packages:/usr/local/lib/python2.7/site-packages:$PYTHONPATH``

    * tbd.


Examples for Linux (Ubuntu)
----------------------------

    * tbd.

    *


.. _minimal_startup:

EnMAP-Box Start Script
----------------------

If your IDE is set up correctly, you should be to start it with the following script::


    if __name__ == '__main__':

        from enmapbox.gui.utils import initQgisApplication
        from enmapbox.gui.enmapboxgui import EnMAPBox

        qgsApp = initQgisApplication()
        enmapBox = EnMAPBox(None)
        enmapBox.openExampleData(mapWindows=1)

        qgsApp.exec_()
        qgsApp.quit()

