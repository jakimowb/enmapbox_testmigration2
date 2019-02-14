
.. _usr_installation:

Installation
============

.. |download_link| raw:: html

   <a href="https://bitbucket.org/hu-geomatics/enmap-box/downloads/" target="_blank">HERE</a>

.. |download_link2| raw:: html

   <a href="https://bitbucket.org/hu-geomatics/enmap-box/downloads/" target="_blank">https://bitbucket.org/hu-geomatics/enmap-box/downloads/</a>

.. |developer_qgis_plugin_repo| raw:: html

    <a href="https://bytebucket.org/hu-geomatics/enmap-box/wiki/qgis_plugin_develop.xml" target="_blank">https://bytebucket.org/hu-geomatics/enmap-box/wiki/qgis_plugin_develop.xml</a>


.. |icon| image:: ../img/icon.png
   :width: 30px
   :height: 30px


.. |osgeoicon| image:: ../img/OSGeo4W.ico
   :width: 30px
   :height: 30px

.. |osgeoinstaller| image:: ../img/osgeoinstaller.png






The **EnMAP-Box** is a plugin for **QGIS** and requires additional **python packages** that need to be installed independent from QGIS.


..       * :ref:`Windows <install-packages-windows>`
..       * :ref:`Linux <install-packages-linux>`
..       * :ref:`Mac <install-packages-mac>`

.. image:: ../img/install.png

....

|


1. Install QGIS
---------------


Install QGIS version 3.4.4 or higher to run the EnMAP-Box. You can `get QGIS here <https://www.qgis.org/en/site/forusers/download.html>`_.
Additional information on the installation process is provided in the `QGIS Documentation <https://www.qgis.org/en/site/forusers/alldownloads.html>`_.

In case you already have QGIS installed, you can skip this step.


....

|

.. _install-python-packages:

2. Install required python packages
-----------------------------------

The EnMAP-Box requires the following python packages:

* `numpy <http://www.numpy.org/>`_
* `scipy <https://www.scipy.org>`_
* `scikit-learn <http://scikit-learn.org/stable/index.html>`_
* `pyqtgraph <http://pyqtgraph.org/>`_
* `matplotlib <https://matplotlib.org/>`_

* `astropy <http://docs.astropy.org>`_ (**optional**, relevant e.g. for certain filtering algorithms)

Follow the platform specific installation instructions below in order to install these packages.


.. _install-packages-windows:

Windows
~~~~~~~


1. Close QGIS, if it is open.

2. Start the OSGeo4W Shell |osgeoicon| with admin rights.

   * :menuselection:`Start Menu --> QGIS 3.xx --> OSGeo4W Shell --> Right-Click --> Run as administrator`

     .. image:: ../img/open_osgeoshell.png
        :width: 500px


     .. hint::

        If you used the OSGeo4W Installer to install QGIS, the OSGeo4W Shell will be listed under *OSGeo4W* in the Start Menu

3. Activate the Python 3 environment by entering:

   .. code-block:: batch

      call py3_env.bat

   .. image:: ../img/shell_callpy3env.png

|
4. Install required python packages by entering:

   .. code-block:: batch

      python3 -m pip install -r https://bitbucket.org/hu-geomatics/enmap-box/raw/develop/requirements.txt

   Now all packages will be installed automatically. After completion, the shell should show something like this:

   .. image:: ../img/shell_install_output.png


   |

   .. error::

      In case you run into problems because pip is not available in your python environment
      (error message ``C:/.../python3.exe: No module named pip`` or similar), follow these steps:

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

      |
      Then use the textbox to filter, select and install the following packages (see video below for help):

      * python3-pip
      * python3-setuptools

      |
      Click on the |osgeoinstaller| symbol once, which should usually change the *Skip* setting to installing the most recent
      version. Only **AFTER** having selected both packages, click :guilabel:`Next`.

       .. raw:: html

          <div><video width="90%" controls muted><source src="../_static/osgeo_install_short.webm" type="video/webm">Your browser does not support HTML5 video.</video>
          <p><i>Demonstration of package selection in the Setup</i></p></div>

      Click :guilabel:`Finish` when the installation is done. **Now repeat the steps 2.- 4. again**.




5. Optionally, also install astropy using pip in the OSGeo4W Shell:


   .. code-block:: batch

      python3 -m pip install astropy


   .. error::

      In case you experience problems with installing **astropy**, you might also try the following:

      * Go to  https://www.lfd.uci.edu/~gohlke/pythonlibs/#astropy and look for the .whl files. Download the newest version
        which fits your windows and python setup, e.g. *astropy‑3.0.5‑cp37‑cp37m‑win_amd64.whl* for Python 3.7 (*cp37*) on a 64 bit windows (*win_amd64)*.
      * Install the downloaded file using pip (**change path accordingly!**):

     .. code-block:: batch

        python3 -m pip install C:\Downloads\astropy-3.0.5-cp37-cp37m-win_amd64.whl

.. _install-packages-linux:

|

Linux
~~~~~

.. note:: Tested on Ubuntu 18.10

#. Open the terminal and install all missing packages using pip:

    .. code-block:: bash

        python3 -m pip install numpy
        python3 -m pip install scipy
        python3 -m pip install scikit-learn
        python3 -m pip install https://bitbucket.org/hu-geomatics/enmap-box/downloads/pyqtgraph-0.11.0.dev0.zip
        python3 -m pip install matplotlib

   *and optionally*:

    .. code-block:: batch

        python3 -m pip install astropy


.. _install-packages-mac:

|

Mac
~~~

#. Open the terminal and install all missing packages using pip:

    .. code-block:: bash

        python3 -m pip install numpy
        python3 -m pip install scipy
        python3 -m pip install scikit-learn
        python3 -m pip install https://bitbucket.org/hu-geomatics/enmap-box/downloads/pyqtgraph-0.11.0.dev0.zip
        python3 -m pip install matplotlib

    *and optionally*:

    .. code-block:: batch

        python3 -m pip install astropy



....


.. _usr_installation_enmapbox:

3. Install or update the EnMAP-Box
----------------------------------


Install from Repository (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Open QGIS and open *Plugins > Manage and Install Plugins > Settings*
#. Add  https://bitbucket.org/hu-geomatics/enmap-box/raw/develop/qgis_plugin_develop.xml as additional plugin repository
   (scroll down and click on :guilabel:`Add...`)

   .. image:: ../img/add_repo.png
      :width: 75%

#. Click :guilabel:`Reload all repositories` to get aware of the latest EnMAP-Box updates
#. Now the EnMAP-Box should be listed in the plugin list: Go to the ``All`` tab and search for "enmap":

   .. figure:: ../img/pluginmanager_all.PNG

   Select it and click :guilabel:`Install plugin` (or :guilabel:`Upgrade plugin` in case you update to a new version)
#. Start the EnMAP-Box via the |icon| icon or from the menubar *Raster* > *EnMAP-Box*




Install from ZIP (alternative)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Download the latest EnMAP-Box from |download_link2|.
#. It is recommended to uninstall previous EnMAP-Box versions (delete folder manually, or in QGIS via *Plugins* > *Manage and Install Plugins*
   > *Installed* > *EnMAP-Box 3* > *Uninstall plugin*)
#. Open *Plugins* > *Manage and Install Plugins* > *Install from ZIP*.
#. Under ``ZIP file`` click :guilabel:`...` and select the downloaded
   *enmapboxplugin.3.x.YYYYMMDDTHHMM.QGIS3.zip* and click :guilabel:`Install plugin`.
#. Start the EnMAP-Box via the |icon| icon or from the menubar *Raster* > *EnMAP-Box*.


|

