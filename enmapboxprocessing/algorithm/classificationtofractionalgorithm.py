from os.path import splitext, basename
from time import time
from typing import Dict, Any, List, Tuple
from warnings import warn

import numpy as np
from osgeo import gdal

from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.typing import CreationOptions
from enmapboxprocessing.utils import Utils
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRectangle,
                        QgsCoordinateReferenceSystem, QgsRasterLayer, QgsPalettedRasterRenderer, QgsMapLayer,
                        QgsCategorizedSymbolRenderer)
from processing.core.Processing import Processing

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class ClassificationToFractionAlgorithm(EnMAPProcessingAlgorithm):
    P_MAP = 'map'
    P_GRID = 'grid'
    P_PRECISION = 'precision'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outraster'

    def displayName(self):
        return 'Classification to Fraction'

    def shortDescription(self):
        return 'Converts a classification (raster or vector) into a multiband class cover fraction raster. ' \
               'Output band order and naming are given by the renderer categories. ' \
               'Values are stored as percentages ranging from 0 to 100.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_MAP, self.helpParameterMapClassification()),
            (self.P_GRID, self.helpParameterGrid()),
            (self.P_PRECISION, 'Processing precision in number of decimals. Default is 0 (accurate to the percent). '
                               'Decimal precision depends on internal oversampling of the source classification. '
                               'Note that processing load increases quadratically with number of decimals.'),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMapLayer(self.P_MAP, 'Classification')
        self.addParameterRasterLayer(self.P_GRID, 'Grid')
        self.addParameterInt(self.P_PRECISION, 'Precision', 0, False, minValue=0, maxValue=2)
        self.addParameterCreationProfile(self.P_CREATION_PROFILE)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterMapClassification(parameters, self.P_MAP, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        map = self.parameterAsLayer(parameters, self.P_MAP, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        precision = self.parameterAsInt(parameters, self.P_PRECISION, context)
        oversampling = [10, 32, 100][precision]
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        if oversampling is None:
            oversampling = 10  # results in integer precision fraction values (oversampling=100 would be 2 decimals)
            assert 0 # todo create oversampled grid

        if isinstance(map, QgsRasterLayer):
            tmpFilename = Utils.tmpFilename(filename, 'oversampled.vrt')
            alg = TranslateClassificationAlgorithm()
            parameters = {
                alg.P_CLASSIFICATION: map,
                alg.P_GRID: gridOversampled,
                alg.P_CREATION_PROFILE: alg.VrtProfile,
                alg.P_OUTPUT_RASTER: tmpFilename
            }
            Processing.runAlgorithm(alg, parameters, feedback=feedback)
            raster = QgsRasterLayer(tmpFilename)
        elif isinstance(map, QgsVectorLayer):
            tmpFilename = Utils.tmpFilename(filename, 'oversampled.tif')
            alg = RasterizeClassificationAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_VECTOR: map,
                alg.P_GRID: gridOversampled,
                alg.P_CREATION_PROFILE: self.TiledAndCompressedGTiffProfile,
                alg.P_OUTPUT_RASTER: tmpFilename
            }
            Processing.runAlgorithm(alg, parameters, feedback=feedback)
            raster = QgsRasterLayer(tmpFilename)
        else:
            assert 0
        categories = Utils.categoriesFromPalettedRasterRenderer(raster.renderer())

        maxClassId = max([c[0] for c in categories])
        indexByClass = np.full(shape=(maxClassId + 1,), fill_value=-1)
        for i, (value, label, color) in enumerate(categories):
            indexByClass[value] = i

        renderer = raster.renderer()
        assert isinstance(renderer, QgsPalettedRasterRenderer)

        feedback.pushInfo('Calculate class fractions')

        # todo iterate blocks
        reader = RasterReader(raster)
        classes = reader.arrayFromBoundingBoxAndSize(
            extent, width * oversampling, height * oversampling, [renderer.band()]
        )[0]
        nc = len(categories)
        if oversampling == 10:
            dtype = np.uint8
        else:
            dtype = np.float32

        counts = np.zeros((nc, height, width), dtype)
        notCovered = np.full_like(counts[0], True, np.bool)

        try:
            from numba import jit
            calculate = jit(nopython=True)(_calculatePurePython)
        except ModuleNotFoundError as error:
            warn(f'{str(error)}. Will fall back into pure Python mode which may be really slow.')
            calculate = _calculatePurePython

        calculate(classes, counts, notCovered, oversampling, indexByClass)

        # scale to percentage
        if oversampling < 10:
            np.divide(counts, oversampling ** 2 / 100, out=counts)
            np.round(counts, 0, out=counts)
            counts = counts.astype(np.uint8)
            noDataValue = 255
        elif oversampling == 10:
            noDataValue = 255
        else:
            np.divide(counts, oversampling ** 2 / 100, out=counts)
            noDataValue = -1

        for a in counts:
            a[notCovered] = noDataValue

        writer = Driver(filename, format, options, feedback).createFromArray(counts, extent, crs)
        writer.setNoDataValue(noDataValue)
        for bandNo, (value, label, color) in enumerate(categories, 1):
            writer.setBandName(label, bandNo)

        #Utils.tmpFilenameDelete(tmpFilename)

        return {self.P_OUTPUT_RASTER: filename}


def _calculatePurePython(classes, counts, notCovered, oversampling, indexByClass):
    height, width = notCovered.shape
    for y in range(height):
        for x in range(width):
            for y2 in range(oversampling):
                for x2 in range(oversampling):
                    c = classes[y * oversampling + y2, x * oversampling + x2]
                    index = indexByClass[c]
                    if index != -1:
                        counts[index, y, x] += 1
                        notCovered[y, x] = False
