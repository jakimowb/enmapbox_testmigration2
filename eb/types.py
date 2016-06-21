from __future__ import print_function, division

from matplotlib.pyplot import axes

__author__ = 'janzandr'

import operator
import tempfile
import hub
from eb.env import PrintProgress, SilentProgress
from eb.applier import ApplierHelper, ApplierControls
from hub.gdal.api import GDALMeta
import hub.gdal.util, hub.gdal.api, hub.envi
import hub.file
import rios.applier
import numpy
#import numpy.ma
import sklearn.metrics
import sklearn.pipeline
import eb.report
from eb.report import *
import shutil
import gdal, ogr

# set default progress object
progress = SilentProgress
#progress = PrintProgress  # useful for debugging


def unpickle(filename, progress=progress):

    result = hub.file.restorePickle(filename)
    progress.setText('unpickle model from file: ' + filename)
    return result


class Type():

    def aside(self, function, *args, **kwargs):

        function(*args, **kwargs)
        return self


    def pickle(self, filename, progress=progress):

        progress.setText('pickle model to file: '+filename)
        hub.file.savePickle(self, filename)
        return self


class Meta(GDALMeta):

    def report(self):

        report = Report('GDAL Datasource')

        text = ''
        text +=   'Projection  = ' + str(self.Projection)
        text += '\nRasterSize  = ' + str(self.RasterXSize) + ' ' + str(self.RasterYSize)
        text += '\nRasterCount = ' + str(self.RasterCount)
        text += '\nPixelSize   = ' + str(self.pixelXSize) + ' ' + str(self.pixelYSize)
        report.append(ReportMonospace(text))

        d = self.getMetadataDict()
        text = '\n'.join([k + ' = ' + str(d[k]) for k in sorted(d.keys())])
        if text != '':
            report.append(ReportHeading('ENVI Domain'))
            report.append(ReportMonospace(text))

        report.append(ReportHeading('GDAL Domains'))
        for name, d in self.domain.items():
            if name == 'ENVI': continue
            report.append(ReportHeading(name, 1))
            text = '\n'.join([k + ' = ' + str(d[k]) for k in sorted(d.keys())])
            report.append(ReportMonospace(text))

        return report

    @property
    def Bands(self): return int(self.getMetadataItem('bands'))


    @property
    def BandNames(self):
        bandNames = self.getMetadataItem('band_names')
        if bandNames is None:
            bandNames = ['Band ' + str(i) for i in range(1, self.RasterCount + 1)]
        return bandNames


    @property
    def Classes(self):
        return int(self.getMetadataItem('classes'))


    @property
    def ClassNames(self):
        return self.getMetadataItem('class_names')


    @property
    def ClassLookup(self):
        return numpy.array(self.getMetadataItem('class_lookup'), dtype=numpy.uint8).reshape(self.Classes, 3)


class Image(Type):
    """
    An GDAL conform image with no further assumptions about the image meta data.
    """

    @staticmethod
    def fromENVISpectralLibrary(filename):

        filenameHdr = os.path.splitext(filename)[0]+'.hdr'
        tempfilename = eb.env.tempfile()
        temptilenameHdr = tempfilename+'.hdr'
        shutil.copy(filename, tempfilename)
        meta = hub.envi.readHeader(filenameHdr)
        meta['file type'] = 'ENVI Standard'
        meta['interleave'] = 'bip'
        meta['bands'], meta['samples'] = meta['samples'], meta['bands']
        hub.envi.writeHeader(temptilenameHdr, meta)
        return Image(tempfilename)


    def __init__(self, filename):

        assert isinstance(filename, basestring), 'Incorrect filename!'
        assert os.path.exists(filename), 'Incorrect filename!'
        self.filename = filename
        self.meta = Meta(filename)
        self._assert()


    def __str__(self):
        return '('+str(self.__class__)+') = '+ self.filename


    def _assert(self):
        pass


    def report(self):

        reportMeta = self.meta.report()
        report = Report('Image Information')
        report.append(ReportMonospace('Filename: ' + self.filename))
        report.appendReport(reportMeta)
        return report


    def saveAs(self, filename=None, options='-of ENVI'):

        if filename is None: filename = env.tempfile()
        hub.gdal.util.gdal_translate(outfile=filename, infile=self.filename, options=options, verbose=True)
        meta = Meta(self.filename)
        meta.writeMeta(filename)
        return self.__class__(filename)


    def statistics(self, mask=None, mode='with histo'):

        return ImageStatistics(self, mask=mask,  mode=mode)


    def stack(self, images=[], resolution=None, filename=None):


        if filename is None: filename = env.tempfile('stack', '.vrt')
        infiles = [image.filename for image in [self] + images]
        options =  ' -resolution user -tr ' + str(self.meta.pixelXSize) + ' ' + str(abs(self.meta.pixelYSize))
        options += ' -vrtnodata 0'
        hub.gdal.util.stack(filename, infiles, options)


        return Image(filename)

    @property
    def SpatialReference(self):

        return None


    @property
    def BoundingBox(self):

        upperLeft = (self.meta.xmin, self.meta.ymin)
        lowerRight = (self.meta.xmax, self.meta.ymax)
        return (upperLeft, lowerRight)


    @property
    def PixelSize(self):

        return (self.meta.pixelXSize, abs(self.meta.pixelYSize))


    @property
    def PixelGrid(self):

        return PixelGrid(self.SpatialReference, self.BoundingBox[0], self.PixelSize)


class PixelGrid():

    def __init__(self, spatialReference, pixelCorner, pixelSize):

        #assert isinstance(spatialReference, ogr)
        self.spatialReference = spatialReference
        self.pixelCorner = pixelCorner
        self.pixelSize = pixelSize


    def project(self, image, boundingBox=None, filename=None):

        assert isinstance(image, Image)

        if filename is None: filename = env.tempfile(suffix='.vrt')

        # calculate exact output bounding box
        # - get image bounding box in target SRS
        if boundingBox is None:
            boundingBox = Image(hub.gdal.util.gdalwarp(env.tempfile(suffix='.vrt'), image.filename, options='-of VRT', verbose=False)).BoundingBox

        # - snap bounding box to target pixel grid
        xoff = (boundingBox[0][0] - self.pixelCorner[0]) % self.pixelSize[0]
        yoff = (boundingBox[0][1] - self.pixelCorner[1]) % abs(self.pixelSize[1])
        boundingBox = ((boundingBox[0][0]-xoff, boundingBox[0][1]-yoff),
                       (boundingBox[1][0]-xoff, boundingBox[1][1]-yoff))

        options  = ' -of VRT'
        options += ' -tr ' + repr(self.pixelSize[0]) + ' ' + repr(self.pixelSize[1])
        options += ' -r average'
        options += ' -te' + ' ' + repr(boundingBox[0][0]) \
                          + ' ' + repr(min(boundingBox[0][1], boundingBox[1][1])) \
                          + ' ' + repr(boundingBox[1][0]) \
                          + ' ' + repr(max(boundingBox[0][1], boundingBox[1][1]))

        hub.gdal.util.gdalwarp(filename, image.filename, options)


        # set up ENVI Metadata
        metaTmp = Meta(filename)
        meta = Meta(image.filename)
        meta.setMetadataItem('samples', metaTmp.RasterXSize)
        meta.setMetadataItem('lines', metaTmp.RasterXSize)
        meta.writeMeta(filename)

        return Image(filename)



class ImageStatistics():

    def __init__(self, image, mode='simple', histoMin=None, histoMax=None, histoBins=100, mask=None):

        assert isinstance(image, Image)
        assert mode in ['simple', 'with histo', 'only histo']
        if mask is not None: assert isinstance(mask, Mask)

        self.image = image
        self.mask = mask
        self.mode = mode
        if mode == 'simple':
            self.doit(firstRun=True)
            self.histoMin = self.min
            self.histoMax = self.max
        elif mode == 'with histo':
            if histoMin is None or histoMax is None:
                self.doit(firstRun=True)
                self.histoMin = self.min
                self.histoMax = self.max
            if histoMin is not None:
                self.histoMin = histoMin
            if histoMax is not None:
                self.histoMax = histoMax
            self.histoBins = histoBins
            self.doit(firstRun=False)
        elif mode == 'only histo':
            self.histoMin = histoMin
            self.histoMax = histoMax
            self.histoBins = histoBins
            self.doit(firstRun=False)

    def doit(self, firstRun=True, progress=progress):

        progress.setText('calculate statistics')

        infiles = rios.applier.FilenameAssociations()
        outfiles = rios.applier.FilenameAssociations()
        args = rios.applier.OtherInputs()
        controls = ApplierControls()

        infiles.image = self.image.filename
        args.useMask = self.mask is not None
        if args.useMask: infiles.mask = self.mask.filename
        args.image = self.image
        args.mask = self.mask
        args.progress = progress
        args.progress.setDebugInfo(str(controls))

        # set up the function to be applied
        def ufunc(info, inputs, outputs, args):

            args.progress.setPercentage(ApplierHelper.progress(info))

            ApplierHelper.reshape2d(inputs)

            # create mask
            mask = numpy.bool(False)
            mask += ApplierHelper.mask(inputs.image, args.image.meta.getNoDataValue())
            if args.useMask:
                mask += ApplierHelper.mask(inputs.mask, args.mask.meta.getNoDataValue(0))

            # extract values
            image = ApplierHelper.maskedArray(inputs.image, mask)

            # calculate statistics
            if ApplierHelper.firstBlock(info):
                self.nvalid = 0
                self.min = numpy.full([self.image.meta.RasterCount], fill_value=+numpy.Inf)
                self.max = numpy.full([self.image.meta.RasterCount], fill_value=-numpy.Inf)
                self.sum = numpy.zeros([self.image.meta.RasterCount], dtype=numpy.float64)
                if not firstRun:
                    self.sumSquaredDeviation = numpy.zeros([self.image.meta.RasterCount], dtype=numpy.float64)
                    self.counts = list()
                    self.binEdges = list()
                    for i in range(self.image.meta.RasterCount):
                        self.counts.append(numpy.full([self.histoBins], fill_value=0, dtype=numpy.uint64))
                        self.binEdges.append(numpy.histogram(numpy.array([numpy.nan]), self.histoBins, range=[self.histoMin[i], self.histoMax[i]])[1])


            self.nvalid += image.shape[1]-numpy.ma.count_masked(image[0,:])
            self.min = numpy.minimum(numpy.min(image, axis=1), self.min)
            self.max = numpy.maximum(numpy.max(image, axis=1), self.max)
            self.sum += numpy.sum(image, axis=1)
            if not firstRun:
                if self.mode != 'only histo':
                    self.sumSquaredDeviation += numpy.sum((image-self.mean.reshape(-1, 1))**2, axis=1)
                for i in range(self.image.meta.RasterCount):
                    counts, binEdges = numpy.histogram(image[i], self.histoBins, range=[self.histoMin[i], self.histoMax[i]])
                    self.counts[i] += counts

        # Apply the function to the inputs, creating the outputs.
        rios.applier.apply(ufunc, infiles, outfiles, args, controls)

        self.mean = self.sum / self.nvalid
        if not firstRun:
            self.stddev = numpy.sqrt(self.sumSquaredDeviation / self.nvalid)

    def report(self):

        report = Report('Image Statistics')

        report.append(ReportMonospace('min: '+str(self.min)))
        report.append(ReportMonospace('max: '+str(self.max)))
        report.append(ReportMonospace('mean: ' + str(self.mean)))
        if self.mode == 'with histo':
            report.append(ReportMonospace('stddev: ' + str(self.stddev)))

        if self.mode != 'simple':

            report.append(ReportHeading('Band Histograms'))
            for i, (counts, binEdges) in enumerate(zip(self.counts, self.binEdges)):
                report.append(ReportHeading('Band '+str(i+1), 1))
                report.append(ReportMonospace('bin edges: ' + str(binEdges)
                                           +'\ncounts:    ' + str(counts)))

        return report


class SpectralImage(Image):
    pass


class SpectralLibrary(SpectralImage):
    pass


class Mask(Image):

    def _assert(self):

        Image._assert(self)
        assert self.meta.RasterCount == 1


class Classification(Mask):


    def _assert(self):

        Mask._assert(self)
        envi = self.meta.getMetadataDict()
        assert envi['file_type'].lower() == 'envi classification'
        assert int(envi['classes']) == len(envi['class_names'])
        assert int(envi['classes'])*3 == len(envi['class_lookup'])


    def assessClassificationPerformance(self, classification, stratification=None):

        assert isinstance(classification, Classification)
        sample = ClassificationSample(self, classification)

        if stratification is None:
            result = ClassificationPerformance.fromSample(sample)
        else:
            assert isinstance(stratification, Classification)
            sampleStratification = ClassificationSample(stratification, classification)
            result = ClassificationPerformanceAdjusted.fromSample(sample, sampleStratification)

        return result


    def assessClusteringPerformance(self, classification):


        assert isinstance(classification, Classification)
        sample = ClassificationSample(self, classification)
        return ClusteringPerformance.fromSample(sample)


    def statistics(self, mask=None):

        if mask is not None:
            assert isinstance(mask, Mask)

        return ClassificationStatistics(self, mask=mask)


class ClassificationStatistics(ImageStatistics):

    def __init__(self, classification, mask=None):

        assert isinstance(classification, Classification)
        if mask is not None: assert isinstance(mask, Mask)

        ImageStatistics.__init__(self, classification, mode='only histo', histoMin=[1], histoMax=[classification.meta.Classes], histoBins=classification.meta.Classes-1, mask=mask)


    def report(self):

        report = Report('Classification Statistics')

        report.append(ReportMonospace('class names: ' + str(self.image.meta.ClassNames[1:])))
        report.append(ReportMonospace('class labels: ' + str(range(1, self.image.meta.Classes))))

        report.append(ReportMonospace('class counts: ' + str(self.counts)))
        report.append(ReportMonospace('class colors: ' + str(self.image.meta.ClassLookup[1:])))


        return report


class Regression(Mask):

    def _assert(self):

        Mask._assert(self)
        envi = self.meta.getMetadataDict()
        assert envi['data_ignore_value'] is not None


    def assessRegressionPerformance(self, regression):

        sample = RegressionSample(self, regression)
        return RegressionPerformance.fromSample(sample)


class Probability(Image):

    def _assert(self):

        envi = self.meta.getMetadataDict()
        assert int(envi['classes']) == len(envi['class_names'])
        assert int(envi['classes'])*3 == len(envi['class_lookup'])
        Image._assert(self)


    def assessProbabilityPerformance(self, classification):
        assert isinstance(classification, Classification)
        sample = ClassificationSample(self, classification)
        return ProbabilityPerformance.fromSample(sample)


class ProbabilityPerformance(Type):

    @staticmethod
    def fromSample(sample):

        assert isinstance(sample, ImageSample), 'Image sample is requiered!'
        assert isinstance(sample.image, Probability), 'Prediction is not a probability image!'
        result = ProbabilityPerformance(sample.mask.meta.Classes-1)
        result.update(yScore=sample.imageData, yTruth=sample.labelData)
        result.assessPerformance()
        result.sample = sample
        return result


    def __init__(self, classes):
        self.yScore = numpy.array([], dtype=numpy.float32).reshape(0, classes)
        self.yTruth = numpy.array([], dtype=numpy.float32)


    def update(self, yScore, yTruth):

        assert isinstance(yScore, numpy.ndarray)
        assert isinstance(yTruth, numpy.ndarray)
        self.yScore = numpy.vstack((self.yScore, yScore))
        self.yTruth = numpy.append(self.yTruth, yTruth)


    def assessPerformance(self):

        self.roc_fpr = dict()
        self.roc_tpr = dict()
        self.roc_thresholds = dict()
        self.roc_auc = dict()
        self.prc_precision = dict()
        self.prc_recall = dict()
        self.prc_thresholds = dict()

        for i in range(self.yScore.shape[1]):
            self.roc_fpr[i], self.roc_tpr[i], self.roc_thresholds[i] = sklearn.metrics.roc_curve(self.yTruth, self.yScore[:,i], pos_label=i+1)
            self.roc_auc[i] = sklearn.metrics.auc(self.roc_fpr[i], self.roc_tpr[i])

            self.prc_precision[i], self.prc_recall[i], self.prc_thresholds[i] = sklearn.metrics.precision_recall_curve(self.yTruth, self.yScore[:,i], pos_label=i+1)


    def report(self):

        report = Report('Probability Performance')

        report.append(ReportHeading('Receiver Operating Characteristic (ROC) Curve'))
        for i, className in enumerate(self.sample.mask.meta.ClassNames[1:]):
            report.append(ReportHeading(className, 1))
            report.append(ReportMonospace('fpr = ' + str(self.roc_fpr[i])))
            report.append(ReportMonospace('tpr = ' + str(self.roc_tpr[i])))
            report.append(ReportMonospace('thresholds = ' + str(self.roc_thresholds[i])))
            report.append(ReportMonospace('auc = ' + str(self.roc_auc[i])))

        report.append(ReportHeading('Precision-Recall Curve'))
        for i, className in enumerate(self.sample.mask.meta.ClassNames[1:]):
            report.append(ReportHeading(className, 1))
            report.append(ReportMonospace('precision = ' + str(self.prc_precision[i])))
            report.append(ReportMonospace('recall = ' + str(self.prc_recall[i])))
            report.append(ReportMonospace('thresholds = ' + str(self.prc_thresholds[i])))

        return report


class Estimator(Type):

    def __init__(self, sklEstimator):

        assert isinstance(sklEstimator, sklearn.pipeline.Pipeline)
        self.sklEstimator = sklEstimator
        self._assert()


    def _assert(self):

        assert callable(getattr(self.sklEstimator, 'fit', None))


    def _fit(self, sample, progress=progress):

        progress.setText('fit model')
        self.sample = sample
        self.sklEstimator.fit(sample.imageData.astype(numpy.float64), sample.labelData)
        return self


    def _predict(self, image, mask=None, predictfile=None, probafile=None, transformfile=None, inversetransformfile=None, progress=progress):

        progress.setText('apply model')

        infiles = rios.applier.FilenameAssociations()
        outfiles = rios.applier.FilenameAssociations()
        args = rios.applier.OtherInputs()

        infiles.x = image.filename
        if predictfile: outfiles.predict = predictfile
        if probafile: outfiles.proba = probafile
        if transformfile: outfiles.transform = transformfile
        if inversetransformfile: outfiles.inversetransform = inversetransformfile

        args.useMask = mask is not None
        if args.useMask: infiles.m = mask.filename
        args.xMeta = image.meta
        if args.useMask: args.mMeta = mask.meta
        try:
            args.estimator_type = self.sklEstimator._estimator_type
        except:
            args.estimator_type = self.sklEstimator._final_estimator.__class__

        controls = ApplierControls()
        controls.setNumThreads(1)
        controls.windowxsize = 50
        controls.windowysize = 50

        progress.setDebugInfo(str(controls))

        if controls.numThreads > 1:
            args.progress = SilentProgress
        else:
            args.progress = progress
        args.progress = progress

        # set up the function to be applied
        def ufunc(info, inputs, outputs, args):

            args.progress.setPercentage(ApplierHelper.progress(info))


            # reshape to 2d
            shape3d = inputs.x.shape
            for k, v in inputs.__dict__.items(): inputs.__dict__[k] = inputs.__dict__[k].reshape((v.shape[0], -1))
            shape2d = inputs.x.shape

            # create mask
            valid = True
            # - from x
            if args.xMeta.getNoDataValue() is not None:
                valid *= numpy.any(inputs.x != args.xMeta.getNoDataValue(), axis=0)
            # - from m
            if args.useMask: valid *= numpy.any(inputs.m != args.mMeta.getNoDataValue(0), axis=0)
            valid = numpy.ravel(valid)

            allValid = valid.all()
            anyValid = valid.any()

            if not anyValid:
                valid = [0]

            # predict valid samples
            if probafile:

                if allValid:
                    valid_proba = self.sklEstimator.predict_proba(inputs.x.T)
                else:
                    valid_proba = self.sklEstimator.predict_proba(inputs.x.T[valid], )

            if predictfile:

                if allValid:
                    valid_predict = self.sklEstimator.predict(inputs.x.T.astype(numpy.float64)).reshape(-1, 1)
                else:
                    valid_predict = self.sklEstimator.predict(inputs.x.T[valid].astype(numpy.float64)).reshape(-1, 1)

                if isinstance(self, Clusterer):
                    valid_predict += 1


            if transformfile:

                if allValid:
                    valid_transform = self.sklEstimator.transform(inputs.x.T.astype(numpy.float64))
                else:
                    valid_transform = self.sklEstimator.transform(inputs.x.T[valid].astype(numpy.float64))

            if inversetransformfile:

                if allValid:
                    valid_inversetransform = self.sklEstimator.inverse_transform(inputs.x.T.astype(numpy.float64))
                else:
                    valid_inversetransform = self.sklEstimator.inverse_transform(inputs.x.T[valid].astype(numpy.float64))


            # prepare outputs

            if probafile:

                if allValid:
                    outputs.proba = valid_proba.astype(self.predictProbabilityDType())
                else:
                    outputs.proba = numpy.full((shape2d[1], valid_proba.shape[1]), dtype=self.predictProbabilityDType(),
                                               fill_value=self.predictProbabilityNoDataValue())
                    outputs.proba[valid] = valid_proba

                if self.finalEstimator().classes_[0] == 0:
                    outputs.proba = outputs.proba[:,1:]

            if predictfile:

                if allValid:
                    outputs.predict = valid_predict.astype(self.predictDType())
                else:
                    outputs.predict = numpy.full((shape2d[1], 1), dtype=self.predictDType(),
                                                 fill_value=self.predictNoDataValue())
                    outputs.predict[valid] = valid_predict

            if transformfile:

                if allValid:
                    outputs.transform = valid_transform.astype(self.transformDType())
                else:
                    outputs.transform = numpy.full((shape2d[1], valid_transform.shape[1]), dtype=self.transformDType(),
                                                   fill_value=self.transformNoDataValue())
                    outputs.transform[valid] = valid_transform

            if inversetransformfile:

                if allValid:
                    outputs.inversetransform = valid_inversetransform.astype(self.transformDType())
                else:
                    outputs.inversetransform = numpy.full((shape2d[1], valid_inversetransform.shape[1]), dtype=self.transformDType(),
                                                   fill_value=self.transformNoDataValue())
                    outputs.inversetransform[valid] = valid_inversetransform


            # reshape to 3d
            for k, v in outputs.__dict__.items():
                outputs.__dict__[k] = outputs.__dict__[k].T.reshape((v.shape[1], shape3d[1], shape3d[2]))

        # Apply the function to the inputs, creating the outputs.
        rios.applier.apply(ufunc, infiles, outfiles, args, controls)

        # Set Metadata for output images

        if predictfile:

            meta = Meta(outfiles.predict)
            self.predictMeta(meta, args.xMeta, self.sample.mask.meta)
            meta.writeMeta(outfiles.predict)

        if transformfile:

            meta = Meta(outfiles.transform)
            self.transformMeta(meta, args.xMeta, self.sample.mask.meta)
            meta.writeMeta(outfiles.transform)

        if inversetransformfile:

            meta = Meta(outfiles.inversetransform)
            self.transformInverseMeta(meta, args.xMeta, self.sample.mask.meta)
            meta.writeMeta(outfiles.inversetransform)

        if probafile:

            meta = Meta(outfiles.proba)
            self.predictProbabilityMeta(meta, args.xMeta, self.sample.mask.meta)
            meta.writeMeta(outfiles.proba)


    def predictDType(self):

        raise Exception('Methode must be overwritten')


    def predictNoDataValue(self):

        raise Exception('Methode must be overwritten')


    def predictMeta(self, meta, imate, mmeta):

        meta.setNoDataValue(self.predictNoDataValue())
        meta.setBandNames([self.name()])


    def transformNoDataValue(self):

        raise Exception('Methode must be overwritten')


    def transformMeta(self, meta, iimeta, immeta):

        meta.setNoDataValue(self.transformNoDataValue())


    def transformInverseMeta(self, meta, iimeta, immeta):

        meta.setNoDataValue(self.transformNoDataValue())


    def name(self):

        return str(self.__class__).split('.')[-1]


    def finalEstimator(self):

        if isinstance(self.sklEstimator._final_estimator, sklearn.grid_search.GridSearchCV):
            finalEstimator = self.sklEstimator._final_estimator.best_estimator_
        else:
            finalEstimator = self.sklEstimator._final_estimator

        return finalEstimator


    def signature(self):

        import inspect
        sig = inspect.getargspec(self.__init__)
        statement = self.name() + '(' + ', '.join([k + '=' + repr(v) for k, v in zip(sig.args[1:], sig.defaults)]) + ')'
        return statement


    def report(self):

        def sklearnName(sklEstimator):

            return str(sklEstimator).split('(')[0]

        def sklearnURL(sklEstimator):

            import urllib2
            try:
                longname = os.path.splitext(sklEstimator.__class__.__module__)[0] + '.' + sklearnName(sklEstimator)
                url = 'http://scikit-learn.org/stable/modules/generated/' + longname + '.html'
                urllib2.urlopen(url)
            except:
                longname = sklEstimator.__class__.__module__ + '.' + sklearnName(sklEstimator)
                url = 'http://scikit-learn.org/stable/modules/generated/' + longname + '.html'
            return url

        hyperlinks = dict()

        finalEstimator = self.finalEstimator()
        finalEstimatorName = str(finalEstimator).split('(')[0]

        report = Report('View ' + finalEstimatorName + ' Model')

        report.append(ReportHeading('Input Files'))
        report.append(ReportMonospace('Image:  ' + self.sample.image.filename + '\nLabels: ' + self.sample.mask.filename))

        report.append(ReportHeading('Training Data'))

        text = 'Number of Samples:  '+str(self.sample.labelData.shape[0])+'\n'
        text += 'Number of Features: '+str(self.sample.imageData.shape[1])+'\n'
        if isinstance(self, Classifier):
            text += 'Number of Classes:  ' + str(int(self.sample.mask.meta.getMetadataItem('classes')) - 1) + '\n'
            text += 'Class Names:        ' + ', '.join(self.sample.mask.meta.getMetadataItem('class names')[1:])

        report.append(ReportMonospace(text))

        report.appendReport(self.reportDetails())

        report.append(ReportHorizontalLine())
        report.append(ReportHeading('Advanced Information', -1))

        report.append(ReportHeading('Final Model Parameter'))
        report.append(ReportMonospace(str(finalEstimator)))

        hyperlinks[sklearnName(finalEstimator)] = sklearnURL(finalEstimator)

        if len(self.sklEstimator.steps) > 1:

            report.append(ReportHeading('Pipeline Parameter'))
            hyperlinks[sklearnName(self.sklEstimator)] = sklearnURL(self.sklEstimator)
            for (name, estimator), i in zip(self.sklEstimator.steps, range(1,len(self.sklEstimator.steps)+1)):

                report.append(ReportHeading('Step ' + str(i) + ': ' + str(estimator).split('(')[0], 1))
                report.append(ReportMonospace(str(estimator)))

                hyperlinks[sklearnName(estimator)] = sklearnURL(estimator)

                if isinstance(estimator, sklearn.grid_search.GridSearchCV):

                    report.append(ReportHeading('Best Parameters', 2))
                    text = '\n'.join([k + ' = ' + str(v) for k,v in estimator.best_params_.items()])
                    report.append(ReportMonospace(text))

                    report.append(ReportHeading('Best Score', 2))
                    text = '\n'.join([k + ' = ' + str(v) for k, v in estimator.best_params_.items()])
                    report.append(ReportMonospace(str(estimator.scoring) + ' = ' + str(estimator.best_score_*estimator.scorer_._sign)))

                    report.append(ReportHeading('Search History', 2))
                    data = [[round(v.mean_validation_score*estimator.scorer_._sign, 4)] + v.parameters.values() for v in estimator.grid_scores_]
                    data = sorted(data, key=operator.itemgetter(0), reverse=estimator.scorer_._sign != -1)
                    table = Table(data, header_row=[str(estimator.scoring)]+estimator.best_params_.keys())
                    report.append(ReportTable(table))

        report.append(ReportHorizontalLine())
        report.append(ReportHeading('Scikit-Learn Documentation', -1))

        for key in sorted(hyperlinks.keys()):
            report.append(ReportHyperlink(hyperlinks[key], key))

        return report


    def reportDetails(self):

        return Report('')

class Classifier(Estimator):

    def __assert(self):

        Estimator._assert(self)
        assert callable(getattr(self.sklEstimator, 'predict', None))


    def fit(self, image, labels, progress=progress):

        assert isinstance(image, Image)
        assert isinstance(labels, Classification)
        sample = ClassificationSample(image, labels)
        return self._fit(sample, progress=progress)


    def predict(self, image, mask=None, filename=env.tempfile('classification'), progress=progress):

        assert isinstance(image, Image)
        if mask is not None:
            assert isinstance(mask, Image)

        self._predict(image, mask, predictfile=filename, progress=progress)
        return Classification(filename)


    def predictDType(self):

        return numpy.uint8


    def predictNoDataValue(self):

        return 0


    def predictProbabilityDType(self):

        return numpy.float32


    def predictProbabilityNoDataValue(self):

        return -1


    def predictProbability(self, image, mask=None, filename=env.tempfile('probability'), progress=progress):

        assert isinstance(image, Image)
        if mask is not None:
            assert isinstance(mask, Image)

        self._predict(image, mask, probafile=filename, progress=progress)
        return Probability(filename)


    def predictMeta(self, meta, imeta, mmeta):

        assert isinstance(meta, Meta)
        Estimator.predictMeta(self, meta, imeta, mmeta)
        meta.setMetadataItem('file_type', 'envi classification')
        for key in ['class_names', 'class_lookup', 'classes']:
            meta.copyMetadataItem(key, self.sample.mask.meta)


    def predictProbabilityMeta(self, meta, imeta, mmeta):

        assert isinstance(meta, Meta)
        meta.setNoDataValue(-1)
        meta.setBandNames(self.sample.mask.meta.getMetadataItem('class names')[1:])
        for key in ['class_names', 'class_lookup', 'classes']:
            meta.copyMetadataItem(key, self.sample.mask.meta)


    def UncertaintyClassifierFP(self):

        return UncertaintyClassifier(self, mode='fp')


    def UncertaintyClassifierFN(self):

        return UncertaintyClassifier(self, mode='fn')


class UncertaintyClassifier(Classifier):

    def __init__(self, classifier, mode):

        assert isinstance(classifier, Classifier)
        from eb.estimators import SklearnClassifiers
        pipe = sklearn.pipeline.make_pipeline(SklearnClassifiers.UncertaintyClassifier(classifier.sklEstimator, mode=mode))
        Classifier.__init__(self, pipe)


class Regressor(Estimator):

    def __assert(self):

        Estimator._assert(self)
        assert callable(getattr(self.sklEstimator, 'predict', None))


    def fit(self, image, labels, progress=progress):

        assert isinstance(image, Image)
        assert isinstance(labels, Regression)
        sample = RegressionSample(image, labels)
        return self._fit(sample, progress=progress)


    def predict(self, image, mask, filename=env.tempfile('regression')):

        self._predict(image, mask, predictfile=filename)
        return Regression(filename)


    def predictDType(self):

        return numpy.float32


    def predictNoDataValue(self):

        return self.sample.mask.meta.getNoDataValue()


    def UncertaintyRegressor(self):

        return UncertaintyRegressor(self)


class UncertaintyRegressor(Regressor):

    def __init__(self, regressor):

        assert isinstance(regressor, Regressor)

        from eb.estimators import SklearnRegressors
        pipe = sklearn.pipeline.make_pipeline(SklearnRegressors.UncertaintyRegressor(regressor.sklEstimator))
        Regressor.__init__(self, pipe)


    def predictNoDataValue(self):

        return 0


class Transformer(Estimator):

    def fit(self, image, mask, progress=progress):

        assert isinstance(image, Image)
        assert isinstance(mask, Mask)
        sample = ImageSample(image, mask)
        return self._fit(sample, progress=progress)


    def transform(self, image, mask=None, filename=env.tempfile('transformation'), progress=progress):

        self._predict(image, mask, transformfile=filename, progress=progress)
        return Image(filename)

    def transformInverse(self, image, mask=None, filename=env.tempfile('inverseTransformation'), progress=progress):

        self._predict(image, mask, inversetransformfile=filename, progress=progress)
        return Image(filename)


    def transformDType(self):

        return numpy.float32


    def transformNoDataValue(self):

        return numpy.finfo(self.transformDType()).max


class Clusterer(Estimator):

    def fit(self, image, mask, progress=progress):

        assert isinstance(image, Image)
        assert isinstance(mask, Mask)
        sample = ImageSample(image, mask)
        return self._fit(sample, progress=progress)


    def predict(self, image, mask=None, filename=env.tempfile('clustering')):

        self._predict(image, mask, predictfile=filename)
        return Classification(filename)


    def predictMeta(self, meta):

        assert isinstance(meta, Meta)
        n_clusters = self.sklEstimator._final_estimator.n_clusters
        meta.setMetadataItem('file_type', 'envi classification')
        meta.setMetadataItem('class_names', ['Undefined'] + ['Cluster ' + str(i) for i in range(1, n_clusters + 1)])
        meta.setMetadataItem('class_lookup',
                             [0, 0, 0] + list(numpy.random.uniform(0, high=255, size=n_clusters * 3).astype(int)))
        meta.setMetadataItem('classes', n_clusters + 1)


    def predictDType(self):

        return numpy.uint8


    def predictNoDataValue(self):

        return 0


class ImageSample(Type):

    def __init__(self, image, mask):
        self.image = image
        self.mask = mask
        self._assert()
        self.imageData, self.labelData = self._readData()

    def __str__(self):
        return '(' + str(self.__class__) + ')\n  ' + str(self.image) + '\n  ' + str(self.mask)+''

    def _assert(self):
        assert isinstance(self.image, Image), 'Image must be an Image'
        assert isinstance(self.mask, Mask), 'Mask must be a Mask'
        # assert image.pixelGrid.equalTo(mask.pixelGrid)
        # assert image.boundingBox.equalTo(mask.boundingBox)

    def _readData(self):

        # use rios for reading the labeled data

        infiles = rios.applier.FilenameAssociations()
        outfiles = rios.applier.FilenameAssociations()
        controls = ApplierControls()

        args = rios.applier.OtherInputs()

        infiles.x = self.image.filename
        infiles.y = self.mask.filename
        args.xMeta = self.image.meta
        args.yMeta = self.mask.meta

        args.x = list()
        args.y = list()

        def ufunc(info, inputs, outputs, args):

            ApplierHelper.reshape2d(inputs)
            mask = ApplierHelper.mask(inputs.y, args.yMeta.getNoDataValue(default=0), inverse=True)
            args.x.append(ApplierHelper.extract(inputs.x, mask))
            args.y.append(ApplierHelper.extract(inputs.y, mask))


        rios.applier.apply(ufunc, infiles, outfiles, args)

        return (numpy.hstack(args.x).T, numpy.hstack(args.y)[0])


class ClassificationSample(ImageSample):

    def _assert(self):
        ImageSample._assert(self)
        assert isinstance(self.mask, Classification), 'Mask is not a Classification!'


class RegressionSample(ImageSample):

    def _assert(self):
        ImageSample._assert(self)
        assert isinstance(self.mask, Regression), 'Mask is not a Regression!'


class ClassificationPerformance(Type):

    @staticmethod
    def fromSample(sample):

        assert isinstance(sample, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(sample.image, Classification), 'Prediction is not a classification!'
        assert int(sample.image.meta.getMetadataItem('classes')) == int(sample.mask.meta.getMetadataItem('classes')), 'Number of classes in prediction and reference do not match!'
        mappedClassSizes = sample.image.statistics().counts[0]
        mappedClassProportions = mappedClassSizes/mappedClassSizes.sum()
        result = ClassificationPerformance(classes=int(sample.mask.meta.getMetadataItem('classes'))-1,
                                           classNames=sample.mask.meta.getMetadataItem('class names')[1:],
                                           mappedClassProportions=mappedClassProportions)
        result.update(yPrediction=sample.imageData, yTruth=sample.labelData)
        result.assessPerformance()
        result.sample = sample
        return result


    @staticmethod
    def _fix(a, fill=0):

        if type(a) == numpy.ndarray:
            a[numpy.logical_not(numpy.isfinite(a))] = 0
        else:
            if not numpy.isfinite(a):
                a = 0

        return a

    def __init__(self, classes, classNames=None, mappedClassProportions=None):

        assert isinstance(classes, int)
        if classNames is None:
            classNames = ['Class '+str(i) for i in range(1,classes+1)]
        assert classes == len(classNames)

        self.classes = classes
        self.classLabels = range(1, self.classes+1)
        self.classNames = classNames
        self.mij = numpy.zeros((classes, classes), dtype=numpy.int64)
        self.m = numpy.int64(0)
        self.Wi = mappedClassProportions


    def update(self, yPrediction, yTruth):

        assert isinstance(yPrediction, numpy.ndarray)
        assert isinstance(yTruth, numpy.ndarray)
        self.mij += sklearn.metrics.confusion_matrix(yTruth, yPrediction, labels=self.classLabels).T
        self.m += yPrediction.size


    def assessPerformance(self):

        old_error_state = numpy.geterr()
        numpy.seterr(divide='ignore', invalid='ignore', over='raise', under='raise')

        # get some stats from the confusion matrix mij
        self.mi_ = numpy.sum(self.mij, axis=0, dtype=numpy.float64) # class-wise sum over all prediction
        self.m_j = numpy.sum(self.mij, axis=1, dtype=numpy.float64) # class-wise sum over references
        self.mii = numpy.diag(self.mij) # main diagonal -> class-wise correctly classified samples

        # estimate mapped class proportions from the reference sample, if not provided by the user
        if self.Wi is None:
            self.Wi = self.mi_/self.m  # note that in this case pij is reduced to pij=mij/m

        # pij is the proportion of area estimate
        # pij = Wi*mij/mi_
        self.pij = numpy.zeros_like(self.mij, dtype=numpy.float64)
        for i in range(self.classes):
            for j in range(self.classes):
                self.pij[i,j] = self.Wi[i]*self.mij[i,j]/self.mi_[i]

        self.pi_ = numpy.sum(self.pij, axis=0, dtype=numpy.float64)
        self.p_j = numpy.sum(self.pij, axis=1, dtype=numpy.float64)
        self.pii = numpy.diag(self.pij)

        # calculate performance measures
        self.UserAccuracy = self._fix(self.mii/self.mi_)
        self.ProducerAccuracy = self._fix(self.mii / self.m_j)
        self.F1Accuracy = self._fix(2 * self.UserAccuracy * self.ProducerAccuracy / (self.UserAccuracy + self.ProducerAccuracy))
        self.ConditionalKappaAccuracy = self._fix((self.m * self.mii - self.mi_ * self.m_j) / (self.m * self.mi_ - self.mi_ * self.m_j))
        self.OverallAccuracy = self._fix(self.mii.sum() / self.m)
        self.KappaAccuracy = self._fix((self.m * self.mii.sum() - numpy.sum(self.mi_ * self.m_j)) / (self.m**2 - numpy.sum(self.mi_ * self.m_j)))

        # calculate squared standard errors (SSE)

        self.OverallAccuracySSE = 0.
        for i in range(self.classes): self.OverallAccuracySSE += self.pij[i,i]*(self.Wi[i]-self.pij[i,i])/(self.Wi[i]*self.m)

        a1 = self.mii.sum()/self.m
        a2 = (self.mi_*self.m_j).sum() / self.m**2
        a3 = (self.mii*(self.mi_+self.m_j)).sum() / self.m**2
        a4 = 0.
        for i in range(self.classes):
            for j in range(self.classes):
                a4 += self.mij[i,j]*(self.mi_[j]+self.m_j[i])**2
        a4 /= self.m**3
        b1 = a1*(1-a1)/(1-a2)**2
        b2 = 2*(1-a1)*(2*a1*a2-a3)/(1-a2)**3
        b3 = (1-a1)**2*(a4-4*a2**2)/(1-a2)**4
        self.KappaAccuracySSE = (b1+b2+b3)/self.m

        self.ProducerAccuracySSE = numpy.zeros(self.classes, dtype=numpy.float64)
        for i in range(self.classes):
            sum = 0.
            for j in range(self.classes):
                if i == j: continue
                sum += self.pij[i,j]*(self.Wi[j]-self.pij[i,j])/(self.Wi[j]*self.m)
                self.ProducerAccuracySSE[i] = self.pij[i,i]*self.p_j[i]**(-4) * (self.pij[i,i]*sum + (self.Wi[i]-self.pij[i,i])*(self.p_j[i]-self.pij[i,i])**2/(self.Wi[i]*self.m))

        self.UserAccuracySSE = numpy.zeros(self.classes, dtype=numpy.float64)
        for i in range(self.classes):
            self.UserAccuracySSE[i] = self.pij[i ,i]*(self.Wi[i]-self.pij[i,i])/(self.Wi[i]**2*self.m)

        self.F1AccuracySSE = self._fix(2 * self.UserAccuracySSE * self.ProducerAccuracySSE / (self.UserAccuracySSE + self.ProducerAccuracySSE))

        self.ConditionalKappaAccuracySSE = self.m*(self.mi_-self.mii) / (self.mi_*(self.m-self.m_j))**3 * ((self.mi_-self.mii)*(self.mi_*self.m_j-self.m*self.mii)+self.m*self.mii*(self.m-self.mi_-self.m_j+self.mii) )

        self.ClassProportion = self.m_j/self.m
        self.ClassProportionSSE = numpy.zeros(self.classes, dtype=numpy.float64)
        for j in range(self.classes):
            for i in range(self.classes):
                self.ClassProportionSSE[j] += self.Wi[i]**2 * ( (self.mij[i,j]/self.mi_[i])*(1-self.mij[i,j]/self.mi_[i]) )/(self.mi_[i]-1)


        numpy.seterr(**old_error_state)

    def confidenceIntervall(self, mean, sse, alpha):

        se = numpy.sqrt(numpy.clip(sse, 0, numpy.inf))
        lower = scipy.stats.norm.ppf(alpha / 2.)*se + mean
        upper = scipy.stats.norm.ppf(1 - alpha / 2.)*se + mean
        return lower, upper

    def report(self):

        report = Report('Classification Performance')


#        report.append(ReportHeading('Input Files'))
#        report.append(ReportMonospace('Reference   ' + self.sample.mask.filename + '\nPrediction: ' + self.sample.image.filename))

        report.append(ReportHeading('Classification Label Overview'))
        report.append(ReportMonospace(str(['Reference: ']+self.sample.mask.meta.getMetadataItem('class names'))))
        report.append(ReportMonospace(str(['Prediction: ']+self.sample.image.meta.getMetadataItem('class names'))))

        report.append(ReportHeading('Confusion Matrix'))
        report.append(ReportMonospace('mij = '+ str(self.mij)))
        report.append(ReportMonospace('mi_ = '+ str(self.mi_)))
        report.append(ReportMonospace('m_j = ' + str(self.m_j)))
        report.append(ReportMonospace('m = ' + str(self.m)))

        report.append(ReportHeading('Proportion Matrix'))
        report.append(ReportMonospace('pij = '+ str(self.pij)))
        report.append(ReportMonospace('pi_ = '+ str(self.pi_)))
        report.append(ReportMonospace('p_j = '+ str(self.p_j)))

        report.append(ReportHeading('Accuracies'))
        report.append(ReportMonospace('UserAccuracy = '+str(self.UserAccuracy)))
        report.append(ReportMonospace('ProducerAccuracy = '+str(self.ProducerAccuracy)))
        report.append(ReportMonospace('F1Accuracy = '+str(self.F1Accuracy)))
        report.append(ReportMonospace('ConditionalKappaAccuracy = '+str(self.ConditionalKappaAccuracy)))
        report.append(ReportMonospace('OverallAccuracy = '+str(self.OverallAccuracy)))
        report.append(ReportMonospace('KappaAccuracy = '+str(self.KappaAccuracy)))

        report.append(ReportHeading('Confidence Intervalls alpha=5%'))
        report.append(ReportMonospace('UserAccuracy = '+str(self.confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05))))
        report.append(ReportMonospace('ProducerAccuracy = '+str(self.confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05))))
        report.append(ReportMonospace('F1Accuracy = '+str(self.confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05))))
        report.append(ReportMonospace('ConditionalKappaAccuracy = '+str(self.confidenceIntervall(self.ConditionalKappaAccuracy, self.ConditionalKappaAccuracySSE, 0.05))))
        report.append(ReportMonospace('OverallAccuracy = '+str(self.confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05))))
        report.append(ReportMonospace('KappaAccuracy = '+str(self.confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05))))
        report.append(ReportMonospace('ClassProportion = '+str(self.confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05))))


        return report


class ClassificationPerformanceAdjusted(ClassificationPerformance):

    @staticmethod
    def fromSample(samplePrediction, sampleStratification):

        assert isinstance(samplePrediction, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(sampleStratification, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(samplePrediction.image, Classification), 'Prediction is not a classification!'
        assert isinstance(sampleStratification.image, Classification), 'Stratification is not a classification!'

        assert int(samplePrediction.image.meta.getMetadataItem('classes')) == int(samplePrediction.mask.meta.getMetadataItem('classes')), 'Number of classes in prediction and reference do not match!'

        import numpy
        strataClasses = sampleStratification.image.meta.Classes - 1
        strataSizes = sampleStratification.image.statistics().counts[0]
        strataSampleSizes = numpy.histogram(sampleStratification.imageData, bins=range(1,strataClasses+2))[0]
        strataWeights = (strataSizes/strataSizes.sum()) / (strataSampleSizes/strataSampleSizes.sum())

        result = ClassificationPerformanceAdjusted(classes=samplePrediction.mask.meta.Classes-1,
                                                   classNames=samplePrediction.mask.meta.ClassNames[1:],
                                                   strataClasses=strataClasses,
                                                   strataClassNames=sampleStratification.image.meta.ClassNames[1:],
                                                   strataWeights=strataWeights)
        result.sample = samplePrediction
        result.sampleStratification = sampleStratification
        result.strataSizes = strataSizes
        result.strataSampleSizes = strataSampleSizes

        result.update(yPrediction=samplePrediction.imageData.ravel(), yTruth=samplePrediction.labelData.ravel(), yS=sampleStratification.imageData.ravel())
        result.assessPerformance()
        return result


    def __init__(self, classes, strataClasses, strataWeights, classNames=None, strataClassNames=None):

        self.strataClasses = strataClasses
        self.strataClassNames = strataClassNames
        self.classificationPerformances = [ClassificationPerformance(classes, classNames) for i in range(1, strataClasses+1)]
        ClassificationPerformance.__init__(self, classes, classNames)
        self.mij = self.mij.astype(numpy.float32)
        self.strataWeights = strataWeights


    def update(self, yPrediction, yTruth, yS):

        assert isinstance(yPrediction, numpy.ndarray)
        assert isinstance(yTruth, numpy.ndarray)
        assert isinstance(yS, numpy.ndarray)

        self.mij *= 0.
        self.m *= 0.
        x=list()
        for stratum, classificationPerformance in enumerate(self.classificationPerformances, 1):
            indices = yS == stratum
            classificationPerformance.update(yTruth[indices], yPrediction[indices])
            self.mij += classificationPerformance.mij * self.strataWeights[stratum-1]
            x.append(classificationPerformance.m)
            self.m += classificationPerformance.m * self.strataWeights[stratum-1]


    def report(self):

        report = ClassificationPerformance.report(self)
        report.title = 'Adjusted '+report.title

        items = list()
        items.append(ReportHeading('Stratification Overview'))
        items.append(ReportMonospace(str('Strata names: ' + str(self.strataClassNames))))
        items.append(ReportMonospace(str('Strata weights: ' + str(self.strataWeights))))
        items.append(ReportMonospace(str('Strata sample sizes: ' + str(self.strataSampleSizes))))
        items.append(ReportMonospace(str('Strata sizes: ' + str(self.strataSizes))))

        report.items = items+report.items

        return report



class RegressionPerformance(Type):


    @staticmethod
    def fromSample(sample):

        assert isinstance(sample, RegressionSample), 'Regression sample is requiered!'
        assert isinstance(sample.image, Regression), 'Prediction is not a regression!'
        result = RegressionPerformance()
        result.update(yPrediction=sample.imageData, yTruth=sample.labelData)
        result.assessPerformance()
        result.sample = sample
        return result

    def __init__(self):
        self.yPrediction = numpy.array([], dtype=numpy.float32)
        self.yTruth = numpy.array([], dtype=numpy.float32)


    def update(self, yPrediction, yTruth):

        assert isinstance(yPrediction, numpy.ndarray)
        assert isinstance(yTruth, numpy.ndarray)
        self.yPrediction = numpy.append(self.yPrediction, yPrediction)
        self.yTruth = numpy.append(self.yTruth, yTruth)


    def assessPerformance(self):

        self.ExplainedVarianceScore = sklearn.metrics.explained_variance_score(self.yTruth, self.yPrediction)
        self.MeanAbsoluteError = sklearn.metrics.mean_absolute_error(self.yTruth, self.yPrediction)
        self.MedianAbsoluteError = sklearn.metrics.median_absolute_error(self.yTruth, self.yPrediction)
        self.RootMeanSquaredError = numpy.sqrt(sklearn.metrics.mean_squared_error(self.yTruth, self.yPrediction))


    def report(self):

        report = Report('Regression Performance')

        report.append(ReportHeading('Accuracies'))
        report.append(ReportMonospace('ExplainedVarianceScore = ' + str(self.ExplainedVarianceScore)))
        report.append(ReportMonospace('MeanAbsoluteError = ' + str(self.MeanAbsoluteError)))
        report.append(ReportMonospace('MedianAbsoluteError = ' + str(self.MedianAbsoluteError)))
        report.append(ReportMonospace('RootMeanSquaredError = ' + str(self.RootMeanSquaredError)))

        report.append(ReportHeading('Scatter Plot'))
        report.append(ReportMonospace('reference =  ' + ', '.join(self.yTruth.astype(str))))
        report.append(ReportMonospace('prediction = ' + ', '.join(self.yPrediction.astype(str))))

        return report


class ClusteringPerformance(Type):

    @staticmethod
    def fromSample(sample):

        assert isinstance(sample, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(sample.image, Classification), 'Prediction is not a classification!'
        result = ClusteringPerformance()
        result.update(yPrediction=sample.imageData, yTruth=sample.labelData)
        result.assessPerformance()
        result.sample = sample
        return result


    def __init__(self):

        self.yPrediction = numpy.array([], dtype=numpy.uint32)
        self.yTruth = numpy.array([], dtype=numpy.uint32)


    def update(self, yPrediction, yTruth):

        assert isinstance(yPrediction, numpy.ndarray)
        assert isinstance(yTruth, numpy.ndarray)
        self.yPrediction = numpy.append(self.yPrediction, yPrediction)
        self.yTruth = numpy.append(self.yTruth, yTruth)


    def assessPerformance(self):

        self.AdjustedRandScore = sklearn.metrics.cluster.adjusted_rand_score(self.yTruth, self.yPrediction)

        self.AdjustedMutualInfoScore = sklearn.metrics.cluster.adjusted_mutual_info_score(self.yTruth, self.yPrediction)
        self.NormalizedMutualInfoScore = sklearn.metrics.cluster.normalized_mutual_info_score(self.yTruth, self.yPrediction)
        self.MutualInfoScore = sklearn.metrics.cluster.mutual_info_score(self.yTruth, self.yPrediction)

        self.CompletenessScore = sklearn.metrics.cluster.completeness_score(self.yTruth, self.yPrediction)
        self.HomogeneityScore = sklearn.metrics.cluster.homogeneity_score(self.yTruth, self.yPrediction)
        self.VMeasureScore = sklearn.metrics.cluster.v_measure_score(self.yTruth, self.yPrediction)


    def report(self):

        report = Report('Clustering Performance')

        report.append(ReportHeading('Adjusted Rand index'))
        report.append(ReportMonospace('adjusted rand score = ' + str(self.AdjustedRandScore)))

        report.append(ReportHeading('Mutual Information based scores'))
        report.append(ReportMonospace('mutual information score =            ' + str(self.MutualInfoScore)))
        report.append(ReportMonospace('adjusted mutual information score =   ' + str(self.AdjustedMutualInfoScore)))
        report.append(ReportMonospace('normalized mutual information score = ' + str(self.NormalizedMutualInfoScore)))

        report.append(ReportHeading('Homogeneity, completeness and V-measure'))
        report.append(ReportMonospace('homogeneity score =  ' + str(self.HomogeneityScore)))
        report.append(ReportMonospace('completeness score = ' + str(self.CompletenessScore)))
        report.append(ReportMonospace('V-measure score =    ' + str(self.VMeasureScore)))

        report.append(ReportHorizontalLine())
        report.append(ReportHeading('Scikit-Learn Documentation', -1))
        report.append(ReportHyperlink(r'http://scikit-learn.org/stable/modules/clustering.html#adjusted-rand-index', 'Adjusted Rand index'))
        report.append(ReportHyperlink(r'http://scikit-learn.org/stable/modules/clustering.html#mutual-information-based-scores', 'Mutual Information based scores'))
        report.append(ReportHyperlink(r'http://scikit-learn.org/stable/modules/clustering.html#homogeneity-completeness-and-v-measure', 'Homogeneity, completeness and V-measure'))

        return report


    def _assessPerformance(self):

        prediction = self.sample.imageData.ravel()
        reference = self.sample.labelData


