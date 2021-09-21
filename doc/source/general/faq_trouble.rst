.. include:: /icon_links.rst
.. include:: /dev_section/external_links.rst

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


**Newsletter**: Subscribe to the EnMAP mailing list to be informed about new EnMAP-Box releases and other EnMAP related news at https://www.enmap.org/contact/


FAQ
===

This is a list of Frequently Asked Questions about the EnMAP-Box. Feel free to
suggest new entries!

.. How do I...
.. -----------

.. _faq_how_to_cite_enmapbox:

* **How to cite the EnMAP-Box?**

  Please cite the EnMAP-Box as::

      EnMAP-Box Developers (2019): EnMAP-Box 3 - A QGIS Plugin to process and visualize
      hyperspectral remote sensing data. https://enmap-box.readthedocs.io

  BibTeX:

  .. code-block:: bibtex

     @misc{enmapbox2019,
     author = {EnMAP-Box Developers},
     title = {EnMAP-Box 3 - A QGIS Plugin to process and visualize hyperspectral remote sensing data},
     year = 2019,
     url = {https://enmap-box.readthedocs.io}
     }

  For the general idea behind the EnMAP-Box please refer to:

  .. code-block:: none

     van der Linden, S., Rabe, A., Held, M., Jakimow, B., Leitão, P., Okujeni, A., Schwieder, M.,
     Suess, S., Hostert, P., 2015. The EnMAP-Box—A Toolbox and Application Programming Interface
     for EnMAP Data Processing. Remote Sensing 7,
     11249–11266. 10.3390/rs70911249.

* **How to install QGIS without administrative rights?**

    Yes, it is possible to install and run QGIS (and the EnMAP-Box) without admin rights.
    You just need to download and install `Conda`_, where you can install QGIS as described
    :ref:`here <dev_installation_create_conda_qgis>`.


* **Spectral Library: Axis visualisation bugs (pyqtgraph)**

   If you experience visualisation bugs in the Spectral Library Window, this might be related to (windows) resolution
   scaling factor. Try setting the scaling to 100% (see corresponding `Issue #603 <https://bitbucket.org/hu-geomatics/enmap-box/issues/603/darstellung-y-achse-bei-spektrum-plot>`_ for more information)

.. _faq_numba:

* **Installation: error ensomap / numba / TypeError jitdebug**

    EnSoMAP requires `Numba`_, a JIT compiler that translates python code into fast machine code.
    Unfortunately, Numba is not part of a standard QGIS installation. Installing it afterwards can be tricky,
    in particular on the standard Windows and macOS QGIS installations.

    If you want to use EnSoMAP and numba, we therefore recommend to use a QGIS that was installed with `Conda`_ instead.

    1.  Install conda and create a conda environment with QGIS
        :ref:`as described here<dev_installation_create_conda_qgis>`.

    2.  Install Numba

        .. code-block:: batch

            (qgis_stable) $>conda install numba --channel=conda-forge

    3.  Start the conda QGIS by:

        .. code-block:: batch

            (qgis_stable) $>qgis

    4.  If not already done, install the EnMAP-Box to your Conda-QGIS with the QGIS Plugin Manager.


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

     <div><video width="90%" controls muted><source src="../_static/videos/osgeo_install_short.webm" type="video/webm">Your browser does not support HTML5 video.</video>
     <p><i>Demonstration of package selection in the Setup</i></p></div>

  Click :guilabel:`Finish` when the installation is done.

....


.. _faq_requirements:

* **Python package installation with requirements.txt does not work**

  Usually, all dependencies can be installed with one line:

     .. code-block:: batch

        python3 -m pip install -r https://bitbucket.org/hu-geomatics/enmap-box/raw/develop/requirements.txt

  If the method above did not work for some reason, try installing the packages listed in the :file:`requirements.txt` line by line, e.g.
  ``python3 -m pip install numpy`` and so on.

  .. literalinclude:: /../../requirements.txt
     :caption: requirements.txt



....


* **Image Cube tool missing qtopengl / Missing OpenGL / QtOpenGL packages**

    On some systems we experiences problems related to a missing OpenGL support (e.g `Issue #299 <https://bitbucket.org/hu-geomatics/enmap-box/issues/299/image-cube-qt-issues-on-linux>`_)

    1. Ensure that you have installed OpenGL drivers that support your graphic card
    2. Ensure that `PyOpenGL <http://pyopengl.sourceforge.net>`_  is installed::

        $ python3 -m pip install PyOpenGL

    On Linux, it might be necessary to install the Python bindings for QtOpenGL in order to start the Image Cube tool.

      .. code-block:: bash

         sudo apt-get install python3-pyqt5.qtopengl


* **Error loading the plugin**

  In case of missing requirements you should see an error message like this

  .. image:: ../img/missing_package_warning.png

  In that case please make sure you :ref:`installed all missing packages <install-python-packages>`,
  in this example ``pyqtgraph`` and ``sklearn`` are missing.

....


* **Installation of Astropy fails**



  In case you experience problems with installing **astropy**, you might also try the following:

  * Go to  https://www.lfd.uci.edu/~gohlke/pythonlibs/#astropy and look for the .whl files. Download the newest version
    which fits your windows and python setup, e.g. *astropy‑3.0.5‑cp37‑cp37m‑win_amd64.whl* for Python 3.7 (*cp37*) on a 64 bit windows (*win_amd64)*.
  * Install the downloaded file using pip (**change path accordingly!**):

    .. code-block:: batch

       python3 -m pip install C:\Downloads\astropy-3.0.5-cp37-cp37m-win_amd64.whl

  In some cases using an older version also does the trick, using pip you can install older versions using the ``==versionnumber`` synthax. ``--force-reinstall``
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

