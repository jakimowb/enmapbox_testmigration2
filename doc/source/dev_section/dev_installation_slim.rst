.. include:: links.rst

*Last Update: 2019-02-18*

Installation (Developers) [minimal]
###################################

Overview
========

For developing EnMAP-Box Applications in PyCharm_, the following setup steps are required.

1. Install QGIS and the EnMAP-Box
=================================

Follow the :ref:`user installation guide <usr_installation>`.

Make sure that you can start the EnMAP-Box inside QGIS.

Make sure that you downloaded the example data: *EnMAP-Box > Project > Load Example Data*

2. Install packages required for developers
===========================================

Start a shell with admin rights and execute (:ref:`OSGeo4W shell <install-packages-windows>` on Windows)::

    py3_env
    python3 -m pip install -r https://bitbucket.org/hu-geomatics/enmap-box/raw/develop/requirements_developer.txt

3. Install PyCharm
==================

`Download PyCharm <https://www.jetbrains.com/pycharm/>`_ and install it to a location of choice.

Remember your **PyCharm installation folder** (e.g. ``C:\Program Files\JetBrains\PyCharm 2018.2.4``), we will need it later!

4. System setup
===============

Windows
-------

Under Windows, we need to execute PyCharm via a user-specific startup script to ensure the correct runtime environment.

1. Find your **QGIS installation folder**

    Start QGIS, open the Python Console (press [Ctrl+Alt+P]) and execute::

        import sys; from os.path import abspath, join; print(abspath(join(sys.executable, '..', '..')))

    The **QGIS installation folder** is located somewhere like here::

         C:\Program Files\QGIS 3.4
         #or
         C:\OSGeo4W64

    .. image:: img2/get_qgis_folder.png

2. Download the `PyCharm Startup Script <../_static/PyCharm_with_QGIS.bat>`_ to your desktop
   (e.g. ``C:\Users\username\Desktop\PyCharm_with_QGIS.bat``):

    .. literalinclude:: ../_static/PyCharm_with_QGIS.bat
        :linenos:

3. Open the script in a text editor:

    - modify the **QGIS installation folder** in line 2:

        .. literalinclude:: ../_static/PyCharm_with_QGIS.bat
            :lines: 2

    - modify the **PyCharm installation folder** in line 5:

        .. literalinclude:: ../_static/PyCharm_with_QGIS.bat
            :lines: 5

4. Double click the startup script on your desktop to run PyCharm:

    .. image:: img2/run_script.png

MacOS
-----

Ensure that the ``QGIS_PREFIX_PATH`` variable is available on your MacOS shell.
If not, edit the users `.bash_profile`:

.. code-block:: bash

    PATH="/Library/Frameworks/Python.framework/Versions/3.6/bin:${PATH}"
    export PATH
    QGIS_PREFIX_PATH="/Applications/QGIS3.app/Contents/MacOS"
    export QGIS_PREFIX_PATH

Linux
-----

.. todo:: Linux descriptions


5. Create a new PyCharm Project
===============================

1. Find the **QGIS Python Interpreter**, **QGIS Python API** and the **EnMAP-Box Plugin** locations on your system:

    In QGIS open the Python Console (press [Ctrl+Alt+P]) and execute::

        import sys; from os.path import join; print(join(sys.base_exec_prefix, 'python.exe'))

    The **QGIS Python Interpreter** is located somewhere like here::

        C:\Program Files\QGIS 3.4\apps\Python37\python.exe
        # or
        C:\OSGeo4W64\apps\Python37\python.exe

    Execute::

        import sys; from os.path import abspath, join; print(abspath(join(sys.base_exec_prefix, '..', 'qgis', 'python')))

    The **QGIS Python API** is located somewhere like here::

        C:\Program Files\QGIS 3.4\apps\qgis\python
        # or
        C:\OSGeo4W64\apps\qgis\python

    Execute::

        from enmapbox import __file__; from os.path import abspath; print(abspath(join(__file__, '..', '..')))

    The **EnMAP-Box Plugin** is located somewhere like here::

        C:\Users\username\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin

2. Open PyCharm and create a new project: *File > New Project...*

    - select **Pure Python**

    - in **Location** rename *untitled* to *EnMAP-Box*

    - expand **Project Interpreter** and select **Existing interpreter**

    .. image:: img2/interpreter1.png

    - click the **'...'** button to open the **Add Python Interpreter** dialog

    - select **System Interpreter**

    .. image:: img2/interpreter2.png

    - click the **'...'** button to open the **Select Python Interpreter** dialog

    - enter the path to the **QGIS Python Interpreter** (see 1.)

    .. image:: img2/interpreter3.png

    - close all dialogs by confirming with **OK**, **OK** and **Create**

3. Open the **Settings** dialog: *File > Settings...*

    - select **Project: EnMAP-Box** and **Project Structur**

    .. image:: img2/settings.png

    - click the **+ Add Content Root** button and enter the **QGIS Python API** folder (see 1.) and click **OK**

    .. image:: img2/content_root1.png

    - click the **+ Add Content Root** button and enter the **EnMAP-Box Plugin** folder (see 1.) and click **OK**

    .. image:: img2/content_root2.png

    - close the **Settings** dialog with click on **OK**

4. Make sure that the checkmark under *View > Tool Buttons* is set. Select the **Project** tab or press [Alt+1].

    Your **Project** should look like this:

    .. image:: img2/project.png

5. Right click on **python/plugins** and *Mark Directory as > Sources Root*

   Right click on **enmapboxplugin/make** and *Mark Directory as > Sources Root*

   Right click on **enmapboxplugin/site-packages** and *Mark Directory as > Sources Root*

    .. image:: img2/mark_as_root.png

5. Start the EnMAP-Box from PyCharm
===================================

Open the **Python Console**: *View > Tool Windows > Python Console*

Press [Ctrl+F5] to assure a fresh instance.

Test if you can start the EnMAP-Box::

    from enmapbox.testing import initQgisApplication
    from enmapbox import EnMAPBox
    qgsApp = initQgisApplication()
    enmapBox = EnMAPBox(None)
    enmapBox.openExampleData(mapWindows=1)
    qgsApp.exec_()

.. warning::

    If an error occurs with the message **ModuleNotFoundError: No module named 'enmapboxtestdata'** in it,
    you have to download the example data via the **EnMAP-Box started from QGIS**: *EnMAP-Box > Project > Load Example Data*
