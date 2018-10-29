import sys, os, site


from qgis.core import Qgis, QgsApplication, QgsProcessingRegistry, QgsProcessingProvider
from qgis.gui import QgsGui
from qgis.PyQt.QtCore import QSettings

__version__ = '3.3' #subsub-version information is added during build process

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
ISSUE_TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
CREATE_ISSUE = 'https://bitbucket.org/hu-geomatics/enmap-box/issues/new'
DEPENDENCIES = ['numpy','scipy','osgeo', 'PyQt5', 'sklearn','pyqtgraph','matplotlib']
DOCUMENTATION = 'https://enmap-box.readthedocs.io/'
URL_TESTDATA = r'https://bitbucket.org/hu-geomatics/enmap-box-testdata/get/master.zip'

DIR_ENMAPBOX = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])
DIR_TESTDATA = os.path.join(DIR_REPO, 'enmapboxtestdata')

ENMAP_BOX_KEY = 'EnMAP-Box'


def enmapboxSettings()->QSettings:
    """
    Returns the QSettings object for EnMAP-Box Settings
    :return: QSettings
    """
    return QSettings('HU-Berlin', ENMAP_BOX_KEY)

settings = enmapboxSettings()

DEBUG = settings.value('EMB_DEBUG', False)
LOAD_PROCESSING_FRAMEWORK = settings.value('EMB_LOAD_PF', True)
LOAD_EXTERNAL_APPS = settings.value('EMB_LOAD_EA', True)
LOAD_INTERNAL_APPS = settings.value('EMB_LOAD_IA', True)

site.addsitedir(DIR_SITEPACKAGES)

# make the EnMAP-Box resources available

if not 'images' in sys.modules.keys():
    import enmapbox.gui.resourcemockup
    sys.modules['images'] = enmapbox.gui.resourcemockup

from enmapbox.gui.ui import resources
resources.qInitResources()

#see https://github.com/pyqtgraph/pyqtgraph/issues/774
WORKAROUND_PYTGRAPH_ISSUE_774 = True
if WORKAROUND_PYTGRAPH_ISSUE_774:
    from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject

    from PyQt5.QtCore import QVariant
    untouched = GraphicsObject.itemChange

    def newFunc(cls, change, value):
        if value != QVariant(None):
            return untouched(cls, change, value)
        else:
            return untouched(cls, change, None)

    GraphicsObject.itemChange = newFunc


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



#init some other requirements
#print('initialize EnMAP-Box editor widget factories')
from enmapbox.gui.plotstyling import registerPlotStyleEditorWidget
registerPlotStyleEditorWidget()

from enmapbox.gui.speclib import registerSpectralProfileEditorWidget
registerSpectralProfileEditorWidget()



_enmapboxProvider = None
def initEnMAPBoxProcessingProvider():
    from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider, ID

    import processing
    processing.Processing.initialize()

    registry = QgsApplication.instance().processingRegistry()
    assert isinstance(registry, QgsProcessingRegistry)
    global _enmapboxProvider
    if not isinstance(_enmapboxProvider, QgsProcessingProvider):
        _enmapboxProvider = registry.providerById(ID)
    if not isinstance(_enmapboxProvider, QgsProcessingProvider):
        _enmapboxProvider = EnMAPBoxAlgorithmProvider()

        assert _enmapboxProvider.id() == ID
        registry.addProvider(_enmapboxProvider)
    assert registry.providerById(ID) == _enmapboxProvider
    assert isinstance(_enmapboxProvider, EnMAPBoxAlgorithmProvider)

    try:
        import enmapboxgeoalgorithms.algorithms
        existingAlgNames = [a.name() for a in registry.algorithms() if a.groupId() == _enmapboxProvider.id()]
        missingAlgs = [a for a in enmapboxgeoalgorithms.algorithms.ALGORITHMS if a.name() not in existingAlgNames]
        _enmapboxProvider.addAlgorithms(missingAlgs)
        #_enmapboxProvider.refreshAlgorithms()
        s = ""
    except Exception as ex:
        info = ['Failed to load QgsProcessingAlgorithms.\n{}'.format(str(ex))]
        info.append('PYTHONPATH:')

        for p in sorted(sys.path):
            info.append(p)

        print('\n'.join(info), file=sys.stderr)


def run():
    import enmapbox.__main__
    enmapbox.__main__.run()


