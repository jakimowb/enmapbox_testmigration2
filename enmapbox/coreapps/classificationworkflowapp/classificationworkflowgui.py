import traceback
import webbrowser
from functools import wraps, partial
from os.path import join, dirname, exists, basename, relpath, abspath, isabs
from tempfile import gettempdir
from typing import Tuple

import numpy as np
from PyQt5.QtGui import QFont, QColor, QTextCursor
from PyQt5.QtWidgets import (QMainWindow, QToolButton, QProgressBar, QComboBox, QPlainTextEdit, QCheckBox, QDialog,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QRadioButton, QTextEdit)
from PyQt5.uic import loadUi
from processing.gui.AlgorithmDialog import AlgorithmDialog
from qgis._core import QgsMapLayerProxyModel, Qgis, QgsProcessingFeedback, QgsRasterLayer, QgsProject
from qgis._gui import QgsFileWidget, QgsMapLayerComboBox, QgsSpinBox, QgsMessageBar, QgsColorButton, QgsDoubleSpinBox

from enmapbox import EnMAPBox
from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.algorithm.classifierfeaturerankingpermutationimportancealgorithm import \
    ClassifierFeatureRankingPermutationImportanceAlgorithm
from enmapboxprocessing.algorithm.classifierperformancealgorithm import ClassifierPerformanceAlgorithm
from enmapboxprocessing.algorithm.colorizeclassprobabilityalgorithm import ColorizeClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.featureclusteringhierarchicalalgorithm import FeatureClusteringHierarchicalAlgorithm
from enmapboxprocessing.algorithm.fitgenericclassifier import FitGenericClassifier
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationsamplefromcsv import PrepareClassificationSampleFromCsv
from enmapboxprocessing.algorithm.prepareclassificationsamplefrommapandraster import \
    PrepareClassificationSampleFromMapAndRaster
from enmapboxprocessing.algorithm.prepareclassificationsamplefromtable import PrepareClassificationSampleFromTable
from enmapboxprocessing.algorithm.prepareclassificationsamplefromvectorandfields import \
    PrepareClassificationSampleFromVectorAndFields
from enmapboxprocessing.algorithm.selectfeaturesubsetfromsamplealgorithm import SelectFeatureSubsetFromSampleAlgorithm
from enmapboxprocessing.algorithm.subsampleclassificationsamplealgorithm import SubsampleClassificationSampleAlgorithm
from enmapboxprocessing.typing import ClassifierDump, Category
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


class MissingParameterError(Exception):
    """Methodes decorated with @errorHandled should raise this error to indicate a missing parameter."""


def errorHandled(func=None, *, successMessage: str = None):
    """Decorator for the various run methods. Will take care of error handling and reporting via the message bar."""
    if func is None:
        return partial(errorHandled, successMessage=successMessage)

    @wraps(func)
    def wrapper(*args, **kwargs):
        gui: ClassificationWorkflowGui
        gui, *argsTail = args
        gui.mMessageBar.clearWidgets()
        try:
            result = func(gui, *argsTail, **kwargs)
        except MissingParameterError:
            return
        except Exception as error:
            message = traceback.format_exc()
            traceback.print_exc()

            def showError():
                class Dialog(QDialog):
                    def __init__(self):
                        QDialog.__init__(self, gui)
                        self.setWindowTitle('Unexpected error')
                        self.setLayout(QHBoxLayout())
                        widget = QPlainTextEdit(message, parent=self)
                        # widget.setLineWrapMode(QPlainTextEdit.NoWrap)
                        widget.setFont(QFont('Courier'))
                        self.layout().addWidget(widget)

                dialog = Dialog()
                dialog.resize(800, 600)
                dialog.exec_()

            widget = gui.mMessageBar.createMessage('Unexpected error', str(error))
            button = QPushButton(widget)
            button.setText('Traceback')
            button.pressed.connect(showError)
            widget.layout().addWidget(button)
            gui.mMessageBar.pushWidget(widget, Qgis.Critical)
            return

        if successMessage is not None:
            gui.mMessageBar.pushSuccess('Success', successMessage)

        return result

    return wrapper


@typechecked
class ClassificationWorkflowGui(QMainWindow):
    mProgress: QProgressBar
    mCancel: QToolButton
    mLog: QTextEdit
    mLogClear: QToolButton

    # quick mapping
    mQuickLabels: QgsMapLayerComboBox
    mQuickFeatures: QgsMapLayerComboBox
    mQuickClassifier: QComboBox
    mRunQuickMapping: QToolButton

    # sample
    mRunImportFromMapLayer: QToolButton
    mRunImportFromVectorLayer: QToolButton
    mRunImportFromVectorTable: QToolButton
    mRunImportFromTextFile: QToolButton
    mRunSplitSample: QToolButton
    mSample: QgsFileWidget
    mViewSample: QToolButton
    mSampleInfo: QLabel
    mSamplesSizeRelative: QRadioButton
    mSamplesSizeAbsolute: QRadioButton
    mSamplesSizeRelativeValue: QgsDoubleSpinBox
    mSamplesSizeAbsoluteValue: QgsSpinBox
    mSetTrainSize: QToolButton
    mSetTestSize: QToolButton
    mSetSplitSize: QToolButton
    mSampleTable: QTableWidget
    mSampleTable2: QTableWidget
    mSampleTableRevert: QToolButton
    mSampleTableSave: QToolButton
    mTrainSample: QgsFileWidget
    mViewTrainSample: QToolButton
    mTrainSampleInfo: QLabel
    mTestSample: QgsFileWidget
    mViewTestSample: QToolButton
    mTestSampleInfo: QLabel

    # classifier
    mPredefined: QComboBox
    mCode: QPlainTextEdit
    mRunClassifierCreate: QToolButton
    mClassifier: QgsFileWidget
    mViewClassifier: QToolButton

    # feature selection
    # - clustering
    mRunFeatureClustering: QToolButton
    mViewFeatureClustering: QToolButton
    mFeatureClustering: QgsFileWidget
    mFeatureClusteringN: QgsSpinBox
    mRunFeatureClusteringSelect: QToolButton
    mTrainSampleClustered: QgsFileWidget
    mViewTrainSampleClustered: QToolButton
    mTrainSampleClusteredInfo: QLabel
    mTestSampleClustered: QgsFileWidget
    mViewTestSampleClustered: QToolButton
    mTestSampleClusteredInfo: QLabel

    # - ranking
    mRunFeatureRankingInternal: QToolButton  #
    mRunFeatureRankingPermutation: QToolButton
    mRunFeatureRankingRFE: QToolButton  # sklearn.feature_selection.RFE
    mRunFeatureRankingSFSForward: QToolButton  # sklearn.feature_selection.SequentialFeatureSelector
    mRunFeatureRankingSFSBackward: QToolButton  # sklearn.feature_selection.SequentialFeatureSelector
    mFeatureRanking: QgsFileWidget
    mViewFeatureRanking: QToolButton
    mFeatureRankingN: QgsSpinBox
    mRunFeatureRankingSelect: QToolButton
    mTrainSampleRanked: QgsFileWidget
    mViewTrainSampleRanked: QToolButton
    mTrainSampleRankedInfo: QLabel
    mTestSampleRanked: QgsFileWidget
    mViewTestSampleRanked: QToolButton
    mTestSampleRankedInfo: QLabel

    # fit
    mRunClassifierFit: QToolButton
    mClassifierFitted: QgsFileWidget
    mViewClassifierFitted: QToolButton
    mRunValidation: QToolButton
    mRunCrossValidation: QToolButton
    mNFold: QgsSpinBox
    mClassifierPerformance: QgsFileWidget
    mViewClassifierPerformance: QToolButton

    # mapping
    mRaster: QgsMapLayerComboBox
    mMask: QgsMapLayerComboBox
    mRunPredict: QToolButton
    mRunPredictProba: QToolButton
    mClassification: QgsMapLayerComboBox
    mProbability: QgsMapLayerComboBox
    mRunMapValidation: QToolButton
    mGroundTruth: QgsMapLayerComboBox
    mClassificationPerformance: QgsFileWidget
    mViewClassificationPerformance: QToolButton

    # settings
    mWorkingDirectory: QgsFileWidget
    mDialogAutoClose: QCheckBox
    mDialogAutoRun: QCheckBox
    mDialogAutoOpen: QCheckBox

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(dirname(__file__), 'main.ui'), self)
        self.mMessageBar = QgsMessageBar()
        self.mMessageBar.setMaximumSize(9999999, 50)
        self.centralWidget().layout().addWidget(self.mMessageBar)
        self.connectSignals()
        self.initFiles()
        self.initLayers()
        self.initClassifier()
        self.enmapBox = EnMAPBox.instance()

    def connectSignals(self):
        self.mLogClear.clicked.connect(lambda: self.mLog.clear())

        # quick mapping
        self.mRunQuickMapping.clicked.connect(self.runQuickMapping)

        # sample
        self.mRunImportFromMapLayer.clicked.connect(
            lambda: self.runImportFromAlg(PrepareClassificationSampleFromMapAndRaster(), None)
        )
        self.mRunImportFromVectorLayer.clicked.connect(
            lambda: self.runImportFromAlg(PrepareClassificationSampleFromVectorAndFields(), None)
        )
        self.mRunImportFromVectorTable.clicked.connect(
            lambda: self.runImportFromAlg(PrepareClassificationSampleFromTable(), None)
        )
        self.mRunImportFromTextFile.clicked.connect(
            lambda: self.runImportFromAlg(PrepareClassificationSampleFromCsv(), None)
        )
        self.mRunSplitSample.clicked.connect(self.runSplitSample)
        self.mSample.fileChanged.connect(self.onSampleChanged)
        self.mSetTrainSize.clicked.connect(self.onSetTrainSize)
        self.mSetTestSize.clicked.connect(self.onSetTestSize)
        self.mSetSplitSize.clicked.connect(self.onSetSplitSize)
        self.mSampleTableRevert.clicked.connect(self.onSampleChanged)  # just reload the sample
        self.mSampleTableSave.clicked.connect(self.onSampleTableSave)

        # classifier
        self.mRunClassifierCreate.clicked.connect(self.runClassifierCreate)

        # feature selection
        # - clustering
        self.mRunFeatureClustering.clicked.connect(self.runFeatureClustering)
        self.mRunFeatureClusteringSelect.clicked.connect(self.runFeatureClusteringSelect)
        # - ranking
        self.mRunFeatureRankingInternal.clicked.connect(self.runFeatureRankingInternal)
        self.mRunFeatureRankingPermutation.clicked.connect(self.runFeatureRankingPermutation)
        self.mRunFeatureRankingRFE.clicked.connect(self.runFeatureRankingRFE)
        self.mRunFeatureRankingSFSForward.clicked.connect(self.runFeatureRankingSFSForward)
        self.mRunFeatureRankingSFSBackward.clicked.connect(self.runFeatureRankingSFSBackward)
        self.mRunFeatureRankingSelect.clicked.connect(self.runFeatureRankingSelect)

        # fit
        self.mRunClassifierFit.clicked.connect(self.runClassifierFit)
        self.mRunValidation.clicked.connect(self.runValidation)
        self.mRunCrossValidation.clicked.connect(self.runCrossValidation)

        # mapping
        self.mRunPredict.clicked.connect(self.runPredict)
        self.mRunMapValidation.clicked.connect(self.runMapValidation)

        # view files
        self.mViewSample.clicked.connect(self.onViewFile)
        self.mViewTrainSample.clicked.connect(self.onViewFile)
        self.mViewTestSample.clicked.connect(self.onViewFile)
        self.mViewClassifier.clicked.connect(self.onViewFile)
        self.mViewFeatureClustering.clicked.connect(self.onViewFile)
        self.mViewTrainSampleClustered.clicked.connect(self.onViewFile)
        self.mViewTestSampleClustered.clicked.connect(self.onViewFile)
        self.mViewFeatureRanking.clicked.connect(self.onViewFile)
        self.mViewTrainSampleRanked.clicked.connect(self.onViewFile)
        self.mViewTestSampleRanked.clicked.connect(self.onViewFile)
        self.mViewClassifierFitted.clicked.connect(self.onViewFile)
        self.mViewClassifierPerformance.clicked.connect(self.onViewFile)
        self.mViewClassificationPerformance.clicked.connect(self.onViewFile)

        # update sample description labels
        self.mTrainSample.fileChanged.connect(lambda: self.updateSampleInfo(self.mTrainSample, self.mTrainSampleInfo))
        self.mTrainSampleClustered.fileChanged.connect(
            lambda: self.updateSampleInfo(self.mTrainSampleClustered, self.mTrainSampleClusteredInfo))
        self.mTrainSampleRanked.fileChanged.connect(
            lambda: self.updateSampleInfo(self.mTrainSampleRanked, self.mTrainSampleRankedInfo))
        self.mTestSample.fileChanged.connect(lambda: self.updateSampleInfo(self.mTestSample, self.mTestSampleInfo))
        self.mTestSampleClustered.fileChanged.connect(
            lambda: self.updateSampleInfo(self.mTestSampleClustered, self.mTestSampleClusteredInfo))
        self.mTestSampleRanked.fileChanged.connect(
            lambda: self.updateSampleInfo(self.mTestSampleRanked, self.mTestSampleRankedInfo))
        for label in [self.mTrainSampleInfo, self.mTrainSampleClusteredInfo, self.mTrainSampleRankedInfo,
                      self.mTestSampleInfo, self.mTestSampleClusteredInfo, self.mTestSampleRankedInfo]:
            label.hide()

        # update default roots when working directory changed
        #self.mWorkingDirectory.fileChanged.connect(self.onWorkingDirectoryChanged)

        #self.mSample.fileChanged.connect(self.onFileChanged)

    def onFileChanged(self, absPath):
        assert 0 # todo fix relative storage
        # assure that the relative path to the default directory is visible
        if isabs(absPath):
            mFile: QgsFileWidget = self.sender()
            relPath = relpath(absPath, mFile.defaultRoot())
            mFile.setFilePath(relPath)

    def initFiles(self):
        self.mWorkingDirectory.setFilePath(join(gettempdir(), 'EnMAPBox', 'ClassificationWorkflow'))
        self.onWorkingDirectoryChanged()

    def initLayers(self):
        self.mClassification.setFilters(QgsMapLayerProxyModel.RasterLayer)

    def initClassifier(self):
        pass

    def _createAlgorithmDialogWrapper(self, onFinish=None, onCancel=None):
        class AlgorithmDialogWrapper(AlgorithmDialog):
            def finish(self_, successful, result, context, feedback, in_place=False):
                super().finish(successful, result, context, feedback, in_place)
                if successful:
                    if self.mDialogAutoClose.isChecked():
                        self_.close()
                    if onFinish is not None:
                        onFinish(result, context, feedback)
                        feedback: QgsProcessingFeedback = self_.feedback
                        self.mLog.moveCursor(QTextCursor.End)
                        self.mLog.insertPlainText(feedback.textLog() + '\n##########\n\n')
                        self.mLog.verticalScrollBar().setValue(self.mLog.verticalScrollBar().maximum())

        return AlgorithmDialogWrapper

    @errorHandled(successMessage='performed quick mapping')
    def runQuickMapping(self, *args):

        # create sample
        labels = self.mQuickLabels.currentLayer()
        if labels is None:
            self.pushParameterMissingLayer('Map with class labels')
            raise MissingParameterError()
        features = self.mQuickFeatures.currentLayer()
        if features is None:
            self.pushParameterMissingLayer('Raster with features')
            raise MissingParameterError()

        parameters = {
            PrepareClassificationSampleFromMapAndRaster.P_MAP: self.mQuickLabels.currentLayer(),
            PrepareClassificationSampleFromMapAndRaster.P_RASTER: self.mQuickFeatures.currentLayer()
        }
        self.runImportFromAlg(PrepareClassificationSampleFromMapAndRaster(), parameters, autoRun=True)

        # fit classifier
        self.mRunClassifierCreate.clicked.emit()
        self.mRunClassifierFit.clicked.emit()

        # mapping
        self.mRaster.setLayer(self.mQuickFeatures.currentLayer())
        self.mRunPredict.clicked.emit()
        self.mGroundTruth.setLayer(self.mQuickGroundTruth.currentLayer())
        self.mRunMapValidation.clicked.emit()

    @errorHandled(successMessage='imported sample')
    def runImportFromAlg(self, alg, parameters, *args, autoRun=False):

        if parameters is None:
            parameters = dict()
        parameters[alg.P_OUTPUT_SAMPLE] = join(self.mWorkingDirectory.filePath(), self.mSampleBasename.text() + '.pkl')

        wrapper = self._createAlgorithmDialogWrapper(
            onFinish=lambda result, *args: self.mSample.setFilePath(result[alg.P_OUTPUT_SAMPLE])
        )
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper, autoRun=autoRun
        )

    @errorHandled(successMessage='splitted sample')
    def runSplitSample(self, *args):
        filename = self.mSample.filePath()
        if filename == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        trainNs = list()
        testNs = list()
        for i in range(self.mSampleTable.rowCount()):
            trainN: QgsSpinBox = self.mSampleTable.cellWidget(i, 4)
            testN: QgsSpinBox = self.mSampleTable.cellWidget(i, 5)
            trainNs.append(trainN.value())
            testNs.append(testN.value())

        # draw train sample
        alg = SubsampleClassificationSampleAlgorithm()

        def onFinish(result, *args):
            self.mTrainSample.setFilePath(result[alg.P_OUTPUT_SAMPLE])
            self.mTestSample.setFilePath(result[alg.P_OUTPUT_COMPLEMENT])  # store complement here...

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        parameters = {alg.P_SAMPLE: filename, alg.P_N: str(trainNs)}
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

        # draw test sample from complement
        if sum(testNs) == 0:
            self.mTestSample.setFilePath('')
        else:
            filenameComplement = self.mTestSample.filePath()  # ... and get it back

            def onFinish(result, *args):
                self.mTestSample.setFilePath(result[alg.P_OUTPUT_SAMPLE])  # now, set the actual test sample

            wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
            parameters = {alg.P_SAMPLE: filenameComplement, alg.P_N: str(testNs)}
            self.enmapBox.showProcessingAlgorithmDialog(
                alg, parameters, show=True, modal=True, parent=self, wrapper=wrapper,
                autoRun=self.mDialogAutoRun.isChecked()
            )

        if sum(trainNs) == 0:
            self.mTrainSample.setFilePath('')

    @errorHandled(successMessage='created (unfitted) classifier')
    def runClassifierCreate(self, *args):

        def onFinish(result, *args):
            self.mClassifier.setFilePath(result[alg.P_OUTPUT_CLASSIFIER])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = FitGenericClassifier()
        parameters = {alg.P_CODE: self.mCode.toPlainText()}
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage=None)
    def getSampleFilenamesForClustering(self, *args):
        filenameTrain = self.mTrainSample.filePath()
        filenameTest = self.mTestSample.filePath()
        if filenameTrain == '':
            filenameTrain = self.mSample.filePath()
            filenameTest = ''
        return filenameTrain, filenameTest

    @errorHandled(successMessage=None)
    def getSampleFilenamesForRanking(self, *args):
        filenameTrain = self.mTrainSampleClustered.filePath()
        filenameTest = self.mTestSampleClustered.filePath()
        if filenameTrain == '':
            filenameTrain, filenameTest = self.getSampleFilenamesForClustering()
        return filenameTrain, filenameTest

    @errorHandled(successMessage=None)
    def getSampleFilenamesForFitting(self, *args):
        filenameTrain = self.mTrainSampleRanked.filePath()
        filenameTest = self.mTestSampleRanked.filePath()
        if filenameTrain == '':
            filenameTrain, filenameTest = self.getSampleFilenamesForRanking()
        return filenameTrain, filenameTest

    @errorHandled(successMessage=None)
    def getClassifierFittedFilename(self, *args):
        return self.mClassifierFitted.filePath()

    @errorHandled(successMessage=None)
    def getClassifierFilename(self, *args):
        filename = self.getClassifierFittedFilename()
        if filename == '':
            filename = self.mClassifier.filePath()
        return filename

    @errorHandled(successMessage='clustered features')
    def runFeatureClustering(self, *args):

        filenameTrain, filenameTest = self.getSampleFilenamesForClustering()
        if filenameTrain == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        def onFinish(result, *args):
            self.mFeatureClustering.setFilePath(result[alg.P_OUTPUT_REPORT])
            if self.mDialogAutoOpen.isChecked():
                self.openWebbrowser(result[alg.P_OUTPUT_REPORT])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = FeatureClusteringHierarchicalAlgorithm()
        parameters = {alg.P_SAMPLE: filenameTrain}
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage='selected most representative features')
    def runFeatureClusteringSelect(self, *args):
        self.mMessageBar.clearWidgets()

        if self.mFeatureClustering.filePath() == '':
            self.pushParameterMissing('Clustering', runAlgo='Cluster features *')
            raise MissingParameterError()

        filenameTrain, filenameTest = self.getSampleFilenamesForClustering()
        if filenameTrain == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        if self.mFeatureClusteringN.value() == 0:
            self.pushParameterWrongValue('n', 'select cluster hierarchy level n>0')
            raise MissingParameterError()

        # get feature subset
        dump = Utils.jsonLoad(self.mFeatureClustering.filePath() + '.json')
        featureList = [index + 1 for index in dump['feature_subset_hierarchy'][self.mFeatureClusteringN.value() - 1]]

        # subset train sample
        def onFinish(result, *args):
            self.mTrainSampleClustered.setFilePath(result[alg.P_OUTPUT_SAMPLE])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = SelectFeatureSubsetFromSampleAlgorithm()
        parameters = {
            alg.P_SAMPLE: self.mTrainSample.filePath(),
            alg.P_FEATURE_LIST: str(featureList)
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

        # subset test sample
        if self.mTestSample.filePath() != '':
            def onFinish(result, *args):
                self.mTestSampleClustered.setFilePath(result[alg.P_OUTPUT_SAMPLE])

            wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
            alg = SelectFeatureSubsetFromSampleAlgorithm()
            parameters = {
                alg.P_SAMPLE: self.mTestSample.filePath(),
                alg.P_FEATURE_LIST: str(featureList)
            }
            self.enmapBox.showProcessingAlgorithmDialog(
                alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
                autoRun=self.mDialogAutoRun.isChecked()
            )

    @errorHandled(successMessage='clustered features')
    def runFeatureRankingInternal(self, *args):
        pass

    @errorHandled(successMessage='ranked features')
    def runFeatureRankingPermutation(self, *args):

        filenameTrain, filenameTest = self.getSampleFilenamesForRanking()
        if filenameTrain == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        filenameClassifier = self.mClassifier.filePath()
        if filenameClassifier == '':
            self.pushParameterMissingClassifier()
            raise MissingParameterError()

        def onFinish(result, *args):
            self.mFeatureRanking.setFilePath(result[alg.P_OUTPUT_REPORT])
            if self.mDialogAutoOpen.isChecked():
                self.openWebbrowser(result[alg.P_OUTPUT_REPORT])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = ClassifierFeatureRankingPermutationImportanceAlgorithm()
        parameters = {
            alg.P_TRAIN_SAMPLE: filenameTrain,
            alg.P_TEST_SAMPLE: filenameTest,
            alg.P_CLASSIFIER: self.mClassifier.filePath()
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage='clustered features')
    def runFeatureRankingRFE(self, *args):
        pass

    @errorHandled(successMessage='clustered features')
    def runFeatureRankingSFSForward(self, *args):
        pass

    @errorHandled(successMessage='clustered features')
    def runFeatureRankingSFSBackward(self, *args):
        pass

    @errorHandled(successMessage='selected most important features')
    def runFeatureRankingSelect(self, *args):
        if self.mFeatureRanking.filePath() == '':
            self.pushParameterMissing('Ranking', runAlgo='Rank features *')
            return

        filenameTrain, filenameTest = self.getSampleFilenamesForRanking()
        if filenameTrain == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        if self.mFeatureRankingN.value() == 0:
            self.pushParameterWrongValue('n', 'select number of features (n>0) to subset')
            raise MissingParameterError()

        # get feature subset
        dump = Utils.jsonLoad(self.mFeatureRanking.filePath() + '.json')
        featureList = [index + 1 for index in dump['feature_subset_hierarchy'][self.mFeatureRankingN.value() - 1]]

        # subset train sample
        def onFinish(result, *args):
            self.mTrainSampleRanked.setFilePath(result[alg.P_OUTPUT_SAMPLE])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = SelectFeatureSubsetFromSampleAlgorithm()
        parameters = {
            alg.P_SAMPLE: filenameTrain,
            alg.P_FEATURE_LIST: str(featureList)
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

        # subset test sample
        if filenameTest != '':
            def onFinish(result, *args):
                self.mTestSampleRanked.setFilePath(result[alg.P_OUTPUT_SAMPLE])

            wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
            alg = SelectFeatureSubsetFromSampleAlgorithm()
            parameters = {
                alg.P_SAMPLE: filenameTest,
                alg.P_FEATURE_LIST: str(featureList)
            }
            self.enmapBox.showProcessingAlgorithmDialog(
                alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
                autoRun=self.mDialogAutoRun.isChecked()
            )

    @errorHandled(successMessage='fitted classifier')
    def runClassifierFit(self, *args):

        filenameTrain, _ = self.getSampleFilenamesForRanking()
        if filenameTrain == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        def onFinish(result, *args):
            self.mClassifierFitted.setFilePath(result[alg.P_OUTPUT_CLASSIFIER])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = FitGenericClassifier()
        parameters = {
            alg.P_SAMPLE: filenameTrain,
            alg.P_CODE: self.mCode.toPlainText()
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage='estimated classifier test performance')
    def runValidation(self, *args):

        _, filenameTest = self.getSampleFilenamesForRanking()
        if filenameTest == '':
            self.pushParameterMissingTestSample()
            raise MissingParameterError()

        filenameClassifier = self.getClassifierFittedFilename()
        if filenameClassifier == '':
            self.pushParameterMissingClassifierFitted()
            raise MissingParameterError()

        def onFinish(result, *args):
            self.mClassifierPerformance.setFilePath(result[alg.P_OUTPUT_REPORT])
            if self.mDialogAutoOpen.isChecked():
                self.openWebbrowser(result[alg.P_OUTPUT_REPORT])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = ClassifierPerformanceAlgorithm()
        parameters = {
            alg.P_CLASSIFIER: filenameClassifier,
            alg.P_SAMPLE: filenameTest
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage='estimated classifier cross-validation performance')
    def runCrossValidation(self, *args):

        filenameTrain, _ = self.getSampleFilenamesForRanking()
        if filenameTrain == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        filenameClassifier = self.getClassifierFilename()
        if filenameClassifier == '':
            self.pushParameterMissingClassifier()
            raise MissingParameterError()

        def onFinish(result, *args):
            self.mClassifierPerformance.setFilePath(result[alg.P_OUTPUT_REPORT])
            if self.mDialogAutoOpen.isChecked():
                self.openWebbrowser(result[alg.P_OUTPUT_REPORT])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = ClassifierPerformanceAlgorithm()
        parameters = {
            alg.P_CLASSIFIER: filenameClassifier,
            alg.P_SAMPLE: filenameTrain,
            alg.P_NFOLD: self.mNFold.value()
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage='predicted maps')
    def runPredict(self, *args):

        filenameClassifier = self.getClassifierFilename()
        if filenameClassifier == '':
            self.pushParameterMissingClassifier()
            raise MissingParameterError()

        raster: QgsRasterLayer = self.mRaster.currentLayer()
        if raster is None:
            self.pushParameterMissingRaster()
            raise MissingParameterError()

        # classification
        filenameClassification = join(self.mWorkingDirectory.filePath(), self.mClassificationBasename.text() + '.tif')

        def onFinish(result, *args):
            layer = QgsRasterLayer(filenameClassification, basename(filenameClassification))
            QgsProject.instance().addMapLayer(layer)
            self.mClassification.setLayer(layer)

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = PredictClassificationAlgorithm()
        parameters = {
            alg.P_CLASSIFIER: filenameClassifier,
            alg.P_RASTER: raster,
            alg.P_MASK: self.mMask.currentLayer(),
            alg.P_OUTPUT_RASTER: filenameClassification
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

        if not self.mProbabilityCheck.isChecked():
            return

        # probability
        filenameProbability = join(self.mWorkingDirectory.filePath(), self.mProbabilityBasename.text() + '.tif')

        def onFinish(result, *args):
            layer = QgsRasterLayer(filenameProbability, basename(filenameProbability))
            QgsProject.instance().addMapLayer(layer)
            self.mProbability.setLayer(layer)

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = PredictClassPropabilityAlgorithm()
        parameters = {
            alg.P_CLASSIFIER: filenameClassifier,
            alg.P_RASTER: raster,
            alg.P_MASK: self.mMask.currentLayer(),
            alg.P_OUTPUT_RASTER: filenameProbability
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

        # colorize probability as RGB
        filenameRgb = join(self.mWorkingDirectory.filePath(), self.mProbabilityBasename.text() + '_rgb.tif')

        wrapper = self._createAlgorithmDialogWrapper()
        alg = ColorizeClassProbabilityAlgorithm()
        parameters = {
            alg.P_SCORE: filenameProbability,
            alg.P_STYLE: filenameClassification,
            alg.P_OUTPUT_RASTER: filenameRgb
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    @errorHandled(successMessage='predicted maps')
    def runMapValidation(self, *args):

        classification = self.mClassification.currentLayer()
        if classification is None:
            self.pushParameterMissingLayer('Classification map')
            raise MissingParameterError()

        reference = self.mGroundTruth.currentLayer()
        if reference is None:
            self.pushParameterMissingLayer('Ground truth')
            raise MissingParameterError()

        filenameReport = join(
            self.mWorkingDirectory.filePath(), self.mClassificationPerformanceBasename.text() + '.html'
        )

        def onFinish(result, *args):
            self.mClassificationPerformance.setFilePath(filenameReport)
            if self.mDialogAutoOpen.isChecked():
                self.openWebbrowser(result[alg.P_OUTPUT_REPORT])

        wrapper = self._createAlgorithmDialogWrapper(onFinish=onFinish)
        alg = ClassificationPerformanceStratifiedAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: classification,
            alg.P_REFERENCE: reference,
            alg.P_STRATIFICATION: classification,
            alg.P_OUTPUT_REPORT: filenameReport
        }
        self.enmapBox.showProcessingAlgorithmDialog(
            alg, parameters=parameters, show=True, modal=True, parent=self, wrapper=wrapper,
            autoRun=self.mDialogAutoRun.isChecked()
        )

    def updateSampleInfo(self, file: QgsFileWidget, label: QLabel):
        filename = file.filePath()
        if exists(filename) and filename.endswith('.pkl'):
            dump = ClassifierDump(**Utils.pickleLoad(filename))
            label.setText(f'{dump.X.shape[0]} samples {dump.X.shape[1]} features  {len(dump.categories)} categories')
            label.show()
        else:
            label.setText('')
            label.hide()

    @errorHandled
    def onWorkingDirectoryChanged(self, *args):
        wd = self.mWorkingDirectory.filePath()
        for mFile in [self.mSample, self.mTrainSample, self.mTestSample,
                     self.mTrainSampleClustered, self.mTestSampleClustered,
                     self.mTrainSampleRanked, self.mTestSampleRanked,
                     self.mClassifier, self.mClassifierFitted,
                     self.mFeatureClustering, self.mFeatureRanking,
                     self.mClassifierPerformance, self.mClassificationPerformance]:
            mFile.setDefaultRoot(wd)

    @errorHandled
    def onSampleChanged(self, *args):
        filename = self.mSample.filePath()
        if exists(filename) and filename.endswith('.pkl'):
            dump = ClassifierDump(**Utils.pickleLoad(filename))
        else:
            dump = ClassifierDump(categories=[], features=[], X=np.zeros((0, 0)), y=np.zeros((0, 1)))

        self.updateSampleInfo(self.mSample, self.mSampleInfo)

        def makeSpinBoxes(c: Category) -> Tuple[int, QgsSpinBox, QgsSpinBox]:
            n = int(np.sum(dump.y == c.value))
            trainN = QgsSpinBox(self.mSampleTable)
            testN = QgsSpinBox(self.mSampleTable)
            trainN.setMinimum(0)
            trainN.setMaximum(n)
            trainN.setValue(n)
            testN.setMinimum(0)
            testN.setMaximum(n)
            testN.setValue(0)
            trainN.valueChanged.connect(lambda v: testN.setValue(min(testN.value(), n - v)))
            testN.valueChanged.connect(lambda v: trainN.setValue(min(trainN.value(), n - v)))
            return n, trainN, testN

        # setup categories
        self.mSampleTable.setRowCount(len(dump.categories))
        headers = list()
        for i, category in enumerate(dump.categories):
            colorButton = QgsColorButton(self.mSampleTable)
            colorButton.setColor(QColor(category.color))
            colorButton.setShowMenu(False)
            colorButton.setAutoRaise(True)
            n, trainN, testN = makeSpinBoxes(category)
            self.mSampleTable.setCellWidget(i, 0, QLabel(f'  {category.value}  ', self.mSampleTable))
            self.mSampleTable.setItem(i, 1, QTableWidgetItem(category.name))
            self.mSampleTable.setCellWidget(i, 2, colorButton)
            if len(dump.y) > 0:
                size = f'  {n} / {np.round(np.divide(n, len(dump.y)) * 100, 1)}%  '
            else:
                size = f'  {n}  '
            self.mSampleTable.setCellWidget(i, 3, QLabel(size, self.mSampleTable))
            self.mSampleTable.setCellWidget(i, 4, trainN)
            self.mSampleTable.setCellWidget(i, 5, testN)
            # headers.append(f'{category.value}: {category.name} [{n}] ({round(n / len(dump.y) * 100, 1)}%)')
            headers.append(f'{i + 1}:')
        self.mSampleTable.setVerticalHeaderLabels(headers)
        self.mSampleTable.resizeColumnsToContents()

        # setup features
        self.mSampleTable2.setRowCount(len(dump.features))
        headers = list()
        for i, feature in enumerate(dump.features):
            self.mSampleTable2.setItem(i, 0, QTableWidgetItem(feature))
            # headers.append(f'{i + 1}: {feature}')
            headers.append(f'{i + 1}:')
        self.mSampleTable2.setVerticalHeaderLabels(headers)
        self.mSampleTable2.resizeColumnsToContents()

    @errorHandled(successMessage='updated sample categories')
    def onSampleTableSave(self, *args):
        filename = self.mSample.filePath()
        if filename == '':
            self.pushParameterMissingSample()
            raise MissingParameterError()

        dump = ClassifierDump(**Utils.pickleLoad(filename))

        categories = list()
        for i, origCategory in enumerate(dump.categories):
            name: QTableWidgetItem = self.mSampleTable.item(i, 1)
            color: QgsColorButton = self.mSampleTable.cellWidget(i, 2)
            categories.append(Category(origCategory.value, name.text(), color.color().name()))

        features = list()
        for i, origFeature in enumerate(dump.features):
            name: QTableWidgetItem = self.mSampleTable.item(i, 0)
            features.append(name)

        # overwrite sample
        dump = dump.withCategories(categories).withFeatures(features)
        Utils.pickleDump(dump._asdict(), filename)

    @errorHandled(successMessage=None)
    def onSetTrainSize(self, *args):
        n = self.mSamplesSizeAbsoluteValue.value()
        p = self.mSamplesSizeRelativeValue.value() / 100.
        for i in range(self.mSampleTable.rowCount()):
            box: QgsSpinBox = self.mSampleTable.cellWidget(i, 4)
            ni = n
            if self.mSamplesSizeRelative.isChecked():
                ni = int(round(p * box.maximum()))
            box.setValue(ni)

    @errorHandled(successMessage=None)
    def onSetTestSize(self, *args):
        n = self.mSamplesSizeAbsoluteValue.value()
        p = self.mSamplesSizeRelativeValue.value() / 100.
        for i in range(self.mSampleTable.rowCount()):
            box: QgsSpinBox = self.mSampleTable.cellWidget(i, 5)
            ni = n
            if self.mSamplesSizeRelative.isChecked():
                ni = int(round(p * box.maximum()))
            box.setValue(ni)

    @errorHandled(successMessage=None)
    def onSetSplitSize(self, *args):
        # assign all samples for testing first...
        for i in range(self.mSampleTable.rowCount()):
            box: QgsSpinBox = self.mSampleTable.cellWidget(i, 5)
            box.setValue(box.maximum())
        # ...and finally set the correct train sizes, which will correct the test sizes
        self.onSetTrainSize()

    def onViewFile(self):
        files = {
            self.mViewSample: self.mSample,
            self.mViewTrainSample: self.mTrainSample,
            self.mViewTestSample: self.mTestSample,
            self.mViewClassifier: self.mClassifier,
            self.mViewFeatureClustering: self.mFeatureClustering,
            self.mViewTrainSampleClustered: self.mTrainSampleClustered,
            self.mViewTestSampleClustered: self.mTestSampleClustered,
            self.mViewFeatureRanking: self.mFeatureRanking,
            self.mViewTrainSampleRanked: self.mTrainSampleRanked,
            self.mViewTestSampleRanked: self.mTestSampleRanked,
            self.mViewClassifierFitted: self.mClassifierFitted,
            self.mViewClassifierPerformance: self.mClassifierPerformance,
            self.mViewClassificationPerformance: self.mClassificationPerformance
        }

        file: QgsFileWidget = files[self.sender()]
        filename = file.filePath()

        if filename.endswith('.pkl'):
            dump = Utils.pickleLoad(filename)
            filename = filename + '.json'
            Utils.jsonDump(dump, filename)
        self.openWebbrowser(filename)

    def openWebbrowser(self, filename: str):
        if filename == '':
            return

        if exists(filename):
            webbrowser.open_new_tab(filename)

    def pushParameterMissing(self, name: str, message='', runAlgo: str = None):
        if runAlgo is not None:
            message = f"run '{runAlgo}' algorithm first"
        self.mMessageBar.pushInfo(f'Missing parameter ({name})', message)

    def pushParameterMissingSample(self):
        self.pushParameterMissing('Sample', runAlgo='Import from *')

    def pushParameterMissingTestSample(self):
        self.pushParameterMissing('Test Sample', runAlgo='Split sample')

    def pushParameterMissingClassifier(self):
        self.pushParameterMissing('Classifier', runAlgo='Create classifier')

    def pushParameterMissingClassifierFitted(self):
        self.pushParameterMissing('Classifier (fitted)', runAlgo='Fit classifier')

    def pushParameterMissingLayer(self, name):
        self.pushParameterMissing(name, message='select layer first')

    def pushParameterMissingRaster(self):
        self.pushParameterMissingLayer('Raster')

    def pushParameterWrongValue(self, name, message):
        self.mMessageBar.pushInfo(f'Wrong parameter value ({name})', message)
