from __future__ import print_function, division

__author__ = 'janzandr'

import shutil
import operator
import hub
from enmapbox.processing.environment import SilentProgress
from hub.gdal.api import GDALMeta
import hub.gdal.util, hub.gdal.api
import hub.file, hub.envi
import rios.applier
import sklearn.metrics
import sklearn.pipeline
from enmapbox.processing.report import *
from enmapbox.processing.applier import ApplierControls, ApplierHelper
import numpy
import matplotlib.pyplot as plt

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


    def report(self):

        return Report('')


    def info(self, filename=Environment.tempfile('report', '.html')):

        self.report().saveHTML(filename=filename).open()

class Meta(GDALMeta):

    pass


class Image(Type):

    @staticmethod
    def importENVISpectralLibrary(infilename, outfilename=Environment.tempfile('ENVISpectralLibrary_')):

        hdrfilename = hub.envi.findHeader(infilename)

        outmeta = hub.envi.readHeader(hdrfilename)
        outmeta['file type'] = 'ENVI Standard'
        outmeta['bands'], outmeta['samples'] = outmeta['samples'], outmeta['bands']
        outmeta['interleave'] = 'bip'

        shutil.copyfile(infilename, outfilename)
        hub.envi.writeHeader(outfilename+'.hdr', outmeta)
        image = Image(outfilename)

        return image

    def __init__(self, filename):

        assert isinstance(filename, basestring), 'Incorrect filename! '+str(filename)
        assert os.path.exists(filename), 'Incorrect filename! '+str(filename)
        self.filename = filename
        self.meta = GDALMeta(filename)
        self._assert()


    def __str__(self):
        return '('+str(self.__class__)+') = '+ self.filename


    def _assert(self):
        pass


    def saveAs(self, filename=None, options='-of ENVI'):

        """
        Save a copy of the image using `GDAL_TRANSLATE <http://www.gdal.org/gdal_translate.html/>`_

        :param filename: Output filename
        :param options:
        :return: Image(filename)
        :rtype: Image
        """

        if filename is None: filename = Environment.tempfile()
        hub.gdal.util.gdal_translate(outfile=filename, infile=self.filename, options=options, verbose=True)
        return self.__class__(filename)

    def statistics(self, bands=None):
        if bands is None:
            bands = range(self.meta.RasterCount)
        imageStatistics = ImageStatistics(self)
        for band in bands:
            imageStatistics.calculateBandStatistics(band=band)
        return imageStatistics

    def report(self):

        report = Report('View Image Matadata')
        report.append(ReportMonospace(self.filename))

        def addDomain(domain):
            report.append(ReportHeading(domain + ' Domain'))
            for key, value in self.meta.getMetadataDict(domain=domain).items():
                report.append(ReportParagraph(key + ' = ' + str(value)))

        addDomain('IMAGE_STRUCTURE')
        addDomain('ENVI')
        for domain in self.meta.getMetadataDomains():
            if domain in ['DEFAULT', 'ENVI', 'IMAGE_STRUCTURE']: continue
            addDomain(domain)
        addDomain('DEFAULT')

        return report




class ImageStatistics(Type):

    def __init__(self, image):
        assert isinstance(image, Image)
        self.image = image
        self.bandStatistics = dict()

    def getStatistic(self, key, bands=None):
        if bands is None:
            bands = sorted(self.bandStatistics.keys())
        result = [self.bandStatistics[band].__dict__[key] for band in bands]
        return result

    def calculateBandStatistics(self, band, progress=progress):

        progress.setText('calculate band ' + str(band+1) + ' min/max')

        infiles = rios.applier.FilenameAssociations()
        outfiles = rios.applier.FilenameAssociations()
        args = rios.applier.OtherInputs()
        controls = ApplierControls()

        infiles.band = self.image.filename
        controls.selectInputImageLayers([band+1], imagename='band')

        args.noDataValue = self.image.meta.getNoDataValue(default=None)
        args.min = +numpy.inf
        args.max = -numpy.inf
        args.countValid = 0
        args.countNegInf = 0
        args.countPosInf = 0
        args.countNan = 0
        args.countNoDataValue = 0
        args.count = self.image.meta.RasterXSize * self.image.meta.RasterYSize
        args.band = band+1

        args.progress = progress
        progress.setDebugInfo(str(controls))

        args.classification = isinstance(self.image, Classification)
        if args.classification:
            classes = int(self.image.meta.getMetadataItem('classes'))
            args.min = 1
            args.max = classes
            args.bins = classes-1
            args.noDataValue = 0
        else:
            args.bins = 256
        args.hist = numpy.zeros([args.bins], dtype=numpy.uint64)

        # set up the function to be applied
        def ufunc(info, inputs, outputs, args):

            args.progress.setPercentage(ApplierHelper.progress(info))

            neginfMask = numpy.isneginf(inputs.band)
            posinfMask = numpy.isposinf(inputs.band)
            nanMask = numpy.isnan(inputs.band)
            if args.noDataValue is None:
                noDataValueMask = numpy.full_like(neginfMask, fill_value=False)
            else:
                noDataValueMask = inputs.band == args.noDataValue
            validMask = numpy.logical_not(neginfMask+posinfMask+nanMask+noDataValueMask)

            if args.firstRun:
                args.countValid += validMask.sum()
                args.countNegInf += neginfMask.sum()
                args.countPosInf += posinfMask.sum()
                args.countNan += nanMask.sum()
                args.countNoDataValue += noDataValueMask.sum()
                if not args.classification:
                    args.min = min(inputs.band[validMask].min(), args.min)
                    args.max = max(inputs.band[validMask].max(), args.max)
            else:
                hist, bin_edges = numpy.histogram(inputs.band[validMask], bins=args.bins, range=[args.min, args.max])
                args.hist += hist.astype(numpy.uint64)
                args.bin_edges = bin_edges

        # Apply the function to the inputs, creating the outputs.
        args.firstRun = True
        rios.applier.apply(ufunc, infiles, outfiles, args, controls)
        args.firstRun = False

        rios.applier.apply(ufunc, infiles, outfiles, args, controls)

        del args.firstRun
        del args.progress
        self.bandStatistics[band] = args

    def report(self):

        report = Report('Image Statistics')
        report.append(ReportMonospace(self.image.filename))
        report.append(ReportHeading('Basic Statistics'))

        #n total	n ignored	n used	min	max

        colHeaders = [['Band','n total', 'n ignored','n used', 'min', 'max']]
        rowSpans = None
        colSpans = [[1,1,1,1,1,1]]
        rowHeaders = None
        data = numpy.transpose([self.getStatistic('band'),self.getStatistic('count'),numpy.array(self.getStatistic('count'))-numpy.array(self.getStatistic('countValid')),self.getStatistic('countValid'),self.getStatistic('min'),self.getStatistic('max')])
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        report.append(ReportParagraph('bands = ' + str(self.getStatistic('band'))))
        report.append(ReportParagraph('mins = ' + str(self.getStatistic('min'))))
        report.append(ReportParagraph('maxs = ' + str(self.getStatistic('max'))))

        report.append(ReportParagraph('countValids = ' + str(self.getStatistic('countValid'))))
        report.append(ReportParagraph('countNegInfs = ' + str(self.getStatistic('countNegInf'))))
        report.append(ReportParagraph('countPosInfs = ' + str(self.getStatistic('countPosInf'))))
        report.append(ReportParagraph('countNans = ' + str(self.getStatistic('countNan'))))
        report.append(ReportParagraph('countNoDataValues = ' + str(self.getStatistic('countNoDataValue'))))
        report.append(ReportParagraph('counts = ' + str(self.getStatistic('count'))))
        report.append(ReportParagraph('noDataValues = ' + str(self.getStatistic('noDataValue'))))

        report.append(ReportHeading('Histograms'))
        for i in range(0,self.bandStatistics.__len__()):
            report.append(ReportHeading('Band ' + str(i+1),sub=1))
            report.append(ReportParagraph('number of bins: ' + str(256)))
            fig, ax = plt.subplots(facecolor='white')
            #todo use band data to also have correct x-axis values instead of bin number, look for usability of bin_edges
            #n, bins, patches = plt.hist(x, 256, facecolor='green', alpha=0.75)
            plt.bar(range(0,256),self.getStatistic('hist')[i])
            ax.set_xlabel('value')
            ax.set_ylabel('counts')
            report.append(ReportPlot(fig, ''))
            plt.close()
        report.append(ReportParagraph('hists = ' + str(self.getStatistic('hist'))))
        report.append(ReportParagraph('bin_edges = ' + str(self.getStatistic('bin_edges'))))

        return report


class Mask(Image):

    def _assert(self):

        Image._assert(self)
        assert self.meta.RasterCount == 1


class NoMask(Mask):

    def __init__(self):

        self.filename = 'no mask selected'
        self.meta = GDALMeta()
        self.meta.setNoDataValue(0)


class Classification(Mask):

    def _assert(self):

        Mask._assert(self)
        assert self.meta.getMetadataItem('file_type').lower() == 'envi classification'
        assert int(self.meta.getMetadataItem('classes')) == len(self.meta.getMetadataItem('class_names'))
        assert int(self.meta.getMetadataItem('classes'))*3 == len(self.meta.getMetadataItem('class_lookup'))


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
        sample = ClassificationSample(self, classification)
        return ClusteringPerformance(sample)


class Regression(Mask):

    def _assert(self):

        Mask._assert(self)
        envi = self.meta.getMetadataDict()
        assert envi['data_ignore_value'] is not None


    def assessRegressionPerformance(self, regression):
        sample = RegressionSample(self, regression)
        return RegressionPerformance(sample)


class Probability(Image):

    def _assert(self):

        envi = self.meta.getMetadataDict()
        assert int(envi['classes']) == len(envi['class_names'])
        assert int(envi['classes'])*3 == len(envi['class_lookup'])
        assert self.meta.getNoDataValue('data_ignore_value') is not None
        Image._assert(self)

    def argmax(self, filename=Environment.tempfile('classification'), progress=progress):

        progress.setText('calculate argmax probability')

        infiles = rios.applier.FilenameAssociations()
        outfiles = rios.applier.FilenameAssociations()
        args = rios.applier.OtherInputs()

        infiles.p = self.filename
        outfiles.c = filename
        args.meta = self.meta

        controls = ApplierControls()
        progress.setDebugInfo(str(controls))

        if controls.numThreads > 1:
            args.progress = SilentProgress
        else:
            args.progress = progress
        args.progress = progress

        # set up the function to be applied
        def ufunc(info, inputs, outputs, args):

            percentage = ApplierHelper.progress(info)
            args.progress.setPercentage(percentage)

            invalid = numpy.any(inputs.p == args.meta.getNoDataValue(), axis=0, keepdims=True)
            outputs.c = numpy.argmax(inputs.p, axis=0).reshape(invalid.shape).astype(numpy.uint8) + 1
            outputs.c[invalid] = 0

        # Apply the function to the inputs, creating the outputs.
        rios.applier.apply(ufunc, infiles, outfiles, args, controls)

        # Set Metadata for output images

        meta = Meta(outfiles.c)
        meta.setMetadataItem('file type', 'ENVI Classification')
        for key in ['classes', 'class_names', 'class_lookup']:
            meta.copyMetadataItem(key, self.meta)
        meta.writeMeta(filename)

        return Classification(filename)

class Estimator(Type):

    def __init__(self, sklEstimator):

        assert isinstance(sklEstimator, sklearn.pipeline.Pipeline)
        self.sklEstimator = sklEstimator
        self.sample = None
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
        controls.windowxsize = 256
        controls.windowysize = 256

        progress.setDebugInfo(str(controls))

        if controls.numThreads > 1:
            args.progress = SilentProgress
        else:
            args.progress = progress
        args.progress = progress

        # set up the function to be applied
        def ufunc(info, inputs, outputs, args):

            percentage = int((info.xblock + info.yblock * info.xtotalblocks) / float(info.xtotalblocks * info.ytotalblocks) * 100)
            args.progress.setPercentage(percentage)


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

        if self.sample is not None:
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
        else:
            report.append(ReportHeading('Unfitted Model Parameter'))
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
                    colHeaders = [[str(estimator.scoring)]+estimator.best_params_.keys()]
                    report.append(ReportTable(data=data, colHeaders=colHeaders))

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


    def predict(self, image, mask=None, filename=Environment.tempfile('classification'), progress=progress):

        assert isinstance(image, Image)
        if mask is not None:
            assert isinstance(mask, Mask)

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


    def predictProbability(self, image, mask=None, filename=Environment.tempfile('probability'), progress=progress):

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
        from enmapbox.processing.estimators import SklearnClassifiers
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


    def predict(self, image, mask, filename=Environment.tempfile('regression'), progress=progress):

        self._predict(image, mask, predictfile=filename, progress=progress)
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

        from enmapbox.processing.estimators import SklearnRegressors
        pipe = sklearn.pipeline.make_pipeline(SklearnRegressors.UncertaintyRegressor(regressor.sklEstimator))
        Regressor.__init__(self, pipe)


    def predictNoDataValue(self):

        return 0


class Transformer(Estimator):

    def fit(self, image, mask, progress=progress):

        if mask is None: mask = NoMask()
        assert isinstance(image, Image)
        assert isinstance(mask, Mask)
        sample = UnsupervisedSample(image, mask)
        return self._fit(sample, progress=progress)


    def transform(self, image, mask=None, filename=Environment.tempfile('transformation'), progress=progress):

        self._predict(image, mask, transformfile=filename, progress=progress)
        return Image(filename)

    def transformInverse(self, image, mask=None, filename=Environment.tempfile('inverseTransformation'), progress=progress):

        self._predict(image, mask, inversetransformfile=filename, progress=progress)
        return Image(filename)


    def transformDType(self):

        return numpy.float32


    def transformNoDataValue(self):

        return numpy.finfo(self.transformDType()).max


class Clusterer(Estimator):

    def fit(self, image, mask, progress=progress):

        if mask is None: mask = NoMask()
        assert isinstance(image, Image)
        assert isinstance(mask, Mask)
        sample = UnsupervisedSample(image, mask)
        return self._fit(sample, progress=progress)


    def predict(self, image, mask=None, filename=Environment.tempfile('clustering'), progress=progress):

        self._predict(image, mask, predictfile=filename, progress=progress)
        return Classification(filename)


    def predictMeta(self, meta, imeta, mmeta):

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


class UnsupervisedSample(Type):

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
        args = rios.applier.OtherInputs()

        infiles.x = self.image.filename
        args.xMeta = self.image.meta

        if not isinstance(self.mask, NoMask):
            infiles.y = self.mask.filename

        args.yMeta = self.mask.meta

        args.x = list()
        args.y = list()

        def ufunc(info, inputs, outputs, args):

            # reshape to 2d
            inputs.x = inputs.x.reshape((inputs.x.shape[0], -1))
            if not isinstance(self.mask, NoMask):
                inputs.y = inputs.y.reshape((1, -1))
            else:
                inputs.y = numpy.ones([1,inputs.x.shape[1]], dtype=numpy.uint8)

                # create mask
            valid = inputs.y[0] != args.yMeta.getNoDataValue(default=0)

            # exclude invalid samples if needed
            if valid.all():
                args.x.append(inputs.x)
                args.y.append(inputs.y[0, :])
            else:
                args.x.append(inputs.x[:, valid])
                args.y.append(inputs.y[0, valid])

        rios.applier.apply(ufunc, infiles, outfiles, args)

        return (numpy.hstack(args.x).T, numpy.hstack(args.y))


class ClassificationSample(UnsupervisedSample):

    def _assert(self):
        UnsupervisedSample._assert(self)
        assert isinstance(self.mask, Classification), 'Mask is not a Classification!'


class RegressionSample(UnsupervisedSample):

    def _assert(self):
        UnsupervisedSample._assert(self)
        assert isinstance(self.mask, Regression), 'Mask is not a Regression!'


class ClassificationPerformance(Type):

    @staticmethod
    def fromSample(sample):

        assert isinstance(sample, ClassificationSample), 'Classification sample is required!'
        assert isinstance(sample.image, Classification), 'Prediction is not a classification!'
        assert int(sample.image.meta.getMetadataItem('classes')) == int(sample.mask.meta.getMetadataItem('classes')), 'Number of classes in prediction and reference do not match!'
        result = ClassificationPerformance(classes=int(sample.mask.meta.getMetadataItem('classes'))-1,
                                           classNames=sample.mask.meta.getMetadataItem('class names')[1:])
        result.update(yP=sample.imageData, yT=sample.labelData)
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

    def __init__(self, classes, classNames=None, classProportions=None):

        assert isinstance(classes, int)
        if classNames is None:
            classNames = ['Class '+str(i) for i in range(1,classes+1)]
        assert classes == len(classNames)

        self.classes = classes
        self.classLabels = range(1, self.classes+1)
        self.classNames = classNames
        self.mij = numpy.zeros((classes, classes), dtype=numpy.int64)
        self.m = numpy.int64(0)
        self.Wi = classProportions
        self.adjusted = False

    def update(self, yP, yT):

        assert isinstance(yP, numpy.ndarray)
        assert isinstance(yT, numpy.ndarray)
        self.mij += sklearn.metrics.confusion_matrix(yT, yP, labels=self.classLabels).T
        self.m += yP.size


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
        self.ProducerAccuracy = self._fix(self.mii/self.mi_)
        self.UserAccuracy = self._fix(self.mii / self.m_j)

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

        report.append(ReportHeading('Input Files'))
        report.append(ReportParagraph('Reference: ' + self.sample.mask.filename))
        report.append(ReportParagraph('Prediction: ' + self.sample.image.filename))
        report.append(ReportParagraph('Stratification: ' + self.sampleStratification.image.filename) if self.adjusted else '')

        if self.adjusted:
            report.append(ReportHeading('Stratification'))
            report.append(ReportParagraph('strataClasses: ' + str(self.strataClasses)))
            report.append(ReportParagraph('strataClassNames: ' + str(self.strataClassNames)))
            report.append(ReportParagraph('strataSizes: ' + str(self.strataSizes)))
            report.append(ReportParagraph('strataSampleSizes: ' + str(self.strataSampleSizes)))
            report.append(ReportParagraph('strataWeights: ' + str(self.strataWeights)))

        report.append(ReportHeading('Classification Label Overview'))
        colHeaders = None
        rowSpans = [[1,2],[1,1,1]]
        colSpans = [[1,1,1,1,1]]
        rowHeaders = [['','Class Names'],['Class ID','Reference', 'Prediction']]
        data = [numpy.hstack((0,self.classLabels)),self.sample.mask.meta.getMetadataItem('class names'),self.sample.image.meta.getMetadataItem('class names')]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Confusion Matrix Table
        report.append(ReportHeading('Confusion Matrix'))
        rowSpans = None
        classNumbers = []
        for i in range(self.classes): classNumbers.append('('+str(i+1)+')')
        colHeaders = [['Reference Class'],classNumbers + ['Sum']]
        colSpans = [[self.classes],numpy.ones(self.classes+1,dtype=int)]
        classNamesColumn = []
        for i in range(self.classes): classNamesColumn.append('('+str(i+1)+') '+self.classNames[i])
        rowHeaders = [classNamesColumn+['Sum']]
        data = numpy.vstack(((numpy.hstack((self.mij,self.m_j[:, None]))),numpy.hstack((self.mi_,self.m)))).astype(int)

        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Accuracies Table
        report.append(ReportHeading('Accuracies'))
        colHeaders = [['Measure', 'Estimate [%]', '95 % Confidence Interval [%]']]
        colSpans = [[1,1,2]]
        rowHeaders = None
        data = [['Overall Accuracy',numpy.round(self.OverallAccuracy*100,2),numpy.round(self.confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[0]*100),round(self.confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[1]*100,2)],
                ['Kappa Accuracy',numpy.round(self.KappaAccuracy*100,2),numpy.round(self.confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[0]*100,2),numpy.round(self.confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[1]*100,2)],
                ['Mean F1 Accuracy',numpy.round(numpy.mean(self.F1Accuracy)*100,2),'-','-']]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Class-wise Accuracies Table
        report.append(ReportHeading('Class-wise Accuracies'))
        colSpans = [[1,3,3,3],[1,1,2,1,2,1,2]]
        colHeaders = [['','User\'s Accuracy [%]','Producer\'s Accuracy [%]','F1 Accuracy'],['Map class','Estimate','95 % Interval','Estimate','95% Interval','Estimate','95% Interval']]
        data = [classNamesColumn,numpy.round(self.UserAccuracy*100,2)
               ,numpy.round(self.confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[0]*100,2)
               ,numpy.round(self.confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[1]*100,2)
               ,numpy.round(self.ProducerAccuracy*100,2)
               ,numpy.round(self.confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[0]*100,2)
               ,numpy.round(self.confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[1]*100,2)
               ,numpy.round(self.F1Accuracy*100,2)
               ,numpy.round(self.confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[0]*100,2)
               ,numpy.round(self.confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[1]*100,2)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Proportion Matrix Table
        report.append(ReportHeading('Proportion Matrix'))
        colHeaders = [['Reference Class'],classNumbers + ['Sum']]
        colSpans = [[self.classes],numpy.ones(self.classes+1,dtype=int)]
        rowHeaders = [classNamesColumn+['Sum']]
        data = numpy.vstack(((numpy.hstack((self.pij*100,self.p_j[:, None]*100))),numpy.hstack((self.pi_*100,100))))
        report.append(ReportTable(numpy.round(data,2), '', colHeaders, rowHeaders, colSpans, rowSpans)) \


        '''report.append(ReportHeading('Confusion Matrix'))
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
        report.append(ReportMonospace('ClassProportion = '+str(self.confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05))))'''


        return report


class ClassificationPerformanceAdjusted(ClassificationPerformance):

    @staticmethod
    def fromSample(samplePrediction, sampleStratification):
        assert isinstance(samplePrediction, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(sampleStratification, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(samplePrediction.image, Classification), 'Prediction is not a classification!'
        assert isinstance(sampleStratification.image, Classification), 'Stratification is not a classification!'

        assert int(samplePrediction.image.meta.getMetadataItem('classes')) == int(samplePrediction.mask.meta.getMetadataItem('classes')), 'Number of classes in prediction and reference do not match!'

        classes=int(samplePrediction.mask.meta.getMetadataItem('classes')) - 1
        classNames=samplePrediction.mask.meta.getMetadataItem('class names')[1:]
        strataClasses = int(sampleStratification.image.meta.getMetadataItem('classes')) - 1
        strataClassNames = sampleStratification.image.meta.getMetadataItem('class names')[1:]
        strataSizes = sampleStratification.image.statistics().getStatistic('hist', bands=[0])[0]
        strataSampleSizes = numpy.histogram(sampleStratification.imageData, bins=strataClasses, range=[1,strataClasses+1])[0]

        result = ClassificationPerformanceAdjusted(classes=classes,
                                                   classNames=classNames,
                                                   strataClasses=strataClasses,
                                                   strataClassNames=strataClassNames,
                                                   strataSizes=strataSizes,
                                                   strataSampleSizes=strataSampleSizes)

        result.sample = samplePrediction
        result.sampleStratification = sampleStratification

        result.update(yP=samplePrediction.imageData.ravel(), yT=samplePrediction.labelData.ravel(), yS=sampleStratification.imageData.ravel())
        result.assessPerformance()
        return result

    def __init__(self, classes, classNames, strataClasses, strataClassNames, strataSizes, strataSampleSizes):

        assert isinstance(strataSizes, numpy.ndarray) and strataSizes.size == strataClasses
        assert isinstance(strataSampleSizes, numpy.ndarray) and strataSampleSizes.size == strataClasses

        self.strataClasses = strataClasses
        self.strataClassNames = strataClassNames
        self.strataSizes = strataSizes
        self.strataSampleSizes = strataSampleSizes
        self.strataWeights = (strataSizes/strataSizes.sum()) / (strataSampleSizes/strataSampleSizes.sum())

        self.classificationPerformances = [ClassificationPerformance(classes, classNames) for i in range(1, strataClasses+1)]
        ClassificationPerformance.__init__(self, classes, classNames)
        self.mij = self.mij.astype(numpy.float32)
        self.m = float(self.m)
        self.adjusted = True

    def update(self, yP, yT, yS):

        assert isinstance(yP, numpy.ndarray)
        assert isinstance(yT, numpy.ndarray)
        assert isinstance(yS, numpy.ndarray)

        for stratum, classificationPerformance in enumerate(self.classificationPerformances, 1):
            indices = yS == stratum
            classificationPerformance.update(yT[indices], yP[indices])
            stratumWeight = self.strataWeights[stratum-1]
            self.mij += classificationPerformance.mij * stratumWeight
            self.m += classificationPerformance.m * stratumWeight


class RegressionPerformance(Type):

    def __init__(self, sample):

        assert isinstance(sample, RegressionSample), 'Regression sample is requiered!'
        assert isinstance(sample.image, Regression), 'Prediction is not a regression!'
        self.sample = sample
        self._assessPerformance()

    def _assessPerformance(self):

        self.prediction = self.sample.imageData.flatten()
        self.reference = self.sample.labelData.flatten()
        self.residuals = self.prediction
        self.n = self.reference.size
        self.explained_variance_score = str(sklearn.metrics.explained_variance_score(self.reference, self.prediction))
        self.mean_absolute_error = str(sklearn.metrics.mean_absolute_error(self.reference, self.prediction))
        self.median_absolute_error = str(sklearn.metrics.median_absolute_error(self.reference, self.prediction))
        self.mean_squared_error = str(sklearn.metrics.mean_squared_error(self.reference, self.prediction)**0.5)

    def report(self):

        report = Report('Regression Performance')

        report.append(ReportHeading('Input Files'))
        report.append(ReportMonospace('Reference:  ' + self.sample.mask.filename + '\nPrediction: ' + self.sample.image.filename))

        report.append(ReportHeading('Performance Measures'))
        report.append(ReportParagraph('n = ' + str(self.n)))
        report.append(ReportParagraph('explained_variance_score = ' + str(self.explained_variance_score)))
        report.append(ReportParagraph('mean_absolute_error = ' + str(self.mean_absolute_error)))
        report.append(ReportParagraph('median_absolute_error = ' + str(self.median_absolute_error)))
        report.append(ReportParagraph('mean_squared_error = ' + str(self.mean_squared_error)))

        report.append(ReportHeading('Residuals'))
        report.append(ReportParagraph('ToDo: Scatter Plot Reference vs. Predicted', font_color='red'))
        report.append(ReportParagraph('ToDo: Plot Residuals Distribution', font_color='red'))

        report.append(ReportParagraph('predicted = ' + str(self.prediction)))
        report.append(ReportParagraph('reference = ' + str(self.reference)))
        report.append(ReportParagraph('residuals = ' + str(self.residuals)))

        return report

class ClusteringPerformance(Type):

    def __init__(self, sample):

        assert isinstance(sample, ClassificationSample), 'Classification sample is requiered!'
        assert isinstance(sample.image, Classification), 'Prediction is not a classification!'
        self.sample = sample
        self._assessPerformance()


    def __str__(self):

        return  self.report


    def _assessPerformance(self):

        self.prediction = self.sample.imageData.flatten()
        self.reference = self.sample.labelData.flatten()
        self.n = self.prediction.size
        self.adjusted_mutual_info_score = sklearn.metrics.cluster.adjusted_mutual_info_score(self.reference, self.prediction)
        self.adjusted_rand_score = sklearn.metrics.cluster.adjusted_rand_score(self.reference, self.prediction)
        self.completeness_score = sklearn.metrics.cluster.completeness_score(self.reference, self.prediction)

    def report(self):

        report = Report('Clustering Performance')

        report.append(ReportHeading('Input Files'))
        report.append(ReportMonospace('Reference:  ' + self.sample.mask.filename + '\nPrediction: ' + self.sample.image.filename))

        report.append(ReportHeading('Performance Measures'))
        report.append(ReportParagraph('n = ' + str(self.n)))
        report.append(ReportParagraph('adjusted_mutual_info_score = ' + str(self.adjusted_mutual_info_score)))
        report.append(ReportParagraph('adjusted_rand_score = ' + str(self.adjusted_rand_score)))
        report.append(ReportParagraph('completeness_score = ' + str(self.completeness_score)))
        report.append(ReportParagraph('ToDo: include Scikit-Learn Hyperlinks!', font_color='red'))

        return report


class PixelExtractor():

    def __init__(self, image, locationsType):
        assert isinstance(image, Image)
        self.locationsType = locationsType

    def extract(self, mask):
        assert isinstance(mask, Mask)
        return

class _UnsupervisedSample(Type):

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
        args = rios.applier.OtherInputs()

        infiles.x = self.image.filename
        args.xMeta = self.image.meta

        if not isinstance(self.mask, NoMask):
            infiles.y = self.mask.filename

        args.yMeta = self.mask.meta

        args.x = list()
        args.y = list()

        def ufunc(info, inputs, outputs, args):

            # reshape to 2d
            inputs.x = inputs.x.reshape((inputs.x.shape[0], -1))
            if not isinstance(self.mask, NoMask):
                inputs.y = inputs.y.reshape((1, -1))
            else:
                inputs.y = numpy.ones([1,inputs.x.shape[1]], dtype=numpy.uint8)

                # create mask
            valid = inputs.y[0] != args.yMeta.getNoDataValue(default=0)

            # exclude invalid samples if needed
            if valid.all():
                args.x.append(inputs.x)
                args.y.append(inputs.y[0, :])
            else:
                args.x.append(inputs.x[:, valid])
                args.y.append(inputs.y[0, valid])

        rios.applier.apply(ufunc, infiles, outfiles, args)

        return (numpy.hstack(args.x).T, numpy.hstack(args.y))