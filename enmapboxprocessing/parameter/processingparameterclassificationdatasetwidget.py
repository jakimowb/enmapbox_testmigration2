from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QToolButton, QMenu
from PyQt5.uic import loadUi
from qgis._gui import QgsFileWidget

from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedlibraryalgorithm import \
    PrepareClassificationDatasetFromCategorizedLibraryAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedrasteralgorithm import \
    PrepareClassificationDatasetFromCategorizedRasterAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvectoralgorithm import \
    PrepareClassificationDatasetFromCategorizedVectorAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvectorandfieldsalgorithm import \
    PrepareClassificationDatasetFromCategorizedVectorAndFieldsAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcodealgorithm import \
    PrepareClassificationDatasetFromCodeAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromfilesalgorithm import \
    PrepareClassificationDatasetFromFilesAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromtablealgorithm import \
    PrepareClassificationDatasetFromTableAlgorithm
from processing import AlgorithmDialog
from processing.gui.wrappers import WidgetWrapper, DIALOG_MODELER, DIALOG_BATCH


class ProcessingParameterClassificationDatasetWidget(QWidget):
    mFile: QgsFileWidget
    mCreate: QToolButton

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)

        menu = QMenu()

        for alg, icon in [
            (PrepareClassificationDatasetFromCategorizedVectorAlgorithm(),
             QIcon(':/images/themes/default/mIconVector.svg')),

            (PrepareClassificationDatasetFromCategorizedRasterAlgorithm(),
             QIcon(':/enmapbox/gui/ui/icons/filelist_classification.svg')),

            (PrepareClassificationDatasetFromCategorizedLibraryAlgorithm(),
             QIcon(':/qps/ui/icons/speclib.svg')),

            (PrepareClassificationDatasetFromCategorizedVectorAndFieldsAlgorithm(),
             QIcon(':/images/themes/default/mActionOpenTable.svg')),

            (PrepareClassificationDatasetFromTableAlgorithm(),
             QIcon(':/images/themes/default/mActionOpenTable.svg')),

            (PrepareClassificationDatasetFromCodeAlgorithm(),
             QIcon(':/images/themes/default/mIconPythonFile.svg')),

            (PrepareClassificationDatasetFromFilesAlgorithm(),
             QIcon(':/images/themes/default/mIconFile.svg')),

        ]:
            action = menu.addAction(alg.displayName())
            action.setIcon(icon)
            action.setText(alg.displayName())
            action.triggered.connect(self.onCreateClicked)
            action.alg = alg

        self.mCreate.setMenu(menu)

    def value(self) -> str:
        return self.mFile.filePath()

    def onCreateClicked(self):
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()

        class AlgorithmDialogWrapper(AlgorithmDialog):
            def finish(self_, successful, result, context, feedback, in_place=False):
                super().finish(successful, result, context, feedback, in_place)
                if successful:
                    self.mFile.setFilePath(result['outputClassificationDataset'])
                    self_.close()

        alg = self.sender().alg
        enmapBox.showProcessingAlgorithmDialog(alg, modal=True, wrapper=AlgorithmDialogWrapper, parent=self)


class ProcessingParameterClassificationDatasetWidgetWrapper(WidgetWrapper):
    widget: ProcessingParameterClassificationDatasetWidget

    def createWidget(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return ProcessingParameterClassificationDatasetWidget()

    def setValue(self, value):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            self.widget.mFile.setFilePath(value)

    def value(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return self.widget.value()
