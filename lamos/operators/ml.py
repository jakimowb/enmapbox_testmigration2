from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc
import hub.file
import enmapbox.processing
from enmapbox.processing.estimators import Classifiers
from enmapbox.processing.env import PrintProgress

class SampleReadApplier(Applier):

    def __init__(self, infolder1, infolder2, inextension1='.img', inextension2='.img', footprints=None):

        Applier.__init__(self, footprints=footprints)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder1),
                                      productName='composite', imageNames=['2000-07-01_380d_61y'],
                                      extension=inextension1))
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder2),
                                      productName='lucas', imageNames=['lucas_lc4'],
                                      extension=inextension2))

    def applyToFootprint(self, footprint):

        print(footprint.name)

        imagefile = self.inputs[0].getFilenameAssociations(footprint).__dict__['composite_2000-07-01_380d_61y']
        labelfile = self.inputs[1].getFilenameAssociations(footprint).__dict__['lucas_lucas_lc4']
        image = enmapbox.processing.Image(imagefile)
        labels = enmapbox.processing.Classification(labelfile)
        sample = enmapbox.processing.ClassificationSample(image, labels)
        return sample

    def apply(self):

        print('Apply '+str(self.__class__).split('.')[-1])
        samples = dict()
        for footprint in self.inputs[0].archive.yieldFootprints(filter=self.footprints):
            samples[footprint.name] = self.applyToFootprint(footprint=footprint)

        return samples


def randomForestFit(samples):

    print('RandomForest Fit')
    rfc = Classifiers.RandomForestClassifier(oob_score=False)
    assert isinstance(rfc, enmapbox.processing.Classifier)

    x = numpy.vstack([sample.imageData for sample in samples.values()])
    y = numpy.hstack([sample.labelData for sample in samples.values()])

    sample = samples.values()[0]  # it is assumed, that the meta data in all samples do match, so simply the first sample (holding the correct meta data) is passed to the fitting methode
    sample.imageData = x
    sample.labelData = y
    rfc._fit(sample)
#    rfc.sklEstimator.fit(X=x, y=y)
    return rfc


class ClassifierPredictApplier(Applier):

    def __init__(self, infolder, inextension, outfolder, classifier, footprints=None):

        Applier.__init__(self, footprints=footprints)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                      productName='composite', imageNames=['2000-07-01_380d_61y'],
                                      extension=inextension))
        self.appendOutput(ApplierOutput(folder=outfolder,
                                           productName='classification', imageNames=['lc4'], extension='.img'))

        assert isinstance(classifier, enmapbox.processing.Classifier)
        self.classifier = classifier


    def applyToFootprint(self, footprint):

        print(footprint.name)
        imagefile = self.inputs[0].getFilenameAssociations(footprint).__dict__.values()[0]
        outfile = self.outputs[0].getFilenameAssociations(footprint).__dict__.values()[0]
        image = enmapbox.processing.Image(imagefile)
        hub.file.mkfiledir(outfile)
        self.classifier.predict(image=image, mask=None, filename=outfile, progress=PrintProgress)


def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'

    folder1 = r'C:\Work\data\gms\productsMGRS'
    folder2 = r'C:\Work\data\gms\lucasMGRS'
    folder3 = r'C:\Work\data\gms\rfcMGRS'

    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']

    sampleReader = SampleReadApplier(infolder1=folder1, infolder2=folder2, footprints=mgrsFootprints)
    samples = sampleReader.apply()

    rfc = randomForestFit(samples)

    predictor = ClassifierPredictApplier(infolder=folder1, inextension='.img', outfolder=folder3, classifier=rfc)
    predictor.apply()





if __name__ == '__main__':

    tic()
    test()
    toc()
