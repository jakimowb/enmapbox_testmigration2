
Installation
============


.. todo:: Structure by OS first (Windows, Linux, Mac)


.. _install_enmapbox:

Install or update the EnMAP-Box
-----------------------------------

The EnMAP-Box 3 is a plugin for the free and open source Geographic Information System `QGIS <https://www.qgis.org>`_ (see :ref:`install_qgis`)
that can be downloaded `here <https://www.qgis.org/en/site/forusers/download.html>`_.

Installing or updating the EnMAP-Box itself is simple:

    #. Download the latest EnMAP-Box from `<https://bitbucket.org/hu-geomatics/enmap-box/downloads/>`_, extract the **enmapboxplugin** folder and put it into the local QGIS Plugin folder.
       For example, let *enmapboxplugin.20180116T1825.zip* be the most recent plugin zip, than do on:

       **Windows**

            Copy the unzipped folder to ``<HOME>.qgis2\python\plugins``, e.g.
            ``C:\Users\ivan_ivanovich\.qgis2\python\plugins\enmapboxplugin``

       **Linux**

            cd ~/.qgis2/python/plugins/
            wget https://bitbucket.org/hu-geomatics/enmap-box/downloads/enmapboxplugin.20180116T1825.zip
            rm enmapboxplugin.20180116T1825.zip

       **macOS (Terminal)**

            cd ~/.qgis2/python/plugins/
            curl https://bitbucket.org/hu-geomatics/enmap-box/downloads/enmapboxplugin.20180116T1825.zip
            rm enmapboxplugin.20180116T1825.zip

    #. Restart QGIS  and activate the EnMAP-Box Plugin via :menuselection:`Plugins --> Manage and Install Plugins...`

        .. image:: img/install_activate_plugin.png

We plan to publish the EnMAP-Box in the QGIS Plugin Repository, which will replace steps 2 and 3 by "two mouse-clicks".

.. note::
       Before you can start the EnMAP-Box the very first time, it is likely required to install additional python packages
       which are not part of a standard QGIS installation.

       Please read:

        * :ref:`install_missing_packages` to get help on package installation.

        * :ref:`install_qgis` for a general plattform specific hints how to install QGIS.



.. _install_missing_packages:

Install missing packages
------------------------

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



To install the required packages please consider the following platform-specific advices:


Windows
.......


#. Close QGIS, if it has been opened. Navigate into the QGIS root folder and call the ``OSGeo4W.bat`` with administative rights to open the OSGeo4W CLI.

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


         .. image:: img/install_osgeo4w_setuptools2.png

       *  Start the installation

       * Note: You can install these packages directly from the OSGeo4W shell by calling the following lines step-by-step::

               set __COMPAT_LAYER=RUNASINVOKER

               setup -k -D -q -P setuptools
               setup -k -D -q -P python-setuptools
               setup -k -D -q -P python-numpy
               setup -k -D -q -P python-scipy
               setup -k -D -q -P python-pip
               setup -k -D -q -P matplotlib

#. Now install the remaining requirements with pip. For this either (a) navigate into the ``enmapbox`` plugin folder and call::

       cd C:\Users\ivan_ivanowitch\.qgis2\python\plugins\enmapboxplugin
       python -m pip install -r requirements.txt

   or (b) install required package directly. This might be necessary for pacakges not mentioned in the ``requirements.txt``::

       python -m pip install pyqtgraph
       python -m pip install sklearn
       python -m pip install rios
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





macOS
.......


#. Open your QGIS Python shell and type::

    import sys
    print(sys.executable)

   to know the exact path of your QGIS python executable.

#. Open the Terminal / the bash shell of your macOS and navigate into the EnMAP-Box Plugin folder::

    cd C:\Users\ivan_ivanowitch\.qgis2\python\plugins\enmapboxplugin

#. Install the required packages, either via (a)::

    python -m pip install -r requirements.txt

   or step by step, e.g. if the requirements.txt is incomplete::

    python -m pip install pyqtgraph
    python -m pip install sklearn
    python -m pip install spectral


Linux
.....

The following way was tested successfully on Ubuntu.

#. Navigate into the EnMAP-Box Plugin folder

#. Install the missing packages using pip. Either call::

    python -m pip install -r requirements.txt


   Or install the missing packages step-by-step::

    python -m pip install scipy
    python -m pip install matplotlib
    python -m pip install sklearn
    python -m pip install pyqtgraph
    python -m pip install spectral


.. _install_qgis:

Install QGIS
------------

Instructions to download and install QGIS can be found on `<http://www.qgis.org/en/site/forusers/download.html>`_.

.. _install_qgis_windows:

Windows
.......


It is possible to install QGIS without administration rights:

#. Download the OSGeo4W Network Installer from `<http://www.qgis.org/en/site/forusers/alldownloads.html>`_
#. Open the windows cmd shell, navigate into the download folder and call ``set __COMPAT_LAYER=RUNASINVOKER``
#. Start the OSGeo4W Installer ``osgeo4w-setup-x86_64.exe``

    #. Advanced Install >>next>>
    #. Download Source: Install from Internet >>next>>
    #. Root Install Directory: Specify a root folder *you have write access to*. We will call this folder herafter ``OSGEO4W_ROOT`` >>next>>
    #. Local Package Directory: Default or specify >>next>>
    #. Internet Connection Default or specify >>next>>
    #. Download Site >>next>>

#. Now use the search filter to select following packages:

    * setup
    * qgis
    * msys
    * gdal and gdal-python
    * setuptools, python-six
    * matplotlib, scipy, numpy, python-pip

    .. image:: img/install_osgeo4w_setuptools2.png

#. If done, press >>next>> to start the installation into the root folder ``OSGEO4W_ROOT``. The installation should look like::

       <OSGEO4W_ROOT>
              \apps
              \bins     <-- contains setup.bat, qgis.exe and many more
              \etc
              \include
              \share
              \lib
              \var
              msvcp110.dll
              msvcr110.dll
              OSGeo4W.bat
              OSGeo4W.ico



To add, update or remove packages in this OSGEO4W installation, open the OSGeo4W shell in ``<OSGEO4W_ROOT>/OSGeo4W.bat`` and call::

    set __COMPAT_LAYER=RUNASINVOKER
    setup -A -R

to open the Installation dialog agains.


macOS
.....

MacOS users might consider to use the `Homebrew Package Manager <https://brew.sh>`_
for installing QGIS from the `OSGeo4Mac Project <https://github.com/OSGeo/homebrew-osgeo4mac>`_.


Linux
.....

Try to install missing packages with ``apt-get install <package name>`` first. If unavailable, use ``python -m pip install <package name>``

