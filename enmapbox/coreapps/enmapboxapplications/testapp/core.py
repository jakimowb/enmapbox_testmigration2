import inspect
import tempfile
import traceback
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapboxapplications.utils import loadUIFormClass
from enmapboxapplications.widgets.core import UiWorkflowMainWindow, WorkflowWorker


from hubflow.core import *

pathUi = join(dirname(__file__), 'ui')

class TestWorkflow(UiWorkflowMainWindow):

    def __init__(self, parent=None):
        UiWorkflowMainWindow.__init__(self, parent)

    def worker(self):
        return Worker()

class Worker(WorkflowWorker):

    def run_(self, progressCallback, *args, **kwargs):
        from hubflow.core import VectorClassification, Classification, Raster, ApplierOptions
        import enmapboxtestdata


        import time
        time.time()

        vector = VectorClassification(filename=enmapboxtestdata.landcover_polygons, classAttribute='level_2_id')
        Classification.fromClassification(
            filename=r'c:\output\classification{}.bsq'.format(str(time.time())), classification=vector,
            grid=Raster(filename=enmapboxtestdata.enmap).grid().atResolution(10),
            **ApplierOptions(progressCallback=progressCallback))