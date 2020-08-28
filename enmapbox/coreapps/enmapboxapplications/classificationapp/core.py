import inspect
import tempfile
import traceback

from PyQt5.uic import loadUi
from qgis._core import QgsPalettedRasterRenderer
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.externals.qps.speclib.core import SpectralLibrary
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.qgsvectorclassificationscheme import QgsVectorClassificationScheme
from hubdsm.processing.savelayerasclassification import saveLayerAsClassification
from hubflow.core import *
from enmapboxapplications.classificationapp.script import classificationWorkflow, ProgressBar

pathUi = join(dirname(__file__), 'ui')


class ClassificationWorkflowApp(QMainWindow):
    uiTrainingType_: QComboBox
    uiType0Raster_: QgsMapLayerComboBox
    uiType0Classification_: QgsMapLayerComboBox
    uiType1Raster_: QgsMapLayerComboBox
    uiType1VectorClassification_: QgsMapLayerComboBox
    uiType2Library_: QgsMapLayerComboBox

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(pathUi, 'main.ui'), self)
        self.uiInfo_ = QLabel()
        self.statusBar().addWidget(self.uiInfo_, 1)

        self.initMaps()
        self.initClassifier()
        self.initOutputs()

        self.uiTrainingType_.currentIndexChanged.connect(self.clearTrainingData)
        self.uiType0Raster_.layerChanged.connect(self.initClasses)
        self.uiType0Classification_.layerChanged.connect(self.initClasses)
        self.uiType1Raster_.layerChanged.connect(self.initClasses)
        self.uiType1VectorClassification_.layerChanged.connect(self.initClasses)
        self.uiType2Library_.layerChanged.connect(self.initClasses)

        self.uiSampleSizePercent_.valueChanged.connect(self.updateSpinboxes)
        self.uiSampleSizePixel_.valueChanged.connect(self.updateSpinboxes)
        self.uiApply_.clicked.connect(self.updateSpinboxes)

        self.uiExecute_.clicked.connect(self.execute)

        self.spinboxes = None

    def clearTrainingData(self):
        self.uiType0Raster_.setLayer(None)
        self.uiType0Classification_.setLayer(None)
        self.uiType1Raster_.setLayer(None)
        self.uiType1VectorClassification_.setLayer(None)
        self.uiType2Library_.setLayer(None)

    def initMaps(self):
        self.uiType0Raster_.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiType0Classification_.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiType1Raster_.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiType1VectorClassification_.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.uiType2Library_.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.uiRaster2_.setFilters(QgsMapLayerProxyModel.RasterLayer)

    def progressBar(self):
        return ProgressBar(bar=self.uiProgressBar())

    def log(self, text):
        self.uiInfo_.setText(str(text))
        QCoreApplication.processEvents()

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

    def classificationTmpFilename(self):
        return '/vsimem/classification_workflow/classification.bsq'

    def initClasses(self, *args):
        self.log('')
        self.spinboxes = None
        self.uiStacked_.setEnabled(False)
        self.widget_.hide()
        self.widget_ = QWidget()
        self.layout_.addWidget(self.widget_)
        layout = QHBoxLayout(self.widget_)
        self.updateTotalSamples()

        if self.uiTrainingType_.currentIndex() == 0: # raster
            rasterLayer: QgsRasterLayer = self.uiType0Raster_.currentLayer()
            classificationLayer: QgsRasterLayer = self.uiType0Classification_.currentLayer()
            if rasterLayer is None or classificationLayer is None:
                return

            if not isinstance(classificationLayer.renderer(), QgsPalettedRasterRenderer):
                self.log('Selected layer is not a valid classification (requires Paletted/Unique values renderer).')
                self.uiType0Classification_.setLayer(None)
                return

            saveLayerAsClassification(
                qgsMapLayer=classificationLayer,
                filename=self.classificationTmpFilename()
            )

            classification = Classification(filename=self.classificationTmpFilename())
        elif self.uiTrainingType_.currentIndex() == 1: # vector
            rasterLayer: QgsRasterLayer = self.uiType1Raster_.currentLayer()
            vectorClassificationLayer: QgsVectorLayer = self.uiType1VectorClassification_.currentLayer()
            if rasterLayer is None or vectorClassificationLayer is None:
                return
            if not isinstance(vectorClassificationLayer.renderer(), QgsCategorizedSymbolRenderer):
                self.uiType1VectorClassification_.setLayer(None)
                self.log('Selected layer is not a valid vector classification (requires Categorized renderer).')
                return

            raster = Raster(filename=self.uiType1Raster_.currentLayer().source())

            if not raster.dataset().projection().equal(
                    Vector(filename=vectorClassificationLayer.source()).dataset().projection()
            ):
                self.log('Projection mismatch between Raster and Vector Classification.')
                return

            self.log('Rasterize vector classification on raster grid')
            saveLayerAsClassification(
                qgsMapLayer=vectorClassificationLayer,
                grid=GdalRaster.open(raster.filename()).grid,
                filename=self.classificationTmpFilename()
            )
            self.log('')

            classification = Classification(filename=self.classificationTmpFilename())
            self.progressBar().setPercentage(0)

        elif self.uiTrainingType_.currentIndex() == 2: # speclib
            libraryLayer: QgsVectorLayer = self.uiType2Library_.currentLayer()
            if libraryLayer is None:
                return

            try:
                libraryLayer = SpectralLibrary(name=libraryLayer.name(), uri=libraryLayer.source())
            except:
                self.uiType2Library_.setLayer(None)
                self.log('Selected layer is not a valid library.')
                return

            if not isinstance(libraryLayer.renderer(), QgsCategorizedSymbolRenderer):
                self.uiType2Library_.setLayer(None)
                self.log('Selected layer is not a valid library classification (requires Categorized renderer).')
                return

            qgsVectorClassificationScheme = QgsVectorClassificationScheme.fromQgsVectorLayer(
                qgsVectorLayer=libraryLayer
            )

            # make pseudo raster
            X = list()
            y = list()
            fieldIndex = None
            for profile in slib:
                if fieldIndex is None:
                    fieldIndex = profile.fieldNames().index('level_2_id')
                X.append(profile.values()['y'])
                y.append(profile.attribute(fieldIndex))
            X = np.array(X, dtype=np.float64)
            y = np.array(y)
            raster = Raster.fromArray(
                array=np.atleast_3d(X.T),
                filename='c:/vsimem/X.bsq'
            )
            classification = GdalRaster.createFromArray(
                array=np.atleast_3d(y),
                filename='c:/vsimem/y.bsq'
            )
            classification.setCategories(list(qgsVectorClassificationScheme.categories.values()))
            del classification
            classification = Classification('c:/vsimem/y.bsq')

        else:
            assert 0


        '''
                elif isinstance(layer, QgsVectorLayer):
                    self.uiAttribute_.setEnabled(True)
                    name = self.uiAttribute_.currentField()
                    if name == '':  # no field selected yet
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
        
                    raster = Raster(filename=self.uiRaster_.currentLayer().source())
        
                    tmpfilename = '/vsimem/classificationapp/reprojected.gpkg'
                    if not ds.projection().equal(raster.grid().projection()):
                        self.log('Projection mismatch between Raster and Reference.')
                        return
        
                        # reproject vector
                        ds.reproject(projection=raster.grid().projection(), filename=tmpfilename, driver=GeoPackageDriver())
                        filename = tmpfilename
        
                    vectorClassification = VectorClassification(filename=filename, classAttribute=name,
                        minDominantCoverage=self.uiPurity_.value() / 100.,
                        oversampling=oversampling)
        
                    self.log(
                        'Rasterize reference on raster grid with x{} resolution oversampling and select pixel with at leased {}% purity'.format(
                            self.uiOversampling_.value(), self.uiPurity_.value()))
                    classification = Classification.fromClassification(filename=self.rasterizationFilename(),
                        classification=vectorClassification, grid=raster.grid(),
                        **ApplierOptions(emitFileCreated=False, progressBar=self.progressBar()))
        
                    try:
                        gdal.Unlink(tmpfilename)
                    except:
                        pass
        
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
        '''

        counts = classification.statistics()
        self.counts = counts

        self.spinboxes = list()
        self.colors = list()
        self.names = list()

        for i in range(classification.classDefinition().classes()):

            layout1 = QVBoxLayout()
            layout2 = QHBoxLayout()
            color = QToolButton()
            color.setStyleSheet(
                'background-color: {}'.format(classification.classDefinition().color(i + 1)._qColor.name()))
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
            name.setMinimumWidth(w + 10)
            layout2.addWidget(name)
            # layout2.addWidget(QLabel('({} px)  '.format(counts[i])))
            self.names.append(name)
            layout1.addLayout(layout2)

            # layout3 = QHBoxLayout()
            spinbox = QSpinBox()
            spinbox.setRange(0, counts[i])
            spinbox.setSingleStep(1)
            spinbox.setValue(counts[i])
            spinbox.setSuffix(' ({} px)'.format(counts[i]))
            spinbox.valueChanged.connect(self.updateTotalSamples)
            self.spinboxes.append(spinbox)
            layout1.addWidget(spinbox)
            # layout3.addWidget(QLabel('({} px)  '.format(counts[i])))
            # layout1.addLayout(layout3)

            layout.addLayout(layout1)

            self.updateTotalSamples()

        # self.widget_.adjustSize()
        # self.adjustSize()

        self.uiStacked_.setEnabled(True)

    def updateTotalSamples(self, *args):
        total = 0
        if self.spinboxes is not None:
            for spinbox in self.spinboxes:
                total += int(spinbox.value())
        self.uiTotalSampleSize_.setText('Total sample size = {}'.format(total))




    def initClassifier(self):
        from enmapboxgeoalgorithms.algorithms import ALGORITHMS, ClassifierFit
        self.classifiers = [alg for alg in ALGORITHMS if isinstance(alg, ClassifierFit)]
        self.classifierNames = [alg.name()[3:] for alg in self.classifiers]
        self.uiClassifier_.addItems(self.classifierNames)
        self.uiClassifier_.currentIndexChanged.connect(
            lambda index: self.uiCode_.setText(self.classifiers[index].code()))
        self.uiClassifier_.setCurrentIndex(self.classifierNames.index('RandomForestClassifier'))

    def initOutputs(self):
        outdir = tempfile.gettempdir()
        self.uiSampledClassificationFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiModelFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiClassificationFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiProbabilityFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiReportFilename_.setStorageMode(QgsFileWidget.SaveFile)
        self.uiSampledClassificationFilename_.setFilePath(join(outdir, 'sample.bsq'))
        self.uiModelFilename_.setFilePath(join(outdir, 'classifier.pkl'))
        self.uiClassificationFilename_.setFilePath(join(outdir, 'classification.bsq'))
        self.uiProbabilityFilename_.setFilePath(join(outdir, 'probability.bsq'))
        self.uiReportFilename_.setFilePath(join(outdir, 'accass.html'))

    def execute(self, *args):
        self.log('')

        try:
            saveSampledClassification = self.uiSampledClassificationFilename_.isEnabled()
            saveSampledClassificationComplement = saveSampledClassification  # self.uiSampledClassificationComplementFilename_.isEnabled()
            saveModel = self.uiModelFilename_.isEnabled()
            saveClassification = self.uiClassificationFilename_.isEnabled()
            saveProbability = self.uiProbabilityFilename_.isEnabled()
            saveRGB = self.uiRGB_.isEnabled()
            saveReport = self.uiReportFilename_.isEnabled()
            filenameSampledClassification = self.uiSampledClassificationFilename_.filePath()
            filenameSampledClassificationComplement = '{}_complement{}'.format(
                *splitext(filenameSampledClassification)
            )
            filenameModel = self.uiModelFilename_.filePath()
            filenameClassification = self.uiClassificationFilename_.filePath()
            filenameProbability = self.uiProbabilityFilename_.filePath()
            filenameReport = self.uiReportFilename_.filePath()

            if self.uiTrainingType_.currentIndex() == 0: # raster
                qgsRaster = self.uiType0Raster_.currentLayer()
                qgsClassification = self.uiType0Classification_.currentLayer()
                if qgsRaster is None:
                    self.log('Error: no raster selected')
                    return
                if qgsClassification is None:
                    self.log('Error: no classification selected')
                    return
                raster = Raster(filename=qgsRaster.source())
            elif self.uiTrainingType_.currentIndex() == 1:  # vector
                qgsRaster = self.uiType1Raster_.currentLayer()
                qgsClassification = self.uiType1VectorClassification_.currentLayer()
                if qgsRaster is None:
                    self.log('Error: no raster selected')
                    return
                if qgsClassification is None:
                    self.log('Error: no classification selected')
                    return
                raster = Raster(filename=qgsRaster.source())
            elif self.uiTrainingType_.currentIndex() == 2:  # speclib
                assert 0
            else:
                assert 0

            colors = list()
            for w in self.colors:
                hex = w.styleSheet().split(' ')[1]
                colors.append(Color(hex))

            names = list()
            for w in self.names:
                names.append(w.text())

            classDefinition = ClassDefinition(names=names, colors=colors)

            classification = Classification(filename=self.classificationTmpFilename(), classDefinition=classDefinition)
            if not raster.grid().equal(other=classification.grid()):
                self.log('Error: raster and reference grids do not match')
                return

            sample = ClassificationSample(raster=raster, classification=classification)

            qgsRaster2 = self.uiRaster2_.currentLayer()
            if (saveClassification or saveProbability) and (qgsRaster2 is None):
                self.log('Error: no raster for mapping selected')
                return
            raster2 = Raster(filename=qgsRaster2.source())

            qgsMask2 = self.uiMask_.currentLayer()
            if isinstance(qgsMask2, QgsRasterLayer):
                mask2 = Mask(filename=qgsMask2.source())
                if not raster.grid().equal(other=mask2.grid()):
                    self.log('Error: raster and mask grids do not match')
                    return
            elif isinstance(qgsMask2, QgsVectorLayer):
                mask2 = VectorMask(filename=qgsMask2.source())
            elif qgsMask2 is None:
                mask2 = None
            else:
                assert 0

            n = [spinbox.value() for spinbox in self.spinboxes]
            if np.sum(n) == np.sum(self.counts):  # perform no random sampling if all samples are used
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
                mask=mask2,
                n=n,
                cv=cv,
                saveSampledClassification=saveSampledClassification,
                saveSampledClassificationComplement=saveSampledClassificationComplement,
                saveModel=saveModel,
                saveClassification=saveClassification,
                saveProbability=saveProbability,
                saveRGB=saveRGB,
                saveReport=saveReport,
                filenameSampledClassification=filenameSampledClassification,
                filenameSampledClassificationComplement=filenameSampledClassificationComplement,
                filenameModel=filenameModel,
                filenameClassification=filenameClassification,
                filenameProbability=filenameProbability,
                filenameReport=filenameReport,
                ui=self)
            self.log('Done!')
            self.progressBar().setPercentage(0)
            self.uiExecute_.setEnabled(True)


        except Exception as error:
            traceback.print_exc()
            self.log('Error: {}'.format(str(error)))
            self.uiExecute_.setEnabled(True)
