import sys, os, site


from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QSettings

__version__ = '3.2.<updated_by_build_script>'

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
ISSUE_TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
CREATE_ISSUE = 'https://bitbucket.org/hu-geomatics/enmap-box/issues/new'
DEPENDENCIES = ['numpy','scipy','osgeo', 'PyQt5', 'sklearn','pyqtgraph','matplotlib']
DOCUMENTATION = 'https://enmap-box.readthedocs.io/'
URL_TESTDATA = r'https://bitbucket.org/hu-geomatics/enmap-box/downloads/enmapboxtestdata.zip'

DIR_ENMAPBOX = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])
DIR_TESTDATA = os.path.join(DIR_REPO, 'enmapboxtestdata')


def enmapboxSettings():
    ENMAP_BOX_KEY = 'EnMAP-Box'
    return QSettings('HU-Berlin', ENMAP_BOX_KEY)

settings = enmapboxSettings()

DEBUG = settings.value('EMB_DEBUG', False)
LOAD_PROCESSING_FRAMEWORK = settings.value('EMB_LOAD_PF', True)
LOAD_EXTERNAL_APPS = settings.value('EMB_LOAD_EA', True)
LOAD_INTERNAL_APPS = settings.value('EMB_LOAD_IA', True)

site.addsitedir(DIR_SITEPACKAGES)



# mockup to make QGIS resources available for uic.loadUiType

if not 'images' in list(sys.modules.keys()):
    import enmapbox.images
    sys.modules['images'] = enmapbox.images

def messageLog(msg, level=Qgis.Info):
    """
    Writes a log message to the QGIS EnMAP-Box Log
    :param msg: log message string
    :param level: Qgis.MessageLevel=[Qgis.Info |  Qgis.Warning| Qgis.Critical| Qgis.Success | Qgis.NONE]
    """

    if not isinstance(msg, str):
        msg = str(msg)
    QgsApplication.instance().messageLog().logMessage(msg, 'EnMAP-Box', level)



#provide important classes in Top-Level Namespace
EnMAPBox = None
EnMAPBoxApplication = None

try: #necessary to allow sphinx documentation
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EnMAPBox = EnMAPBox

    from enmapbox.gui.applications import EnMAPBoxApplication
    EnMAPBoxApplication = EnMAPBoxApplication

except:

    pass


