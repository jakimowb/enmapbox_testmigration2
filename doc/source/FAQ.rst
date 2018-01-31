.. _faq:

EnMAP-Box FAQ
=============

This is a list of Frequently Asked Questions about the EnMAP-Box. Feel free to
suggest new entries!

How do I...
-----------

... **install QGIS on Windows without having administrative rights**?

    * yes, it is possible to install and run QGIS withouht any admin rights on windows.
      Read :ref:`install_qgis_windows` for more details on this.


How can I solve the following error...
--------------------------------------

... **Wrong value for parameter MSYS**

    This error sometimes occurs when activating the EnMAP-Box AlgorithmProvider in Windows.

    Please install the *msys (command line utilities)* package with the OSGeo4W package installer.

... **This plugin is broken: 'module' object has not attribute 'GRIORA_NearestNeighbor'**

    Your GDAL version seems to be outdated. update it to a version > 2.0