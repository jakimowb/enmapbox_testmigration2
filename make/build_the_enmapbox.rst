
How to testm build and publish the EnMAP-Box
============================================

#. Update external APIs / packages, e.g. with ``make/updateexternals.py`` (modify after ``if __name__ == "__main__":``)

    * add/modify remote sources with ``RemoteInfo.create`` to specify external git repository sources to be part of EnMAP-Box Source code


#. (optional) Compile Qt resource files.

   For example, to compile ``myresources.qrc`` into ``myresources.py``, call the shell command:

   ```pyrcc5 -o myproject/myresources.py myproject/myresources.qrc```

   use `compile_rc_files(ROOT)` from `make/guimake.py` to list the pyrcc5 commands for all *.qrc files within directory `ROOT`

# if necessary, increase version in ``enmapbox/__init__.py`` ``__version__ = '3.3'`` #subsub-version information is added during build process.

#. Push updated source code!

3. Start & test the EnMAP-Box from inside your IDE by running `enmapbox/__main__.py`

4. Call ``make/deploy.py`` to build the EnMAP-Box as QGIS Plugin zip::

        #1. update deploy/enmapboxplugin and
        #   create deploy/enmapboxplugin.<version>.<branch>.zip
        build()

        #2. run updateRepositoryXML() to create QGIS Plugin Repository XMLs
        # deploy/qgis_plugin_develop.xml (remote, points on https://bitbucket.org/hu-geomatics/enmap-box/src/<branch>/qgis_plugin_develop.xml)
        # deploy/qgis_plugin_develop.xml (local, points on deploy/enmapboxplugin.<version>.<branch>.zip
        updateRepositoryXML()

5. Test again

    #3. Upload to Repository
    # upload deploy/enmapboxplugin.<version>.<branch>.zip to https://api.bitbucket.org/2.0/repositories/hu-geomatics/enmap-box/downloads
    uploadDeveloperPlugin()

