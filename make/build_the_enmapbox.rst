How to test, build and publish the EnMAP-Box
============================================
#. After an initial repository checkout of if any resource paths were modified, you need to compile the Qt resource (`*.qrc`) into corresponding python modules (`*.py`).
For this you use `make/guimake.py` and call::

        compileResourceFiles()

The EnMAP-Box uses a couple of icons that are provided by the QGIS Desktop application.


        #2. run updateRepositoryXML() to create QGIS Plugin Repository XMLs
        # deploy/qgis_plugin_develop.xml (remote, points on https://bitbucket.org/hu-geomatics/enmap-box/src/<branch>/qgis_plugin_develop.xml)
        # deploy/qgis_plugin_develop.xml (local, points on deploy/enmapboxplugin.<version>.<branch>.zip
        updateRepositoryXML()

if your



#. Update external APIs / packages, e.g. with ``make/updateexternals.py`` (modify after ``if __name__ == "__main__":``)

    .. note:: add/modify remote sources with ``RemoteInfo.create`` to specify external git repository sources to be part of EnMAP-Box Source code


#. (optional) Compile Qt resource files.

   For example, to compile ``myresources.qrc`` into ``myresources.py``, call the shell command:

   ```pyrcc5 -o myproject/myresources.py myproject/myresources.qrc```

   use `compile_rc_files(ROOT)` from `make/guimake.py` to list the pyrcc5 commands for all \*.qrc files within directory `ROOT`

#. EnMAP-Box version: if necessary, increase in ``enmapbox/__init__.py``, e.g.::

    __version__ = '3.3'

   .. note:: subsub-version information is added during build process.

#. Testdata version: if necessary, increase minimal requirement in ``enmapbox/__init__.py``, e.g.::

    MIN_VERSION_TESTDATA = '0.6'

#. Start & test the EnMAP-Box from inside your IDE by running `enmapbox/__main__.py`

#. Call ``make/deploy.py`` to build the EnMAP-Box as QGIS Plugin zip::

        #1. update deploy/enmapboxplugin and
        #   create deploy/enmapboxplugin.<version>.<branch>.zip
        build()

        #2. run updateRepositoryXML() to create QGIS Plugin Repository XMLs
        # deploy/qgis_plugin_develop.xml (remote, points on https://bitbucket.org/hu-geomatics/enmap-box/src/<branch>/qgis_plugin_develop.xml)
        # deploy/qgis_plugin_develop.xml (local, points on deploy/enmapboxplugin.<version>.<branch>.zip
        updateRepositoryXML()

#. Test again

    #3. Upload to Repository
    # upload deploy/enmapboxplugin.<version>.<branch>.zip to https://api.bitbucket.org/2.0/repositories/hu-geomatics/enmap-box/downloads
    uploadDeveloperPlugin()

#. Push updated source code!