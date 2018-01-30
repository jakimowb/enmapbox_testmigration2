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


.. _install_missing_packages:

Install missing packages
------------------------

The following package need to be available in your QGIS Python to run the EnMAP-Box:

=============================================================== ========================
Package                                                         Notes
=============================================================== ========================
`qgis <http://www.gdal.org>`_                                   :ref:`(1) <pkg_default>`
`PyQt4 <http://www.gdal.org>`_                                  :ref:`(1) <pkg_default>`
`gdal <http://www.gdal.org>`_                                   :ref:`(1) <pkg_default>`
`numpy <http://www.numpy.org>`_                                 :ref:`(1) <pkg_default>`
`scipy <https://www.scipy.org>`_                                :ref:`(2) <pkg_default>`
`setuptools <https://pypi.python.org/pypi/setuptools>`_         :ref:`(2) <pkg_default>`
`pip <https://pypi.python.org/pypi/pip>`_                       :ref:`(2) <pkg_default>`
`pyqtgraph <https://pypi.python.org/pypi/pip>`_                 :ref:`(3) <pkg_ins_pip>`
`scikit-learn <https://pypi.python.org/pypi/pip>`_              :ref:`(3) <pkg_ins_pip>`
`rios <http://rioshome.org>`_                                   :ref:`(4) <pkg_ins_pip_ext>`
`spectral <http://www.spectralpython.net/installation.html>`_   :ref:`(3) <pkg_default>`

=============================================================== ========================

.. _pkg_default:

(1) should be installed with QGIS by default

.. _pkg_ins_os:

(2) usually require to run a plattform specific package manager:


.. _pkg_ins_pip:

(3) can be installed with `pip <https://pypi.python.org/pypi/pip>`_

.. _pkg_ins_pip_ext:

(4) can be installed with `pip <https://pypi.python.org/pypi/pip>`_ but not listed in the python package index

To install these required packages please follow these plattform specifc advices:

Windows
.......

1. Navigate into the QGIS root folder and call the ``OSGeo4W.bat`` with administative rights to open the OSGeo4W CLI.

2. Install the package requirements maintained by OSGeo4W::

              set __COMPAT_LAYER=RUNASINVOKER

              setup -k -q -P setuptools
              setup -k -q -P python-numpy
              setup -k -q -P python-scipy
              setup -k -q -P python-pip
              setup -k -q -P matplotlib


3. Install the package requirements maintained by pip. Either by

       a) Navigate into the ``enmapbox`` plugin folder and calling the ``requirements.txt``::

              cd C:\Users\ivan_ivanowitch\.qgis2\python\plugins\enmapboxplugin
              python -m pip install -r requirements.txt

       b) or, call the single pip commands step by step (e.g. if requirements.txt) is incomplete::

              python -m pip install pyqtgraph
              python -m pip install sklearn
              python -m pip install https://bitbucket.org/chchrsc/rios/downloads/rios-1.4.4.zip
              python -m pip install rios
              python -m pip install spectral



Linux
.....

The following way was tested successfully on Ubuntu

1.

macOS
.......



Standard Installation
^^^^^^^^^^^^^^^^^^^^^

The default QGIS binaries for macOS make use of the default macOS python.

1. Open your shell and call the



       >>>import sys

Homebrew Installation
^^^^^^^^^^^^^^^^^^^^^

1. Open your
3. Install the package requirements maintained by pip. Either by

       a) Navigate into the ``enmapbox`` plugin folder and calling the ``requirements.txt``::

              cd C:\Users\ivan_ivanowitch\.qgis2\python\plugins\enmapboxplugin
              python -m pip install -r requirements.txt

       b) or, step by step, e.g. if the requirements.txt is incomplete::

              python -m pip install pyqtgraph
              python -m pip install sklearn
              python -m pip install rios
              python -m pip install spectral



Linux
.....




If your QGIS misses a python package the EnMAP-Box depends on, it will show you a message like this:





Now, try to install missing package using your OS-specific package manager first

If a package like ``sklearn`` is not available, use `pip` <https://pypi.python.org/pypi/pip>, either from::
    A. inside a python shell::

        import pip
        pip.main('install sklearn'.split())

       this might work also from inside the QGIS Python shell

    B. or your system shell by calling python::

        $python -m pip install sklearn


Repeat this for each missing package.


.. _install_qgis:

Installing QGIS
---------------

Instructions to download and install QGIS can be found on `<http://www.qgis.org/en/site/forusers/download.html>`_.

.. _install_qgis_windows:



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
       setup -k -D -q -P qgis pyqt4 setuptools python-numpy python-scipy python-test python-pip matplotlib
       setup -k -q -P qgis pyqt4 setuptools python-numpy python-scipy python-test python-pip matplotlib
       python -m pip install setuptools
       python -m pip install sklearn

Hints for macOS users
.....................

MacOS users might consider to use the `Homebrew Package Manager <https://brew.sh>`_
to install QGIS from the `OSGeo4Mac Project <https://github.com/OSGeo/homebrew-osgeo4mac>`_.


Hint for Linux (Ubuntu) users
.............................

tbd.



FAQ / Troubleshooting
---------------------

**I get the following Error dialog: Wrong value for parameter MSYS**

    Description:** the following error occurs when activating the EnMAP-Box AlgorithmProvider in windows

    ![Unbenannt.PNG](https://bitbucket.org/repo/7bo7M8/images/4131973787-Unbenannt.PNG)

    **Solution:** install the *msys (command line utilities)* package with the OSGeo4W package installer.



