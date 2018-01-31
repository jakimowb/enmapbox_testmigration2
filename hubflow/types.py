from operator import xor
import random, os, pickle
from osgeo import gdal, ogr, osr
import numpy as np
import sklearn.metrics
import sklearn.multioutput

from hubdc.progressbar import ProgressBar
from hubdc.model import openRaster, openVector, Grid, SpatialGeometry
from hubflow.applier import Applier, ApplierOperator, ApplierControls

from hubflow.report import *
from hubflow import signals

import spectral

spectral.settings.envi_support_nonlowercase_params = True


class FlowObjectPickleFileError(Exception):
    pass


class FlowObjectTypeError(Exception):
    pass


class FlowObject(object):
    def pickle(self, filename, progressBar=None):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)
        signals.sigFileCreated.emit(filename)

        if progressBar is not None:
            assert isinstance(progressBar, ProgressBar)
            progressBar.setText('{}.pickle(filename={}'.format(self.__class__.__name__, filename))

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
                raise FlowObjectTypeError('wrong type ({t1}), expected type: {t2}'.format(t1=obj.__class__, t2=cls))
            else:
                return None
        return obj


class Raster(FlowObject):
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return '{cls}(filename={filename})'.format(cls=self.__class__.__name__, filename=str(self.filename))

    def dataset(self):
        return openRaster(self.filename)

    @property
    def grid(self):
        return self.dataset().grid()

    @classmethod
    def fromVector(cls, filename, vector, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowVector('vector', vector=vector)
        applier.setOutputRaster('raster', filename=filename)
        applier.apply(operatorType=_RasterFromVector, vector=vector)
        return Raster(filename=filename)

    def asMask(self, noData=None):
        return Mask(filename=self.filename, noData=noData)

    def basicStatistics(self, bandIndicies=None, mask=None, **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('raster', raster=self)
        applier.setFlowMask('mask', mask=mask)
        results = applier.apply(operatorType=_RasterBasicStatistics, raster=self, bandIndicies=bandIndicies, mask=mask)

        results = np.array(results, dtype=np.float64)
        min = np.nanmin(results[:, :, 0], axis=0)
        max = np.nanmax(results[:, :, 1], axis=0)
        sum = np.nansum(results[:, :, 2], axis=0)
        n = np.sum(results[:, :, 3], axis=0)
        mean = sum / n
        return min, max, mean, n

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

    def applyMask(self, filename, mask, fillValue, noDataValue=None, **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('raster', raster=self)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('maskedRaster', filename=filename)
        applier.apply(operatorType=_RasterApplyMask, raster=self, mask=mask, fillValue=fillValue)
        return Raster(filename=filename)


class _RasterBasicStatistics(ApplierOperator):
    def ufunc(self, raster, bandIndicies, mask):
        array = self.flowRasterArray('raster', raster=raster, indicies=bandIndicies).astype(dtype=np.float64)
        maskValid = self.flowMaskArray('mask', mask=mask)

        def bandBasicStatistics(index, band):
            valid = self.maskFromBandArray(array=band, noDataSource='raster', index=index)
            valid *= maskValid
            band[np.logical_not(valid)] = np.nan
            min = np.nanmin(band)
            max = np.nanmax(band)
            sum = np.nansum(band)
            n = np.sum(valid)
            return min, max, sum, n

        return [bandBasicStatistics(index=i, band=band[None]) for i, band in enumerate(array)]


class _RasterFromVector(ApplierOperator):
    def ufunc(self, vector):
        array = self.flowVectorArray('vector', vector=vector)
        self.outputRaster.raster(key='raster').setArray(array=array)


class _RasterScatterMatrix(ApplierOperator):
    def ufunc(self, raster1, raster2, bandIndex1, bandIndex2, bins, mask, stratification):

        band1 = self.flowRasterArray('raster1', raster=raster1, indicies=[bandIndex1])
        band2 = self.flowRasterArray('raster2', raster=raster2, indicies=[bandIndex2])
        strata = self.flowClassificationArray('stratification', classification=stratification)

        valid = self.maskFromBandArray(array=band1, noDataSource='raster1', index=bandIndex1)
        valid *= self.maskFromBandArray(array=band2, noDataSource='raster2', index=bandIndex2)
        valid *= self.flowMaskArray('mask', mask=mask)

        x = band1[valid]
        y = band2[valid]

        if strata.size == 0:
            H = np.histogram2d(x=x, y=y, bins=bins)[0]
        else:
            s = strata[valid]
            HList = list()
            for i in range(1, stratification.classDefinition.classes + 1):
                v = s == i
                Hi = np.histogram2d(x=x[v], y=y[v], bins=bins)[0]
                HList.append(np.array(Hi))
            H = np.stack(HList)

        return H


class _RasterApplyMask(ApplierOperator):
    def ufunc(self, raster, mask, fillValue, noDataValue):
        array = self.flowRasterArray('raster', raster=raster)
        marray = self.flowMaskArray('mask', mask=mask)
        tobefilled = np.logical_not(marray[0])
        array[:, tobefilled] = fillValue
        outraster = self.outputRaster.raster(key='maskedRaster')
        outraster.setArray(array=array)

        metadataDict = self.inputRaster.raster(key='raster').metadataDict()
        outraster.setMetadataDict(metadataDict)
        outraster.setNoDataValue(value=noDataValue)


class Mask(Raster):
    def __init__(self, filename, noData=None):
        Raster.__init__(self, filename)
        if noData is None:
            noData = openRaster(filename=filename).noDataValue(default=0)
        self.noData = noData

    def __repr__(self):
        return '{cls}(filename={filename}, noData={noData})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            noData=repr(self.noData))

    @staticmethod
    def fromVector(filename, vector, grid, **kwargs):
        return Raster.fromVector(filename=filename, vector=vector, grid=grid).asMask()

    @staticmethod
    def fromRaster(filename, raster, initValue=False, trueValues=(), trueRanges=(), falseValues=(), falseRanges=(),
                   invert=False, aggregateFunction=None, **kwargs):
        assert isinstance(raster, Raster)
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('mask', filename=filename)
        applier.apply(operatorType=_MaskFromRaster, raster=raster, initValue=initValue, trueValues=trueValues,
                      trueRanges=trueRanges, falseValues=falseValues, falseRanges=falseRanges, invert=invert,
                      aggregateFunction=None)
        return Mask(filename=filename)


class _MaskFromRaster(ApplierOperator):
    def ufunc(self, raster, initValue, trueValues, trueRanges, falseValues, falseRanges, invert,
              aggregateFunction=None):
        array = self.flowRasterArray('raster', raster=raster)
        marray = np.full_like(array, fill_value=initValue, dtype=np.bool)

        for v in trueValues:
            marray[array == v] = True

        for vmin, vmax in trueRanges:
            marray[(array >= vmin) * (array <= vmax)] = True

        for v in falseValues:
            marray[array == v] = False

        for vmin, vmax in falseRanges:
            marray[(array >= vmin) * (array <= vmax)] = False

        if invert:
            marray = np.logical_not(marray)

        if aggregateFunction is not None:
            marray = aggregateFunction(marray)
            assert (marray.ndim == 3 and len(marray) == 1) or marray.ndim == 2

        self.outputRaster.raster(key='mask').setArray(array=marray)


class Vector(FlowObject):
    def __init__(self, filename, layer=0, initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                 filterSQL=None, dtype=np.float32):
        self.filename = filename
        self.layer = layer
        self.initValue = initValue
        self.burnValue = burnValue
        self.burnAttribute = burnAttribute
        self.allTouched = allTouched
        self.filterSQL = filterSQL
        self.dtype = dtype

    def __repr__(self):
        return '{cls}(filename={filename}, layer={layer}, initValue={initValue}, burnValue={burnValue}, burnAttribute={burnAttribute}, allTouched={allTouched}, filterSQL={filterSQL}, dtype={dtype})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            layer=repr(self.layer),
            initValue=repr(self.initValue),
            burnValue=repr(self.burnValue),
            burnAttribute=repr(self.burnAttribute),
            allTouched=repr(self.allTouched),
            filterSQL=repr(self.filterSQL),
            dtype=repr(self.dtype))

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
        vector = openVector(filename=self.filename, layerNameOrIndex=self.layer)
        layer = vector.ogrLayer()
        layer.SetAttributeFilter(self.filterSQL)
        if spatialFilter is not None:
            assert isinstance(spatialFilter, SpatialGeometry)
            spatialFilterReprojected = spatialFilter.reproject(targetProjection=vector.projection())
            layer.SetSpatialFilter(spatialFilterReprojected.ogrGeometry())
        return sorted(set(feature.GetField(attribute) for feature in layer))


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

        # Create the output shapefile
        # driver = ogr.GetDriverByName('ESRI Shapefile')
        driver = ogr.GetDriverByName('GPKG')

        if os.path.exists(filename):
            driver.DeleteDataSource(filename)
        ds = driver.CreateDataSource(filename)
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
        assert len(n) == classification.classDefinition.classes
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

        # Create the output shapefile
        # driver = ogr.GetDriverByName('ESRI Shapefile')
        driver = ogr.GetDriverByName('GPKG')

        if os.path.exists(filename):
            driver.DeleteDataSource(filename)
        ds = driver.CreateDataSource(filename)
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
    def __init__(self, filename, classDefinition, idAttribute=None, nameAttribute=None, layer=0, minOverallCoverage=0.5,
                 minWinnerCoverage=0.5, dtype=np.uint8):

        Vector.__init__(self, filename=filename, layer=layer, burnAttribute=idAttribute, dtype=dtype)

        assert isinstance(classDefinition, ClassDefinition)
        self.classDefinition = classDefinition
        assert xor(idAttribute is None, nameAttribute is None)
        if idAttribute is not None:
            self.classAttribute = idAttribute
            self.classAttributeType = 'id'
        if nameAttribute is not None:
            self.classAttribute = nameAttribute
            self.classAttributeType = 'name'
        self.minOverallCoverage = minOverallCoverage
        self.minWinnerCoverage = minWinnerCoverage


class ClassDefinition(FlowObject):
    @staticmethod
    def fromENVIMeta(filename):
        ds = openRaster(filename)
        classes = ds.metadataItem(key='classes', domain='ENVI', dtype=int)
        names = ds.metadataItem(key='class names', domain='ENVI')
        lookup = ds.metadataItem(key='class lookup', domain='ENVI', dtype=int)
        return ClassDefinition(classes=classes - 1, names=names[1:],
                               lookup=np.array(lookup[3:]).reshape((classes - 1, 3)))

    def __init__(self, classes=None, names=None, lookup=None):

        assert classes is not None or names is not None
        if classes is None:
            classes = len(names)
        #assert classes > 0
        self.classes = classes
        if names is None:
            names = ['class {}'.format(i + 1) for i in range(classes)]
        if lookup is None:
            lookup = [(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)) for i in range(classes)]
        if len(lookup) == classes * 3:
            lookup = [[lookup[i * 3 + k] for k in range(3)] for i in range(classes)]

        assert len(names) == classes
        assert len(lookup) == classes
        for color in lookup:
            assert len(color) == 3, color

        self.names = [str(name) for name in names]
        self.lookup = [[int(v) for v in color] for color in lookup]

    def __repr__(self):
        return '{cls}(classes={classes}, names={names}, lookup={lookup})'.format(
            cls=self.__class__.__name__,
            classes=repr(self.classes),
            names=repr(self.names),
            lookup=repr(self.lookup))

    def equal(self, other, compareLookup=True):
        assert isinstance(other, ClassDefinition)
        equal = self.classes == other.classes
        equal &= all([a == b for a, b in zip(self.names, other.names)])
        if compareLookup:
            for color1, color2 in zip(self.lookup, other.lookup):
                for v1, v2 in zip(color1, color2):
                    equal &= v1 == v2
        return equal

    def getColor(self, label):
        return self.lookup[label - 1]

    def getColorByName(self, name):
        return self.getColor(label=self.names.index((name)) + 1)

    def getName(self, label):
        return self.names[label - 1]

    def getLabelByName(self, name):
        return self.names.index(name) + 1


class Classification(Raster):
    def __init__(self, filename, classDefinition=None, minOverallCoverage=0.5, minWinnerCoverage=0.5):
        Raster.__init__(self, filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        self.classDefinition = classDefinition
        self.noData = 0
        self.dtype = np.uint8
        self.minOverallCoverage = minOverallCoverage
        self.minWinnerCoverage = minWinnerCoverage

    def __repr__(self):
        return '{cls}(filename={filename}, classDefinition={classDefinition}, minOverallCoverage={minOverallCoverage}, minWinnerCoverage={minWinnerCoverage})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            classDefinition=repr(self.classDefinition),
            minOverallCoverage=repr(self.minOverallCoverage),
            minWinnerCoverage=repr(self.minWinnerCoverage))

    @classmethod
    def fromVectorClassification(cls, filename, vectorClassification, grid, oversampling, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('vectorClassification', classification=vectorClassification)
        applier.setOutputRaster('classification', filename=filename)
        applier.apply(operatorType=_ClassificationFromVectorClassification, vectorClassification=vectorClassification,
                      oversampling=oversampling)
        return Classification(filename=filename)

    @classmethod
    def fromProbability(cls, filename, probability, **kwargs):
        applier = Applier(defaultGrid=probability, **kwargs)
        applier.setFlowProbability('probability', probability=probability)
        applier.setOutputRaster('classification', filename=filename)
        applier.apply(operatorType=_ClassificationFromProbability, probability=probability)
        return Classification(filename=filename)

    def reclassify(self, filename, classDefinition, mapping, **kwargs):
        assert isinstance(classDefinition, ClassDefinition)
        assert isinstance(mapping, dict)
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('inclassification', raster=self)
        applier.setOutputRaster('outclassification', filename=filename)
        applier.apply(operatorType=_ClassificationReclassify, classification=self, classDefinition=classDefinition,
                      mapping=mapping)
        return Classification(filename=filename)


class _ClassificationReclassify(ApplierOperator):
    def ufunc(self, classification, classDefinition, mapping):
        inclassification = self.flowClassificationArray('inclassification', classification=classification)
        outclassification = self.full(value=0, bands=1, dtype=np.uint8)
        for inclass, outclass in mapping.items():
            if inclass in classification.classDefinition.names:
                inclass = classification.classDefinition.names.index(inclass) + 1
            if outclass in classDefinition.names:
                outclass = classDefinition.names.index(outclass) + 1
            outclassification[inclassification == inclass] = outclass
        self.outputRaster.raster(key='outclassification').setArray(array=outclassification)
        self.setFlowMetadataClassDefinition(name='outclassification', classDefinition=classDefinition)


class _ClassificationFromVectorClassification(ApplierOperator):
    def ufunc(self, vectorClassification, oversampling):
        array = self.flowClassificationArray('vectorClassification', classification=vectorClassification,
                                             oversampling=oversampling)
        self.outputRaster.raster(key='classification').setArray(array=array)
        self.setFlowMetadataClassDefinition(name='classification',
                                            classDefinition=vectorClassification.classDefinition)


class _ClassificationFromProbability(ApplierOperator):
    def ufunc(self, probability):
        array = self.flowClassificationArray('probability', classification=probability)
        self.outputRaster.raster(key='classification').setArray(array=array)
        self.setFlowMetadataClassDefinition(name='classification', classDefinition=probability.classDefinition)


class Regression(Raster):
    def __init__(self, filename, noData=None, outputNames=None, minOverallCoverage=0.5):
        Raster.__init__(self, filename)
        if noData is None:
            noData = openRaster(filename).noDataValue()
        if outputNames is None:
            outputNames = [band.description() for band in openRaster(filename).bands()]
        assert noData is not None
        self.noData = noData
        self.outputNames = outputNames
        self.minOverallCoverage = minOverallCoverage

    def __repr__(self):
        return '{cls}(filename={filename}, noData={noData}, outputNames={outputNames}, minOverallCoverage={minOverallCoverage})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            noData=repr(self.noData),
            outputNames=repr(self.outputNames),
            minOverallCoverage=repr(self.minOverallCoverage))

    def asMask(self):
        return Raster.asMask(self, noData=self.noData)


class Probability(Regression):
    def __init__(self, filename, classDefinition=None):
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        assert isinstance(classDefinition, ClassDefinition)
        Regression.__init__(self, filename=filename, noData=-1, outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def __repr__(self):
        return '{cls}(filename={filename}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            classDefinition=repr(self.classDefinition))

    @classmethod
    def fromVectorClassification(cls, filename, vectorClassification, grid, oversampling=1, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('vectorClassification', classification=vectorClassification)
        applier.setOutputRaster('probability', filename=filename)
        applier.apply(operatorType=_ProbabilityFromVectorClassification, vectorClassification=vectorClassification,
                      oversampling=oversampling)

        return Probability(filename=filename)

    def subsetClasses(self, filename, labels, **kwargs):
        indicies = [label - 1 for label in labels]
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('probability', raster=self)
        applier.setOutputRaster('probabilitySubset', filename=filename)
        applier.apply(operatorType=_ProbabilitySubsetClasses, indicies=indicies, probability=self)
        return Probability(filename=filename)

    def subsetClassesByName(self, filename, names, **kwargs):
        labels = [self.classDefinition.names.index(name) + 1 for name in names]
        return self.subsetClasses(filename=filename, labels=labels, **kwargs)

    def asClassColorRGBRaster(self, filename, filterById=None, filterByName=None, **kwargs):
        filter = []
        if filterById is not None:
            filter.extend(filterById)
        if filterByName is not None:
            filter.extend([self.classDefinition.names.index[name] for name in filterByName])
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('probability', raster=self)
        applier.setOutputRaster('raster', filename=filename)
        applier.apply(operatorType=_ProbabilityAsClassColorRGBRaster, probability=self, filter=filter)
        return Raster(filename=filename)


class _ProbabilityAsClassColorRGBRaster(ApplierOperator):
    def ufunc(self, filter, probability):
        assert isinstance(probability, Probability)
        colors = np.array(probability.classDefinition.lookup).reshape((-1, 3))
        array = self.flowRasterArray('probability', raster=probability)
        rgb = self.full(value=0, bands=3, dtype=np.float32)
        for id, (band, color) in enumerate(zip(array, colors), start=1):
            if len(filter) > 0 and id not in filter: continue
            rgb += band * color.reshape((3, 1, 1))
        np.uint8(np.clip(rgb, a_min=0, a_max=255, out=rgb))
        mask = np.any(rgb != 0, axis=0)
        np.clip(rgb, a_min=1, a_max=255, out=rgb)
        rgb *= mask
        self.outputRaster.raster(key='raster').setArray(array=np.uint8(rgb))


class _ProbabilityFromVectorClassification(ApplierOperator):
    def ufunc(self, vectorClassification, oversampling):
        array = self.flowProbabilityArray('vectorClassification', probability=vectorClassification,
                                          oversampling=oversampling)
        self.outputRaster.raster(key='probability').setArray(array=array)
        self.setFlowMetadataProbabilityDefinition(name='probability',
                                                  classDefinition=vectorClassification.classDefinition)


class _ProbabilitySubsetClasses(ApplierOperator):
    def ufunc(self, indicies, probability):
        classes = len(indicies)
        lookup = [probability.classDefinition.getColor(label=index + 1) for index in indicies]
        names = [probability.classDefinition.getName(label=index + 1) for index in indicies]
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)
        probabilitySubset = self.inputRaster.raster(key='probability').bandArray(indicies=indicies)
        self.outputRaster.raster(key='probabilitySubset').setArray(array=probabilitySubset)
        self.setFlowMetadataProbabilityDefinition(name='probabilitySubset', classDefinition=classDefinition)


class ProbabilityPerformance(FlowObject):
    def __init__(self, yP, yT, classDefinitionP, classDefinitionT):
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes == classDefinitionP.classes
        assert isinstance(yP, np.ndarray)
        assert isinstance(yT, np.ndarray)
        assert yT.shape[1] == yP.shape[1]
        assert len(yT) == 1
        assert len(yP) == classDefinitionP.classes

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP

        self.yP = yP.T
        self.yT = yT[0]
        self.n = yP.shape[1]
        self.log_loss = sklearn.metrics.log_loss(y_true=self.yT, y_pred=self.yP)
        self.roc_curves = dict()
        self.roc_auc_scores = dict()

        for i in range(1, self.classDefinitionT.classes + 1):
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
    def fromRaster(self, prediction, reference, **kwargs):
        assert isinstance(prediction, Probability)
        assert isinstance(reference, Classification)
        yP = UnsupervisedSample.fromRasterAndMask(raster=prediction, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features
        yT = UnsupervisedSample.fromRasterAndMask(raster=reference, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features
        return ProbabilityPerformance(yP=yP, yT=yT, classDefinitionP=prediction.classDefinition,
                                      classDefinitionT=reference.classDefinition)

    def report(self):
        classes = self.classDefinitionT.classes
        names = self.classDefinitionT.names
        report = Report('Probability Performance')
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
            rgb = [v / 255. for v in self.classDefinitionP.lookup[i]]
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


class UnsupervisedSample(FlowObject):
    def __init__(self, features, metadata=None):
        assert isinstance(features, np.ndarray) and features.ndim == 2
        if metadata is None:
            metadata = dict()
        self.features = features
        self.metadata = metadata
        self.nbands, self.nsamples = self.features.shape

    def __repr__(self):
        return '{cls}(features=array{features}, metadata={metadata})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            metadata=repr(self.metadata))

    @staticmethod
    def fromENVISpectralLibrary(filename):
        headers = [filename + '.hdr', filename[:-4] + '.hdr']
        for header in headers:
            if os.path.exists(header):
                library = spectral.envi.open(file=header)
                return UnsupervisedSample(features=library.spectra.T, metadata=library.metadata)
        raise Exception('header file not found')

    @staticmethod
    def fromRasterAndMask(raster, mask=None, mask2=None, grid=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster(name='raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        results = applier.apply(operatorType=_UnsupervisedSampleFromRasterAndMask, raster=raster, mask=mask,
                                mask2=mask2)
        features = np.hstack(results)
        sample = UnsupervisedSample(features=features)
        applier.controls.progressBar.setText(repr(sample))
        return sample

    @staticmethod
    def fromSample(sample):
        return UnsupervisedSample(features=sample.features, metadata=sample.metadata)

    def saveAsENVISpectralLibrary(self, filename):
        metadata = self.metadata.copy()
        if 'spectra names' not in metadata:
            metadata['spectra names'] = ['profile ' + str(i + 1) for i in range(self.features.shape[1])]
        if 'wavelength' not in metadata:
            metadata['wavelength'] = range(self.features.shape[0])
            metadata['wavelength units'] = 'indices'

        library = spectral.envi.SpectralLibrary(data=self.features.T, header=metadata, params=None)
        fileBaseName = filename.replace('.hdr', '').replace('.sli', '').replace('.esl', '')
        library.save(fileBaseName=fileBaseName)

        header = spectral.envi.read_envi_header(file=fileBaseName + '.hdr')
        self._saveAsENVISpectralLibraryUpdateHeader(header)
        spectral.envi.write_envi_header(fileName=fileBaseName + '.hdr', header_dict=header, is_library=True)

    def _saveAsENVISpectralLibraryUpdateHeader(self, header):
        for key in ['data ignore value', 'wavelength', 'wavelength units']:
            if key not in self.metadata:
                del header[key]

    def scaleFeaturesInplace(self, factor):
        self.features = self.features * factor

    def classifyByName(self, names, classDefinition):
        assert len(names) == self.nsamples
        assert isinstance(classDefinition, ClassDefinition)
        assert set(names).issubset(set(classDefinition.names))
        labels = [classDefinition.names.index(name) + 1 for name in names]
        labels = np.atleast_2d(np.array(labels, dtype=np.uint8))
        return ClassificationSample(features=self.features, labels=labels, metadata=self.metadata,
                                    classDefinition=classDefinition)


class _UnsupervisedSampleFromRasterAndMask(ApplierOperator):
    def ufunc(self, raster, mask, mask2):
        features = self.flowRasterArray(name='raster', raster=raster)
        labeled = self.maskFromArray(array=features, noDataSource='raster')
        labeled *= self.flowMaskArray('mask', mask=mask)
        labeled *= self.flowMaskArray('mask2', mask=mask2)
        return features[:, labeled[0]]


class SupervisedSample(UnsupervisedSample):
    def __init__(self, features, labels, noData, outputNames, metadata=None):
        UnsupervisedSample.__init__(self, features=features, metadata=metadata)

        assert isinstance(labels, np.ndarray) and features.ndim == 2
        assert self.features.shape[1] == labels.shape[1]
        self.labels = labels
        self.noData = noData
        self.outputNames = outputNames


class ClassificationSample(SupervisedSample):
    def __init__(self, features, labels, classDefinition, metadata=None, outputName='classification'):
        SupervisedSample.__init__(self, features, labels, noData=0, metadata=metadata, outputNames=[outputName])
        assert labels.shape[0] == 1
        assert isinstance(classDefinition, ClassDefinition)
        self.classDefinition = classDefinition
        self.histogram = \
            np.histogram(labels, bins=self.classDefinition.classes, range=[1, self.classDefinition.classes + 1])[0]

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))

    @staticmethod
    def fromENVISpectralLibrary(filename, classificationSchemeName=''):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=filename)
        names = sample.metadata[classificationSchemeName + 'class names'][1:]
        classes = len(names)
        lookup = np.array(sample.metadata[classificationSchemeName + 'class lookup'][3:]).reshape((classes, 3))
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)

        labels = np.array(sample.metadata[classificationSchemeName + 'class spectra names'])
        for i, name in enumerate(names):
            labels[labels == name] = str(i + 1)
        labels = np.atleast_2d(np.uint8(labels))
        return ClassificationSample(features=sample.features, labels=labels, classDefinition=classDefinition)

    def _saveAsENVISpectralLibraryUpdateHeader(self, header):
        UnsupervisedSample._saveAsENVISpectralLibraryUpdateHeader(self, header=header)
        header['classes'] = self.classDefinition.classes + 1
        header['class names'] = ['Unclassified'] + self.classDefinition.names
        header['class lookup'] = [0, 0, 0] + self.classDefinition.lookup
        header['class spectra names'] = np.array(self.classDefinition.names)[self.labels.ravel() - 1]

    @classmethod
    def fromRasterAndProbability(cls, raster, probability, grid=None, mask=None, mask2=None,
                                 minOverallCoverage=0.5, minWinnerCoverage=0.5, **kwargs):
        if grid is None:
            grid = raster.grid
        probabilitySample = ProbabilitySample.fromRasterAndProbability(raster=raster, probability=probability,
                                                                       grid=grid,
                                                                       mask=mask, mask2=mask2, **kwargs)
        classificationSample = ClassificationSample.fromProbabilitySample(sample=probabilitySample,
                                                                          minOverallCoverage=minOverallCoverage,
                                                                          minWinnerCoverage=minWinnerCoverage)
        return classificationSample

    @classmethod
    def fromRasterAndClassification(cls, raster, classification, grid=None, mask=None, mask2=None, **kwargs):
        return cls.fromRasterAndProbability(raster=raster, probability=classification, grid=grid,
                                            mask=mask, mask2=mask2, **kwargs)

    @classmethod
    def fromProbabilitySample(cls, sample, minOverallCoverage=0.5, minWinnerCoverage=0.5):
        assert isinstance(sample, ProbabilitySample)
        fractions = sample.labels

        labels = np.argmax(sample.labels, axis=0)[None] + 1
        overallCoverage = np.sum(fractions, axis=0, keepdims=True)
        winnerCoverage = np.max(sample.labels, axis=0, keepdims=True)
        valid = overallCoverage >= minOverallCoverage
        valid *= winnerCoverage >= minWinnerCoverage

        features = sample.features[:, valid[0]]
        labels = labels[:, valid[0]]
        return ClassificationSample(features=features, labels=labels, classDefinition=sample.classDefinition)

    def asProbabilitySample(self):
        probabilityArray = np.zeros(shape=(self.classDefinition.classes, self.nsamples), dtype=np.float32)
        for index in range(self.classDefinition.classes):
            probabilityArray[index][self.labels[0] == index + 1] = 1.
        return ProbabilitySample(features=self.features, labels=probabilityArray, classDefinition=self.classDefinition,
                                 metadata=self.metadata)

    def synthMix(self, mixingComplexities, classLikelihoods=None, n=10):

        if classLikelihoods is None:
            classLikelihoods = 'proportional'
        if classLikelihoods is 'proportional':
            classLikelihoods = {i + 1: float(count) / sum(self.histogram) for i, count in enumerate(self.histogram)}
        elif classLikelihoods is 'equalized':
            classLikelihoods = {i + 1: 1. / self.classDefinition.classes for i in range(self.classDefinition.classes)}

        assert isinstance(mixingComplexities, dict)
        assert isinstance(classLikelihoods, dict)

        features = self.features
        labels = self.labels
        classes = self.classDefinition.classes

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
            complexity = np.random.choice(mixingComplexities.keys(), p=mixingComplexities.values())
            drawnLabels = np.random.choice(classLikelihoods.keys(), size=complexity, replace=True,
                                           p=classLikelihoods.values())
            drawnIndices = [np.random.choice(indices[label]) for label in drawnLabels]
            drawnFeatures = features[:, drawnIndices]
            drawnFractions = zeroOneFractions[:, drawnIndices]
            randomWeights = np.atleast_2d(np.float32(np.random.randint(low=1, high=100, size=complexity)))
            randomWeights /= randomWeights.sum()
            mixtures.append(np.sum(drawnFeatures * randomWeights, axis=1))
            fractions.append(np.sum(drawnFractions * randomWeights, axis=1))

        mixtures, fractions = np.array(mixtures).T, np.array(fractions).T
        return ProbabilitySample(features=mixtures, labels=fractions, classDefinition=self.classDefinition)


class RegressionSample(SupervisedSample):
    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, noData={noData}, outputNames={outputNames})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            noData=repr(self.noData),
            outputNames=repr(self.outputNames))

    @staticmethod
    def fromRasterAndRegression(raster, regression, grid, mask=None, mask2=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster(name='raster', raster=raster)
        applier.setFlowRegression(name='regression', regression=regression)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        results = applier.apply(operatorType=_RegressionSampleFromRasterAndRegression, raster=raster,
                                regression=regression, mask=mask, mask2=mask2)
        features = np.hstack(result[0] for result in results)
        fractions = np.hstack(result[1] for result in results)
        return RegressionSample(features=features, labels=fractions, noData=regression.noData,
                                outputNames=regression.outputNames)

    @staticmethod
    def fromProbabilitySample(sample):
        assert isinstance(sample, ProbabilitySample)
        return RegressionSample(features=sample.features, labels=sample.labels, noData=sample.noData,
                                outputNames=sample.outputNames)


class _RegressionSampleFromRasterAndRegression(ApplierOperator):
    def ufunc(self, raster, regression, mask, mask2):
        features = self.flowRasterArray(name='raster', raster=raster)
        labels = self.flowRegressionArray(name='regression', regression=regression)
        labeled = self.maskFromArray(array=features, noDataSource='raster')
        labeled *= self.maskFromArray(array=labels, noData=regression.noData)
        #labeled *= labels != regression.noData
        labeled *= self.flowMaskArray('mask', mask=mask)
        labeled *= self.flowMaskArray('mask2', mask=mask2)
        return features[:, labeled[0]], labels[:, labeled[0]]


class ProbabilitySample(RegressionSample):
    def __init__(self, features, labels, classDefinition, metadata=None):
        assert isinstance(classDefinition, ClassDefinition)
        assert labels.shape[0] == classDefinition.classes
        RegressionSample.__init__(self, features, labels, noData=-1, metadata=metadata,
                                  outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))

    @classmethod
    def fromRasterAndClassification(cls, raster, classification, mask=None, mask2=None, **kwargs):
        return cls.fromRasterAndProbability(raster=raster, probability=classification, mask=mask, mask2=mask2, **kwargs)

    @staticmethod
    def fromRasterAndProbability(raster, probability, grid, mask=None, mask2=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster(name='raster', raster=raster)
        applier.setFlowProbability(name='probability', probability=probability)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        results = applier.apply(operatorType=_ProbabilitySampleFromRasterAndProbability, raster=raster,
                                probability=probability, mask=mask, mask2=mask2)
        features = np.hstack(result[0] for result in results)
        fractions = np.hstack(result[1] for result in results)
        return ProbabilitySample(features=features, labels=fractions, classDefinition=probability.classDefinition)

    def subsetClassesByName(self, names):
        labels = [self.classDefinition.getLabelByName(name) for name in names]
        return self.subsetClasses(labels=labels)

    def subsetClasses(self, labels):
        indicies = [label - 1 for label in labels]
        classDefinition = ClassDefinition(classes=len(indicies),
                                          names=[self.classDefinition.getName(index + 1) for index in indicies],
                                          lookup=[self.classDefinition.getColor(index + 1) for index in indicies])
        return ProbabilitySample(features=self.features, labels=self.labels[indicies], classDefinition=classDefinition)


class _ProbabilitySampleFromRasterAndProbability(ApplierOperator):
    def ufunc(self, raster, probability, mask, mask2):
        features = self.flowRasterArray(name='raster', raster=raster)
        fractions = self.flowProbabilityArray(name='probability', probability=probability)
        labeled = self.maskFromArray(array=features, noDataSource='raster')
        labeled *= np.any(fractions != -1, axis=0, keepdims=True)
        labeled *= self.flowMaskArray('mask', mask=mask)
        labeled *= self.flowMaskArray('mask2', mask=mask2)
        return features[:, labeled[0]], fractions[:, labeled[0]]


class Estimator(FlowObject):
    SAMPLE_TYPE = SupervisedSample
    PREDICT_TYPE = Raster

    def __init__(self, sklEstimator):
        self.sklEstimator = sklEstimator
        self.sample = None

    def __repr__(self):
        return '{cls}(sklEstimator={sklEstimator})'.format(cls=self.__class__.__name__,
                                                           sklEstimator=repr(self.sklEstimator))

    def _fit(self, sample):
        assert isinstance(sample, self.SAMPLE_TYPE)
        self.sample = sample

        X = np.float64(sample.features.T)

        if hasattr(sample, 'labels'):
            if sample.labels.shape[0] == 1 and not isinstance(self.sklEstimator,
                                                              sklearn.multioutput.MultiOutputEstimator):
                y = sample.labels.ravel()
            else:
                y = sample.labels.T
        else:
            y = None

        self.sklEstimator.fit(X=X, y=y)

        if isinstance(self, Clusterer):
            yTrain = self.sklEstimator.predict(X=X)
            self.classDefinition = ClassDefinition(classes=max(yTrain)+1)
        return self

    def _predict(self, filename, raster, mask=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('prediction', filename=filename)
        applier.apply(operatorType=_EstimatorPredict, raster=raster, estimator=self, mask=mask)
        prediction = self.PREDICT_TYPE(filename=filename)
        assert isinstance(prediction, Raster)
        return prediction

    def _predictProbability(self, filename, raster, mask=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('probability', filename=filename)
        applier.apply(operatorType=_EstimatorPredictProbability, raster=raster, estimator=self, mask=mask)
        probability = Probability(filename=filename)
        return probability

    def _transform(self, filename, raster, inverse=False, mask=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('transformation', filename=filename)
        applier.apply(operatorType=_EstimatorTransform, estimator=self, raster=raster, mask=mask, inverse=inverse)
        return Raster(filename=filename)

    def _inverseTransform(self, filename, raster, mask=None, **kwargs):
        return self._transform(filename=filename, raster=raster, inverse=True, mask=mask, **kwargs)


class _EstimatorPredict(ApplierOperator):
    def ufunc(self, estimator, raster, mask):
        self.features = self.flowRasterArray('raster', raster=raster)
        etype, dtype, noutputs = self.getInfos(estimator)

        if isinstance(estimator, (Classifier, Clusterer)):
            noData = 0
        else:
            noData = estimator.sample.noData

        prediction = self.full(value=noData, bands=noutputs, dtype=dtype)

        valid = self.maskFromArray(array=self.features, noDataSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)

        X = np.float64(self.features[:, valid[0]].T)
        y = estimator.sklEstimator.predict(X=X)
        prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='prediction').setArray(array=prediction)

        if isinstance(estimator, Classifier):
            self.setFlowMetadataClassDefinition('prediction', classDefinition=estimator.sample.classDefinition)
        elif isinstance(estimator, Clusterer):
            self.setFlowMetadataClassDefinition('prediction', classDefinition=estimator.classDefinition)
        elif isinstance(estimator, Regressor):
            if isinstance(estimator.sample, ProbabilitySample):
                self.setFlowMetadataProbabilityDefinition('prediction',
                                                          classDefinition=estimator.sample.classDefinition)
            else:
                self.outputRaster.raster(key='prediction').setNoDataValue(value=noData)
            self.setFlowMetadataBandNames('prediction', bandNames=estimator.sample.outputNames)

    def getInfos(self, estimator):
        etype = estimator.sklEstimator._estimator_type
        if etype in ['classifier', 'clusterer']:
            noutputs = 1
            dtype = np.uint8
        elif etype == 'regressor':
            X0 = np.float64(np.atleast_2d(self.features[:, 0, 0]))
            y0 = estimator.sklEstimator.predict(X=X0)
            noutputs = max(y0.shape)
            dtype = np.float32
        else:
            raise Exception('unexpected estimator type')
        return etype, dtype, noutputs


class _EstimatorPredictProbability(ApplierOperator):
    def ufunc(self, estimator, raster, mask):
        assert isinstance(estimator, Classifier)
        self.features = self.flowRasterArray('raster', raster=raster)
        noutputs = estimator.sample.classDefinition.classes
        noData = -1
        prediction = self.full(value=noData, bands=noutputs, dtype=np.float32)

        valid = self.maskFromArray(array=self.features, noDataSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)

        X = np.float64(self.features[:, valid[0]].T)
        y = estimator.sklEstimator.predict_proba(X=X)
        prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='probability').setArray(array=prediction)
        self.setFlowMetadataProbabilityDefinition('probability', classDefinition=estimator.sample.classDefinition)


class _EstimatorTransform(ApplierOperator):
    def ufunc(self, estimator, raster, mask, inverse):
        if inverse:
            sklTransform = estimator.sklEstimator.inverse_transform
        else:
            sklTransform = estimator.sklEstimator.transform

        noData = np.finfo(np.float32).min
        features = self.flowRasterArray('raster', raster=raster)

        X0 = np.float64(np.atleast_2d(features[:, 0, 0]))
        _, noutputs = sklTransform(X=X0).shape

        transformation = self.full(value=noData, bands=noutputs, dtype=np.float32)

        valid = self.maskFromArray(array=features, noDataSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)

        X = np.float64(features[:, valid[0]].T)
        y = sklTransform(X=X)
        transformation[:, valid[0]] = np.float32(y.reshape(-1, noutputs).T)

        self.outputRaster.raster(key='transformation').setArray(array=transformation)
        self.outputRaster.raster(key='transformation').setNoDataValue(value=noData)


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
    SAMPLE_TYPE = UnsupervisedSample
    PREDICT_TYPE = Raster
    fit = Estimator._fit
    transform = Estimator._transform
    inverseTransform = Estimator._inverseTransform


class Clusterer(Estimator):
    SAMPLE_TYPE = UnsupervisedSample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict
    transform = Estimator._transform

    def __init__(self, sklEstimator):
        Estimator.__init__(self, sklEstimator=sklEstimator)
        self.classDefinition = ClassDefinition(classes=0)

class ClassificationPerformance(FlowObject):
    def __init__(self, yP, yT, classDefinitionP, classDefinitionT, classProportions=None):
        assert isinstance(yP, np.ndarray) and yP.ndim == 1
        assert isinstance(yT, np.ndarray) and yT.shape == yP.shape
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes == classDefinitionP.classes

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP

        import sklearn.metrics
        self.yP = yP
        self.yT = yT
        self.mij = np.int64(
            sklearn.metrics.confusion_matrix(yT, yP, labels=range(1, classDefinitionT.classes + 1)).T)
        self.m = np.int64(yP.size)
        self.Wi = classProportions
        self.adjusted = False
        self._assessPerformance()

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT}, classDefinitionP={classDefinitionP}, classDefinitionT={classDefinitionT}, classProportions={classProportions})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)),
            classDefinitionP=repr(self.classDefinitionP),
            classDefinitionT=repr(self.classDefinitionT),
            classProportions=repr(list(self.Wi)))

    @classmethod
    def fromRaster(self, prediction, reference, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        yP = UnsupervisedSample.fromRasterAndMask(raster=prediction, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features[0]
        yT = UnsupervisedSample.fromRasterAndMask(raster=reference, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features[0]
        return ClassificationPerformance(yP=yP, yT=yT, classDefinitionP=prediction.classDefinition,
                                         classDefinitionT=reference.classDefinition)

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
        for i in range(self.classDefinitionT.classes):
            for j in range(self.classDefinitionT.classes):
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
        for i in range(self.classDefinitionT.classes): self.OverallAccuracySSE += self.pij[i, i] * (
            self.Wi[i] - self.pij[i, i]) / (self.Wi[i] * self.m)

        a1 = self.mii.sum() / self.m
        a2 = (self.mi_ * self.m_j).sum() / self.m ** 2
        a3 = (self.mii * (self.mi_ + self.m_j)).sum() / self.m ** 2
        a4 = 0.
        for i in range(self.classDefinitionT.classes):
            for j in range(self.classDefinitionT.classes):
                a4 += self.mij[i, j] * (self.mi_[j] + self.m_j[i]) ** 2
        a4 /= self.m ** 3
        b1 = a1 * (1 - a1) / (1 - a2) ** 2
        b2 = 2 * (1 - a1) * (2 * a1 * a2 - a3) / (1 - a2) ** 3
        b3 = (1 - a1) ** 2 * (a4 - 4 * a2 ** 2) / (1 - a2) ** 4
        self.KappaAccuracySSE = (b1 + b2 + b3) / self.m

        self.ProducerAccuracySSE = np.zeros(self.classDefinitionT.classes, dtype=np.float64)
        for i in range(self.classDefinitionT.classes):
            sum = 0.
            for j in range(self.classDefinitionT.classes):
                if i == j: continue
                sum += self.pij[i, j] * (self.Wi[j] - self.pij[i, j]) / (self.Wi[j] * self.m)
                self.ProducerAccuracySSE[i] = self.pij[i, i] * self.p_j[i] ** (-4) * (
                    self.pij[i, i] * sum + (self.Wi[i] - self.pij[i, i]) * (self.p_j[i] - self.pij[i, i]) ** 2 / (
                        self.Wi[i] * self.m))

        self.UserAccuracySSE = np.zeros(self.classDefinitionT.classes, dtype=np.float64)
        for i in range(self.classDefinitionT.classes):
            self.UserAccuracySSE[i] = self.pij[i, i] * (self.Wi[i] - self.pij[i, i]) / (self.Wi[i] ** 2 * self.m)

        self.F1AccuracySSE = self._fix(
            2 * self.UserAccuracySSE * self.ProducerAccuracySSE / (self.UserAccuracySSE + self.ProducerAccuracySSE))

        self.ConditionalKappaAccuracySSE = self.m * (self.mi_ - self.mii) / (self.mi_ * (self.m - self.m_j)) ** 3 * (
            (self.mi_ - self.mii) * (self.mi_ * self.m_j - self.m * self.mii) + self.m * self.mii * (
                self.m - self.mi_ - self.m_j + self.mii))

        self.ClassProportion = self.m_j / self.m
        self.ClassProportionSSE = np.zeros(self.classDefinitionT.classes, dtype=np.float64)
        for j in range(self.classDefinitionT.classes):
            for i in range(self.classDefinitionT.classes):
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

        # if self.adjusted:
        #    report.append(ReportHeading('Stratification'))

        #    colHeaders = [['DN','Stratum', 'Stratum Size', 'Stratum Sample Size', 'Adjustment Weight']]
        #    colSpans = [[1,1,1,1,1]]
        #    data = np.transpose([np.array(range(0, self.strataClasses))+1, self.strataClassNames, self.strataSizes, self.strataSampleSizes, np.round(self.strataWeights,2) ])
        #    report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        report.append(ReportHeading('Class Overview'))
        colHeaders = None
        rowSpans = [[1, 2], [1, 1, 1]]
        colSpans = [[1, 1, 1, 1, 1]]
        rowHeaders = [['', 'Class Names'], ['Class ID', 'Reference', 'Prediction']]
        data = [np.hstack((range(1, self.classDefinitionT.classes + 1))), self.classDefinitionT.names,
                self.classDefinitionP.names]
        report.append(
            ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans, rowSpans=rowSpans))

        # Confusion Matrix Table
        report.append(ReportHeading('Confusion Matrix'))
        rowSpans = None
        classNumbers = []
        for i in range(self.classDefinitionT.classes): classNumbers.append('(' + str(i + 1) + ')')
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes], np.ones(self.classDefinitionT.classes + 1, dtype=int)]
        classNamesColumn = []
        for i in range(self.classDefinitionT.classes): classNamesColumn.append(
            '(' + str(i + 1) + ') ' + self.classDefinitionT.names[i])
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(((np.hstack((self.mij, self.m_j[:, None]))), np.hstack((self.mi_, self.m)))).astype(
            int)

        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

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
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Proportion Matrix Table
        report.append(ReportHeading('Proportion Matrix'))
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes], np.ones(self.classDefinitionT.classes + 1, dtype=int)]
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(
            ((np.hstack((self.pij * 100, self.p_j[:, None] * 100))), np.hstack((self.pi_ * 100, 100))))
        report.append(ReportTable(np.round(data, 2), '', colHeaders, rowHeaders, colSpans, rowSpans))
        return report


class RegressionPerformance(FlowObject):
    def __init__(self, yT, yP, outputNamesT, outputNamesP):
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
    def fromRaster(self, prediction, reference, **kwargs):
        assert isinstance(prediction, Regression)
        assert isinstance(reference, Regression)
        yP = UnsupervisedSample.fromRasterAndMask(raster=prediction, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features
        yT = UnsupervisedSample.fromRasterAndMask(raster=reference, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features
        return RegressionPerformance(yP=yP, yT=yT, outputNamesP=prediction.outputNames,
                                     outputNamesT=reference.outputNames)

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
    def fromRaster(prediction, reference, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        yP = UnsupervisedSample.fromRasterAndMask(raster=prediction, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features
        yT = UnsupervisedSample.fromRasterAndMask(raster=reference, mask=reference.asMask(), grid=reference,
                                                  **kwargs).features
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
