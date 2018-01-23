.. _faq:

EnMAP-Box FAQ
=============

This is a list of Frequently Asked Questions about the EnMAP-Box. Feel free to
suggest new entries!

How do I...
-----------

... remove the error **Wrong value for parameter MSYS**?

    This error sometimes occurs when activating the EnMAP-Box AlgorithmProvider in Windows.

    Please install the *msys (command line utilities)* package with the OSGeo4W package installer.

... install QGIS on Windows without having administrative rights?

    * Download the QGIS installer from `<https://www.qgis.org/en/site/forusers/download.html>`_, e.g. `QGIS-OSGeo4W-2.18.16-1-Setup-x86_64.exe`

    * open a windows shell (`cmd.exe`) and navigate to the download folder

    * call ``set __COMPAT_LAYER=RUNASINVOKER``

    * now start the installer

... update QGIS on Windows without having administrative rights?

