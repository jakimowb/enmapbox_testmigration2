from typing import Dict, Any, List, Tuple

import processing
from PyQt5.QtCore import QVariant
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRectangle,
                        QgsCoordinateReferenceSystem, QgsVectorFileWriter,
                        QgsProject, QgsField, QgsCoordinateTransform, QgsRasterLayer, QgsProcessingException)
from qgis.core import edit

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import HexColor, Category
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class RasterizeCategorizedVectorAlgorithm(EnMAPProcessingAlgorithm):
    P_CATEGORIZED_VECTOR, _CATEGORIZED_VECTOR = 'categorizedVector', 'Categorized vector layer'
    P_GRID, _GRID = 'grid', 'Grid'
    P_COVERAGE, _COVERAGE = 'coverage', 'Minimum pixel coverage'
    P_MAJORITY_VOTING, _MAJORITY_VOTING = 'majorityVoting', 'Majority voting'
    P_OUTPUT_CATEGORIZED_RASTER, _OUTPUT_CATEGORIZED_RASTER = 'outputRasterizedCategories', \
                                                              'Output categorized raster layer'

    def displayName(self):
        return 'Rasterize categorized vector layer'

    def shortDescription(self):
        return 'Rasterize a categorized vector layer into a categorized raster layer. ' \
               'Output category names and colors are given by the source layer.\n' \
               'Resampling is done via a two-step majority voting approach. ' \
               'First, the categorized raster layer is resampled at x10 finer resolution, ' \
               'and subsequently aggregated back to the target resolution using majority voting. ' \
               'This approach leads to pixel-wise class decisions that are accurate to the percent.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CATEGORIZED_VECTOR, 'A categorized vector layer to be rasterized.'),
            (self._GRID, 'The target grid.'),
            (self._COVERAGE, 'Exclude all pixel where (polygon) coverage is smaller than given threshold.'),
            (self._MAJORITY_VOTING, 'Whether to use majority voting. '
                                    'Turn off to use simple nearest neighbour resampling, which is much faster, '
                                    'but may result in highly inaccurate decisions.'),
            (self._OUTPUT_CATEGORIZED_RASTER, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_CATEGORIZED_VECTOR, self._CATEGORIZED_VECTOR)
        self.addParameterRasterLayer(self.P_GRID, self._GRID)
        self.addParameterInt(self.P_COVERAGE, self._COVERAGE, 0, False, 0, 100, advanced=True)
        self.addParameterBoolean(self.P_MAJORITY_VOTING, self._MAJORITY_VOTING, True, False, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_CATEGORIZED_RASTER, self._OUTPUT_CATEGORIZED_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterVectorClassification(parameters, self.P_CATEGORIZED_VECTOR, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        vector = self.parameterAsVectorLayer(parameters, self.P_CATEGORIZED_VECTOR, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        minCoverage = self.parameterAsInt(parameters, self.P_COVERAGE, context) / 100.
        majorityVoting = self.parameterAsBoolean(parameters, self.P_MAJORITY_VOTING, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CATEGORIZED_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            fieldName = 'derived_id'
            tmpVector, names, colors = self.categoriesToField(
                vector, fieldName, grid.extent(), grid.crs(), Utils.tmpFilename(filename, 'categorized.gpkg'), feedback2
            )

            geometryType = vector.geometryType()
            dataType = Utils.smallesUIntDataType(len(names))
            simpleBurn = not Utils.isPolygonGeometry(geometryType) or not majorityVoting or (minCoverage > 0)
            if simpleBurn:
                alg = RasterizeVectorAlgorithm()
                parameters = {
                    alg.P_GRID: grid,
                    alg.P_VECTOR: tmpVector,
                    alg.P_DATA_TYPE: self.O_DATA_TYPE.index(Utils.qgisDataTypeName(dataType)),
                    alg.P_BURN_ATTRIBUTE: fieldName,
                    alg.P_RESAMPLE_ALG: self.NearestNeighbourResampleAlg,  # simple burn
                    alg.P_OUTPUT_RASTER: filename
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
            else:
                alg = RasterizeVectorAlgorithm()
                parameters = {
                    alg.P_GRID: grid,
                    alg.P_VECTOR: tmpVector,
                    alg.P_DATA_TYPE: self.O_DATA_TYPE.index(Utils.qgisDataTypeName(dataType)),
                    alg.P_BURN_ATTRIBUTE: fieldName,
                    alg.P_RESAMPLE_ALG: self.ModeResampleAlg,  # use 10x oversampling
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'rasterized.tif')
                }
                classification = processing.run(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_RASTER]

                feedback.pushInfo('Calculate pixel coverage')
                alg = RasterizeVectorAlgorithm()
                parameters = {
                    alg.P_GRID: grid,
                    alg.P_VECTOR: tmpVector,
                    alg.P_DATA_TYPE: self.Float32,
                    alg.P_RESAMPLE_ALG: self.AverageResampleAlg,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'coverage.tif')
                }
                coverageRaster = processing.run(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_RASTER]

                info = 'Mask pixel with low coverage'
                feedback.pushInfo(info)
                array = RasterReader(classification).array()
                marray = RasterReader(coverageRaster).array()[0] < minCoverage
                array[0][marray] = 0
                driver = Driver(filename, self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions, feedback2)
                driver.createFromArray(array, grid.extent(), grid.crs())

            # setup renderer
            layer = QgsRasterLayer(filename)
            categories = [Category(value, label, color) for value, (label, color) in enumerate(zip(names, colors), 1)]
            renderer = Utils.palettedRasterRendererFromCategories(layer.dataProvider(), 1, categories)
            layer.setRenderer(renderer)
            message, success = layer.saveDefaultStyle()
            if not success:
                raise QgsProcessingException(message)

            result = {self.P_OUTPUT_CATEGORIZED_RASTER: filename}
            self.toc(feedback, result)

        return result

    @classmethod
    def categoriesToField(
            cls, vector: QgsVectorLayer, fieldName: str, extent: QgsRectangle, crs: QgsCoordinateReferenceSystem,
            filename: str = None,
            feedback: QgsProcessingFeedback = None
    ) -> Tuple[QgsVectorLayer, List[str], List[HexColor]]:

        # make copy of layer (class attribute only)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(vector.renderer())
        values = [c.value for c in categories if c.name != '']
        names = [c.name for c in categories if c.name != '']
        colors = [c.color for c in categories if c.name != '']
        classFieldName = vector.renderer().classAttribute()
        fieldIndex = vector.fields().indexOf(classFieldName)
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        options.attributes = [fieldIndex]
        if vector.crs() != crs:
            options.ct = QgsCoordinateTransform(vector.crs(), crs, QgsProject().instance())
        options.filterExtent = extent
        transformContext = QgsProject().instance().transformContext()
        error, message = QgsVectorFileWriter.writeAsVectorFormatV2(vector, filename, transformContext, options)
        assert error == QgsVectorFileWriter.NoError, f'Fail error {error}:{message}'

        # calculate class ids [1..nCategories]
        vector2 = QgsVectorLayer(filename)
        fieldIndex = vector2.fields().indexOf(classFieldName)
        idOfValue = {value: id for id, value in enumerate(values, 1)}

        n = vector2.featureCount()
        with edit(vector2):
            vector2.addAttribute(QgsField(fieldName, QVariant.Int))
            vector2.updateFields()
            for i, feature in enumerate(vector2.getFeatures()):
                feedback.setProgress(i / n)
                feature.setAttribute(feature.fieldNameIndex(fieldName), idOfValue.get(str(feature[fieldIndex]), 0))
                vector2.updateFeature(feature)

        return vector2, names, colors
