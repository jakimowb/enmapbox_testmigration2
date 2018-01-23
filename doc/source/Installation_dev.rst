Installation for Developers
===========================

Background
----------

The EnMAP-Box 3 is a QGIS plugin and therefore uses the Python distribution that is delivered with or linked into QGIS.
If you like to use an Integrated Development Environment (IDE) to develop and debug python applications for the EnMAP-Box,
or in general QGIS, we recommend that your IDE runs under the same environmental settings as your QGIS does.

The following sections describe how to do so in case of the IDE PyCharm, but generally apply for other IDEs like PyDev as well.

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



.. _env_variables:

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

To ensure that your IDE's Syntax help / Intellisense can finde it, you should add the most important paths
as source paths to your IDE project, for example:


    * the QGIS Python site-package folder, e.g.


    * the QGIS internal python plugin folder, e.g. to access the QGIS Processing Plugin code


    * the QGIS PyQt4 packages


Example Windows (OSGeo4W)
-------------------------

    *

    *

    *


Examples for macOS (standard installation)
------------------------------------------

 from `http://www.kyngchaos.com/software/qgis`_):

    * ``/usr/local/opt/python/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages``

    * ``/usr/local/opt/qgis2/libexec/python2.7/site-packages``

    * ``/usr/local/Cellar/qgis2/2.18.11_1/QGIS.app/Contents/MacOS/../Resources/python/plugins/processing``

    * ``/Users/benjamin.jakimow/.qgis2//python``


Examples for macOS
------------------

(homebrew cask installation `https://github.com/OSGeo/homebrew-osgeo4mac`_):

    * ``/usr/local/opt/python/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages``

    * ``/usr/local/opt/qgis2/libexec/python2.7/site-packages``

    * ``/usr/local/Cellar/qgis2/2.18.11_1/QGIS.app/Contents/MacOS/../Resources/python/plugins/processing``

    * ``/Users/benjamin.jakimow/.qgis2//python``


Examples for Linux (Ubuntu)
----------------------------

    *

    *


