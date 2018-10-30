from PyQt5.QtWidgets import QApplication, QProgressBar
from hubflow.core import *


class ProgressBar(hubdc.progressbar.CUIProgressBar):

    def __init__(self, bar):
        assert isinstance(bar, QProgressBar)
        self.bar = bar
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)

    def setText(self, text):
        pass

    def setPercentage(self, percentage):
        self.bar.setValue(int(percentage))
        QApplication.processEvents()


def classificationWorkflow(sample, classifier, raster, n, cv,
                           saveSampledClassificationComplement, saveSampledClassification,
                           saveModel, saveClassification, saveProbability, saveRGB, saveReport,
                           filenameSampledClassification, filenameSampledClassificationComplement,
                           filenameModel, filenameClassification, filenameProbability, filenameReport,
                           ui=None):

    assert isinstance(sample, ClassificationSample)
    assert isinstance(classifier, Classifier)

    def setInfo(text):
        if ui is not None:
            ui.log(text)

    if ui is not None:
        progressBar = ProgressBar(ui.uiProgressBar_)
    else:
        progressBar = None


    setInfo('Step 1: draw random sample')
    if n is not None:
        points = Vector.fromRandomPointsFromClassification(filename='/vsimem/classification_workflow_random_points.gpkg', #filename=join(tempfile.gettempdir(), 'classification_workflow_random_points.gpkg'),
                                                           classification=sample.classification(), n=n,
                                                           **ApplierOptions(progressBar=progressBar))
        sample = ClassificationSample(raster=sample.raster(),
                                      classification=sample.classification(),
                                      mask=points)
    else:
        points = None

    if saveSampledClassification:
        sampledClassification = sample.classification().applyMask(filename=filenameSampledClassification, mask=points,
                                                                  **ApplierOptions(progressBar=progressBar))
    else:
        sampledClassification = None

    if saveSampledClassificationComplement:
        if sampledClassification is None:
            sampledClassification = sample.classification().applyMask(filename='/vsimem/classification_workflow/sampled.bsq', mask=points)
        sample.classification().applyMask(filename=filenameSampledClassificationComplement,
                                          mask=Mask(filename=sampledClassification.filename(), invert=True),
                                          **ApplierOptions(progressBar=progressBar))

    setInfo('Step 2: fit classifier')
    classifier.fit(sample)

    if saveModel:
        classifier.pickle(filename=filenameModel, emit=False)
        print(filenameModel)

    setInfo('Step 3: predict classification')
    if saveClassification:
        classifier.predict(filename=filenameClassification, raster=raster, progressBar=progressBar)

    setInfo('Step 4: predict probability')
    if saveProbability:
        probability = classifier.predictProbability(filename=filenameProbability, raster=raster, progressBar=progressBar)
        if saveRGB:
            probability.asClassColorRGBRaster(filename='{}_rgb{}'.format(*splitext(filenameProbability)))

    setInfo('Step 5: assess cross-validation performance')
    if saveReport:
        classifier.crossValidation(cv=cv).report().saveHTML(filename=filenameReport)


def test():
    from sklearn.ensemble import RandomForestClassifier
    import enmapboxtestdata
    library = ENVISpectralLibrary(filename=enmapboxtestdata.library)
    labels = Classification.fromENVISpectralLibrary(filename='/vsimem/synthmixRegressionEnsemble/labels.bsq',
                                                    library=library, attribute='level 2')

    sample = ClassificationSample(raster=library.raster(), classification=labels)
    outdir = r'c:\outputs'
    classificationWorkflow(sample=sample,
                           classifier=Classifier(sklEstimator=RandomForestClassifier()),
                           raster=Raster(filename=enmapboxtestdata.enmap),
                           n=labels.classDefinition().classes() * [10],
                           cv=10,
                           saveModel=True,
                           saveClassification=True,
                           saveProbability=True,
                           saveReport=True,
                           filenameModel=join(outdir, 'model.pkl'),
                           filenameClassification=join(outdir, 'classification.bsq'),
                           filenameProbability=join(outdir, 'probability.bsq'),
                           filenameReport=join(outdir, 'report.html'))

if __name__ == '__main__':
    test()