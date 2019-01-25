=====================
FAQ & Troubleshooting
=====================

Bug report & feedback
=====================

.. |link_bitbucket| raw:: html

   <a href="https://bitbucket.org/hu-geomatics/enmap-box/issues/new" target="_blank">Bitbucket Repository</a>


.. note:: Your feedback is more than welcome! In case you encounter any problems with the EnMAP-Box or have
          suggestions of any kind for improving it (or this documentation), please let us know!

.. attention:: **It's best to report issues (bugs, suggestions etc.)
               via our** |link_bitbucket|.


|
|
|

EnMAP-Box FAQ
=============

This is a list of Frequently Asked Questions about the EnMAP-Box. Feel free to
suggest new entries!

How do I...
-----------

.. ... **install QGIS on Windows without having administrative rights**?

..     yes, it is possible to install and run QGIS withouht any admin rights on windows.
..      Read :ref:`install_qgis_windows` for more details on this.

.. todo:: to be continued


How can I solve the following error...
--------------------------------------

... **Error loading the plugin**

    In case of missing requirements you should see an error message like this

    .. image:: ../img/missing_package_warning.png

    In that case please make sure you :ref:`installed all missing packages <install-python-packages>`,
    in this example ``pyqtgraph`` and ``sklearn`` are missing.

... **Installation of Astropy fails**

    In some cases using an older version does the trick, using pip you can install older versions using the ``==versionnumber`` synthax. ``--force-reinstall``
    is used here to ensure clean installation.

    .. code-block:: batch

       python3 -m pip install astropy==3.0.3 --force-reinstall


... **Wrong value for parameter MSYS**

    This error sometimes occurs when activating the EnMAP-Box AlgorithmProvider in Windows. Please install
    the *msys (command line utilities)* package with the OSGeo4W package installer.

... **This plugin is broken: 'module' object has not attribute 'GRIORA_NearestNeighbor'**

    Your GDAL version seems to be outdated. update it to a version > 2.0