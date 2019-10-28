.. include:: /icon_links.rst

.. |osgeoicon| image:: ../img/OSGeo4W.ico
   :width: 30px
   :height: 30px

.. |osgeoinstaller| image:: ../img/osgeoinstaller.png


=====================
FAQ & Troubleshooting
=====================


Bug report & feedback
=====================

.. |link_bitbucket| raw:: html

   <a href="https://bitbucket.org/hu-geomatics/enmap-box/issues/new" target="_blank">Bitbucket Repository</a>


.. note:: Your feedback is more than welcome! In case you encounter any problems with the EnMAP-Box or have
          suggestions of any kind for improving it (or this documentation), please let us know!

          **Please report issues (bugs, suggestions etc.) via our** |link_bitbucket|.

Contact
=======

**E-Mail:** enmapbox@enmap.org


|
|

EnMAP-Box FAQ
=============

This is a list of Frequently Asked Questions about the EnMAP-Box. Feel free to
suggest new entries!

.. How do I...
.. -----------

.. ... **install QGIS on Windows without having administrative rights**?

..     yes, it is possible to install and run QGIS withouht any admin rights on windows.
..      Read :ref:`install_qgis_windows` for more details on this.



How can I solve the following error...
--------------------------------------

.. _faq_no_pip:

* **Installation: no module named pip**

  In case you run into problems during installation because pip is not available in your python environment
  (error message ``C:/.../python3.exe: No module named pip`` or similar), follow these steps (Windows):

  Start the OSGeo4W installer from the OSGeo4W Shell by calling

  .. code-block:: batch

     setup

  .. image:: ../img/shell_setup.png

  which will open the OSGeo4W Setup dialog.

  Now navigate through the first pages of the dialog, by selecting the following settings:

  * Advanced Installation :guilabel:`Next`
  * Installation from Internet :guilabel:`Next`
  * default OSGeo4W root directory :guilabel:`Next`
  * local temp directory :guilabel:`Next`
  * direct connection :guilabel:`Next`
  * Select downloadsite ``http://download.osgeo.ogr`` :guilabel:`Next`

  Then use the textbox to filter, select and install the following packages (see video below for help):

  * python3-pip
  * python3-setuptools


  Click on the |osgeoinstaller| symbol once, which should usually change the *Skip* setting to installing the most recent
  version. Only **AFTER** having selected both packages, click :guilabel:`Next`.

  .. raw:: html

     <div><video width="90%" controls muted><source src="../_static/osgeo_install_short.webm" type="video/webm">Your browser does not support HTML5 video.</video>
     <p><i>Demonstration of package selection in the Setup</i></p></div>

  Click :guilabel:`Finish` when the installation is done. **Now repeat the steps 2.- 4. again**.

....


.. _faq_requirements:

* **Python package installation with requirements.txt does not work**

  Usually, all dependencies can be installed with one line:

     .. code-block:: batch

        python3 -m pip install -r https://bitbucket.org/hu-geomatics/enmap-box/raw/develop/requirements.txt

  If the method above did not work for some reason, try installing the packages one by one:

      .. code-block:: bash

          python3 -m pip install numpy
          python3 -m pip install scipy
          python3 -m pip install scikit-learn
          python3 -m pip install matplotlib

     *and optionally*:

      .. code-block:: batch

          python3 -m pip install astropy

....


* **Linux: Image Cube tool missing qtopengl**

  It might be necessary to install the Python bindings for QtOpenGL in order to start the Image Cube tool.

  .. code-block:: bash

     sudo apt-get install python3-pyqt5.qtopengl


....

* **Error loading the plugin**

  In case of missing requirements you should see an error message like this

  .. image:: ../img/missing_package_warning.png

  In that case please make sure you :ref:`installed all missing packages <install-python-packages>`,
  in this example ``pyqtgraph`` and ``sklearn`` are missing.

....


* **Installation of Astropy fails**

  In some cases using an older version does the trick, using pip you can install older versions using the ``==versionnumber`` synthax. ``--force-reinstall``
  is used here to ensure clean installation.

  .. code-block:: batch

     python3 -m pip install astropy==3.0.3 --force-reinstall

....


* **Wrong value for parameter MSYS**

  This error sometimes occurs when activating the EnMAP-Box AlgorithmProvider in Windows. Please install
  the *msys (command line utilities)* package with the OSGeo4W package installer.

....


* **This plugin is broken: 'module' object has not attribute 'GRIORA_NearestNeighbor'**

  Your GDAL version seems to be outdated. update it to a version > 2.0

....

* **Exception: Unable to find full path for "dockpanel.ui". Make its directory known to UI_DIRECTORIES**

    It's likely that an update of the EnMAP-Box plugin failed to remove a previous version properly.
    The following workaround might help:

    1. Navigate into the active QGIS profile folder. It can be opened via Settings >  User Profiles > Open Active Profile Folder
    2. Close QGIS. This is necessary to avoid any file handles on files or folders of the EnMAP-Box plugin.
    3. Delete the EnMAP-Box plugin folder manually, e.g. `default/python/plugins/enmapboxplugin` if the active QGIS profile is 'default'.
    4. Restart QGIS and install the most-recent EnMAP-Box version

    This description was taken from https://bitbucket.org/hu-geomatics/enmap-box/issues/304/exception-unable-to-find-full-path-for