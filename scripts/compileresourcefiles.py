import os, sys, fnmatch, six, subprocess, re, pathlib, typing
import qgis.testing


def compileEnMAPBoxResources():
    #app = qgis.testing.start_app()
    from enmapbox.externals.qps.resources import compileResourceFiles

    DIR_REPO = pathlib.Path(__file__).parents[1]
    directories = [DIR_REPO / 'enmapbox',
                   DIR_REPO / 'site-packages'
                   ]

    for d in directories:
        compileResourceFiles(d)

    print('Finished')


if __name__ == "__main__":
    compileEnMAPBoxResources()