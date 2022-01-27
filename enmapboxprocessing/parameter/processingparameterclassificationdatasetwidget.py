from os.path import basename

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QToolButton, QMenu
from PyQt5.uic import loadUi
from qgis._gui import QgsFileWidget

from enmapbox import EnMAPBox
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

        self.menu = QMenu()
        self.menu.setToolTipsVisible(True)

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
            action = self.menu.addAction(alg.displayName())
            action.setIcon(icon)
            action.setText(alg.displayName())
            action.triggered.connect(self.onCreateClicked)
            action.alg = alg

        if EnMAPBox.instance() is not None:
            self.menu.addSeparator()
            for filename in EnMAPBox.instance().dataSources('MODEL', True):
                if filename.endswith('.pkl'):
                    action = self.menu.addAction(alg.displayName())
                    action.setIcon(QIcon(':/images/themes/default/mIconFile.svg'))
                    action.setText(basename(filename))
                    action.setToolTip(rf'<html><head/><body><p>{filename}</p></body></html>')
                    action.triggered.connect(self.onFilenameClicked)
                    action.filename = filename

        self.mCreate.setMenu(self.menu)

    def value(self) -> str:
        return self.mFile.filePath()

    def setValue(self, value):
        self.mFile.setFilePath(value)

    filePath = value
    setFilePath = setValue

    def onCreateClicked(self):
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()

        class AlgorithmDialogWrapper(AlgorithmDialog):
            def finish(self_, successful, result, context, feedback, in_place=False):
                super().finish(successful, result, context, feedback, in_place)
                if successful:
                    filename = result['outputClassificationDataset']
                    self.mFile.setFilePath(filename)

                    # add to the list!
                    action = self.menu.addAction(alg.displayName())
                    action.setIcon(QIcon(':/images/themes/default/mIconFile.svg'))
                    action.setText(basename(filename))
                    action.setToolTip(rf'<html><head/><body><p>{filename}</p></body></html>')
                    action.triggered.connect(self.onFilenameClicked)
                    action.filename = filename

                    self_.close()

        alg = self.sender().alg
        enmapBox.showProcessingAlgorithmDialog(alg, modal=True, wrapper=AlgorithmDialogWrapper, parent=self)

    def onFilenameClicked(self):
        filename = self.sender().filename
        self.mFile.setFilePath(filename)

class ProcessingParameterClassificationDatasetWidgetWrapper(WidgetWrapper):
    widget: ProcessingParameterClassificationDatasetWidget

    def createWidget(self):
        #if self.dialogType == DIALOG_MODELER:
        #    raise NotImplementedError()
        #elif self.dialogType == DIALOG_BATCH:
        #    raise NotImplementedError()
        #else:
        return ProcessingParameterClassificationDatasetWidget()

    def setValue(self, value):
        #if self.dialogType == DIALOG_MODELER:
        #    raise NotImplementedError()
        #elif self.dialogType == DIALOG_BATCH:
        #    raise NotImplementedError()
        #else:
        self.widget.setValue(value)

    def value(self):
        #if self.dialogType == DIALOG_MODELER:
        #    raise NotImplementedError()
        #elif self.dialogType == DIALOG_BATCH:
        #    raise NotImplementedError()
        #else:
        return self.widget.value()
