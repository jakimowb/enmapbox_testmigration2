"""
Just prints some information on the standard QGIS installation.
specificially the PKGDATAPATH={path to library}
To be used from the CLI, e.g. calling python qgisinfo.py
"""
import pathlib
import qgis
from qgis.core import QgsApplication
from qgis.testing import start_app
app = start_app()
pkg = pathlib.Path(QgsApplication.pkgDataPath())
print(f'PKGDATAPATH={pkg}')
app.quit()
