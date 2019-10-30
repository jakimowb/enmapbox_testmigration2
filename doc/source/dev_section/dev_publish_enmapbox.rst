.. _dev_build_enmapbox_plugin:

Build and publish the EnMAP-Box
###############################



Build the EnMAP-Box Plugin
==========================

Building the EnMAP-Box plugin is done by creating a zip file the QGIS Plugin Manager uses to install the EnMAP-Box
from. This requires that:

1. you have the development specific python packages installed (see :ref:`dev_install_dependencies`)

2. git is available in your shell/command line (see :ref:`_dev_installation_detailed`)

3. you use the EnMAP-Box code from the `EnMAP-Box repository` (see :ref:`dev_install_add_enmapbox_code`) instead from your local QGIS installation.


Calling:

.. code-block:: batch

    python make/deploy.py

creates or updates:

* ``deploy/enmapboxplugin/`` which contains the plugin code + additional files
* ``deploy/enmapboxplugin.3.3.20190214T1125.develop.zip`` - just ``deploy/enmapboxplugin`` as zip file
* ``deploy/qgis_plugin_develop_local.xml`` a QGIS Plugin Repository XML that can be used for local testing

.. note::

    The ``<subsubversion>`` consists of ``<date>T<time>.<active branch>`` and is generated automatically.

    This helps to generate, test and differentiate between EnMAP-Box versions of different development steps.

A successful ends with a printout like::

    ### To update/install the EnMAP-Box, run this command on your QGIS Python shell:

    from pyplugin_installer.installer import pluginInstaller
    pluginInstaller.installFromZipFile(r"C:\Users\user\Repositories\QGIS_Plugins\enmap-box\deploy\enmapboxplugin.3.5.20191030T0634.develop.zip")
    #### Close (and restart manually)

    QProcess.startDetached(QgsApplication.arguments()[0], [])
    QgsApplication.quit()

    ## press ENTER

Copy and run it in your QGIS python shell to install the build EnMAP-Box plugin and restart QGIS.
Alternatively, you can install the plugin in QGIS with a few mouse clicks more by:

1. Open the QGIS Plugin Manager
3. Install from ZIP with the created ZIP file
4. Restart QGIS to account for activate changes in python code



Publish the EnMAP-Box
=====================

Official EnMAP-Box plugin *master* versions are named like ``enmapboxplugin.3.3.20190214T1125.master.zip``. They need to be uploaded
to http://plugins.qgis.org/plugins/ using an OSGeo account.

Other versions, e.g. *development snapshots* are named like ``enmapboxplugin.3.3.20190214T1125.develop.zip`` or ``enmapboxplugin.3.3.20190214T1125.my_feature_branch.zip``
and might be distributed using the repositories download section https://bitbucket.org/hu-geomatics/enmap-box/downloads/.

..
    Update external developments
    ----------------------------

    The EnMAP-Box repository source code includes source code that is maintained in other `external` repositories.
    These locations and how its code is copied into the EnMAP-Box repository is described in ``make/updateexternals.py``.

    To update code developed in an external location, e.g. call:

    .. code-block:: python

        import updateexternals
        updateexternals.updateRemotes('qps')
        updateexternals.updateRemotes('hub-datacube')
        updateexternals.updateRemotes('hub-workflow')
        updateexternals.updateRemotes('enmapboxapplications')
        updateexternals.updateRemotes('enmapboxgeoalgorithms')

    .. note:: add/modify remote sources with ``RemoteInfo.create`` to specify other external git repository sources
              to be part of EnMAP-Box Source code


Publish the EnMAP-Box documentation
===================================

Updates to the EnMAP-Box documentation (folder :code:`doc/source`) are automatically detected by readthedocs if they get pushed either to
the *develop* or *master* branch.


To create the HTML based documentation on your local system call:

    cd doc
    make html

This creates a folder :code:`doc/build` with the HTML documentation. To visualize it, just open :code:`doc/build/html/index.html`
in your webbrowser.


