from typing import Dict, Any, List, Tuple

from PyQt5.QtCore import QVariant
from qgis.core import edit
from processing.core.Processing import Processing
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRectangle,
                        QgsCoordinateReferenceSystem, QgsVectorFileWriter,
                        QgsProject, QgsField, QgsCoordinateTransform, QgsRasterLayer, QgsProcessingException)

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.typing import HexColor
from enmapboxprocessing.utils import Utils
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class RasterizeClassificationAlgorithm(EnMAPProcessingAlgorithm):
    P_VECTOR = 'vector'
    P_GRID = 'grid'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outraster'

    def displayName(self):
        return 'Rasterize Classification'

    def shortDescription(self):
        return 'Converts a categorized vector into a classification by evaluating renderer categories. ' \
               'Output class ids run from 1 to number of categories, in the order of the given categories. ' \
               'Class names and colors are given by the category legend and symbol color. ' \
               '\nRasterization is done by class majority voting at x10 oversampled resolution, using 100 classified ' \
               'subpixel to be accurate to the percent.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_VECTOR, self.helpParameterVectorClassification()),
            (self.P_GRID, self.helpParameterGrid()),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_VECTOR, 'Vector Classification')
        self.addParameterRasterLayer(self.P_GRID, 'Grid')
        self.addParameterCreationProfile(self.P_CREATION_PROFILE)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, 'Output Classification')

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterVectorClassification(parameters, self.P_VECTOR, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        vector = self.parameterAsVectorLayer(parameters, self.P_VECTOR, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        creationProfile = self.parameterAsInt(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        info = 'Derive class ids from renderer categories'
        feedback.pushInfo(info)

        # create vector layer with class id attribute (values from 1...n) matching the given categories
        fieldName = 'derived_id'
        tmpVectorFilename = Utils.tmpFilename(filename, 'categorized.gpkg')
        tmpVector, names, colors = self.categoriesToField(
            vector, fieldName, grid.extent(), grid.crs(), tmpVectorFilename, feedback
        )

        geometryType = vector.geometryType()
        if Utils.isPolygonGeometry(geometryType):
            resampleAlg = self.ModeResampleAlg  # use 10x oversampling
        else:
            resampleAlg = self.NearestNeighbourResampleAlg  # simple burn

        dataType = Utils.smallesUIntDataType(len(names))
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: grid,
            alg.P_VECTOR: tmpVector,
            alg.P_DATA_TYPE: self.O_DATA_TYPE.index(Utils.qgisDataTypeName(dataType)),
            alg.P_BURN_ATTRIBUTE: fieldName,
            alg.P_RESAMPLE_ALG: resampleAlg,
            alg.P_CREATION_PROFILE: creationProfile,
            alg.P_OUTPUT_RASTER: filename
        }
        Processing.runAlgorithm(alg, parameters, None, feedback, context)

        # setup renderer
        layer = QgsRasterLayer(filename)
        categories = [(value, label, color) for value, (label, color) in enumerate(zip(names, colors), 1)]
        renderer = Utils.palettedRasterRendererFromCategories(layer.dataProvider(), 1, categories)
        layer.setRenderer(renderer)
        message, success = layer.saveDefaultStyle()
        if not success:
            raise QgsProcessingException(message)

        return {self.P_OUTPUT_RASTER: filename}

    @classmethod
    def categoriesToField(
            cls, vector: QgsVectorLayer, fieldName: str, extent: QgsRectangle, crs: QgsCoordinateReferenceSystem,
            filename: str = None,
            feedback: QgsProcessingFeedback = None
    ) -> Tuple[QgsVectorLayer, List[str], List[HexColor]]:

        # make copy of layer (class attribute only)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(vector.renderer())
        values = [c[0] for c in categories if c[1] != '']
        names = [c[1] for c in categories if c[1] != '']
        colors = [c[2] for c in categories if c[1] != '']
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
