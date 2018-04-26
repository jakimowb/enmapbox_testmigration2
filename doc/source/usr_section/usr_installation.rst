
Installation
============


.. note:: * The EnMAP-Box plugin requires QGIS Version 2.18.xx or higher
          * You can get QGIS `here <https://www.qgis.org/en/site/forusers/download.html>`_

.. important:: :ref:`Additional python packages <Package requirements>` are needed and some of them are not delivered with the standard QGIS python environment,
               hence they have to be installed. Follow platform-specific advices below.





Package requirements
-------------------------------

The following python packages need to be available in the QGIS python to run the EnMAP-Box:

=============================================================== ========= ============ =================
Package                                                         Notes     Windows      Linux
                                                                          (OSGeo4W)    (apt-get)
=============================================================== ========= ============ =================
`qgis <http://www.gdal.org>`_                                   default   qgis
`PyQt4 <http://www.gdal.org>`_                                  default   PyQt4
`gdal <http://www.gdal.org>`_                                   default   gdal
`numpy <http://www.numpy.org>`_                                 OS        python-numpy python-numpy
`scipy <https://www.scipy.org>`_                                OS        python-scipy python-scipy
`setuptools <https://pypi.python.org/pypi/setuptools>`_         OS        setuptools   python-setuptools
`pip <https://pypi.python.org/pypi/pip>`_                       OS        python-pip   python-pip
`matplotlib <https://matplotlib.org/>`_                         OS
`pyqtgraph <https://pypi.python.org/pypi/pip>`_                 pip                    python-pyqtgraph
`scikit-learn <https://pypi.python.org/pypi/pip>`_              pip                    python-sklearn
`spectral <http://www.spectralpython.net/installation.html>`_   pip

=============================================================== ========= ============ =================

    * *OSGeo4W* = package name to be installed using the OSGeo4W installer for QGIS on windows systems.
    * *Linux* = package name to be installed using apt-get on Linux (tested on Ubuntu).
    * *default* = usually already installed with QGIS
    * *OS* = usually requires a platform-specific installation
    * *pip* = can be installed with `pip <https://pip.pypa.io>`_
      (the `preferred installer <https://packaging.python.org/guides/tool-recommendations/>`_ to install python packages).



To install the required packages please consider the following platform-specific advices below.


.. _install_enmapbox:

Install or update the EnMAP-Box
-------------------------------

Windows
~~~~~~~

.. note:: On windows we recommend to install QGIS via the OSGeo4W Network Installer!

**Install required packages:**

#. Close QGIS, if it has been opened. Navigate into the QGIS root folder and call the ``OSGeo4W.bat`` with administrative rights to open the OSGeo4W CLI.

#. Install the package requirements maintained by OSGeo4W.

       * Open the OSGeo4W installer by calling ``setup`` and go through the menu:

              * Advanced Installation

              * Installation from Internet

              * default OSGeo4W root directory

              * local temp directory

              * direct connection

              * Downloadsite: ``http://download.osgeo.ogr``

       * Now use the textbox to filter and select the following packages::

              python-setuptools
              python-numpy
              python-pip
              python-scipy
              matplotlib


         .. image:: ../img/install_osgeo4w_setuptools2.png

       *  Start the installation

        *Note: You can install these packages directly from the OSGeo4W Shell by calling the following lines step-by-step*::

               set __COMPAT_LAYER=RUNASINVOKER

               setup -k -D -q -P setuptools
               setup -k -D -q -P python-setuptools
               setup -k -D -q -P python-numpy
               setup -k -D -q -P python-scipy
               setup -k -D -q -P python-pip
               setup -k -D -q -P matplotlib

#. Now install the remaining requirements with **pip** from the **OSGeo4W Shell**. For this either **(a)** navigate into the ``enmapbox`` plugin folder and call::

       cd C:\Users\ivan_ivanowitch\.qgis2\python\plugins\enmapboxplugin
       python -m pip install -r requirements.txt

   or **(b)** install required package directly. This might be necessary for packages not mentioned in the ``requirements.txt``::

       python -m pip install pyqtgraph
       python -m pip install sklearn
       python -m pip install spectral

.. Comment startscript:
    set OSGEO4W_ROOT=<path to your OSGEO4W installation>\<OSGEO4W_ROOT>
    set __COMPAT_LAYER=RUNASINVOKER
    start "" %OSGEO4W_ROOT%\bin\osgeo4w-setup.exe -A -R %OSGEO4W_ROOT%

.. Comment installscript:
    set __COMPAT_LAYER=RUNASINVOKER
    osgeo4w-setup -k -D -q -P qgis pyqt4 setuptools python-numpy python-scipy python-test python-pip matplotlib
    osgeo4w-setup -k -q -P qgis pyqt4 setuptools python-numpy python-scipy python-test python-pip matplotlib
    osgeo4w-setup -k -q -P qgis python-pip



**Install the plugin**:

1. Download the latest EnMAP-Box from `<https://bitbucket.org/hu-geomatics/enmap-box/downloads/>`_
2. Extract the **enmapboxplugin** folder and put it into the local QGIS Plugin folder.
   For example, let *enmapboxplugin.20180116T1825.zip* be the most recent plugin zip, then copy the unzipped folder to ``<HOME>.qgis2\python\plugins``, e.g.
   ``C:\Users\ivan_ivanovich\.qgis2\python\plugins\enmapboxplugin``

3. Restart QGIS and activate the EnMAP-Box Plugin via **Plugins >> Manage and Install Plugins...**

   .. image:: ../img/install_activate_plugin.png

|
4. You can now start the EnMAP-Box via the |icon| icon


.. |icon| image:: ../img/icon.png
   :width: 30px
   :height: 30px


Linux
~~~~~

*The following way was tested successfully on Ubuntu*

#. You can download and install the EnMAP-Box directly from your shell. Open it an run the following lines::

    # Navigate to the QGIS Plugin directory (change "~" accordingly)
    cd ~/.qgis2/python/plugins/
    # Download and unzip the EnMAP-Box
    wget https://bitbucket.org/hu-geomatics/enmap-box/downloads/enmapboxplugin.20180116T1825.zip
    # Remove archive
    rm enmapboxplugin.20180116T1825.zip

#. Navigate into the EnMAP-Box Plugin folder

#. Install the missing packages using pip. Either call::

    python -m pip install -r requirements.txt


   or install the missing packages step-by-step::

    python -m pip install scipy
    python -m pip install matplotlib
    python -m pip install sklearn
    python -m pip install pyqtgraph
    python -m pip install spectral

#. Restart QGIS and activate the EnMAP-Box Plugin via **Plugins >> Manage and Install Plugins...**

#. You can now start the EnMAP-Box via the |icon| icon

Mac
~~~

#. You can download and install the EnMAP-Box directly from the Terminal. Open it an run the following lines::

    # Navigate to the QGIS Plugin directory (change "~" accordingly)
    cd ~/.qgis2/python/plugins/
    # Download and unzip the EnMAP-Box
    curl https://bitbucket.org/hu-geomatics/enmap-box/downloads/enmapboxplugin.20180116T1825.zip
    # Remove archive
    rm enmapboxplugin.20180116T1825.zip

|
#. Open your QGIS Python shell and type (to know the exact path of your QGIS python executable)::

    import sys
    print(sys.executable)

#. Open the Terminal / the bash shell of your macOS and navigate into the EnMAP-Box Plugin folder::

    cd C:\Users\ivan_ivanowitch\.qgis2\python\plugins\enmapboxplugin

#. Install the required packages, either via (a)::

    python -m pip install -r requirements.txt

   or step by step, e.g. if the requirements.txt is incomplete::

    python -m pip install scipy
    python -m pip install matplotlib
    python -m pip install sklearn
    python -m pip install pyqtgraph
    python -m pip install spectral

#. Restart QGIS and activate the EnMAP-Box Plugin via **Plugins >> Manage and Install Plugins...**

#. You can now start the EnMAP-Box via the |icon| icon