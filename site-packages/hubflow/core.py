from operator import xor
import random, pickle
from collections import OrderedDict
import sklearn.metrics
import sklearn.multioutput
from PyQt5.QtGui import QColor

from hubdc.progressbar import ProgressBar
from hubdc.core import *
from hubdc.applier import ApplierOutputRaster
from hubflow.applier import Applier, ApplierOperator, ApplierControls

from hubflow.report import *
from hubflow import signals


class FlowObjectPickleFileError(Exception):
    pass


class FlowObjectTypeError(Exception):
    pass


class FlowObject(object):
    def pickle(self, filename, progressBar=None):
        self._initPickle()
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)
        signals.sigFileCreated.emit(filename)

        if progressBar is not None:
            assert isinstance(progressBar, ProgressBar)
            progressBar.setText('{}.pickle(filename={})'.format(self.__class__.__name__, filename))
            progressBar.setText(repr(self))

        return self

    @classmethod
    def unpickle(cls, filename, raiseError=True):
        try:
            with open(filename, 'rb') as f:
                obj = pickle.load(file=f)
        except:
            if raiseError:
                raise FlowObjectPickleFileError('not a valid pickle file: ' + str(filename))
            else:
                return None

        if not isinstance(obj, cls):
            if raiseError:
                raise FlowObjectTypeError('wrong type ({t1}), expected type: {t2}'.format(t1=obj.__class__.__name__,
                                                                                          t2=cls.__name__))
            else:
                return None
        return obj

    def _initPickle(self):
        pass


class MapCollection(FlowObject):
    def __init__(self, maps):
        self._maps = maps

    def __repr__(self):
        return '{cls}(maps={maps})'.format(cls=self.__class__.__name__, maps=repr(self.maps()))

    def _initPickle(self):
        for map in self.maps():
            map._initPickle()

    def maps(self):
        return self._maps

    def extractAsArray(self, masks, grid=None, onTheFlyResampling=False, **kwargs):
        if grid is None:
            grid = self.maps()[0].grid()
        assert isinstance(grid, Grid)
        equalGrids = True
        for map in self.maps() + masks:
            if isinstance(map, Raster):
                equalGrids &= map.grid().equal(other=grid)

        if equalGrids:

            def getRasterDataset(map):
                if isinstance(map, Raster):
                    rasterDataset = map.dataset()
                elif isinstance(map, Vector):
                    gdalType = gdal_array.NumericTypeCodeToGDALTypeCode(map.dtype())
                    rasterDataset = map.dataset().rasterize(grid=grid,
                                                            gdalType=gdalType,
                                                            initValue=map.initValue(),
                                                            burnValue=map.burnValue(),
                                                            burnAttribute=map.burnAttribute(),
                                                            allTouched=map.allTouched(),
                                                            filterSQL=map.filterSQL(),
                                                            noDataValue=map.noDataValue())
                elif map is None:
                    rasterDataset = None
                else:
                    assert 0, repr(map)
                return rasterDataset

            # calculate overall mask
            marray = np.full(shape=grid.shape(), fill_value=np.True_)
            for map in masks:
                rasterDataset = getRasterDataset(map=map)
                if rasterDataset is None:
                    continue
                for band in rasterDataset.bands():
                    marray *= band.readAsArray() != band.noDataValue(default=0)

            nothingToExtract = not marray.any()

            # extract values for all masked pixels
            arrays = list()
            for map in self.maps():
                zsize = map.dataset().zsize()
                if nothingToExtract:
                    zsize = map.dataset().zsize()
                    profiles = np.empty(shape=(zsize, 0), dtype=np.uint8)
                else:
                    array = getRasterDataset(map=map).readAsArray()
                    profiles = array[:, marray]

                arrays.append(profiles)

        else:
            assert onTheFlyResampling is True
            arrays = extractPixels(inputs=self.maps(), masks=masks, grid=grid, **kwargs)
        return arrays

    def extractAsRaster(self, filenames, grid, masks, onTheFlyResampling=False, **kwargs):
        assert isinstance(filenames, list)
        assert len(filenames) == len(self.maps())
        arrays = self.extractAsArray(grid=grid, masks=masks, onTheFlyResampling=onTheFlyResampling, **kwargs)
        rasters = list()

        for filename, array, map in zip(filenames, arrays, self.maps()):
            # from single line 3d array ...
            array = np.atleast_3d(array)

            # ... to multiple line 3d array (to avoid very long lines)
            from math import ceil
            bands = array.shape[0]
            lines = min(3600, array.shape[1])
            samples = ceil(array.shape[1] / float(lines))
            print(map)
            array2 = np.full(shape=(bands, lines*samples, 1), fill_value=map.noDataValue(default=np.nan),
                             dtype=map.dtype())
            array2[:, :array.shape[1]] = array[:]
            array2 = np.reshape(array2, (bands, lines, samples))

            rasterDataset = createRasterDatasetFromArray(array=array2,
                                                         filename=filename,
                                                         driver=RasterDriver.fromFilename(filename=filename))

            if isinstance(map, (Classification, VectorClassification)):
                MetadataEditor.setClassDefinition(rasterDataset=rasterDataset,
                                                  classDefinition=map.classDefinition())
            elif isinstance(map, Fraction):
                MetadataEditor.setFractionDefinition(rasterDataset=rasterDataset,
                                                     classDefinition=map.classDefinition())
            elif isinstance(map, Regression):
                MetadataEditor.setRegressionDefinition(rasterDataset=rasterDataset,
                                                       noDataValues=map.noDataValues(),
                                                       outputNames=map.outputNames())
            elif isinstance(map, Vector):
                pass
            elif isinstance(map, Raster):
                bandCharacteristics = MetadataEditor.bandCharacteristics(rasterDataset=rasterDataset)
                MetadataEditor.setBandCharacteristics(rasterDataset=rasterDataset, **bandCharacteristics)
            else:
                assert 0, repr(map)

            rasterDataset.flushCache()
            if isinstance(map, Raster):
                raster = type(map).fromRasterDataset(rasterDataset=rasterDataset)
            else:
                raster = Raster.fromRasterDataset(rasterDataset=rasterDataset)
            rasters.append(raster)
        return rasters

class ConvolutionKernel(FlowObject):
    pass

class Raster(FlowObject):
    def __init__(self, filename):
        self._filename = filename
        self._rasterDataset = None

    def __repr__(self):
        return '{cls}(filename={filename})'.format(cls=self.__class__.__name__, filename=str(self.filename()))

#    def __setstate__(self, state):
#        self.__init__(**state)

#    def __getstate__(self):
#        state = {'filename': self.filename()}
#        return state

    def _initPickle(self):
        self._rasterDataset = None


    def filename(self):
        return self._filename

    def dataset(self):
        if self._rasterDataset is None:
            self._rasterDataset = openRasterDataset(self.filename())
        assert isinstance(self._rasterDataset, RasterDataset)
        return self._rasterDataset

    def noDataValue(self, default=None):
        return self.dataset().noDataValue(default=default)

    def dtype(self):
        return self.dataset().dtype()

    def grid(self):
        return self.dataset().grid()

    @classmethod
    def fromRasterDataset(cls, rasterDataset, **kwargs):
        assert isinstance(rasterDataset, RasterDataset)
        filename = rasterDataset.filename()
        raster = cls(rasterDataset.filename(), **kwargs)
        raster._rasterDataset = rasterDataset
        return raster

    @classmethod
    def fromVector(cls, filename, vector, grid, noDataValue=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowVector('vector', vector=vector)
        applier.setOutputRaster('raster', filename=filename)
        applier.apply(operatorType=_RasterFromVector, vector=vector, noDataValue=noDataValue)
        return Raster(filename=filename)

    @staticmethod
    def fromENVISpectralLibrary(filename, library):
        assert isinstance(library, ENVISpectralLibrary)
        rasterDataset = library.raster().dataset().translate(filename=filename,
                                                             driver=RasterDriver.fromFilename(filename=filename))
        rasterDataset.copyMetadata(other=library.raster().dataset())
        return Raster.fromRasterDataset(rasterDataset=rasterDataset)

    def uniqueValues(self, index):
        values = np.unique(self.dataset().band(index=index).readAsArray())
        return values

    def convolve(self, filename, kernel, **kwargs):
        from astropy.convolution import Kernel
        assert isinstance(kernel, Kernel)
        assert kernel.dimension <= 3
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('inraster', raster=self)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_RasterConvolve, raster=self, kernel=kernel)
        return Raster(filename=filename)

    def applySpatial(self, filename, function, **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.controls.setBlockFullSize()
        applier.setFlowRaster('inraster', raster=self)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_RasterApplySpatial, raster=self, function=function)
        return Raster(filename=filename)

    def resample(self, filename, grid, resampleAlg=gdal.GRA_NearestNeighbour, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster('inraster', raster=self)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_RasterResample, raster=self, resampleAlg=resampleAlg)
        return Raster(filename=filename)

    def asMask(self, noDataValues=None, minOverallCoverage=0.5, index=None):
        return Mask(filename=self.filename(), noDataValues=noDataValues, minOverallCoverage=minOverallCoverage,
                    index=index)

    def statistics(self, bandIndicies=None, mask=None,
                   calcPercentiles=False, calcHistogram=False, calcMean=False, calcStd=False,
                   histogramRanges=None, histogramBins=None,
                   **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.controls.setBlockFullSize()
        applier.setFlowRaster('raster', raster=self)
        applier.setFlowMask('mask', mask=mask)
        return applier.apply(operatorType=_RasterStatistics, raster=self, bandIndicies=bandIndicies, mask=mask,
                             calcPercentiles=calcPercentiles, calcMean=calcMean, calcStd=calcStd,
                             calcHistogram=calcHistogram, histogramRanges=histogramRanges, histogramBins=histogramBins)

    def scatterMatrix(self, raster2, bandIndex1, bandIndex2, range1, range2, bins=256, mask=None, stratification=None,
                      **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('raster1', raster=self)
        applier.setFlowRaster('raster2', raster=raster2)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowClassification('stratification', classification=stratification)

        _, xedges, yedges = np.histogram2d(x=[0], y=[0], bins=bins, range=[range1, range2])
        bins = [xedges, yedges]
        results = applier.apply(operatorType=_RasterScatterMatrix, raster1=self, raster2=raster2,
                                bandIndex1=bandIndex1, bandIndex2=bandIndex2, bins=bins, mask=mask,
                                stratification=stratification)
        H = np.sum(np.stack(results), axis=0, dtype=np.uint64)
        return H, xedges, yedges

    def applyMask(self, filename, mask, **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('raster', raster=self)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('maskedRaster', filename=filename)
        applier.apply(operatorType=_RasterApplyMask, raster=self, mask=mask)
        return Raster(filename=filename)

    #    def metadataDict(self):
    #        return self.dataset().metadataDict()

    def metadataWavelength(self):
        wavelength = self.dataset().metadataItem(key='wavelength', domain='ENVI', dtype=float, required=True)
        unit = self.dataset().metadataItem(key='wavelength units', domain='ENVI', required=True)
        assert unit.lower() in ['nanometers', 'micrometers']
        wavelength = [float(v) for v in wavelength]
        if unit.lower() == 'micrometers':
            wavelength = [v * 1000 for v in wavelength]
        return wavelength

    def metadataFWHM(self, required=False):
        fwhm = self.dataset().metadataItem(key='fwhm', domain='ENVI', dtype=float, required=required)
        if fwhm is None:
            fwhm = [None] * self.dataset().zsize()
        else:
            unit = self.dataset().metadataItem(key='wavelength units', domain='ENVI', required=True)
            assert unit.lower() in ['nanometers', 'micrometers']
            fwhm = [float(v) for v in fwhm]
            if unit.lower() == 'micrometers':
                fwhm = [v * 1000 for v in fwhm]

        return fwhm

    def sensorDefinition(self):
        return SensorDefinition.fromFWHM(centers=self.metadataWavelength(), fwhms=self.metadataFWHM())


class _RasterResample(ApplierOperator):
    def ufunc(self, raster, resampleAlg):
        inraster = self.inputRaster.raster(key='inraster')
        outraster = self.outputRaster.raster(key='outraster')

        array = inraster.array(resampleAlg=resampleAlg)
        metadataDict = inraster.metadataDict()
        noDataValues = inraster.noDataValues()

        outraster.setArray(array=array)
        outraster.setMetadataDict(metadataDict=metadataDict)
        outraster.setNoDataValues(values=noDataValues)


class _RasterConvolve(ApplierOperator):
    def ufunc(self, raster, kernel):
        from astropy.convolution import convolve, CustomKernel

        if kernel.dimension == 3:
            pass
        elif kernel.dimension == 2:
            kernel = CustomKernel(array=kernel.array[None])
        elif kernel.dimension == 1:
            kernel = CustomKernel(array=kernel.array.reshape(-1, 1, 1))

        inraster = self.inputRaster.raster(key='inraster')
        outraster = self.outputRaster.raster(key='outraster')
        zsize, ysize, xsize = kernel.shape
        overlap = int((max(ysize, xsize)+1)/2.)
        array = np.float32(inraster.array(overlap=overlap))
        noDataValues = self.inputRaster.raster(key='inraster').noDataValues()
        for band, noDataValue in zip(array, noDataValues):
            if noDataValue is not None:
                band[band==noDataValue] = np.nan
        outarray = convolve(array=array, kernel=kernel,
                            fill_value=np.nan, nan_treatment='fill',
                            normalize_kernel=False)
        outraster.setArray(array=outarray, overlap=overlap)
        #outraster.setMetadataDict(metadataDict=inraster.metadataDict())
        outraster.setNoDataValue(value=np.nan)


class _RasterApplySpatial(ApplierOperator):
    def ufunc(self, raster, function):

        inraster = self.inputRaster.raster(key='inraster')
        outraster = self.outputRaster.raster(key='outraster')
        outraster.setZsize(zsize=inraster.dataset().zsize())
        for index in range(inraster.dataset().zsize()):
            array = inraster.bandArray(indicies=[index])[0]
            outarray = function(array)
            outraster.band(index=index).setArray(array=outarray)


class _RasterStatistics(ApplierOperator):
    def ufunc(self, raster, bandIndicies, mask, calcPercentiles, calcHistogram, calcMean, calcStd,
              histogramRanges, histogramBins):

        maskValid = self.flowMaskArray('mask', mask=mask)

        if bandIndicies is None:
            bandIndicies = range(self.inputRaster.raster('raster').dataset().zsize())

        result = list()
        for i, index in enumerate(bandIndicies):
            self.progressBar.setPercentage((float(i) + 1) / len(bandIndicies) * 100)
            band = self.flowRasterArray('raster', raster=raster, indices=[index]).astype(dtype=np.float64)
            valid = self.maskFromBandArray(array=band, noDataValueSource='raster', index=index)
            valid *= maskValid
            values = band[valid]  # may still contain NaN
            bandResult = {'index': index}
            bandResult['nvalid'] = np.sum(valid)
            bandResult['ninvalid'] = np.product(band.shape) - bandResult['nvalid']

            if calcPercentiles:
                qs = [0, 5, 25, 50, 75, 95, 100]
                ps = np.nanpercentile(values, q=qs)
                bandResult['percentiles'] = list(zip(qs, ps))
                bandResult['min'] = ps[qs.index(0)]
                bandResult['max'] = ps[qs.index(100)]
                bandResult['median'] = ps[qs.index(50)]
            else:
                bandResult['min'] = np.nanmin(values)
                bandResult['max'] = np.nanmax(values)

            if calcStd:
                bandResult['std'] = np.nanstd(values)

            if calcMean:
                bandResult['mean'] = np.nanmean(values)

            if calcHistogram:
                if histogramRanges is None:
                    range_ = [bandResult['min'], bandResult['max']]
                else:
                    assert len(histogramRanges) == len(bandIndicies)
                    range_ = histogramRanges[index]
                if histogramBins is None:
                    bins = 256
                else:
                    assert len(histogramBins) == len(bandIndicies)
                    bins = histogramBins[index]

                hist, bin_edges = np.histogram(values, bins=bins, range=range_)
                bandResult['histo'] = {'hist': hist, 'bin_edges': bin_edges}

            result.append(bandResult)
        return result

    @staticmethod
    def aggregate(blockResults, grid, *args, **kwargs):
        return blockResults[0]

class _RasterFromVector(ApplierOperator):
    def ufunc(self, vector, noDataValue):
        array = self.flowVectorArray('vector', vector=vector)
        self.outputRaster.raster(key='raster').setArray(array=array)
        self.setFlowMetadataNoDataValues('raster', noDataValues=[noDataValue])


class _RasterScatterMatrix(ApplierOperator):
    def ufunc(self, raster1, raster2, bandIndex1, bandIndex2, bins, mask, stratification):

        band1 = self.flowRasterArray('raster1', raster=raster1, indices=[bandIndex1])
        band2 = self.flowRasterArray('raster2', raster=raster2, indices=[bandIndex2])
        strata = self.flowClassificationArray('stratification', classification=stratification)

        valid = self.maskFromBandArray(array=band1, noDataValueSource='raster1', index=bandIndex1)
        valid *= self.maskFromBandArray(array=band2, noDataValueSource='raster2', index=bandIndex2)
        valid *= self.flowMaskArray('mask', mask=mask)

        x = band1[valid]
        y = band2[valid]

        if strata.size == 0:
            H = np.histogram2d(x=x, y=y, bins=bins)[0]
        else:
            s = strata[valid]
            HList = list()
            for i in range(1, stratification.classDefinition().classes() + 1):
                v = s == i
                Hi = np.histogram2d(x=x[v], y=y[v], bins=bins)[0]
                HList.append(np.array(Hi))
            H = np.stack(HList)

        return H


class _RasterApplyMask(ApplierOperator):
    def ufunc(self, raster, mask):
        noDataValue = self.inputRaster.raster(key='raster').noDataValue(default=0)
        array = self.flowRasterArray('raster', raster=raster)
        marray = self.flowMaskArray('mask', mask=mask)
        tobefilled = np.logical_not(marray[0])
        array[:, tobefilled] = noDataValue
        outraster = self.outputRaster.raster(key='maskedRaster')
        outraster.setArray(array=array)
        metadataDict = self.inputRaster.raster(key='raster').metadataDict()
        outraster.setMetadataDict(metadataDict)
        outraster.setNoDataValue(value=noDataValue)


class WavebandDefinition():
    def __init__(self, center, fwhm=None, wavelengths=None, responses=None, name=None):
        if wavelengths is not None:
            wavelengths = np.array(wavelengths, dtype=np.float32)
        if responses is not None:
            responses = np.array(responses, dtype=np.float32)

        self._center = float(center)
        if fwhm is not None:
            fwhm = float(fwhm)
        self._fwhm = fwhm
        self._wavelengths = wavelengths
        self._responses = responses
        self._name = name

    def __repr__(self):
        return '{cls}(center={center}, wavelengths={wavelengths}, responses={responses})'.format(
            cls=self.__class__.__name__,
            center=str(self._center),
            wavelengths='array[{}]'.format(len(self._wavelengths)),
            responses='array[{}]'.format(len(self._responses)))

    @staticmethod
    def fromFWHM(center, fwhm, sigmaLimits=3):
        center = float(center)
        if fwhm is not None:
            fwhm = float(fwhm)
            sigma = fwhm / 2.3548
            wavelengths = np.array(range(int(center - sigmaLimits * sigma), int(center + sigmaLimits * sigma)))
            responses = np.exp(-(wavelengths - center) ** 2 / (2 * sigma ** 2))
        else:
            wavelengths = None
            responses = None
        return WavebandDefinition(center=center, fwhm=fwhm, wavelengths=wavelengths, responses=responses)

    def center(self):
        return self._center

    def fwhm(self):
        return self._fwhm

    def wavelengths(self):
        assert isinstance(self._wavelengths, np.ndarray)
        return self._wavelengths

    def responses(self):
        assert isinstance(self._responses, np.ndarray)
        return self._responses

    def name(self):
        return self._name

    def resamplingWeights(self, sensor):
        assert isinstance(sensor, SensorDefinition)
        centers = sensor.wavebandCenters()
        weights = list()
        for center in centers:
            if center > self._wavelengths[-1] or center < self._wavelengths[0]:
                weight = 0.
            else:
                weight = self._responses[np.abs(np.subtract(self._wavelengths, center)).argmin()]
            weights.append(weight)
        return weights

    def plot(self, plotWidget=None, yscale=1., **kwargs):
        import pyqtgraph as pg
        if plotWidget is None:
            plotWidget = pg.plot(title='Response Curve')
        plotWidget.plot(x=self.wavelengths(), y=self.responses() * yscale, **kwargs)
        return plotWidget


class SensorDefinition():
    RESAMPLE_RESPONSE = 'response'
    RESAMPLE_LINEAR = 'linear'
    RESAMPLE_OPTIONS = [RESAMPLE_LINEAR, RESAMPLE_RESPONSE]

    def __init__(self, wavebandDefinitions):
        self._wavebandDefinitions = wavebandDefinitions

    def __repr__(self):
        return '{cls}(wavebandDefinitions={wavebandDefinitions})'.format(
            cls=self.__class__.__name__,
            wavebandDefinitions=str(self._wavebandDefinitions))

    @classmethod
    def fromENVISpectralLibrary(cls, library):
        assert isinstance(library, ENVISpectralLibrary)

        names = library.raster().dataset().metadataItem(key='spectra names', domain='ENVI')
        wavelengths = np.float32(library.raster().metadataWavelength())

        isResponseFunction = True
        for i in range(len(wavelengths) - 1):
            if (wavelengths[i + 1] - wavelengths[i]) != 1:
                isResponseFunction = False
                break

        if isResponseFunction:
            responsess = library.raster().dataset().readAsArray().T[0]  # sample.features.T
            sensor = cls.fromResponseFunctions(centers=None, names=names, wavelengths=wavelengths,
                                               responsess=responsess)
        else:
            fwhm = library.raster().metadataFWHM(required=True)
            sensor = cls.fromFWHM(centers=wavelengths, fwhms=fwhm)

        return sensor

    @staticmethod
    def fromResponseFunctions(centers, names, wavelengths, responsess):
        if names is None:
            names = [None] * len(responsess)
        if centers is None:
            centers = [None] * len(responsess)

        assert len(centers) == len(names)
        assert isinstance(wavelengths, np.ndarray) and wavelengths.ndim == 1
        assert isinstance(responsess, np.ndarray) and responsess.ndim == 2
        assert wavelengths.shape[0] == responsess.shape[1]

        wavebandDefinitions = list()
        for responses, name, center in zip(responsess, names, centers):
            if center is None:
                center = wavelengths[responses > 0.01][[0, -1]].mean()
            valid = responses > 0.01
            wavebandDefinitions.append(WavebandDefinition(center=center,
                                                          fwhm=None,
                                                          wavelengths=wavelengths[valid],
                                                          responses=responses[valid],
                                                          name=name))

        return SensorDefinition(wavebandDefinitions=wavebandDefinitions)

    @staticmethod
    def fromFWHM(centers, fwhms):
        assert len(centers) == len(fwhms)
        wavebandDefinitions = [WavebandDefinition.fromFWHM(center=center, fwhm=fwhm)
                               for center, fwhm in zip(centers, fwhms)]
        return SensorDefinition(wavebandDefinitions=wavebandDefinitions)

    @staticmethod
    def fromRaster(raster):
        assert isinstance(raster, Raster)
        return raster.sensorDefinition()

    def wavebandDefinition(self, index):
        wavebandDefinition = self._wavebandDefinitions[index]
        assert isinstance(wavebandDefinition, WavebandDefinition)
        return wavebandDefinition

    def wavebandDefinitions(self):
        for index in range(self.wavebandCount()):
            yield self.wavebandDefinition(index=index)

    def wavebandCount(self):
        return len(self._wavebandDefinitions)

    def plot(self, plotWidget=None, yscale=1., **kwargs):
        import pyqtgraph as pg
        if plotWidget is None:
            plotWidget = pg.plot()

        for wavebandDefinition in self.wavebandDefinitions():
            wavebandDefinition.plot(plotWidget=plotWidget, yscale=yscale, **kwargs)

        return plotWidget

    def wavebandCenters(self):
        return [wavebandDefinition.center() for wavebandDefinition in self.wavebandDefinitions()]

    def wavebandFwhms(self):
        return [wavebandDefinition.fwhm() for wavebandDefinition in self.wavebandDefinitions()]

    def wavebandResponses(self):
        return [wavebandDefinition.responses() for wavebandDefinition in self.wavebandDefinitions()]

    def wavebandWavelengths(self):
        return [wavebandDefinition.wavelengths() for wavebandDefinition in self.wavebandDefinitions()]

    def resampleRaster(self, filename, raster, minResponse=None, resampleAlg=None, **kwargs):
        assert isinstance(raster, Raster)
        if resampleAlg is None:
            resampleAlg = self.RESAMPLE_LINEAR
        assert resampleAlg in self.RESAMPLE_OPTIONS
        sourceSensor = raster.sensorDefinition()
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_SensorDefinitionResampleRaster, raster=raster,
                      targetSensor=self, sourceSensor=sourceSensor, minResponse=minResponse, resampleAlg=resampleAlg)
        return Raster(filename=filename)

    def resampleProfiles(self, array, wavelength, wavelengthUnits):
        array = np.array(array)
        samples, bands = array.shape
        assert len(wavelength) == bands

        rasterDataset = createRasterDatasetFromArray(array=np.atleast_3d(array.T),
                                                     filename='/vsimem/SensorDefinitionResampleOutProfiles.bsq',
                                                     driver=ENVIBSQDriver())
        MetadataEditor.setBandCharacteristics(rasterDataset=rasterDataset,
                                              wavelength=wavelength,
                                              wavelengthUnits=wavelengthUnits)
        rasterDataset.flushCache()
        raster = Raster.fromRasterDataset(rasterDataset=rasterDataset)
        outraster = self.resampleRaster(filename='/vsimem/SensorDefinitionResampleOutProfiles.bsq',
                                        raster=raster, controls=ApplierControls().setWriteENVIHeader(False))
        outarray = outraster.dataset().readAsArray().T[0]
        return outarray

class _SensorDefinitionResampleRaster(ApplierOperator):
    def ufunc(self, raster, targetSensor, sourceSensor, minResponse, resampleAlg):
        assert isinstance(targetSensor, SensorDefinition)
        assert isinstance(sourceSensor, SensorDefinition)
        self.targetSensor = targetSensor
        self.sourceSensor = sourceSensor
        self.raster = raster

        if minResponse is None:
            minResponse = 0
        self.minResponse = minResponse

        self.marray = self.flowMaskArray(name='raster', mask=raster.asMask(index=0))

        # resample
        if resampleAlg == SensorDefinition.RESAMPLE_LINEAR:
            outarray = self.resampleWithLinearInterpolation()
        elif resampleAlg == SensorDefinition.RESAMPLE_RESPONSE:
            outarray = self.resampleWithResponseFunction()

        # mask
        if raster.dataset().noDataValue() is not None:
            outarray[:, np.logical_not(self.marray[0])] = raster.dataset().noDataValue()

        # write and set metadata
        outraster = self.outputRaster.raster(key='outraster')
        outraster.setArray(array=outarray)
        self.setFlowMetadataSensorDefinition(name='outraster', sensor=targetSensor)
        outraster.setNoDataValue(value=raster.dataset().noDataValue())

    def resampleWithResponseFunction(self):
        outarray = self.full(value=0, bands=self.targetSensor.wavebandCount(), dtype=np.float32)
        for outindex, wavebandDefinition in enumerate(self.targetSensor.wavebandDefinitions()):
            assert isinstance(wavebandDefinition, WavebandDefinition)
            weights = wavebandDefinition.resamplingWeights(sensor=self.sourceSensor)
            weightsSum = 0.

            for inindex, weight in enumerate(weights):
                if weight > self.minResponse:
                    weightsSum += weight
                    invalues = self.flowRasterArray(name='raster',
                                                   raster=self.raster,
                                                   indices=[inindex])[self.marray]
                    outarray[outindex][self.marray[0]] += weight * invalues
            if weightsSum == 0:  # if no source bands are inside the responsive region of the target band
                import warnings
                warnings.warn(Warning(
                    'target waveband ({}, from {} nm to {} nm) is outside the responsive region'.format(
                        wavebandDefinition.name(), wavebandDefinition.wavelengths()[0],
                        wavebandDefinition.wavelengths()[-1])))
                outarray[outindex] = np.nan
            else:
                outarray[outindex][self.marray[0]] /= weightsSum

        return outarray


    def resampleWithLinearInterpolation(self):
        outarray = self.full(value=0, bands=self.targetSensor.wavebandCount(), dtype=np.float32)
        incenters = self.sourceSensor.wavebandCenters()
        outcenters = self.targetSensor.wavebandCenters()

        for outindex, outcenter in enumerate(outcenters):
            if outcenter <= incenters[0]:
                indexA = indexB = 0
                wA = wB = 0.5
            elif outcenter >= incenters[-1]:
                indexA = indexB = -1
                wA = wB = 0.5
            else:
                for inindex, incenter in enumerate(incenters):
                    if incenter > outcenter:
                        indexA = inindex - 1
                        indexB = inindex
                        distanceA = np.abs(incenters[indexA]-outcenter)
                        distanceB = np.abs(incenters[indexB]-outcenter)
                        wA = 1. - distanceA / (distanceA + distanceB)
                        wB = 1. - wA
                        break

            inarrayA, inarrayB = self.flowRasterArray(name='raster', raster=self.raster, indices=[indexA, indexB])
            outarray[outindex][self.marray[0]] = inarrayA[self.marray[0]] * wA + inarrayB[self.marray[0]] * wB
        return outarray


class ENVISpectralLibrary(FlowObject):
    def __init__(self, filename):
        self._filename = filename

    def __repr__(self):
        return '{cls}(filename={filename})'.format(cls=self.__class__.__name__, filename=str(self.filename()))

    def filename(self):
        return self._filename

    def raster(self, transpose=True):
        filename = r'/vsimem/{filename}{transpose}.vrt'.format(filename=self.filename(),
                                                               transpose='.transposed' if transpose else '')
        try:
            raster = Raster(filename=filename)
            raster.dataset()  # try opening
        except (RuntimeError, errors.InvalidGDALDatasetError):
            metadata = ENVI.readHeader(filenameHeader=ENVI.findHeader(filenameBinary=self.filename()))
            gdalType = ENVI.gdalType(enviType=int(metadata['data type']))
            bytes = ENVI.typeSize(enviType=int(metadata['data type']))
            byteOrder = ['LSB', 'MSB'][int(metadata['byte order'])]

            profiles = int(metadata['lines'])
            bands = int(metadata['samples'])
            options = 'subclass=VRTRawRasterBand\n' \
                      'SourceFilename={SourceFilename}\n' \
                      'ByteOrder={ByteOrder}\n'

            if transpose:
                rasterDataset = RasterDriver(name='VRT').create(grid=PseudoGrid(size=Size(x=1, y=profiles)),
                                                                bands=0, gdalType=gdalType, filename=filename)

                options += 'ImageOffset={ImageOffset}\n' \
                           'PixelOffset={PixelOffset}\n' \
                           'LineOffset={LineOffset}'

                for band in range(bands):
                    rasterDataset.gdalDataset().AddBand(datatype=gdalType,
                                                        options=options.format(SourceFilename=self.filename(),
                                                                               ByteOrder=byteOrder,
                                                                               ImageOffset=band * bytes,
                                                                               PixelOffset=bands * bytes,
                                                                               LineOffset=bands * bytes).split('\n'))

            else:
                rasterDataset = RasterDriver(name='VRT').create(grid=PseudoGrid(size=Size(x=bands, y=profiles)),
                                                                bands=0, gdalType=gdalType, filename=filename)

                rasterDataset.gdalDataset().AddBand(datatype=gdalType,
                                                    options=options.format(SourceFilename=self.filename(),
                                                                           ByteOrder=byteOrder).split('\n'))

            for key in ['file compression', 'band names']:
                metadata.pop(key=key, default=None)

            rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')

            rasterDataset.flushCache()
            rasterDataset.close()
            raster = Raster(filename=filename)

        return raster

    @staticmethod
    def fromRaster(filename, raster):
        assert isinstance(raster, Raster)
        bands = raster.dataset().zsize()
        array = raster.dataset().readAsArray().reshape(bands, -1).T[None]
        rasterDataset = createRasterDatasetFromArray(array=array, grid=PseudoGrid.fromArray(array=array),
                                                     filename=filename, driver=ENVIBSQDriver())
        metadata = raster.dataset().metadataDomain(domain='ENVI')
        for key in ['file compression']:
            metadata.pop(key, None)
        rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')
        rasterDataset.band(0).setDescription('Spectral Library')
        rasterDataset.flushCache()
        rasterDataset.close()

        # fix header

        # - delete PAM header
        try:
            remove(filename + '.aux.xml')
        except:
            pass

        # - rewrite ENVI header
        filenameHeader = ENVI.findHeader(filenameBinary=filename)
        metadata = ENVI.readHeader(filenameHeader=filenameHeader)
        metadata['file type'] = 'ENVI Spectral Library'
        for key in ['file compression', 'coordinate system string', 'map info', 'projection_info', 'x start',
                    'y start']:
            metadata.pop(key, None)
        ENVI.writeHeader(filenameHeader=filenameHeader, metadata=metadata)
        return ENVISpectralLibrary(filename=filename)


class RasterStack(FlowObject):
    def __init__(self, rasters):
        self._rasters = rasters

    def __repr__(self):
        return '{cls}(rasters={rasters})'.format(
            cls=self.__class__.__name__,
            rasters=repr(list(self.rasters())))

    def raster(self, i):
        assert isinstance(self._rasters[i], Raster)
        return self._rasters[i]

    def rasters(self):
        for i in range(len(self._rasters)):
            yield self.raster(i)


class Mask(Raster):
    def __init__(self, filename, noDataValues=None, minOverallCoverage=0.5, index=None):
        Raster.__init__(self, filename)
        if noDataValues is None:
            noDataValues = self.dataset().noDataValues(default=0)
        self._noDataValues = noDataValues
        self._minOverallCoverage = float(minOverallCoverage)
        self.index = index  # use only that band to generate the mask, otherwise reduce over all bands, reduce function is np.all

    def __repr__(self):
        return '{cls}(filename={filename}, noDataValues={noDataValues})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename()),
            noDataValues=repr(self.noDataValues()))

    def noDataValues(self):
        assert isinstance(self._noDataValues, list)
        return self._noDataValues

    def minOverallCoverage(self):
        return self._minOverallCoverage

    @staticmethod
    def fromVector(filename, vector, grid, **kwargs):
        return Raster.fromVector(filename=filename, vector=vector, grid=grid).asMask()

    @staticmethod
    def fromRaster(filename, raster, initValue=False, true=(), false=(),
                   invert=False, aggregateFunction=None, **kwargs):
        assert isinstance(raster, Raster)
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('mask', filename=filename)
        applier.apply(operatorType=_MaskFromRaster, raster=raster, initValue=initValue,
                      true=true, false=false, invert=invert,
                      aggregateFunction=aggregateFunction)
        return Mask(filename=filename)

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowMask('inmask', mask=self)
        applier.setOutputRaster('outmask', filename=filename)
        applier.apply(operatorType=_MaskResample, mask=self)
        return Mask(filename=filename, minOverallCoverage=self.minOverallCoverage())


class _MaskResample(ApplierOperator):
    def ufunc(self, mask):
        array = self.flowMaskArray('inmask', mask=mask)
        self.outputRaster.raster(key='outmask').setArray(array=array)


class _MaskFromRaster(ApplierOperator):
    def ufunc(self, raster, initValue, true, false, invert,
              aggregateFunction=None):
        array = self.flowRasterArray('raster', raster=raster)
        marray = np.full_like(array, fill_value=initValue, dtype=np.bool)

        for value in true:
            if isinstance(value, (int, float)):
                marray[array == value] = True
            elif isinstance(value, range):
                assert value.step == 1
                marray[(array >= value.start) * (array <= value.stop)] = True

        for value in false:
            if isinstance(value, (int, float)):
                marray[array == value] = False
            elif isinstance(value, range):
                assert value.step == 1
                marray[(array >= value.start) * (array <= value.stop)] = False

        if invert:
            marray = np.logical_not(marray)

        if aggregateFunction is not None:
            marray = aggregateFunction(marray)
            assert (marray.ndim == 3 and len(marray) == 1) or marray.ndim == 2

        self.outputRaster.raster(key='mask').setArray(array=marray)


class Vector(FlowObject):
    def __init__(self, filename, layer=0, initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                 filterSQL=None, dtype=np.float32, noDataValue=None, oversampling=1):
        self._filename = filename
        self._layer = layer
        self._initValue = initValue
        self._burnValue = burnValue
        self._burnAttribute = burnAttribute
        self._allTouched = allTouched
        self._filterSQL = filterSQL
        self._dtype = dtype
        self._oversampling = oversampling
        self._noDataValue = noDataValue
        self._vectorDataset = None

    def filename(self):
        return self._filename

    def layer(self):
        return self._layer

    def initValue(self):
        return self._initValue

    def burnValue(self):
        return self._burnValue

    def burnAttribute(self):
        return self._burnAttribute

    def allTouched(self):
        return self._allTouched

    def filterSQL(self):
        return self._filterSQL

    def dtype(self):
        return self._dtype

    def noDataValue(self, default=None):
        if self._noDataValue is None:
            return default
        return self._noDataValue

    def oversampling(self):
        return self._oversampling

    def dataset(self):
        if self._vectorDataset is None:
            self._vectorDataset = openVectorDataset(self.filename(), layerNameOrIndex=self.layer())
        assert isinstance(self._vectorDataset, VectorDataset)
        return self._vectorDataset

    def __repr__(self):
        return '{cls}(filename={filename}, layer={layer}, initValue={initValue}, burnValue={burnValue}, burnAttribute={burnAttribute}, allTouched={allTouched}, filterSQL={filterSQL}, dtype={dtype})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename()),
            layer=repr(self.layer()),
            initValue=repr(self.initValue()),
            burnValue=repr(self.burnValue()),
            burnAttribute=repr(self.burnAttribute()),
            allTouched=repr(self.allTouched()),
            filterSQL=repr(self.filterSQL()),
            dtype=repr(self.dtype()))

    def _initPickle(self):
        self._vectorDataset = None


    @classmethod
    def fromRandomPointsFromMask(cls, filename, mask, n, grid=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowMask('mask', mask=mask)
        applier.apply(operatorType=_VectorFromRandomPointsFromMask, mask=mask, n=n, filename=filename)
        return Vector(filename=filename)

    @classmethod
    def fromRandomPointsFromClassification(cls, filename, classification, n, grid=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('classification', classification=classification)
        applier.apply(operatorType=_VectorFromRandomPointsFromClassification, classification=classification, n=n,
                      filename=filename)
        return Vector(filename=filename)

    def uniqueValues(self, attribute, spatialFilter=None):
        vector = openVectorDataset(filename=self.filename(), layerNameOrIndex=self.layer())
        layer = vector.ogrLayer()
        layer.SetAttributeFilter(self.filterSQL())
        values = OrderedDict()
        if spatialFilter is not None:
            assert isinstance(spatialFilter, SpatialGeometry)
            spatialFilterReprojected = spatialFilter.reproject(targetProjection=vector.projection())
            layer.SetSpatialFilter(spatialFilterReprojected.ogrGeometry())
        for feature in layer:
            values[feature.GetField(attribute)] = None
        return list(values.keys())


class _VectorFromRandomPointsFromMask(ApplierOperator):
    def ufunc(self, mask, n, filename):
        array = self.flowMaskArray('mask', mask=mask)
        xmap = self.subgrid().xMapCoordinatesArray()[array[0]]
        ymap = self.subgrid().yMapCoordinatesArray()[array[0]]
        return xmap, ymap

    @staticmethod
    def aggregate(blockResults, grid, mask, n, filename):
        assert isinstance(grid, Grid)
        xmap = np.concatenate([result[0] for result in blockResults])
        ymap = np.concatenate([result[1] for result in blockResults])
        indicis = np.arange(0, len(xmap), 1)
        indicis = np.random.choice(indicis, size=n, replace=False)
        xmap, ymap = xmap[indicis], ymap[indicis]

        # Create the output vector
        driver = VectorDriver.fromFilename(filename=filename)
        driver.prepareCreation(filename)
        ds = driver.ogrDriver().CreateDataSource(filename)
        srs = grid.projection().osrSpatialReference()
        layer = ds.CreateLayer('random_points', srs, ogr.wkbPoint)

        for x, y in zip(xmap, ymap):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(x, y)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(point)
            layer.CreateFeature(feature)

        layer = None
        ds = None


class _VectorFromRandomPointsFromClassification(ApplierOperator):
    def ufunc(self, classification, n, filename):
        array = self.flowClassificationArray('classification', classification=classification)
        valid = array != 0
        xmap = self.subgrid().xMapCoordinatesArray()[valid[0]]
        ymap = self.subgrid().yMapCoordinatesArray()[valid[0]]
        id = array[valid]
        return xmap, ymap, id

    @staticmethod
    def aggregate(blockResults, grid, classification, n, filename):
        assert isinstance(grid, Grid)
        assert len(n) == classification.classDefinition().classes(), 'n must be a list with length of number of classes'
        xmap = np.concatenate([result[0] for result in blockResults])
        ymap = np.concatenate([result[1] for result in blockResults])
        id = np.concatenate([result[2] for result in blockResults])
        indicis = np.arange(0, len(xmap), 1)

        indicisList = list()
        for i, ni in enumerate(n):
            indicisi = indicis[id == i + 1]
            ni = min(ni, len(indicisi))
            indicisi = np.random.choice(indicisi, size=ni, replace=False)
            indicisList.append(indicisi)

        indicis = np.concatenate(indicisList)
        xmap, ymap = xmap[indicis], ymap[indicis]

        # Create the output vector
        driver = VectorDriver.fromFilename(filename=filename)
        driver.prepareCreation(filename)

        ds = driver.ogrDriver().CreateDataSource(filename)
        srs = grid.projection().osrSpatialReference()
        layer = ds.CreateLayer('random_points', srs, ogr.wkbPoint)

        for x, y in zip(xmap, ymap):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(x, y)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(point)
            layer.CreateFeature(feature)

        layer = None
        ds = None


class VectorClassification(Vector):
    def __init__(self, filename, classDefinition, classAttribute, layer=0, minOverallCoverage=0.5,
                 minDominantCoverage=0.5, dtype=np.uint8, oversampling=1):
        Vector.__init__(self, filename=filename, layer=layer, burnAttribute=classAttribute, dtype=dtype,
                        oversampling=oversampling)

        assert isinstance(classDefinition, ClassDefinition)
        self._classDefinition = classDefinition
        self._minOverallCoverage = float(minOverallCoverage)
        self._minDominantCoverage = float(minDominantCoverage)

    def __repr__(self):
        return '{}(filename={}, classDefinition={}, classAttribute={}, layer={}' \
               ', minOverallCoverage={}, minDominantCoverage={}, dtype={}, oversampling={})'.format(
            self.__class__.__name__,
            str(self.filename()),
            repr(self.classDefinition()),
            repr(self.classAttribute()),
            repr(self.layer()),
            repr(self.minOverallCoverage()),
            repr(self.minDominantCoverage()),
            repr(self.dtype()),
            repr(self.oversampling()))

    def classDefinition(self):
        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition

    def classAttribute(self):
        return self.burnAttribute()

    def minOverallCoverage(self):
        return self._minOverallCoverage

    def minDominantCoverage(self):
        return self._minDominantCoverage


class ClassDefinition(FlowObject):
    def __init__(self, classes=None, names=None, colors=None):

        if classes is not None:
            pass
        elif names is not None:
            classes = len(names)
        elif colors is not None:
            classes = len(colors)
        else:
            assert 0

        if names is None:
            names = ['class {}'.format(i + 1) for i in range(classes)]
        if colors is None:  # create random colors
            colors = [random.randint(1, 255) for i in range(classes * 3)]
        if len(colors) == classes * 3:  # format as tripels
            colors = [colors[i * 3: i * 3 + 3] for i in range(classes)]

        assert len(names) == classes
        assert len(colors) == classes

        self._classes = int(classes)
        self._names = [str(name) for name in names]
        self._colors = [QColor(*c) if isinstance(c, (list, tuple)) else QColor(c) for c in colors]

    def __repr__(self):
        return '{cls}(classes={classes}, names={names}, colors={colors})'.format(
            cls=self.__class__.__name__,
            classes=repr(self.classes()),
            names=repr(self.names()),
            colors=repr([str(c.name()) for c in self.colors()]))

    def classes(self):
        return self._classes

    def names(self):
        assert isinstance(self._names, list)
        return self._names

    def colors(self):
        assert isinstance(self._colors, list)
        return self._colors

    @staticmethod
    def fromENVIClassification(raster):
        assert isinstance(raster, Raster)
        ds = raster.dataset()
        classes = ds.metadataItem(key='classes', domain='ENVI', dtype=int, required=True)
        names = ds.metadataItem(key='class names', domain='ENVI', required=True)
        lookup = ds.metadataItem(key='class lookup', domain='ENVI', dtype=int, required=True)
        return ClassDefinition(classes=classes - 1, names=names[1:], colors=lookup[3:])

    @staticmethod
    def fromENVIFraction(raster):
        assert isinstance(raster, Raster)
        ds = raster.dataset()
        names = ds.metadataItem(key='band names', domain='ENVI')
        lookup = ds.metadataItem(key='band lookup', domain='ENVI', dtype=int)
        return ClassDefinition(names=names, colors=lookup)

    @staticmethod
    def fromGDALMeta(raster, index=0, skipZeroClass=True):
        assert isinstance(raster, Raster)
        ds = raster.dataset()
        names = ds.gdalDataset().GetRasterBand(index + 1).GetCategoryNames()
        classes = len(names)
        colors = [ds.gdalDataset().GetRasterBand(index + 1).GetColorTable().GetColorEntry(i)[:3] for i in
                  range(classes)]
        if skipZeroClass:
            classes = classes - 1
            names = names[1:]
            colors = colors[1:]
        return ClassDefinition(classes=classes, names=names, colors=colors)

    def dtype(self):
        for dtype in [np.uint8, np.uint16, np.uint32, np.uint64]:
            if self.classes() == dtype(self.classes()):
                return dtype

    def equal(self, other, compareColors=True):
        assert isinstance(other, ClassDefinition)
        equal = self.classes() == other.classes()
        equal &= all([a == b for a, b in zip(self.names(), other.names())])
        if compareColors:
            for color1, color2 in zip(self.colors(), other.colors()):
                equal &= color1.red() == color2.red()
                equal &= color1.green() == color2.green()
                equal &= color1.blue() == color2.blue()

        return equal

    def color(self, label):
        return self.colors()[label - 1]

    def colorByName(self, name):
        return self.color(label=self.names().index((name)) + 1)

    def name(self, label):
        return self.names()[label - 1]

    def labelByName(self, name):
        return self.names().index(name) + 1

    def colorsFlatRGB(self):
        values = list()
        for color in self.colors():
            values.append(color.red())
            values.append(color.green())
            values.append(color.blue())
        return values


class Classification(Raster):
    def __init__(self, filename, classDefinition=None, minOverallCoverage=0.5, minDominantCoverage=0.5):
        Raster.__init__(self, filename)
        self._classDefinition = classDefinition
        self._minOverallCoverage = minOverallCoverage
        self._minDominantCoverage = minDominantCoverage

    def __repr__(self):
        return '{cls}(filename={filename}, classDefinition={classDefinition}, minOverallCoverage={minOverallCoverage}, minDominantCoverage={minDominantCoverage})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename()),
            classDefinition=repr(self.classDefinition()),
            minOverallCoverage=repr(self.minOverallCoverage()),
            minDominantCoverage=repr(self.minDominantCoverage()))

    def classDefinition(self):
        if self._classDefinition is None:
            self._classDefinition = ClassDefinition.fromENVIClassification(raster=self)
        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition

    def minOverallCoverage(self):
        assert isinstance(self._minOverallCoverage, float)
        return self._minOverallCoverage

    def minDominantCoverage(self):
        assert isinstance(self._minDominantCoverage, float)
        return self._minDominantCoverage

    def noDataValues(self):
        return [0]

    def dtype(self):
        return self.classDefinition().dtype()

    def asMask(self, minOverallCoverage=1):
        return Raster.asMask(self, minOverallCoverage=minOverallCoverage)

    @classmethod
    def fromClassification(cls, filename, classification, grid=None, masks=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('classification', classification=classification)
        applier.setOutputRaster('classification', filename=filename)
        applier.setFlowMasks(masks=masks)
        applier.apply(operatorType=_ClassificationFromClassification, classification=classification, masks=masks)
        return Classification(filename=filename)

    @classmethod
    def fromRasterAndFunction(cls, filename, raster, ufunc, classDefinition, **kwargs):
        assert isinstance(classDefinition, ClassDefinition)
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('classification', filename=filename)
        applier.apply(operatorType=_ClassificationFromRasterAndFunction, raster=raster, ufunc=ufunc,
                      classDefinition=classDefinition)
        return Classification(filename=filename)

    @classmethod
    def fromRasterMetadata(cls, filename, raster, classificationSchemeName=''):
        assert isinstance(raster, Raster)

        names = raster.dataset().metadataItem(key='{} class names'.format(classificationSchemeName),
                                              domain='ENVI', required=True)[1:]
        classes = len(names)
        lookup = raster.dataset().metadataItem(key='{} class lookup'.format(classificationSchemeName),
                                               domain='ENVI', dtype=int, required=True)[3:]

        lookup = [int(v) for v in lookup]
        classDefinition = ClassDefinition(classes=classes, names=names, colors=lookup)
        labels = np.array(raster.dataset().metadataItem(key='{} class spectra names'.format(classificationSchemeName),
                                                        domain='ENVI', required=True))
        array = np.zeros(shape=len(labels))
        for i, name in enumerate(names):
            array[labels == name] = str(i + 1)

        bands, lines, samples = raster.dataset().shape()
        array = array.reshape(1, lines, samples).astype(dtype=classDefinition.dtype())

        rasterDataset = createRasterDatasetFromArray(array=array, filename=filename,
                                                     driver=RasterDriver.fromFilename(filename=filename))
        MetadataEditor.setClassDefinition(rasterDataset=rasterDataset, classDefinition=classDefinition)
        rasterDataset.setNoDataValues(values=[0])
        rasterDataset.flushCache().close()
        return Classification(filename=filename)

    def toRasterMetadata(self, raster, classificationSchemeName=''):
        assert isinstance(raster, Raster)
        assert self.grid().equal(other=raster.grid())

        labels = self.dataset().readAsArray()

        classSpectraNames = list(np.array(['Unclassified'] + self.classDefinition().names())[labels.ravel()])
        classLookup = [0, 0, 0] + self.classDefinition().colorsFlatRGB()

        raster.dataset().setMetadataItem(key=classificationSchemeName + ' class spectra names',
                                         value=list(labels[0]), domain='ENVI')
        raster.dataset().setMetadataItem(key=classificationSchemeName + ' class names',
                                         value=['Unclassified'] + self.classDefinition().names(), domain='ENVI')
        raster.dataset().setMetadataItem(key=classificationSchemeName + ' class lookup',
                                         value=classLookup, domain='ENVI')
        raster.dataset().setMetadataItem(key=classificationSchemeName + ' class spectra names',
                                         value=classSpectraNames, domain='ENVI')

    def reclassify(self, filename, classDefinition, mapping, **kwargs):
        assert isinstance(classDefinition, ClassDefinition)
        assert isinstance(mapping, dict)
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowClassification('inclassification', classification=self)
        applier.setOutputRaster('outclassification', filename=filename)
        applier.apply(operatorType=_ClassificationReclassify, classification=self, classDefinition=classDefinition,
                      mapping=mapping)
        return Classification(filename=filename)

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('inclassification', classification=self)
        applier.setOutputRaster('outclassification', filename=filename)
        applier.apply(operatorType=_ClassificationResample, classification=self)
        return Classification(filename=filename)


class _ClassificationReclassify(ApplierOperator):
    def ufunc(self, classification, classDefinition, mapping):
        inclassification = self.flowClassificationArray('inclassification', classification=classification)
        outclassification = self.full(value=0, bands=1, dtype=np.uint8)
        for inclass, outclass in mapping.items():
            if inclass in classification.classDefinition().names():
                inclass = classification.classDefinition().names().index(inclass) + 1
            if outclass in classDefinition.names():
                outclass = classDefinition.names().index(outclass) + 1
            outclassification[inclassification == inclass] = outclass
        self.outputRaster.raster(key='outclassification').setArray(array=outclassification)
        self.setFlowMetadataClassDefinition(name='outclassification', classDefinition=classDefinition)


class _ClassificationResample(ApplierOperator):
    def ufunc(self, classification):
        array = self.flowClassificationArray('inclassification', classification=classification)
        self.outputRaster.raster(key='outclassification').setArray(array=array)
        self.setFlowMetadataClassDefinition(name='outclassification', classDefinition=classification.classDefinition())


class _ClassificationFromClassification(ApplierOperator):
    def ufunc(self, classification, masks):
        array = self.flowClassificationArray('classification', classification=classification)
        marray = self.flowMasksArray(masks=masks)
        array[marray == 0] = 0
        self.outputRaster.raster(key='classification').setArray(array=array)
        self.setFlowMetadataClassDefinition(name='classification', classDefinition=classification.classDefinition())


class _ClassificationFromRasterAndFunction(ApplierOperator):
    def ufunc(self, raster, ufunc, classDefinition):
        array = self.flowRasterArray('raster', raster=raster)
        metadataDict = self.inputRaster.raster(key='raster').metadataDict()
        classificationArray = ufunc(array, metadataDict)
        self.outputRaster.raster(key='classification').setArray(array=classificationArray)
        self.setFlowMetadataClassDefinition(name='classification', classDefinition=classDefinition)


class Regression(Raster):
    def __init__(self, filename, noDataValues=None, outputNames=None, minOverallCoverage=0.5):
        Raster.__init__(self, filename)
        self._noDataValues = noDataValues
        self._outputNames = outputNames
        self._minOverallCoverage = float(minOverallCoverage)

    def __repr__(self):
        return '{cls}(filename={filename}, noDataValues={noDataValues}, outputNames={outputNames}, minOverallCoverage={minOverallCoverage})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename()),
            noDataValues=repr(self.noDataValues()),
            outputNames=repr(self.outputNames()),
            minOverallCoverage=repr(self.minOverallCoverage()))

    def noDataValues(self):
        if self._noDataValues is None:
            self._noDataValues = self.dataset().noDataValues(required=True)
        assert isinstance(self._noDataValues, list)
        return self._noDataValues

    def outputNames(self):
        if self._outputNames is None:
            self._outputNames = [band.description() for band in self.dataset().bands()]
        assert isinstance(self._outputNames, list)
        return self._outputNames

    def minOverallCoverage(self):
        assert isinstance(self._minOverallCoverage, float)
        return self._minOverallCoverage

    @staticmethod
    def fromRasterMetadata(filename, raster, outputNames, noDataValues=None):
        assert isinstance(raster, Raster)
        assert isinstance(outputNames, list)

        metadata = raster.dataset().metadataDomain(domain='ENVI')

        if noDataValues is None:
            noDataValues = [float(metadata['{} no data value'.format(outName)]) for outName in outputNames]
        assert isinstance(noDataValues, list)

        array = np.atleast_3d([np.array(metadata[outName], dtype=np.float32) for outName in outputNames])

        rasterDataset = createRasterDatasetFromArray(array=array,
                                                     filename=filename,
                                                     driver=RasterDriver.fromFilename(filename=filename))

        MetadataEditor.setRegressionDefinition(rasterDataset=rasterDataset, noDataValues=noDataValues,
                                               outputNames=outputNames)
        rasterDataset.flushCache().close()
        return Regression(filename=filename)

    def toRasterMetadata(self, raster):
        assert isinstance(raster, Raster)

        labels = self.dataset().readAsArray()
        outputNames = self.outputNames()
        noDataValues = self.noDataValues()
        for i, (outname, values, noDataValue) in enumerate(zip(outputNames, labels, noDataValues)):
            raster.dataset().setMetadataItem(key=outname, value=list(values.ravel()), domain='ENVI')
            raster.dataset().setMetadataItem(key=outname + ' no data value', value=noDataValue, domain='ENVI')


    def asMask(self, minOverallCoverage=None):
        if minOverallCoverage is None:
            minOverallCoverage = self.minOverallCoverage()
        return Raster.asMask(self, noDataValues=self.noDataValues(), minOverallCoverage=minOverallCoverage)

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRegression('inregression', regression=self)
        applier.setOutputRaster('outregression', filename=filename)
        applier.apply(operatorType=_RegressionResample, regression=self)
        return Regression(filename=filename)


class _RegressionResample(ApplierOperator):
    def ufunc(self, regression):
        array = self.flowRegressionArray('inregression', regression=regression)
        self.outputRaster.raster(key='outregression').setArray(array=array)
        self.setFlowMetadataRegressionDefinition(name='outregression', noDataValues=regression.noDataValues(),
                                                 outputNames=regression.outputNames())


class Fraction(Regression):
    def __init__(self, filename, classDefinition=None, minOverallCoverage=0.5, minDominantCoverage=0.5):
        Raster.__init__(self, filename=filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIFraction(raster=self)
        self._classDefinition = classDefinition
        Regression.__init__(self, filename=filename, noDataValues=self.noDataValues(),
                            outputNames=classDefinition.names())
        self._minOverallCoverage = minOverallCoverage
        self._minDominantCoverage = minDominantCoverage

    def classDefinition(self):
        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition

    def minOverallCoverage(self):
        return self._minOverallCoverage

    def minDominantCoverage(self):
        return self._minDominantCoverage

    def noDataValues(self):
        return [-1.] * self.classDefinition().classes()

    def __repr__(self):
        return '{cls}(filename={filename}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename()),
            classDefinition=repr(self.classDefinition()))

    @classmethod
    def fromClassification(cls, filename, classification, grid=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('classification', classification=classification)
        applier.setOutputRaster('fraction', filename=filename)
        applier.apply(operatorType=_FractionFromClassification, classification=classification)
        return Fraction(filename=filename)

    def toRasterMetadata(self, raster):
        assert isinstance(raster, Raster)

        labels = self.dataset().readAsArray()
        outputNames = self.outputNames()
        noDataValues = self.noDataValues()
        colors = self.classDefinition().colors()
        for i, (outname, values, noDataValue, color) in enumerate(zip(outputNames, labels, noDataValues, colors)):
            raster.dataset().setMetadataItem(key=outname, value=list(values.ravel()), domain='ENVI')
            raster.dataset().setMetadataItem(key=outname + ' no data value', value=noDataValue, domain='ENVI')
            raster.dataset().setMetadataItem(key=outname + ' color', value=[color.red(), color.green(), color.blue()], domain='ENVI')

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowFraction('infraction', fraction=self)
        applier.setOutputRaster('outfraction', filename=filename)
        applier.apply(operatorType=_FractionResample, fraction=self)
        return Fraction(filename=filename)

    def subsetClasses(self, filename, labels, **kwargs):
        indicies = [label - 1 for label in labels]
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('fraction', raster=self)
        applier.setOutputRaster('fractionSubset', filename=filename)
        applier.apply(operatorType=_FractionSubsetClasses, indicies=indicies, fraction=self)
        return Fraction(filename=filename)

    def subsetClassesByName(self, filename, names, **kwargs):
        labels = [self.classDefinition().names().index(name) + 1 for name in names]
        return self.subsetClasses(filename=filename, labels=labels, **kwargs)

    def asClassColorRGBRaster(self, filename, filterById=None, filterByName=None, **kwargs):
        filter = []
        if filterById is not None:
            filter.extend(filterById)
        if filterByName is not None:
            filter.extend([self.classDefinition().names().index[name] for name in filterByName])
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('fraction', raster=self)
        applier.setOutputRaster('raster', filename=filename)
        applier.apply(operatorType=_FractionAsClassColorRGBRaster, fraction=self, filter=filter)
        return Raster(filename=filename)


class _FractionAsClassColorRGBRaster(ApplierOperator):
    def ufunc(self, filter, fraction):
        assert isinstance(fraction, Fraction)
        colors = fraction.classDefinition().colors()
        array = self.flowRasterArray('fraction', raster=fraction)
        rgb = self.full(value=0, bands=3, dtype=np.float32)
        for id, (band, color) in enumerate(zip(array, colors), start=1):
            if len(filter) > 0 and id not in filter: continue
            colorRGB = (color.red(), color.green(), color.blue())
            rgb += band * np.reshape(colorRGB, newshape=(3, 1, 1))
        np.uint8(np.clip(rgb, a_min=0, a_max=255, out=rgb))
        mask = np.any(rgb != 0, axis=0)
        np.clip(rgb, a_min=1, a_max=255, out=rgb)
        rgb *= mask
        self.outputRaster.raster(key='raster').setArray(array=np.uint8(rgb))


class _FractionFromClassification(ApplierOperator):
    def ufunc(self, classification):
        array = self.flowFractionArray('classification', fraction=classification)
        self.outputRaster.raster(key='fraction').setArray(array=array)
        self.setFlowMetadataFractionDefinition(name='fraction',
                                               classDefinition=classification.classDefinition())


class _FractionResample(ApplierOperator):
    def ufunc(self, fraction):
        array = self.flowFractionArray('infraction', fraction=fraction)
        self.outputRaster.raster(key='outfraction').setArray(array=array)
        self.setFlowMetadataFractionDefinition(name='outfraction', classDefinition=fraction.classDefinition())


class _FractionSubsetClasses(ApplierOperator):
    def ufunc(self, indicies, fraction):
        classes = len(indicies)
        colors = [fraction.classDefinition().color(label=index + 1) for index in indicies]
        names = [fraction.classDefinition().name(label=index + 1) for index in indicies]
        classDefinition = ClassDefinition(classes=classes, names=names, colors=colors)
        fractionSubset = self.inputRaster.raster(key='fraction').bandArray(indicies=indicies)
        self.outputRaster.raster(key='fractionSubset').setArray(array=fractionSubset)
        self.setFlowMetadataFractionDefinition(name='fractionSubset', classDefinition=classDefinition)


class FractionPerformance(FlowObject):
    def __init__(self, yP, yT, classDefinitionP, classDefinitionT):
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes() == classDefinitionP.classes()
        assert isinstance(yP, np.ndarray)
        assert isinstance(yT, np.ndarray)
        assert yT.shape[1] == yP.shape[1]
        assert len(yT) == 1
        assert len(yP) == classDefinitionP.classes()

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP

        self.yP = yP.T
        self.yT = yT[0]
        self.n = yP.shape[1]
        self.log_loss = sklearn.metrics.log_loss(y_true=self.yT, y_pred=self.yP)
        self.roc_curves = dict()
        self.roc_auc_scores = dict()

        for i in range(1, self.classDefinitionT.classes() + 1):
            self.roc_curves[i] = sklearn.metrics.roc_curve(y_true=self.yT, y_score=self.yP[:, i - 1], pos_label=i,
                                                           drop_intermediate=True)
            self.roc_auc_scores[i] = sklearn.metrics.roc_auc_score(y_true=self.yT == i, y_score=self.yP[:, i - 1])

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT}, classDefinitionP={classDefinitionP}, classDefinitionT={classDefinitionT})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)),
            classDefinitionP=repr(self.classDefinitionP),
            classDefinitionT=repr(self.classDefinitionT))

    @classmethod
    def fromRaster(self, prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Fraction)
        assert isinstance(reference, Classification)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask])

        return FractionPerformance(yP=yP, yT=yT, classDefinitionP=prediction.classDefinition(),
                                   classDefinitionT=reference.classDefinition())

    def report(self):
        classes = self.classDefinitionT.classes()
        names = self.classDefinitionT.names()
        report = Report('Fraction Performance')
        report.append(ReportHeading('Performance Measures'))
        colHeaders = [['', 'AUC'], ['n', 'Log loss'] + names]
        colSpans = [[2, classes], [1] * (classes + 2)]
        roc_auc_scores_rounded = [round(elem, 3) for elem in self.roc_auc_scores.values()]
        data = [[str(self.n), numpy.round(self.log_loss, 2)] + roc_auc_scores_rounded]
        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        report.append(ReportHeading('Receiver Operating Characteristic (ROC) Curves'))

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(facecolor='white', figsize=(9, 6))
        for i in range(len(self.roc_curves)):
            # rgb = [v / 255. for v in self.classDefinitionP.color[i]]
            plt.plot(self.roc_curves[i + 1][0], self.roc_curves[i + 1][1]
                     , label=names[i])  # , color=rgb) # problem: plots do not show the correct RGB colors
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.legend(loc="lower right")
        fig.tight_layout()
        report.append(ReportPlot(fig, 'ROC Curves'))

        report.append(ReportHeading('Scikit-Learn Documentation'))
        report.append(ReportHyperlink('http://scikit-learn.org/stable/modules/model_evaluation.html#roc-metrics',
                                      'ROC User Guide'))
        report.append(ReportHyperlink('http://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html',
                                      'ROC Curve'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html#sklearn.metrics.roc_auc_score',
            'AUC score'))
        report.append(ReportHyperlink('http://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html',
                                      'Log Loss Metric'))

        return report


class Sample(MapCollection):
    def __init__(self, raster, mask=None, grid=None):
        assert isinstance(raster, Raster)
        if grid is None:
            grid = raster.dataset().grid()
        assert isinstance(grid, Grid), repr(grid)
        MapCollection.__init__(self, maps=[raster])
        self._mask = mask
        self._grid = grid

    def __repr__(self):
        return '{cls}(raster={raster}, mask={mask}, grid={grid})'.format(
            cls=self.__class__.__name__,
            raster=repr(self.raster()),
            mask=repr(self.mask()),
            grid=repr(self.grid()))

    def _initPickle(self):
        MapCollection._initPickle(self)
        if self._mask is not None:
            self._mask._initPickle()

    def raster(self):
        raster = self.maps()[0]
        assert isinstance(raster, Raster)
        return raster

    def mask(self):
        return self._mask

    def masks(self):
        return [self.raster(), self.mask()]

    def grid(self):
        assert isinstance(self._grid, Grid)
        return self._grid

    ''''@staticmethod
    def _fromSample(filenameRaster, sample, **kwargs):
        assert isinstance(sample, Sample)
        features = np.atleast_3d(sample.extractFeatures(**kwargs))
        rasterDataset = createRasterDatasetFromArray(array=features, filename=filenameRaster,
                                                     driver=RasterDriver.fromFilename(filename=filenameRaster))
        metadata = sample.raster().dataset().metadataDomain(domain='ENVI')
        for key in ENVI.SPATIAL_KEYS:
            metadata.pop(key, None)

        rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')
        rasterDataset.flushCache().close()
        return Sample(raster=Raster(filename=filenameRaster))'''

    def extractAsArray(self, grid=None, masks=None, onTheFlyResampling=False, **kwargs):
        if grid is None:
            grid = self.grid()
        if masks is None:
            masks = self.masks()
        return MapCollection.extractAsArray(self, grid=grid, masks=masks, onTheFlyResampling=onTheFlyResampling, **kwargs)

    def extractAsRaster(self, filenames, grid=None, masks=None, onTheFlyResampling=False, **kwargs):
        if grid is None:
            grid = self.grid()
        if masks is None:
            masks = self.masks()
        return MapCollection.extractAsRaster(self, filenames=filenames, grid=grid, masks=masks,
                                             onTheFlyResampling=onTheFlyResampling, **kwargs)

class ClassificationSample(Sample):
    def __init__(self, raster, classification, mask=None, grid=None):
        Sample.__init__(self, raster=raster, mask=mask, grid=grid)
        assert isinstance(classification, Classification)
        self.maps().append(classification)
        #self._classification = classification

    def __repr__(self):
        return '{cls}(raster={raster}, classification={classification}, mask={mask}, grid={grid}'.format(
            cls=self.__class__.__name__,
            raster=repr(self.raster()),
            classification=repr(self.classification()),
            mask=repr(self.mask()),
            grid=repr(self.grid()))

    def masks(self):
        return Sample.masks(self) + [self.classification()]

    def classification(self):
        classification = self.maps()[1]
        assert isinstance(classification, Classification)
        return classification


    def synthMix(self, filenameFeatures, filenameFractions, mixingComplexities, classLikelihoods=None, n=10, **kwargs):

        classDefinition = self.classification().classDefinition()
        if classLikelihoods is None:
            classLikelihoods = 'proportional'
        if classLikelihoods is 'proportional':
            statistics = self.classification().statistics(calcHistogram=True,
                                                          histogramBins=[classDefinition.classes()],
                                                          histogramRanges=[(1, classDefinition.classes() + 1)])
            histogram = statistics[0]['histo']['hist']
            classLikelihoods = {i + 1: float(count) / sum(histogram) for i, count in enumerate(histogram)}
        elif classLikelihoods is 'equalized':
            classLikelihoods = {i + 1: 1. / classDefinition().classes() for i in range(classDefinition().classes())}

        assert isinstance(mixingComplexities, dict)
        assert isinstance(classLikelihoods, dict)

        features, labels = self.extractAsArray(**kwargs)
        classes = self.classification().classDefinition().classes()

        # cache label indices and setup 0%/100% fractions from class labels
        indices = dict()
        zeroOneFractions = np.zeros((classes, features.shape[1]), dtype=np.float32)
        for label in range(1, classes + 1):
            indices[label] = np.where(labels == label)[1]
            zeroOneFractions[label - 1, indices[label]] = 1.

        # create mixtures
        mixtures = list()
        fractions = list()
        for i in range(n):
            complexity = np.random.choice(list(mixingComplexities.keys()), p=list(mixingComplexities.values()))
            drawnLabels = np.random.choice(list(classLikelihoods.keys()), size=complexity, replace=True,
                                           p=list(classLikelihoods.values()))
            drawnIndices = [np.random.choice(indices[label]) for label in drawnLabels]
            drawnFeatures = features[:, drawnIndices]
            drawnFractions = zeroOneFractions[:, drawnIndices]
            randomWeights = np.atleast_2d(np.float32(np.random.randint(low=1, high=100, size=complexity)))
            randomWeights /= randomWeights.sum()
            mixtures.append(np.sum(drawnFeatures * randomWeights, axis=1))
            fractions.append(np.sum(drawnFractions * randomWeights, axis=1))

        mixtures = np.atleast_3d(np.transpose(mixtures))
        fractions = np.atleast_3d(np.transpose(fractions))

        featuresDataset = createRasterDatasetFromArray(array=mixtures, filename=filenameFeatures,
                                                       driver=RasterDriver.fromFilename(filename=filenameFeatures))
        featuresDataset.flushCache().close()
        fractionsDataset = createRasterDatasetFromArray(array=fractions, filename=filenameFractions,
                                                        driver=RasterDriver.fromFilename(filename=filenameFractions))
        MetadataEditor.setFractionDefinition(rasterDataset=fractionsDataset, classDefinition=classDefinition)
        fractionsDataset.flushCache().close()

        return FractionSample(raster=Raster(filename=filenameFeatures),
                              fraction=Fraction(filename=filenameFractions))


class RegressionSample(Sample):
    def __init__(self, raster, regression, mask=None, grid=None):
        Sample.__init__(self, raster=raster, mask=mask, grid=grid)
        assert isinstance(regression, Regression)
        self.maps().append(regression)
        self._regression = regression

    def __repr__(self):
        return '{cls}(raster={raster}, regression={regression}, mask={mask}, grid={grid}'.format(
            cls=self.__class__.__name__,
            raster=repr(self.raster()),
            regression=repr(self.regression()),
            mask=repr(self.mask()),
            grid=repr(self.grid()))

    def masks(self):
        return Sample.masks(self) + [self.regression()]

    def regression(self):
        assert isinstance(self._regression, Regression)
        return self._regression

    '''def extractFeatures(self, grid=None, mask=None, **kwargs):
        features, labels = self.extractFeaturesAndLabels(grid=grid, mask=mask, **kwargs)
        return features

    def extractFeaturesAndLabels(self, grid=None, mask=None, **kwargs):

        extracted = (grid is None and
                     self.raster().dataset().xsize() == 1 and
                     self.regression().dataset().xsize() == 1 and
                     self.raster().dataset().ysize() == self.regression().dataset().ysize())

        if extracted:
            assert mask is None # todo consider mask
            features = self.raster().dataset().readAsArray().reshape(self.raster().dataset().zsize(), -1)
            labels = self.regression().dataset().readAsArray().reshape(self.regression().dataset().zsize(), -1)
        else:
            if grid is None:
                grid = self.grid()
            features, labels = extractPixels(inputs=[self.raster(), self.regression()],
                                             masks=[self.raster().asMask(), self.regression().asMask(), self.mask(), mask],
                                             grid=grid, **kwargs)
        return features, labels

    @staticmethod
    def fromSample(filenameRaster, filenameRegression, sample):
        assert isinstance(sample, FractionSample)
        features, labels = sample.extractFeaturesAndLabels()
        features = np.atleast_3d(features)
        labels = np.atleast_3d(labels)

        # craete raster
        rasterDataset = createRasterDatasetFromArray(array=features, filename=filenameRaster,
                                                     driver=RasterDriver.fromFilename(filename=filenameRaster))
        metadata = sample.raster().dataset().metadataDomain(domain='ENVI')
        for key in ENVI.SPATIAL_KEYS:
            metadata.pop(key, None)
        rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')
        rasterDataset.flushCache().close()
        raster = Raster(filename=filenameRaster)

        # create fraction
        rasterDataset = createRasterDatasetFromArray(array=labels, filename=filenameRegression,
                                                     driver=RasterDriver.fromFilename(filename=filenameRegression))
        metadata = sample.fraction().dataset().metadataDomain(domain='ENVI')
        for key in ENVI.SPATIAL_KEYS:
            metadata.pop(key, None)
        rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')
        MetadataEditor.setRegressionDefinition(rasterDataset=rasterDataset,
                                               noDataValues=sample.fraction().noDataValues(),
                                               outputNames=sample.fraction().outputNames())
        rasterDataset.flushCache().close()
        regression = Regression(filename=filenameRegression)

        return RegressionSample(raster=raster, regression=regression)'''



class FractionSample(RegressionSample):
    def __init__(self, raster, fraction, mask=None, grid=None):
        assert isinstance(fraction, Fraction)
        RegressionSample.__init__(self, raster=raster, regression=fraction, mask=mask, grid=grid)

    def __repr__(self):
        return '{cls}(raster={raster}, fraction={fraction}, mask={mask}, grid={grid})'.format(
            cls=self.__class__.__name__,
            raster=repr(self.raster()),
            fraction=repr(self.fraction()),
            mask=repr(self.mask()),
            grid=repr(self.grid()))

    def fraction(self):
        return self.regression()


class Estimator(FlowObject):
    SAMPLE_TYPE = Sample
    PREDICT_TYPE = Raster

    def __init__(self, sklEstimator):
        self._sklEstimator = sklEstimator
        self._sample = None

    def __repr__(self):
        return '{cls}(sklEstimator={sklEstimator})'.format(cls=self.__class__.__name__,
                                                           sklEstimator=repr(self.sklEstimator()))

    def _initPickle(self):
        if isinstance(self._sample, Sample):
            self._sample._initPickle()

    def sklEstimator(self):
        return self._sklEstimator

    def sample(self):
        assert isinstance(self._sample, Sample)
        return self._sample

    def _fit(self, sample):
        assert isinstance(sample, self.SAMPLE_TYPE)
        self._sample = sample

        if isinstance(sample, (ClassificationSample, RegressionSample, FractionSample)):
            features, labels = sample.extractAsArray()
            X = np.float64(features.T)
            if labels.shape[0] == 1 and not isinstance(self.sklEstimator(), sklearn.multioutput.MultiOutputEstimator):
                y = labels.ravel()
            else:
                y = labels.T
        elif isinstance(sample, Sample):
            features, = sample.extractAsArray()
            X = np.float64(features.T)
            y = None
        else:
            assert 0
        self.sklEstimator().fit(X=X, y=y)

        if isinstance(self, Clusterer):
            yTrain = self.sklEstimator().predict(X=X)
            self._classDefinition = ClassDefinition(classes=max(yTrain) + 1)
        return self

    def _predict(self, filename, raster, mask=None, **kwargs):

        if isinstance(raster, Raster):
            grid = raster.grid()
        elif isinstance(raster, RasterStack):
            grid = raster.raster(0).grid()
        else:
            assert 0

        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('prediction', filename=filename)
        applier.apply(operatorType=_EstimatorPredict, raster=raster, estimator=self, mask=mask)
        prediction = self.PREDICT_TYPE(filename=filename)
        assert isinstance(prediction, Raster)
        return prediction

    def _predictProbability(self, filename, raster, mask=None, mask2=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        applier.setOutputRaster('fraction', filename=filename)
        applier.apply(operatorType=_EstimatorPredictProbability, raster=raster, estimator=self, mask=mask, mask2=mask2)
        fraction = Fraction(filename=filename)
        return fraction

    def _transform(self, filename, raster, inverse=False, mask=None, mask2=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        applier.setOutputRaster('transformation', filename=filename)
        applier.apply(operatorType=_EstimatorTransform, estimator=self, raster=raster, mask=mask, mask2=mask2,
                      inverse=inverse)
        return Raster(filename=filename)

    def _inverseTransform(self, filename, raster, mask=None, mask2=None, **kwargs):
        return self._transform(filename=filename, raster=raster, inverse=True, mask=None, mask2=None, **kwargs)


class _EstimatorPredict(ApplierOperator):
    def ufunc(self, estimator, raster, mask):
        self.features = self.flowRasterArray('raster', raster=raster)
        etype, dtype, noutputs = self.getInfos(estimator)

        if isinstance(estimator, (Classifier, Clusterer)):
            noDataValues = [0]
        elif isinstance(estimator, Regressor):
            noDataValues = estimator.sample().regression().noDataValues()
        else:
            assert 0

        prediction = self.full(value=noDataValues, bands=noutputs, dtype=dtype)

        valid = self.maskFromArray(array=self.features, noDataValueSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)

        X = np.float64(self.features[:, valid[0]].T)
        y = estimator.sklEstimator().predict(X=X)
        prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='prediction').setArray(array=prediction)

        if isinstance(estimator, Classifier):
            self.setFlowMetadataClassDefinition('prediction',
                                                classDefinition=estimator.sample().classification().classDefinition())
        elif isinstance(estimator, Clusterer):
            self.setFlowMetadataClassDefinition('prediction', classDefinition=estimator._classDefinition)
        elif isinstance(estimator, Regressor):
            if isinstance(estimator.sample(), FractionSample):
                self.setFlowMetadataFractionDefinition('prediction',
                                                       classDefinition=estimator.sample().fraction().classDefinition())
            else:
                self.outputRaster.raster(key='prediction').setNoDataValues(values=noDataValues)
            self.setFlowMetadataBandNames('prediction', bandNames=estimator.sample().regression().outputNames())

    def getInfos(self, estimator):
        etype = estimator.sklEstimator()._estimator_type
        if etype in ['classifier', 'clusterer']:
            noutputs = 1
            dtype = np.uint8
        elif etype == 'regressor':
            X0 = np.float64(np.atleast_2d(self.features[:, 0, 0]))
            y0 = estimator.sklEstimator().predict(X=X0)
            noutputs = max(y0.shape)
            dtype = np.float32
        else:
            raise Exception('unexpected estimator type')
        return etype, dtype, noutputs


class _EstimatorPredictProbability(ApplierOperator):
    def ufunc(self, estimator, raster, mask, mask2):
        assert isinstance(estimator, Classifier)
        self.features = self.flowRasterArray('raster', raster=raster)
        noutputs = estimator.sample().classification().classDefinition().classes()
        noDataValue = -1
        prediction = self.full(value=noDataValue, bands=noutputs, dtype=np.float32)

        valid = self.maskFromArray(array=self.features, noDataValueSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)
        valid *= self.flowMaskArray('mask2', mask=mask2)

        X = np.float64(self.features[:, valid[0]].T)
        y = estimator.sklEstimator().predict_proba(X=X)
        prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='fraction').setArray(array=prediction)
        self.setFlowMetadataFractionDefinition('fraction',
                                               classDefinition=estimator.sample().classification().classDefinition())


class _EstimatorTransform(ApplierOperator):
    def ufunc(self, estimator, raster, mask, mask2, inverse):
        if inverse:
            sklTransform = estimator.sklEstimator().inverse_transform
        else:
            sklTransform = estimator.sklEstimator().transform

        noDataValue = np.finfo(np.float32).min
        features = self.flowRasterArray('raster', raster=raster)

        X0 = np.float64(np.atleast_2d(features[:, 0, 0]))
        _, noutputs = sklTransform(X=X0).shape

        transformation = self.full(value=noDataValue, bands=noutputs, dtype=np.float32)

        valid = self.maskFromArray(array=features, noDataValueSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)
        valid *= self.flowMaskArray('mask2', mask=mask2)

        X = np.float64(features[:, valid[0]].T)
        y = sklTransform(X=X)
        transformation[:, valid[0]] = np.float32(y.reshape(-1, noutputs).T)

        self.outputRaster.raster(key='transformation').setArray(array=transformation)
        self.outputRaster.raster(key='transformation').setNoDataValue(value=noDataValue)


class Classifier(Estimator):
    SAMPLE_TYPE = ClassificationSample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict
    predictProbability = Estimator._predictProbability


class Regressor(Estimator):
    SAMPLE_TYPE = RegressionSample
    PREDICT_TYPE = Regression
    fit = Estimator._fit
    predict = Estimator._predict


class Transformer(Estimator):
    SAMPLE_TYPE = Sample
    PREDICT_TYPE = Raster
    fit = Estimator._fit
    transform = Estimator._transform
    inverseTransform = Estimator._inverseTransform


class Clusterer(Estimator):
    SAMPLE_TYPE = Sample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict
    transform = Estimator._transform

    def __init__(self, sklEstimator):
        Estimator.__init__(self, sklEstimator=sklEstimator)
        self.classDefinition = ClassDefinition(classes=0)


class ClassificationPerformance(FlowObject):
    def __init__(self, yP, yT, classDefinitionP, classDefinitionT, classProportions=None, N=0):
        assert isinstance(yP, np.ndarray) and yP.ndim == 1
        assert isinstance(yT, np.ndarray) and yT.shape == yP.shape
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes() == classDefinitionP.classes()

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP
        self.N = N

        import sklearn.metrics
        self.yP = yP
        self.yT = yT
        self.mij = np.int64(
            sklearn.metrics.confusion_matrix(yT, yP, labels=range(1, classDefinitionT.classes() + 1)).T)
        self.m = np.int64(yP.size)
        self.Wi = classProportions
        self._assessPerformance()

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT}, classDefinitionP={classDefinitionP}, classDefinitionT={classDefinitionT}, classProportions={classProportions})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)),
            classDefinitionP=repr(self.classDefinitionP),
            classDefinitionT=repr(self.classDefinitionT),
            classProportions=repr(list(self.Wi)))

    @staticmethod
    def fromRaster(prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        stratification = prediction
        classes = stratification.classDefinition().classes()
        statistics = stratification.statistics(calcHistogram=True,
                                               histogramBins=[classes],
                                               histogramRanges=[(1, classes + 1)], **kwargs)
        histogram = statistics[0]['histo']['hist']
        classProportions = [float(count) / sum(histogram) for i, count in enumerate(histogram)]
        N = sum(histogram)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask])

        return ClassificationPerformance(yP=yP[0], yT=yT[0],
                                         classDefinitionP=prediction.classDefinition(),
                                         classDefinitionT=reference.classDefinition(),
                                         classProportions=classProportions,
                                         N=N)

    def _assessPerformance(self):

        old_error_state = np.geterr()
        np.seterr(divide='ignore', invalid='ignore', over='raise', under='raise')

        # get some stats from the confusion matrix mij
        self.mi_ = np.sum(self.mij, axis=0, dtype=np.float64)  # class-wise sum over all prediction
        self.m_j = np.sum(self.mij, axis=1, dtype=np.float64)  # class-wise sum over references
        self.mii = np.diag(self.mij)  # main diagonal -> class-wise correctly classified samples

        # estimate mapped class proportions from the reference sample, if not provided by the user
        if self.Wi is None:
            self.Wi = self.mi_ / self.m  # note that in this case pij is reduced to pij=mij/m

        # pij is the proportion of area estimate
        # pij = Wi*mij/mi_
        self.pij = np.zeros_like(self.mij, dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            for j in range(self.classDefinitionT.classes()):
                self.pij[i, j] = self.Wi[i] * self.mij[i, j] / self.mi_[i]

        self.pi_ = np.sum(self.pij, axis=0, dtype=np.float64)
        self.p_j = np.sum(self.pij, axis=1, dtype=np.float64)
        self.pii = np.diag(self.pij)

        # calculate performance measures
        self.ProducerAccuracy = self._fix(self.mii / self.mi_)
        self.UserAccuracy = self._fix(self.mii / self.m_j)

        self.F1Accuracy = self._fix(
            2 * self.UserAccuracy * self.ProducerAccuracy / (self.UserAccuracy + self.ProducerAccuracy))
        self.ConditionalKappaAccuracy = self._fix(
            (self.m * self.mii - self.mi_ * self.m_j) / (self.m * self.mi_ - self.mi_ * self.m_j))
        self.OverallAccuracy = self._fix(self.mii.sum() / float(self.m))
        self.KappaAccuracy = self._fix(
            (self.m * self.mii.sum() - np.sum(self.mi_ * self.m_j)) / (self.m ** 2 - np.sum(self.mi_ * self.m_j)))

        # calculate squared standard errors (SSE)

        self.OverallAccuracySSE = 0.
        for i in range(self.classDefinitionT.classes()): self.OverallAccuracySSE += self.pij[i, i] * (
            self.Wi[i] - self.pij[i, i]) / (self.Wi[i] * self.m)

        a1 = self.mii.sum() / self.m
        a2 = (self.mi_ * self.m_j).sum() / self.m ** 2
        a3 = (self.mii * (self.mi_ + self.m_j)).sum() / self.m ** 2
        a4 = 0.
        for i in range(self.classDefinitionT.classes()):
            for j in range(self.classDefinitionT.classes()):
                a4 += self.mij[i, j] * (self.mi_[j] + self.m_j[i]) ** 2
        a4 /= self.m ** 3
        b1 = a1 * (1 - a1) / (1 - a2) ** 2
        b2 = 2 * (1 - a1) * (2 * a1 * a2 - a3) / (1 - a2) ** 3
        b3 = (1 - a1) ** 2 * (a4 - 4 * a2 ** 2) / (1 - a2) ** 4
        self.KappaAccuracySSE = (b1 + b2 + b3) / self.m

        self.ProducerAccuracySSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            sum = 0.
            for j in range(self.classDefinitionT.classes()):
                if i == j: continue
                sum += self.pij[i, j] * (self.Wi[j] - self.pij[i, j]) / (self.Wi[j] * self.m)
                self.ProducerAccuracySSE[i] = self.pij[i, i] * self.p_j[i] ** (-4) * (
                    self.pij[i, i] * sum + (self.Wi[i] - self.pij[i, i]) * (self.p_j[i] - self.pij[i, i]) ** 2 / (
                        self.Wi[i] * self.m))

        self.UserAccuracySSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            self.UserAccuracySSE[i] = self.pij[i, i] * (self.Wi[i] - self.pij[i, i]) / (self.Wi[i] ** 2 * self.m)

        self.F1AccuracySSE = self._fix(
            2 * self.UserAccuracySSE * self.ProducerAccuracySSE / (self.UserAccuracySSE + self.ProducerAccuracySSE))

        self.ConditionalKappaAccuracySSE = self.m * (self.mi_ - self.mii) / (self.mi_ * (self.m - self.m_j)) ** 3 * (
            (self.mi_ - self.mii) * (self.mi_ * self.m_j - self.m * self.mii) + self.m * self.mii * (
                self.m - self.mi_ - self.m_j + self.mii))

        self.ClassProportion = self.m_j / self.m
        self.ClassProportionSSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for j in range(self.classDefinitionT.classes()):
            for i in range(self.classDefinitionT.classes()):
                self.ClassProportionSSE[j] += self.Wi[i] ** 2 * (
                    (self.mij[i, j] / self.mi_[i]) * (1 - self.mij[i, j] / self.mi_[i])) / (self.mi_[i] - 1)

        np.seterr(**old_error_state)

    def _confidenceIntervall(self, mean, sse, alpha):
        import scipy.stats
        se = np.sqrt(np.clip(sse, 0, np.inf))
        lower = scipy.stats.norm.ppf(alpha / 2.) * se + mean
        upper = scipy.stats.norm.ppf(1 - alpha / 2.) * se + mean
        return lower, upper

    def _fix(self, a, fill=0):
        if isinstance(a, np.ndarray):
            a[np.logical_not(np.isfinite(a))] = 0
        else:
            if not np.isfinite(a):
                a = 0
        return a

    def report(self):

        report = Report('Classification Performance')

        report.append(ReportHeading('Class Overview'))
        colHeaders = None
        rowSpans = [[1, 2], [1, 1, 1]]
        rowHeaders = [['', 'Class Names'], ['Class ID', 'Reference', 'Prediction']]
        data = [np.hstack((range(1, self.classDefinitionT.classes() + 1))), self.classDefinitionT.names(),
                self.classDefinitionP.names()]

        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders,
                                  colSpans=None, rowSpans=rowSpans))

        # Confusion Matrix Table
        report.append(ReportHeading('Confusion Matrix'))
        classNumbers = []
        for i in range(self.classDefinitionT.classes()): classNumbers.append('(' + str(i + 1) + ')')
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes()], np.ones(self.classDefinitionT.classes() + 1, dtype=int)]
        classNamesColumn = []
        for i in range(self.classDefinitionT.classes()): classNamesColumn.append(
            '(' + str(i + 1) + ') ' + self.classDefinitionT.names()[i])
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(((np.hstack((self.mij, self.m_j[:, None]))), np.hstack((self.mi_, self.m)))).astype(
            int)

        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans))

        # Accuracies Table
        report.append(ReportHeading('Accuracies'))
        colHeaders = [['Measure', 'Estimate [%]', '95 % Confidence Interval [%]']]
        colSpans = [[1, 1, 2]]
        rowHeaders = None
        data = [['Overall Accuracy', np.round(self.OverallAccuracy * 100, 2),
                 np.round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[0] * 100),
                 round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[1] * 100, 2)],
                ['Kappa Accuracy', np.round(self.KappaAccuracy * 100, 2),
                 np.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[0] * 100, 2),
                 np.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[1] * 100, 2)],
                ['Mean F1 Accuracy', np.round(np.mean(self.F1Accuracy) * 100, 2), '-', '-']]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Class-wise Accuracies Table
        report.append(ReportHeading('Class-wise Accuracies'))
        colSpans = [[1, 3, 3, 3], [1, 1, 2, 1, 2, 1, 2]]
        colHeaders = [['', 'User\'s Accuracy [%]', 'Producer\'s Accuracy [%]', 'F1 Accuracy'],
                      ['Map class', 'Estimate', '95 % Interval', 'Estimate', '95% Interval', 'Estimate',
                       '95% Interval']]
        data = [classNamesColumn, np.round(self.UserAccuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[1] * 100, 2)
            , np.round(self.ProducerAccuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[1] * 100, 2)
            , np.round(self.F1Accuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[1] * 100, 2)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans))

        # Proportion Matrix Table
        report.append(ReportHeading('Proportion Matrix'))
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes()], np.ones(self.classDefinitionT.classes() + 1, dtype=int)]
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(
            ((np.hstack((self.pij, self.p_j[:, None]))), np.hstack((self.pi_, 1))))
        report.append(ReportTable(np.round(data, 4), '', colHeaders=colHeaders, rowHeaders=rowHeaders,
                                  colSpans=colSpans))

        # Class-wise Area Estimates
        report.append(ReportHeading('Class-wise Proportion and Area Estimates'))
        colSpans = [[1, 3, 3], [1, 1, 2, 1, 2]]
        colHeaders = [['', 'Proportion', 'Area [px]'],
                      ['Map class', 'Estimate', '95 % Interval', 'Estimate', '95 % Interval']]
        data = [classNamesColumn,
                np.round(self.ClassProportion, 4),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[0], 4),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[1], 4),
                np.round(self.ClassProportion * self.N, 1),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[0] * self.N, 1),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[1] * self.N, 1)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        return report


class RegressionPerformance(FlowObject):
    def __init__(self, yT, yP, outputNamesT, outputNamesP):
        assert isinstance(yT, np.ndarray)
        assert isinstance(yP, np.ndarray)
        assert yT.ndim == 2
        assert yP.ndim == 2
        assert yT.shape == yP.shape

        self.yP = yP
        self.yT = yT
        self.outputNamesT = outputNamesT
        self.outputNamesP = outputNamesP
        self.residuals = self.yP - self.yT
        self.n = self.yT[0].size

        self.explained_variance_score = [sklearn.metrics.explained_variance_score(self.yT[i], self.yP[i]) for i, _ in
                                         enumerate(outputNamesT)]
        self.mean_absolute_error = [sklearn.metrics.mean_absolute_error(self.yT[i], self.yP[i]) for i, _ in
                                    enumerate(outputNamesT)]
        self.mean_squared_error = [sklearn.metrics.mean_squared_error(self.yT[i], self.yP[i]) for i, _ in
                                   enumerate(outputNamesT)]
        self.median_absolute_error = [sklearn.metrics.median_absolute_error(self.yT[i], self.yP[i]) for i, _ in
                                      enumerate(outputNamesT)]
        self.r2_score = [sklearn.metrics.r2_score(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT}, outputNamesT={outputNamesT}, outputNamesP={outputNamesP})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)),
            outputNamesT=repr(self.outputNamesT),
            outputNamesP=repr(self.outputNamesP))

    @classmethod
    def fromRaster(self, prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Regression)
        assert isinstance(reference, Regression)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask])

        return RegressionPerformance(yP=yP, yT=yT, outputNamesP=prediction.outputNames(),
                                     outputNamesT=reference.outputNames())

    def report(self):
        import matplotlib
        # matplotlib.use('QT4Agg')
        from matplotlib import pyplot

        report = Report('Regression Performance')

        report.append(ReportHeading('Outputs Overview'))
        colHeaders = [['Outputs']]
        colSpans = [[len(self.outputNamesT)]]
        rowHeaders = [['Reference', 'Prediction']]
        data = [self.outputNamesT, self.outputNamesP]

        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans, rowHeaders=rowHeaders))

        report.append(ReportHeading('Metrics'))

        report.append(ReportParagraph('Number of samples: {}'.format(self.n)))

        colHeaders = [['Outputs'], self.outputNamesT]
        colSpans = [[len(self.outputNamesT)], [1] * len(self.outputNamesT)]
        rowHeaders = [['Explained variance score',
                       'Mean absolute error (MAE)',
                       'Mean squared error (MSE)',
                       'Root MSE (RMSE)',
                       'Median absolute error (MedAE)',
                       'Coefficient of determination (R^2)']]

        data = np.array([np.round(np.array(self.explained_variance_score).astype(float), 4),
                         np.round(np.array(self.mean_absolute_error).astype(float), 4),
                         np.round(np.array(self.mean_squared_error).astype(float), 4),
                         np.round(np.sqrt(np.array(self.mean_squared_error)).astype(float), 4),
                         np.round(np.array(self.median_absolute_error).astype(float), 4),
                         np.round(np.array(self.r2_score).astype(float), 4)])

        report.append(
            ReportTable(data, colHeaders=colHeaders, colSpans=colSpans, rowHeaders=rowHeaders, attribs_align='left'))

        report.append(
            ReportHyperlink(url=r'http://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics',
                            text='See Scikit-Learn documentation for details.'))

        report.append(ReportHeading('Scatter and Residuals Plots'))

        for i, name in enumerate(self.outputNamesT):
            fig, ax = pyplot.subplots(facecolor='white', figsize=(7, 7))
            # prepare 2x2 grid for plotting scatterplot on lower left, and adjacent histograms
            gs = matplotlib.gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3])

            ax0 = pyplot.subplot(gs[0, 0])
            ax0.hist(self.yT[i], bins=100, edgecolor='None', )
            pyplot.xlim([np.min(self.yT[i]), np.max(self.yT[i])])
            pyplot.tick_params(which='both', direction='out', length=10, pad=10)
            # hide ticks and ticklabels
            ax0.set_xticklabels([])
            ax0.set_ylabel('counts')
            ax0.set_title(name)
            ax0.xaxis.set_ticks_position('bottom')
            ax0.yaxis.set_ticks_position('left')

            # plot only every second tick, starting with the second
            # for label in ax0.get_yticklabels()[1::2]: label.set_visible(False)
            # plot only first and last ticklabel
            # for label in ax0.get_yticklabels()[1:-1]: label.set_visible(False)

            ax1 = pyplot.subplot(gs[1, 1])
            ax1.hist(self.yP[i], orientation='horizontal', bins=100, edgecolor='None')
            pyplot.tick_params(which='both', direction='out', length=10, pad=10)
            pyplot.ylim([np.min(self.yT[i]), np.max(self.yT[i])])
            # hide ticks and ticklabels
            ax1.set_yticklabels([])
            ax1.set_xlabel('counts')
            ax1.yaxis.set_ticks_position('left')
            ax1.xaxis.set_ticks_position('bottom')
            # plot only every second tick, starting with the second
            # for label in ax1.get_xticklabels()[1::2]: label.set_visible(False)
            # plot only first and last ticklabel
            # for label in ax1.get_xticklabels()[1:-1]: label.set_visible(False)

            ax2 = pyplot.subplot(gs[1, 0])
            ax2.scatter(self.yT[i], self.yP[i], s=10, edgecolor='', color='navy')
            pyplot.xlim([np.min(self.yT[i]), np.max(self.yT[i])])
            pyplot.ylim([np.min(self.yT[i]), np.max(self.yT[i])])
            pyplot.tick_params(which='both', direction='out')
            pyplot.xlabel('Observed')
            pyplot.ylabel('Predicted')

            # 1:1 line
            pyplot.plot([np.min(self.yT[i]), np.max(self.yT[i])], [np.min(self.yT[i]), np.max(self.yT[i])],
                        'k-')

            # Colorbar
            # cbaxes = fig.add_axes([0.05, 0.1, 0.05, 0.35])
            # cBar = pyplot.colorbar(sct, ticklocation='left', extend='neither', drawedges=False,cax = cbaxes)
            # cBar.ax.set_ylabel('label')

            fig.tight_layout()
            report.append(ReportPlot(fig))
            pyplot.close()

            fig, ax = pyplot.subplots(facecolor='white', figsize=(7, 5))
            ax.hist(self.residuals[i], bins=100, edgecolor='None')
            ax.set_title(name)
            ax.set_xlabel('Predicted - Observed')
            ax.set_ylabel('Counts')
            fig.tight_layout()
            report.append(ReportPlot(fig))
            pyplot.close()

        return report


class ClusteringPerformance(FlowObject):
    def __init__(self, yT, yP):
        assert isinstance(yP, np.ndarray)
        assert isinstance(yT, np.ndarray)
        assert yT.shape == yP.shape
        assert len(yT) == 1 and len(yP) == 1
        self.yP = yP.flatten()
        self.yT = yT.flatten()
        self.n = yT.shape[1]
        self.adjusted_mutual_info_score = sklearn.metrics.cluster.adjusted_mutual_info_score(labels_true=self.yT,
                                                                                             labels_pred=self.yP)
        self.adjusted_rand_score = sklearn.metrics.cluster.adjusted_rand_score(labels_true=self.yT, labels_pred=self.yP)
        self.completeness_score = sklearn.metrics.cluster.completeness_score(labels_true=self.yT, labels_pred=self.yP)

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)))

    @staticmethod
    def fromRaster(prediction, reference, grid, mask=None, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        yP, yT = extractPixels(inputs=[prediction, reference],
                               masks=[prediction, reference, mask],
                               grid=grid)
        return ClusteringPerformance(yP=yP, yT=yT)

    def report(self):
        report = Report('Clustering Performance')
        report.append(ReportHeading('Performance Measures'))
        report.append(ReportParagraph('n = ' + str(self.n)))
        rowHeaders = [['Adjusted Mutual Information', 'Adjusted Rand Score', 'Completeness Score']]
        data = numpy.transpose([[numpy.round(self.adjusted_mutual_info_score, 3),
                                 numpy.round(self.adjusted_rand_score, 3), numpy.round(self.completeness_score, 3)]])
        report.append(ReportTable(data, '', rowHeaders=rowHeaders))
        report.append(ReportHeading('Scikit-Learn Documentation'))
        report.append(
            ReportHyperlink('http://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation',
                            'Clustering Performance Evaluation Overview'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_mutual_info_score.html#sklearn.metrics.adjusted_mutual_info_score',
            'Adjusted Mutual Information'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html#sklearn.metrics.adjusted_rand_score',
            'Adjusted Rand Score'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.completeness_score.html#sklearn.metrics.completeness_score',
            'Completeness Score'))

        return report


class StringParser():
    class Range():
        def __init__(self, start, end):
            self.start = int(start)
            self.end = int(end)
            self.step = np.sign(end - start)

        def range(self):
            return range(self.start, self.end + self.step, self.step)

    def eval(self, text):
        if text.startswith('\eval'):
            return eval(text.replace('\eval', ''))
        else:
            raise Exception('text must start with "\python"')

    def range(self, text):
        # try resolve range syntax, e.g. 2-4 as [2,4] or -4--2 as [-4, -2]
        i = text.index('-', 1)
        return self.Range(start=int(text[:i]), end=int(text[i + 1:]))

    def value(self, text):

        # try to evaluate as int or float
        try:
            result = float(text)
            if str(int(text)) == str(result):
                result = int(result)
        except:
            # try to evaluate as range
            try:
                result = self.range(text)
            except:
                result = text
        return result

    def strlist(self, text):
        for c in '''[]{}()'",''':
            text = text.replace(c, ' ')

        if text == '':
            return None
        else:
            return text.split()

    def list(self, text, extendRanges=True):

        # try to evaluate as python expression
        try:
            result = self.eval(text)
            assert isinstance(result, list)
        except:
            strlist = self.strlist(text)
            if strlist is None:
                result = None
            else:
                result = list()
                for strvalue in strlist:
                    value = self.value(strvalue)
                    if isinstance(value, self.Range):
                        if extendRanges:
                            result.extend(value.range())
                        else:
                            result.append((value.start, value.end))
                    else:
                        result.append(value)
        return result


def extractPixels(inputs, masks, grid, **kwargs):
    applier = Applier(defaultGrid=grid, **kwargs)
    for i, input in enumerate(inputs):
        name = 'input' + str(i)
        applier.setFlowInput(name=name, input=input)

    for i, mask in enumerate(masks):
        name = 'mask' + str(i)
        applier.setFlowMask(name=name, mask=mask)

    results = applier.apply(operatorType=_ExtractPixels, inputs=inputs, masks=masks)
    return results


class _ExtractPixels(ApplierOperator):
    def ufunc(self, inputs, masks):

        # calculate overall mask
        marray = self.full(value=True)
        nothingToExtract = False
        for i, mask in enumerate(masks):
            name = 'mask' + str(i)
            imarray = self.flowMaskArray(name=name, mask=mask)
            np.logical_and(marray, imarray, out=marray)
            if not marray.any():
                nothingToExtract = True
                break

        # extract values for all masked pixels
        result = list()
        for i, input in enumerate(inputs):
            name = 'input' + str(i)
            if nothingToExtract:
                zsize = self.flowInputZSize(name=name, input=input)
                dtype = np.uint8
                profiles = np.empty(shape=(zsize, 0), dtype=dtype)
            else:
                array = self.flowInputArray(name=name, input=input)
                profiles = array[:, marray[0]]

            result.append(profiles)
        return result

    @staticmethod
    def aggregate(blockResults, grid, inputs, *args, **kwargs):
        result = list()
        for i, input in enumerate(inputs):
            profilesList = [r[i] for r in blockResults]
            profiles = np.concatenate(profilesList, axis=1)
            result.append(profiles)
        return result


class MetadataEditor(object):

    @staticmethod
    def setClassDefinition(rasterDataset, classDefinition):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        assert isinstance(classDefinition, ClassDefinition)

        names = ['unclassified'] + classDefinition.names()
        lookup = [0, 0, 0] + list(
            np.array([(c.red(), c.green(), c.blue()) for c in classDefinition.colors()]).flatten())

        rasterDataset.setNoDataValue(value=0)

        # setup in ENVI domain
        rasterDataset.setMetadataItem(key='classes', value=classDefinition.classes() + 1, domain='ENVI')
        rasterDataset.setMetadataItem(key='class names', value=names, domain='ENVI')
        rasterDataset.setMetadataItem(key='file type', value='ENVI Classification', domain='ENVI')
        rasterDataset.setMetadataItem(key='class lookup', value=lookup, domain='ENVI')

        # setup in GDAL data model
        colors = np.array(lookup).reshape(-1, 3)
        colors = [tuple(color) for color in colors]
        band = rasterDataset.band(0)
        band.setCategoryNames(names=names)
        band.setCategoryColors(colors=colors)
        band.setDescription('Classification')

    @classmethod
    def setFractionDefinition(cls, rasterDataset, classDefinition):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        assert isinstance(classDefinition, ClassDefinition)

        lookup = classDefinition.colorsFlatRGB()
        rasterDataset.setMetadataItem(key='band lookup', value=lookup, domain='ENVI')
        cls.setBandNames(rasterDataset=rasterDataset, bandNames=classDefinition.names())
        rasterDataset.setNoDataValue(value=-1)

    @classmethod
    def setRegressionDefinition(cls, rasterDataset, noDataValues, outputNames):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        rasterDataset.setNoDataValues(values=noDataValues)
        cls.setBandNames(rasterDataset=rasterDataset, bandNames=outputNames)

    @classmethod
    def setBandNames(cls, rasterDataset, bandNames):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        assert len(bandNames) == rasterDataset.zsize()
        rasterDataset.setMetadataItem(key='band names', value=bandNames, domain='ENVI')
        for band, bandName in zip(rasterDataset.bands(), bandNames):
            band.setDescription(value=bandName)

    @classmethod
    def setBandCharacteristics(cls, rasterDataset, bandNames=None, wavelength=None, fwhm=None, wavelengthUnits=None):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        if bandNames is not None:
            cls.setBandNames(rasterDataset=rasterDataset, bandNames=bandNames)
        if wavelength is not None:
            rasterDataset.setMetadataItem(key='wavelength', value=wavelength, domain='ENVI')
        if fwhm is not None:
            rasterDataset.setMetadataItem(key='fwhm', value=fwhm, domain='ENVI')
        if wavelengthUnits is not None:
            rasterDataset.setMetadataItem(key='wavelength units', value=wavelengthUnits, domain='ENVI')

    @classmethod
    def bandNames(cls, rasterDataset):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        return [band.description() for band in rasterDataset.bands()]

    @classmethod
    def bandCharacteristics(cls, rasterDataset):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        return {'bandNames': cls.bandNames(rasterDataset=rasterDataset),
                'wavelength': rasterDataset.metadataItem(key='wavelength', domain='ENVI'),
                'fwhm': rasterDataset.metadataItem(key='fwhm', domain='ENVI'),
                'wavelengthUnits': rasterDataset.metadataItem(key='wavelength units', domain='ENVI')}
