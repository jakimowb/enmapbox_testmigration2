EnMAP-Box repository
####################

The EnMAP-Box source code is hosted in a Git repository at https://bitbucket.org/hu-geomatics/enmap-box

.. _dev_enmapox_repo_structure:

Structure
=========

Overview
--------

The repository contains the following files and folders:

=============================== ========================================================================================
Folder/File                     Purpose
=============================== ========================================================================================
doc/                            Sphinx documentation
enmapbox/                       EnMAP-Box source code
enmapboxtesting/                Unit tests
examples/                       Code examples how to use the EnMAP-Box API
examples/minimumexample/        Exemplary EnMAP-Box Application
site-packages/                  Other python libraries the EnMAP-Box depends on
snippets/                       Small source code snippets.
CHANGES.txt
LICENCE.txt
LICENCE.md
README.md
__init__.py
contributors.txt
index.html
pb_tool.cfg
qgis_plugin_develop.xml
requirements.txt
requirements_developer.txt
setup.py
.gitattributes
.readthedocs.yml
.gitignore
=============================== ========================================================================================

Scripts for Developers
----------------------

The ``make`` directory contains scrips to support developers. Ensure that this folder is part of your python path, e.g add
it as source in your PyCharm project (left-mouse, mark directory as source):

============================== =========================================================================================================
Script                         Purpose
============================== =========================================================================================================
``make/deploy.py``             Create the EnMAP-Box Plugin ZIP file.
``make/guimake.py``            Routines to handle PyQt5 issues, e.g. to create Qt resource files.
``make/iconselect.py``         A widget to show Qt internal resource icons and to copy its path to the clipboard.
``make/updateexternals.py``    update parts of the EnMAP-Box code which are hosted in external repositories.
============================== =========================================================================================================

Generated Folders
-----------------

Some directories and files are not part of the repository and explicitly ignore in the `.gitignore` file, but required or
created during the development process. These are:

================================ =========================================================================================================
enmapboxtestdata/                Official EnMAP-Box testdata. Not part of repository code, installed afterwards.
qgisresources/                   QGIS resources compiled as python modules. Read :ref:`here<dev_repo_installation>` for details.
deploy/                          Builds of the EnMAP-Box plugin.
deploy/enmapboxplugin            Folder with last EnMAP-Box Plugin build.
deploy/enmapboxplugin.3.X...zip  Zipped version of a EnMAP-box Plugin build.
================================ =========================================================================================================


.. _dev_repo_installation:

Install the EnMAP-Box repository
================================

#. Open your shell and clone the EnMAP-Box repository:

    .. code-block:: batch

        cd <my_repositories>
        git clone https://bitbucket.org/hu-geomatics/enmap-box.git
        cd enmap-box

#. Add ``<my_repositories>/enmapbox/`` as source location to your PyCharm project
    (instead of that in your QGIS active profile!)


#. (Optional) install the QGIS source code repository.

    For the next step, but also if you like to discover the QGIS ++ code, it is recommended to install the
    QGIS repository as well


    .. code-block:: batch

        cd <my_repositories>
        git clone https://github.com/qgis/QGIS.git

    Now define a environmental variable ``DIR_QGIS_REPO`` in the IDE / PyCharm startup script (:ref:`dev_setup_pycharm`)


    ============= ====================================================================
    OS            Command
    ============= ====================================================================
    Windows       set DIR_QGIS_REPO=<my_repositories/QGIS>
    Linux /macOS  DIR_QGIS_REPO=<my_repositories/QGIS>
                  export DIR_QGIS_REPO
    ============= ====================================================================


#. Run ``make/setuprepository.py`` to create Qt resource modules and perform a dependency check.

   The EnMAP-Box uses the Qt resource system (see https://doc.qt.io/qt-5/resources.html for details) to access icons.
   This step creates for each Qt resource file (``filename.qrc``) a corresponding python module
   (``filename.py``) that contains a binary encrypted description of resources (icons, images, etc.).
   During startup, these resources are loaded and can be accessed by resource path strings.

   The EnMAP-Box re-uses several icons provided by the QGIS desktop application. For example,
   the QGIS icon for raster layers is available at ``:/images/themes/default/mIconPolygonLayer.svg`` and can be
   visualized in the QGIS python shell as followed:

    .. code-block:: batch

        icon = QIcon(r':/images/themes/default/mIconRaster.svg')
        label = QLabel()
        label.setPixmap(icon.pixmap(QSize(150,150)))
        label.show()

    .. figure:: img/resources_qgis_icon_example.png
         :width: 200px

         The QGIS icon for raster (mIconRaster.svg)

   If we start and develop application from inside PyCharm, we usually don't have access to QGIS desktop application
   resources. However, if you have downloaded the QGIS repository as described above, ``make/setuprepository.py``
   will look for it, compile the resource files and write them into folder ``enmap-box/qgisresources``.



Install / Update EnMAP-Box Testdata
===================================

#. Testdata version: if necessary, increase minimal requirement in ``enmapbox/__init__.py``, e.g.::

    MIN_VERSION_TESTDATA = '0.6'

#. Start & test the EnMAP-Box from inside your IDE by running `enmapbox/__main__.py`

