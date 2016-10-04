from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc
import hub.file
from enmapbox.processing.types import Image, Classification, SupervisedSample, Classifier
from enmapbox.processing.estimators import Classifiers
from enmapbox.processing.environment import PrintProgress

class SampleReadApplier(Applier):

    def __init__(self, featureFolder, featureProduct, featureImage, featureExtension,
                 labelFolder, labelProduct, labelImage, labelExtension,
                 footprints=None):

        Applier.__init__(self, footprints=footprints)

        self.appendInput(ApplierInput(archive=MGRSArchive(folder=labelFolder),
                                      productName=labelProduct, imageNames=[labelImage],
                                      extension=labelExtension))

        self.appendInput(ApplierInput(archive=MGRSArchive(featureFolder),
                                        productName=featureProduct,
                                        imageNames=[featureImage],
                                        extension=featureExtension))

    def applyToFootprint(self, footprint):

        print(footprint.name)

        if len(self.inputs[0].getFilenameAssociations(footprint).__dict__.values()) == 1:
            labelfile = self.inputs[0].getFilenameAssociations(footprint).__dict__.values()[0]
            imagefile = self.inputs[1].getFilenameAssociations(footprint).__dict__.values()[0]
            image = Image(imagefile)
            labels = Classification(labelfile)
            sample = SupervisedSample.fromLocations(image=image, labels=labels, locations=labels.getLocations())
        else:
            sample = None
        return sample


    def apply(self):

        print('Apply '+str(self.__class__).split('.')[-1])
        # get samples of all footprints
        samples = dict()
        for footprint in self.inputs[0].archive.yieldFootprints(filter=self.footprints):
            samples[footprint.name] = self.applyToFootprint(footprint=footprint)

        # merge all samples
        x = numpy.vstack([sample.featureSample.dataSample.data for sample in samples.values() if sample is not None])
        y = numpy.vstack([sample.labelsSample.dataSample.data for sample in samples.values() if sample is not None])
        sample = samples.values()[0]  # it is assumed, that the meta data in all samples match, so simply the meta data of the first sample is used
        sample.featureSample.dataSample.data = x # store all features
        sample.labelsSample.dataSample.data = y # store all labels
        return sample

def exportSampleAsJSON(sample, rfc, outfile):
    assert isinstance(sample, SupervisedSample)
    result = dict()
    result['x'] = [map(int, v) for v in sample.imageData.T]
    result['y'] = map(int, sample.labelData)
    result['samples'] = len(sample.labelData)
    result['features'] = len(sample.imageData[0])
    result['feature names'] = sample.image.meta.getMetadataItem('band_names')
    result['classes'] = int(sample.mask.meta.getMetadataItem('classes'))
    result['class names'] = sample.mask.meta.getMetadataItem('class_names')
    result['class ids'] = map(int, rfc.sklEstimator.classes_)
    result['class lookup'] = map(int, sample.mask.meta.getMetadataItem('class_lookup'))
    result['rfc feature_importances'] = map(float, rfc.sklEstimator._final_estimator.feature_importances_)
    result['rfc oob probabilities'] = [map(float, v) for v in rfc.sklEstimator._final_estimator.oob_decision_function_.T]

    hub.file.saveJSON(var=result, file=outfile)


class ClassifierPredictApplier(Applier):

    def __init__(self, featureFolder, featureProduct, featureImage, featureExtension,
                 outFolder, outProduct, outClassification, outProbability, outExtension,
                 classifier, footprints=None):

        Applier.__init__(self, footprints=footprints)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=featureFolder),
                                      productName=featureProduct,
                                      imageNames=[featureImage],
                                      extension=featureExtension))
        for imageName in [outClassification, outProbability]:
            self.appendOutput(ApplierOutput(folder=outFolder,
                                            productName=outProduct,
                                            imageNames=[imageName],
                                            extension=outExtension))

        assert isinstance(classifier, Classifier)
        self.classifier = classifier


    def applyToFootprint(self, footprint):

        print(footprint.name)
        imagefile = self.inputs[0].getFilenameAssociations(footprint).__dict__.values()[0]
        outfileClassification = self.outputs[0].getFilenameAssociations(footprint).__dict__.values()[0]
        outfileProbability= self.outputs[1].getFilenameAssociations(footprint).__dict__.values()[0]

        image = Image(imagefile)
        hub.file.mkfiledir(outfileProbability)
        probability = self.classifier.predictProbability(image=image, mask=None, filename=outfileProbability, progress=PrintProgress)
        classification = probability.argmax(filename=outfileClassification, progress=PrintProgress)



def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'

    folder1 = r'C:\Work\data\gms\lucasMGRS'
    folder2 = r'C:\Work\data\gms\stackMGRS'
    folder3 = r'C:\Work\data\gms\rfcMGRS'
    filename1 = r'C:\Work\data\gms\lucas_lc4.pkl'
    filename2 = r'C:\Work\data\gms\lucas_lc4.json'
    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']
#    mgrsFootprints = ['32UQC']

    sampleReader = SampleReadApplier(featureFolder=folder2, featureProduct='stack', featureImage='stack', featureExtension='.vrt',
                                     labelFolder=folder1, labelProduct='lucas', labelImage='lucas_lc4', labelExtension='.img',
                                     footprints=mgrsFootprints)
    if 0:
        sample = sampleReader.apply()
        hub.file.savePickle(var=sample, file=filename1)
    else:
        sample = hub.file.restorePickle(file=filename1)

    rfc = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100, class_weight='balanced', n_jobs=-1)
    rfc._fit(sample)
    exportSampleAsJSON(sample=sample, rfc=rfc, outfile=filename2)

    predictor = ClassifierPredictApplier(featureFolder=folder2, featureProduct='stack', featureImage='stack', featureExtension='.vrt',
                                         labelFolder=folder3, labelProduct='lucas', labelImage='lucas_lc4', labelExtension='.img',
                                         classifier=rfc, footprints=mgrsFootprints)
    predictor.apply()





if __name__ == '__main__':

    tic()
    test()
    toc()
