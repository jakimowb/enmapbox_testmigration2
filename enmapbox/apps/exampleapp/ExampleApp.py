import os
from PyQt4.QtGui import *


from enmapbox.gui.utils import loadUIFormClass
from exampleapp import APP_DIR
pathUi = os.path.join(APP_DIR, 'example.ui')
class MyAppUserInterface(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(MyAppUserInterface, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initUiElements()
        self.radioButtonSet1.setChecked(True)
        self.updateSummary()

    def initUiElements(self):
        self.radioButtonSet1.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.radioButtonSet2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.buttonBox.accepted.connect(self.updateSummary)



        #update summary if any parameter was changed
        self.stackedWidget.currentChanged.connect(self.updateSummary)
        self.colorButtonP1.colorChanged.connect(self.updateSummary)

        for spinBox in self.findChildren(QAbstractSpinBox):
            spinBox.editingFinished.connect(self.updateSummary)
        for comboBox in self.findChildren(QComboBox):
            comboBox.currentIndexChanged.connect(self.updateSummary)


    def updateSummary(self, *args):
        #read parameters
        from collections import OrderedDict
        params = OrderedDict()
        params['file'] = self.comboBoxMapLayer.currentLayer()

        if self.radioButtonSet1.isChecked():
            params['mode'] = 'mode 1'
            params['parameter 1'] = self.comboBoxP1.currentText()
            params['color '] = self.colorButtonP1.color().getRgb()

        elif self.radioButtonSet2.isChecked():
            params['mode'] = 'mode 2'
            params['parameter 1'] = self.doubleSpinBox.value()
            params['parameter 2'] = self.comboBoxP2.currentText()
        info = []
        for parameterName, parameterValue in params.items():
            info.append('{} = {}'.format(parameterName, parameterValue))

        self.textBox.setPlainText('\n'.join(info))



from processing.core.Processing import Processing
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster
class MyAppGeoAlgorithm(GeoAlgorithm):

        def defineCharacteristics(self):
            self.name = 'NDVI (using GDAL)'
            self.group = 'TestGeoAlgorithms'

            self.addParameter(ParameterRaster('infile', 'Spectral Image'))
            self.addOutput(OutputRaster('outfile', 'NDVI'))

        def processAlgorithm(self, progress):
            from .ndviWithGDAL import ndviWithGDAL
            infile = self.getParameterValue('infile')
            outfile = self.getOutputValue('outfile')
            ndviWithGDAL(infile=infile, outfile=outfile, progress=progress)

        def help(self):
            return True, 'Calculates the NDVI using GDAL'


