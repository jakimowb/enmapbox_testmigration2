import traceback
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.utils import loadUIFormClass
from enmapboxapplications.widgets.core import UiLabeledLibrary
from enmapboxapplications.synthmixapp.script import synthmixRegressionEnsemble
from hubflow.core import *

pathUi = join(dirname(__file__), 'ui')

class SynthmixApp(QMainWindow, loadUIFormClass(pathUi=join(pathUi, 'main.ui'))):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.uiInfo_ = QLabel()
        self.statusBar().addWidget(self.uiInfo_, 1)
        self.initRegressor()
        self.initOutputFolder()
        self.initAggregations()
        self.uiLabeledLibrary().uiField().currentIndexChanged.connect(self.setTargets)
        self.setTargets(0)
        self.uiRaster_.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiExecute().clicked.connect(self.execute)

    def uiLabeledLibrary(self):
        assert isinstance(self.uiLabeledLibrary_, UiLabeledLibrary)
        return self.uiLabeledLibrary_

    def uiInfo(self):
        return self.uiInfo_

    def uiRaster(self):
        assert isinstance(self.uiRaster_, QgsMapLayerComboBox)
        return self.uiRaster_

    def uiTargets(self):
        assert isinstance(self.uiTargets_, QgsCheckableComboBox)
        return self.uiTargets_

    def uiRegressor(self):
        assert isinstance(self.uiRegressor_, QComboBox)
        return self.uiRegressor_

    def uiExecute(self):
        assert isinstance(self.uiExecute_, QToolButton)
        return self.uiExecute_

    def setTargets(self, index):
        library = self.uiLabeledLibrary().currentLibrary()
        field = self.uiLabeledLibrary().currentField()
        for i in range(self.uiTargets().count()):
            self.uiTargets().removeItem(0)
        if field is not None:
            definitions = library.attributeDefinitions()
            try:
                classDefinition = AttributeDefinitionEditor.makeClassDefinition(definitions=definitions, attribute=field)
                self.names = classDefinition.names()
            except:
                self.names = []
            self.uiTargets().addItems(self.names)
        self.uiTargets().selectAllOptions()

    def initRegressor(self):
        from enmapboxgeoalgorithms.algorithms import ALGORITHMS, RegressorFit
        self.regressors = [alg for alg in ALGORITHMS if isinstance(alg, RegressorFit)]
        self.regressorNames = [alg.name()[3:] for alg in self.regressors]
        self.uiRegressor().addItems(self.regressorNames)
        self.uiRegressor().currentIndexChanged.connect(lambda index: self.uiCode_.setText(self.regressors[index].code()))
        self.uiRegressor().setCurrentIndex(self.regressorNames.index('RandomForestRegressor'))

    def initOutputFolder(self):
        assert isinstance(self.uiOutputFolder_, QgsFileWidget)
        self.uiOutputFolder_.setStorageMode(self.uiOutputFolder_.GetDirectory)
        import tempfile
        self.uiOutputFolder_.setFilePath(join(tempfile.gettempdir(), 'RegressionBasedUnmixing'))
        self.uiOutputBasename_.setText('fraction.bsq')

    def initAggregations(self):
        self.uiAggregations_.setCheckedItems(['mean'])

    def execute(self, *args):
        self.uiInfo().setText('')
        try:
            library = self.uiLabeledLibrary().currentLibrary()
            if library is None:
                self.uiInfo().setText('Error: no library selected')
                return

            field = self.uiLabeledLibrary().currentField()
            if field is None:
                self.uiInfo().setText('Error: no attribute selected')
                return

            qgsRaster = self.uiRaster().currentLayer()
            if qgsRaster is None:
                self.uiInfo().setText('Error: no raster selected')
                return
            raster = Raster(filename=self.uiRaster().currentLayer().source())

            targets = [self.names.index(name)+1 for name in self.uiTargets().checkedItems()]
            if len(targets) == 0:
                self.uiInfo().setText('Error: no target classes selected')
                return

            mixingComplexities = dict()

            for key, ui in zip([2,3,4], [self.uiComplexity2_, self.uiComplexity3_, self.uiComplexity4_]):
                try:
                    mixingComplexities[key] = float(ui.text())
                    assert mixingComplexities[key] >= 0 and mixingComplexities[key] <= 1
                except:
                    self.uiInfo().setText('Error: mixing complexity likelihoods must be values between 0 and 1')
                    return

            if sum(mixingComplexities.values()) != 1:
                self.uiInfo().setText('Error: mixing complexity likelihoods must sum to 1')
                return

            classLikelihoods = self.uiClassLikelihoods_.currentText().lower()

            includeEndmember = self.uiIncludeLibrarySpectra_.isChecked()
            includeWithinclassMixtures = self.uiIncludeWithinclassMixtures_.isChecked()
            useEnsemble = self.uiUseEnsemble_.isChecked()


            try:
                n = int(self.uiNumberOfSamples_.text())
                assert n >= 0
            except:
                self.uiInfo().setText('Error: number of samples must be greater than or equal to 0')
                return

            if n == 0 and not includeEndmember:
                self.uiInfo().setText('Error: number of samples is 0 and endmember from library are not included')
                return

            if not useEnsemble:
                runs = 1
            else:
                try:
                    runs = int(self.uiNumberOfEstimators_.text())
                    assert n > 0
                except:
                    self.uiInfo().setText('Error: number of estimators must be greater than 0')
                    return

            namespace = dict()
            code = self.uiCode_.toPlainText()
            exec(code, namespace)
            sklEstimator = namespace['estimator']

            classificationSample = ClassificationSample(raster=library.raster(),
                                                        classification=Classification.fromENVISpectralLibrary(
                                                            filename='/vsimem/synthmixapp/classification.bsq',
                                                            library=library,
                                                            attribute=field))

            self.uiExecute().setEnabled(False)

            filename = join(self.uiOutputFolder_.filePath(), self.uiOutputBasename_.text())
            synthmixRegressionEnsemble(filename=filename,
                                       classificationSample=classificationSample,
                                       targets=targets,
                                       regressor=Regressor(sklEstimator=sklEstimator),
                                       raster=raster,
                                       runs=runs, n=n,
                                       mixingComplexities=mixingComplexities,
                                       classLikelihoods=classLikelihoods,
                                       includeWithinclassMixtures=includeWithinclassMixtures,
                                       includeEndmember=includeEndmember,
                                       saveSamples=self.uiSaveTraining_.isChecked(),
                                       saveModels=self.uiSaveModels_.isChecked(),
                                       savePredictions=self.uiSavePredictions_.isChecked(),
                                       saveMedian=self.uiAggregations_.itemCheckState(0) != 0 and useEnsemble,
                                       saveMean=self.uiAggregations_.itemCheckState(1) != 0,
                                       saveIQR=self.uiAggregations_.itemCheckState(2) != 0 and useEnsemble,
                                       saveStd=self.uiAggregations_.itemCheckState(3) != 0 and useEnsemble,
                                       saveRGB=self.uiSaveRGB_.isChecked() != 0,
                                       saveClassification=self.uiSaveClassification_.isChecked() != 0,
                                       clip=True,
                                       ui=self)

            self.uiExecute().setEnabled(True)


        except:
            traceback.print_exc()
