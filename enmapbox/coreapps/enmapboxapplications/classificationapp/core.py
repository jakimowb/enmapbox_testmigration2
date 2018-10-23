import inspect
import tempfile
import traceback
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapboxapplications.utils import loadUIFormClass
from hubflow.core import *
from enmapboxapplications.classificationapp.script import classificationWorkflow, ProgressBar


pathUi = join(dirname(__file__), 'ui')


class ClassificationWorkflowApp(QMainWindow, loadUIFormClass(pathUi=join(pathUi, 'main.ui'))):

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.uiInfo_ = QLabel()
        self.statusBar().addWidget(self.uiInfo_, 1)

        self.initMaps()
        self.initClassifier()
        self.initOutputs()
        self.uiRaster_.layerChanged.connect(self.onRasterLayerChanged)
        self.uiClassification_.layerChanged.connect(self.onClassificationLayerChanged)
        self.uiExecute_.clicked.connect(self.execute)
        self.uiAttribute_.fieldChanged.connect(self.initClasses)
        self.uiAttribute_.hide()
        self.uiAttributeLabel_.hide()
        self.uiOversampling_.valueChanged.connect(self.onRasterizationOptionsChanged)
        self.uiPurity_.valueChanged.connect(self.onRasterizationOptionsChanged)
        self.uiAdvanced_.clicked.connect(self.onAdvancedClicked)
        self.uiAdvanced_.hide() # advanced button not wanted :-(, use F1 key instead :-)
        self.uiSampleSizePercent_.valueChanged.connect(self.updateSpinboxes)
        self.uiSampleSizePixel_.valueChanged.connect(self.updateSpinboxes)
        self.uiStacked_.setEnabled(False)
        self.spinboxes = None
        self._advancedWidgets = [self.uiOversampling_, self.uiPurity_]
        self.onAdvancedClicked()


    def progressBar(self):
        return ProgressBar(bar=self.uiProgressBar())

    def log(self, text):
        self.uiInfo_.setText(str(text))
        QCoreApplication.processEvents()

    def uiAttributeLabel(self):
        obj = self.uiAttributeLabel_ #inspect.getcurrentframe()
        assert isinstance(obj, QLabel)
        return obj

    def uiProgressBar(self):
        obj = self.uiProgressBar_
        assert isinstance(obj, QProgressBar)
        return obj

    def pickClassColor(self):
        w = self.sender()
        color = QColorDialog.getColor()
        if color.name() != '#000000':
            w.setStyleSheet('background-color: {}'.format(color.name()))

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_F1:
            self.onAdvancedClicked()

    def onAdvancedClicked(self, *args):
        for w in self._advancedWidgets:
            w.setVisible(w.isHidden())

    def onRasterizationOptionsChanged(self, *args):
        self.uiAttribute_.setCurrentIndex(-1)
        self.initClasses()

    def onRasterLayerChanged(self, *args):
        self.uiClassification_.setLayer(None)
        self.uiClassification_.setEnabled(self.uiRaster_.currentLayer() is not None)
        self.uiAttribute_.hide()
        self.uiAttributeLabel_.hide()
        self.uiAttribute_.setCurrentIndex(-1)
        self.initClasses()

    def onClassificationLayerChanged(self, *args):
        layer = self.uiClassification_.currentLayer()
        isVector = isinstance(layer, QgsVectorLayer)

        try:
            openVectorDataset(filename=layer.source())
        except Exception as error:
            self.log('GDAL Error:{}'.format(str(error)))
            self.uiAttribute_.setCurrentIndex(-1)
            self.uiClassification_.setLayer(None)
            return

        self.uiAttribute_.setEnabled(isVector)
        self.uiAttribute_.setVisible(isVector)
        self.uiAttributeLabel().setVisible(isVector)

        self.uiOversampling_.setEnabled(isVector)
        self.uiPurity_.setEnabled(isVector)

    def updateSpinboxes(self, *args):
        self.log('')

        if self.uiSampeMode_.currentText() == 'Percent':
            value = float(self.uiSampleSizePercent_.value())
        else:
            value = float(self.uiSampleSizePixel_.value())

        for spinbox, count in zip(self.spinboxes, self.counts):
            if self.uiSampeMode_.currentText() == 'Percent':
                spinbox.setValue(int(round(count * value / 100.)))
            else:
                spinbox.setValue(int(value))

    def rasterizationFilename(self):
        return '/vsimem/classification_workflow/rasterizedClassification.bsq'

    def initClasses(self, *args):

        self.log('')
        self.spinboxes = None
        self.uiStacked_.setEnabled(False)
        self.widget_.hide()
        self.widget_ = QWidget()
        self.layout_.addWidget(self.widget_)
        layout = QHBoxLayout(self.widget_)
        self.updateTotalSamples()

        layer = self.uiClassification_.currentLayer()
        if layer is None:
            return
        elif isinstance(layer, QgsVectorLayer):
            self.uiAttribute_.setEnabled(True)
            name = self.uiAttribute_.currentField()
            if name == '': # no field selected yet
                return

            filename = layer.source()
            ds = openVectorDataset(filename=filename)

            if ds.ogrDataSource().GetDriver().LongName == 'GeoPackage' and name == 'fid':
                self.log('Using GeoPackage fid as class attribute is not supported.')
                self.uiAttribute_.setCurrentIndex(-1)
                return


            if 'Point' in ds.geometryTypeName():
                oversampling = 1
            else:
                oversampling = self.uiOversampling_.value()

            vectorClassification = VectorClassification(filename=filename, classAttribute=name,
                                                        minDominantCoverage=self.uiPurity_.value() / 100.,
                                                        oversampling=oversampling)
            raster = Raster(filename=self.uiRaster_.currentLayer().source())
            self.log('Rasterize reference on raster grid with x{} resolution oversampling and select pixel with at leased {}% purity'.format(self.uiOversampling_.value(), self.uiPurity_.value()))
            classification = Classification.fromClassification(filename=self.rasterizationFilename(),
                                                               classification=vectorClassification, grid=raster.grid(),
                                                               **ApplierOptions(emitFileCreated=False, progressBar=self.progressBar()))
            self.log('')
            self.progressBar().setPercentage(0)

        elif isinstance(layer, QgsRasterLayer):
            self.uiAttribute_.setEnabled(False)
            filename = layer.source()
            raster = Raster(filename=filename)
            isClassification = raster.dataset().zsize() == 1

            if isClassification:
                classification = Classification(filename=filename)
            else:
                self.log('Selected layer is not a valid classification.')
                self.uiClassification_.setLayer(None)
                return
        else:
            assert 0

        counts = classification.statistics()
        self.counts = counts

        self.spinboxes = list()
        self.colors = list()
        self.names = list()

        for i in range(classification.classDefinition().classes()):

            layout1 = QVBoxLayout()
            layout2 = QHBoxLayout()
            color = QToolButton ()
            color.setStyleSheet('background-color: {}'.format(classification.classDefinition().color(i+1)._qColor.name()))
            color.setMaximumWidth(25)
            color.setMaximumHeight(18)

            color.setAutoRaise(True)
            color.clicked.connect(self.pickClassColor)
            self.colors.append(color)
            layout2.addWidget(color)
            layout2.addWidget(QLabel('{}:'.format(i + 1)))
            name = QLineEdit(classification.classDefinition().name(i + 1))
            text = name.text()
            fm = name.fontMetrics()
            w = fm.boundingRect(text).width()
            name.resize(w, name.height())
            name.setMinimumWidth(w+10)
            layout2.addWidget(name)
            # layout2.addWidget(QLabel('({} px)  '.format(counts[i])))
            self.names.append(name)
            layout1.addLayout(layout2)

            #layout3 = QHBoxLayout()
            spinbox = QSpinBox()
            spinbox.setRange(0, counts[i])
            spinbox.setSingleStep(1)
            spinbox.setValue(counts[i])
            spinbox.setSuffix(' ({} px)'.format(counts[i]))
            spinbox.valueChanged.connect(self.updateTotalSamples)
            self.spinboxes.append(spinbox)
            layout1.addWidget(spinbox)
            #layout3.addWidget(QLabel('({} px)  '.format(counts[i])))
            #layout1.addLayout(layout3)


            layout.addLayout(layout1)

            self.updateTotalSamples()

        # self.widget_.adjustSize()
        #self.adjustSize()

        self.uiStacked_.setEnabled(True)

    def updateTotalSamples(self, *args):
        total = 0
        if self.spinboxes is not None:
            for spinbox in self.spinboxes:
                total += int(spinbox.value())
        self.uiTotalSampleSize_.setText('Total sample size = {}'.format(total))

    def initMaps(self):
        assert isinstance(self.uiAttribute_, QgsFieldComboBox)
        self.uiRaster_.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiRaster2_.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiClassification_.layerChanged.connect(self.initClasses)
        self.uiAttribute_.setFilters(QgsFieldProxyModel.Numeric)  # All, Date, Double, Int, LongLong, Numeric, String, Time

    def initClassifier(self):
        from enmapboxgeoalgorithms.algorithms import ALGORITHMS, ClassifierFit
        self.classifiers = [alg for alg in ALGORITHMS if isinstance(alg, ClassifierFit)]
        self.classifierNames = [alg.name()[3:] for alg in self.classifiers]
        self.uiClassifier_.addItems(self.classifierNames)
        self.uiClassifier_.currentIndexChanged.connect(lambda index: self.uiCode_.setText(self.classifiers[index].code()))
        self.uiClassifier_.setCurrentIndex(self.classifierNames.index('RandomForestClassifier'))

    def initOutputs(self):
        outdir = tempfile.gettempdir()
        self.uiSampledClassificationFilename_.setStorageMode(QgsFileWidget.SaveFile)
#        self.uiSampledClassificationComplementFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiModelFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiClassificationFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiProbabilityFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiReportFilename_.setStorageMode(QgsFileWidget.SaveFile)

        self.uiSampledClassificationFilename_.setFilePath(join(outdir, 'sample.bsq'))
#        self.uiSampledClassificationComplementFilename_.setFilePath(join(outdir, 'complement.bsq'))
        self.uiModelFilename_.setFilePath(join(outdir, 'classifier.pkl'))
        self.uiClassificationFilename_.setFilePath(join(outdir, 'classification.bsq'))
        self.uiProbabilityFilename_.setFilePath(join(outdir, 'probability.bsq'))
        self.uiReportFilename_.setFilePath(join(outdir, 'accass.html'))

    def execute(self, *args):
        self.log('')

        try:
            saveSampledClassification = self.uiSampledClassificationFilename_.isEnabled()
            saveSampledClassificationComplement = saveSampledClassification #self.uiSampledClassificationComplementFilename_.isEnabled()
            saveModel = self.uiModelFilename_.isEnabled()
            saveClassification = self.uiClassificationFilename_.isEnabled()
            saveProbability = self.uiProbabilityFilename_.isEnabled()
            saveReport = self.uiReportFilename_.isEnabled()
            filenameSampledClassification = self.uiSampledClassificationFilename_.filePath()
            filenameSampledClassificationComplement = '{}_complement{}'.format(*splitext(filenameSampledClassification)) #self.uiSampledClassificationComplementFilename_.filePath()
            filenameModel = self.uiModelFilename_.filePath()
            filenameClassification = self.uiClassificationFilename_.filePath()
            filenameProbability = self.uiProbabilityFilename_.filePath()
            filenameReport = self.uiReportFilename_.filePath()

            qgsRaster = self.uiRaster_.currentLayer()
            if qgsRaster is None:
                self.log('Error: no raster selected')
                return
            raster = Raster(filename=qgsRaster.source())

            qgsClassification = self.uiClassification_.currentLayer()
            if qgsClassification is None:
                self.log('Error: no reference selected')
                return

            colors = list()
            for w in self.colors:
                hex = w.styleSheet().split(' ')[1]
                colors.append(Color(hex))

            names = list()
            for w in self.names:
                names.append(w.text())

            classDefinition = ClassDefinition(names=names, colors=colors)

            if isinstance(qgsClassification, QgsRasterLayer):
                classification = Classification(filename=qgsClassification.source(), classDefinition=classDefinition)
                if not raster.grid().equal(other=classification.grid()):
                    self.log('Error: raster and reference grids do not match')
                    return
            elif isinstance(qgsClassification, QgsVectorLayer):
                classification = Classification(filename=self.rasterizationFilename(), classDefinition=classDefinition)
            else:
                assert 0

            sample = ClassificationSample(raster=raster, classification=classification)

            qgsRaster2 = self.uiRaster2_.currentLayer()
            if (saveClassification or saveProbability) and (qgsRaster2 is None):
                self.log('Error: no raster for mapping selected')
                return
            raster2 = Raster(filename=qgsRaster2.source())

            n = [spinbox.value() for spinbox in self.spinboxes]
            if np.sum(n) == np.sum(self.counts): # perform no random sampling if all samples are used
                n = None

            cv = self.uiNFold_.value()

            namespace = dict()
            code = self.uiCode_.toPlainText()
            exec(code, namespace)
            sklEstimator = namespace['estimator']
            classifier = Classifier(sklEstimator=sklEstimator)

            self.uiExecute_.setEnabled(False)

            classificationWorkflow(sample=sample,
                                   classifier=classifier,
                                   raster=raster2,
                                   n=n,
                                   cv=cv,
                                   saveSampledClassification=saveSampledClassification,
                                   saveSampledClassificationComplement=saveSampledClassificationComplement,
                                   saveModel=saveModel,
                                   saveClassification=saveClassification,
                                   saveProbability=saveProbability,
                                   saveReport=saveReport,
                                   filenameSampledClassification=filenameSampledClassification,
                                   filenameSampledClassificationComplement=filenameSampledClassificationComplement,
                                   filenameModel=filenameModel,
                                   filenameClassification=filenameClassification,
                                   filenameProbability=filenameProbability,
                                   filenameReport=filenameReport,
                                   ui=self)
            self.log('Done!')
            self.uiAttributeLabel()
            self.progressBar().setPercentage(0)
            self.uiExecute_.setEnabled(True)


        except Exception as error:
            traceback.print_exc()
            self.log('Error: {}'.format(str(error)))
            self.uiExecute_.setEnabled(True)

