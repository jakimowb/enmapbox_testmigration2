import traceback

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from enmapboxapplications.synthmixapp.script import synthmixRegressionEnsemble
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.parameter.processingparameterclassificationdatasetwidget import \
    ProcessingParameterClassificationDatasetWidget
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from hubflow.core import *
from qgis.core import *
from qgis.gui import *
from typeguard import typechecked

pathUi = join(dirname(__file__), 'ui')


class SynthmixApp(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(pathUi, 'main.ui'), self)
        # self.setupUi(self)
        self.uiInfo_ = QLabel()
        self.statusBar().addWidget(self.uiInfo_, 1)
        self.initRegressor()
        self.initOutputFolder()
        self.initAggregations()
        self.uiLabeledLibrary().mFile.fileChanged.connect(self.setTargets)
        self.setTargets(0)
        self.uiRaster().setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiRaster().setCurrentIndex(0)
        self.uiExecute().clicked.connect(self.execute)

    def uiLabeledLibrary(self):
        assert isinstance(self.uiLabeledLibrary_, ProcessingParameterClassificationDatasetWidget)
        return self.uiLabeledLibrary_

    def uiInfo(self):
        assert isinstance(self.uiInfo_, QLabel)
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

        for i in range(self.uiTargets().count()):
            self.uiTargets().removeItem(0)

        filename = self.uiLabeledLibrary().value()
        if filename == '':
            return

        dump = ClassifierDump(**Utils.pickleLoad(filename))
        self.names = [c.name for c in dump.categories]
        self.uiTargets().addItems(self.names)
        self.uiTargets().selectAllOptions()

    def initRegressor(self):
        from enmapboxgeoalgorithms.algorithms import ALGORITHMS, RegressorFit
        self.regressors = [alg for alg in ALGORITHMS if isinstance(alg, RegressorFit)]
        self.regressorNames = [alg.name()[3:] for alg in self.regressors]
        self.uiRegressor().addItems(self.regressorNames)
        self.uiRegressor().currentIndexChanged.connect(
            lambda index: self.uiCode_.setText(self.regressors[index].code()))
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
        try:
            filenameDataset = self.uiLabeledLibrary().value()
            if filenameDataset is None:
                self.uiInfo().setText('Error: select Endmember Dataset first')
                return

            qgsRaster = self.uiRaster().currentLayer()
            if qgsRaster is None:
                self.uiInfo().setText('Error: no raster selected')
                return
            raster = Raster(filename=self.uiRaster().currentLayer().source())

            targets = [self.names.index(name) + 1 for name in self.uiTargets().checkedItems()]
            if len(targets) == 0:
                self.uiInfo().setText('Error: no target classes selected')
                return

            mixingComplexities = dict()

            for key, ui in zip([2, 3, 4], [self.uiComplexity2_, self.uiComplexity3_, self.uiComplexity4_]):
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

            filename = join(self.uiOutputFolder_.filePath(), self.uiOutputBasename_.text())

            classificationSample = utilsMakeClassificationSampleFromCategorizedLibrary(filenameDataset, filename)

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
            self.uiInfo().setText(traceback.format_exc())
            traceback.print_exc()
            self.uiProgressBar_.setValue(0)
            return


# fix for #734
# note that we mix old hubflow API with new enmapboxprocessing API
# SynthMix will be overhauled for version 3.10!
@typechecked
def utilsMakeClassificationSampleFromCategorizedLibrary(filenameDataset: str, filename: str) -> ClassificationSample:
    dump = ClassifierDump(**Utils.pickleLoad(filenameDataset))
    X = dump.X
    y = dump.y
    categories = dump.categories

    filenameRaster = Utils.tmpFilename(filename, 'X.tif')
    filenameClassification = Utils.tmpFilename(filename, 'y.tif')
    Driver(filenameRaster).createFromArray(np.expand_dims(X.T, 2))
    Driver(filenameClassification).createFromArray(np.expand_dims(y.T, 2))
    classDefinition = ClassDefinition(
        classes=len(categories), names=[c.name for c in categories], colors=[Color(c.color) for c in categories]
    )
    raster = Raster(filenameRaster)
    classification = Classification(filenameClassification, classDefinition=classDefinition)

    return ClassificationSample(raster, classification)
