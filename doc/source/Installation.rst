Installation
============

.. _install_enmapbox:

Installing & Updating the EnMAP-Box
-----------------------------------

The EnMAP-Box 3 is a plugin for the free and open source Geographic Information System `QGIS <https://www.qgis.org>`_ (see :ref:`install_qgis`)
that can be downloaded `here <https://www.qgis.org/en/site/forusers/download.html>`_.

Installing or updating the EnMAP-Box itself is pretty easy:

    1. Download the latest EnMAP-Box from `<https://bitbucket.org/hu-geomatics/enmap-box/downloads/>`_

    2. Extract the downloaded zip file and put the folder ``enmapboxplugin`` into your
       local QGIS Plugin folder ``<HOME>.qgis2\python\plugins``,
       e.g. ``C:\Users\ivan_ivanovich\.qgis2\python\plugins``

    3. Activate the EnMAP-Box Plugin in QGIS via *Plugins >> Manage and Install Plugins...*


We plan to publish the EnMAP-Box in the QGIS Plugin Repository, which will replace steps 2 and 3 by "two mouse-clicks".

Note:
       Before you can start the EnMAP-Box the very first time, it is likely required to install some additional python packages
       that are not part of your QGIS. Please read install_qgis_ for plattform specific advice on this topic.


.. _install_qgis:

Installing QGIS
---------------

Instructions to download and install QGIS can be found on `<http://www.qgis.org/en/site/forusers/download.html>`_.

.. _install_qgis_windows:


Package                                                   Notes
========================================================= ============

`numpy <http://www.numpy.org>`_                           :ref:``
`scipy <https://www.scipy.org>`_
`gdal <http://www.gdal.org>`_
`setuptools <https://pypi.python.org/pypi/setuptools>`_
`pip <https://pypi.python.org/pypi/pip>`_
`scikit-learn <https://pypi.python.org/pypi/pip>`_
`pyqtgraph <https://pypi.python.org/pypi/pip>`_

.. pkh_ins_qgs

1. installed with QGIS by default

.. _pkg_ins_plt:

1. should be installed with a plattfor speci

.. _pkg_install_win:

1. to be installed via the OSGeo4W package installer

.. _pkg_install_pip:

2. to be installed via pip, e.g. calling `python -m pip install <package>`



Hints for Windows Users
.......................


It is possible to install QGIS without administration rights:

1. Download the OSGeo4W Network Installer from `<http://www.qgis.org/en/site/forusers/alldownloads.html>`_
2. Open the windows cmd shell, navigate into the download folder and call ``set __COMPAT_LAYER=RUNASINVOKER``
3. Start the OSGeo4W Installer ``osgeo4w-setup-x86_64.exe``

    1. Advanced Install >>next>>
    2. Download Source: Install from Internet >>next>>
    3. Root Install Directory: Specify a root folder *you have write access to* >>next>>
    4. Local Package Directory: Default or specify >>next>>
    5. Internet Connection Default or specify >>next>>
    6. Download Site >>next>>

4. now use the search filter to select following packages:

    * setup
    * qgis
    * msys
    * gdal and gdal-python
    * setuptools, python-six
    * matplotlib, scipy, numpy, python-pip


5. press >>next>> to start the installation into the root folder ``OSGEO4W_ROOT``. The installation should look like::

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



* after installation: to update, remove or re-install packages just call ``set __COMPAT_LAYER=RUNASINVOKER`` before
  starting ``<OSGEO4W_ROOT>\bin\setup.bat``. For regular updates this batch script might become practical (replace ``< >`` with your local file paths)::

       set OSGEO4W_ROOT=<path to your OSGEO4W installation>\<OSGEO4W_ROOT>
       set __COMPAT_LAYER=RUNASINVOKER
       start "" %OSGEO4W_ROOT%\bin\osgeo4w-setup.exe -A -R %OSGEO4W_ROOT%


* the QGIS.exe and other binaries can be found in ``OSGEO4W\bin``


We haven't tested this much in detail, but according to the `OSGeo4W CLI docs <https://trac.osgeo.org/osgeo4w/wiki/CommandLine>`_
packages can be installed directly from the command line as well::

       set __COMPAT_LAYER=RUNASINVOKER
       osgeo4w-setup -k -D -q -P qgis pyqt4 setuptools python-numpy python-scipy python-test python-pip matplotlib
       osgeo4w-setup -k -q -P qgis pyqt4 setuptools python-numpy python-scipy python-test python-pip matplotlib
       python -m pip install setuptools
       python -m pip install sklearn

Hints for macOS users
.....................

MacOS users might consider to use the `Homebrew Package Manager <https://brew.sh>`_
to install QGIS from the `OSGeo4Mac Project <https://github.com/OSGeo/homebrew-osgeo4mac>`_.


Hint for Linux (Ubuntu) users
.............................

tbd.

.. _install_missing_packages:

Install missing packages
------------------------

Missing packages will be highlighted in a dialog. Copy this information into a text editor that you can track missing things.

Now, try to install missing package using your OS-specific package manager first

If a package like ``sklearn`` is not available, use `pip` <https://pypi.python.org/pypi/pip>, either from::
    A. inside a python shell::

        import pip
        pip.main('install sklearn'.split())

       this might work also from inside the QGIS Python shell

    B. or your system shell by calling python::

        $python -m pip install sklearn


Repeat this for each missing package.



FAQ / Troubleshooting
---------------------

**I get the following Error dialog: Wrong value for parameter MSYS**

    Description:** the following error occurs when activating the EnMAP-Box AlgorithmProvider in windows

    ![Unbenannt.PNG](https://bitbucket.org/repo/7bo7M8/images/4131973787-Unbenannt.PNG)

    **Solution:** install the *msys (command line utilities)* package with the OSGeo4W package installer.



