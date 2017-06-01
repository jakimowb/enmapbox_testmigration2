### Graphical User Interfaces
### that allow for sophisticated and more user friendly input of algorithm parameterization
###
import os, collections
from PyQt4.QtGui import *

### A simple dialog to parameterize NDVI calculation
###
class MyNDVIUserInterface(QDialog):
    def __init__(self, parent=None):
        super(MyNDVIUserInterface, self).__init__(parent)
        self.initWidgets()
        self.initInteractions()
        self.setWindowTitle('My NDVI GUI')
        self.setWindowIcon(QIcon(os.path.join(APP_DIR,'icon.png')))

    SUPPORTED_GDALDRIVERS = {
        'ENVI':'ENVI (*.bsq)',
        'GTiff':'GeoTIFF (*.tif)'
    }

    def initWidgets(self):
        mainLayout = QGridLayout(self)
        self.setLayout(mainLayout)

        self.btnSetInputFile = QPushButton('...', self)
        self.btnSetOutputFile = QPushButton('...', self)
        self.tbInputFile = QLineEdit(self)
        self.tbInputFile.setPlaceholderText('Set input image')
        self.tbInputFile.setValidator(RasterFilePathValidator())
        self.tbOutputFile = QLineEdit(self)
        self.tbOutputFile.setPlaceholderText('Set output image')

        mainLayout.addWidget(QLabel('Input'), 0, 0)
        mainLayout.addWidget(self.tbInputFile, 0, 1)
        mainLayout.addWidget(self.btnSetInputFile, 0, 2)

        box = QHBoxLayout()
        self.sbRedBand = QSpinBox(self)
        self.sbNIRBand = QSpinBox(self)
        box.addWidget(QLabel('Red Band'))
        box.addWidget(self.sbRedBand)
        box.addWidget(QLabel('NIR Band'))
        box.addWidget(self.sbNIRBand)
        # within the vertical box, the spacer will push widgets to it's left
        box.addSpacerItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Expanding))
        mainLayout.addLayout(box, 1, 1, 1, 2)  # span 2nd (index 1) and 3rd (+ 1) column

        mainLayout.addWidget(QLabel('Output'), 2, 0)
        mainLayout.addWidget(self.tbOutputFile, 2, 1)
        mainLayout.addWidget(self.btnSetOutputFile, 2, 2)

        self.outputFormat = QComboBox()
        for driver, description in MyNDVIUserInterface.SUPPORTED_GDALDRIVERS.items():
            self.outputFormat.addItem(description, driver)
        from qgis.gui import QgsRasterFormatSaveOptionsWidget
        self.outputOptions = QgsRasterFormatSaveOptionsWidget(parent=self,
                                                              type=QgsRasterFormatSaveOptionsWidget.Default)
        box = QHBoxLayout()
        self.outputOptions.setFormat('GTiff')
        self.outputOptions.setRasterFileName('foobar.bqs')
        box.addWidget(QLabel('Format'))
        box.addWidget(self.outputFormat)
        box.addSpacerItem(QSpacerItem(0,0,hPolicy=QSizePolicy.Expanding))
        mainLayout.addLayout(box, 3, 1, 1, 2)
        mainLayout.addWidget(self.outputOptions, 4, 1, 2,2)

        box = QHBoxLayout()
        self.btAccept = QPushButton('Accept', self)
        self.btCancel = QPushButton('Cancel', self)
        box.addSpacerItem(QSpacerItem(0,0, hPolicy=QSizePolicy.Expanding))
        box.addWidget(self.btCancel)
        box.addWidget(self.btAccept)
        mainLayout.addLayout(box, 6, 1, 1, 2)

    def initInteractions(self):
        self.tbInputFile.textChanged.connect(self.validateParameters)
        self.sbRedBand.valueChanged.connect(self.validateParameters)
        self.sbNIRBand.valueChanged.connect(self.validateParameters)

        #select input file name via QFileDialog
        self.btnSetInputFile.clicked.connect(
            lambda : self.tbInputFile.setText(
                QFileDialog.getOpenFileName(self, 'Input image'))
        )

        # select output file name via QFileDialog
        self.btnSetOutputFile.clicked.connect(
            lambda: self.tbOutputFile.setText(
                QFileDialog.getSaveFileName(self, 'NDVI image'))
        )

        self.outputFormat.currentIndexChanged.connect(
            lambda : self.outputOptions.setFormat(
                self.outputFormat.itemData(
                    self.outputFormat.currentIndex()
                )
            )
        )
        self.outputFormat.setCurrentIndex(0)

        self.btAccept.clicked.connect(self.accept)
        self.btCancel.clicked.connect(self.reject)

    def validateParameters(self, *args):

        pass


    def parameters(self):
        params = dict()
        params['']

class RasterFilePathValidator(QValidator):
    def __init__(self, parent=None):
        super(RasterFilePathValidator, self).__init__(parent)

    def validate(self, path, cursorPosition):
        from osgeo import gdal
        if os.path.exists(path) and gdal.Open(path) is not None:
            return QValidator.Acceptable
        else:
            return QValidator.Invalid

### Use QtDesigner to design a GUI that is stored in an *.ui file
### The example.ui is compiled during runtime and
from enmapbox.gui.utils import loadUIFormClass
from __init__ import APP_DIR
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

    def startAlgorithm(self):
        params = self.collectParameters()
        from algorithms import dummyAlgorithm
        dummyAlgorithm(params)

    def collectParameters(self):
        params = collections.OrderedDict()
        params['file'] = self.comboBoxMapLayer.currentLayer()

        if self.radioButtonSet1.isChecked():
            params['mode'] = 'mode 1'
            params['parameter 1'] = self.comboBoxP1.currentText()
            params['color '] = self.colorButtonP1.color().getRgb()

        elif self.radioButtonSet2.isChecked():
            params['mode'] = 'mode 2'
            params['parameter 1'] = self.doubleSpinBox.value()
            params['parameter 2'] = self.comboBoxP2.currentText()
        return params

    def updateSummary(self, *args):
        info = []
        params = self.collectParameters()
        for parameterName, parameterValue in params.items():
            info.append('{} = {}'.format(parameterName, parameterValue))

        self.textBox.setPlainText('\n'.join(info))


