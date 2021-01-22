from enum import Enum, IntEnum
from time import time
from typing import Dict, Any, List, Tuple

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from osgeo import gdal

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.typing import CreationOptions
from enmapboxprocessing.utils import Utils
from python.core.additions.edit import edit
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRectangle,
                        QgsCoordinateReferenceSystem, QgsVectorFileWriter,
                        QgsProject, QgsField, QgsCoordinateTransform)

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
               'Class ids run from 1 to number of categories, in the order of the given categories. ' \
               'Class names and colors are given by the category legend and symbol color. ' \
               'Rasterization is done by an Oversampling Majority Voting approach, ' \
               'that burns classes at x10 finer resolution, ' \
               'resulting in 100 classified subpixel used for the final majority vote.'

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
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterVectorClassification(parameters, self.P_VECTOR, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        vector = self.parameterAsVectorLayer(parameters, self.P_VECTOR, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        oversampling = 10
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        width = grid.width()
        height = grid.height()

        self.processQgis(
            vector, grid.extent(), width, height, grid.crs(), oversampling, filename, format, options, feedback
        )
        return {self.P_OUTPUT_RASTER: filename}

    @classmethod
    def processQgis(
            cls, vector: QgsVectorLayer, extent: QgsRectangle, width: int, height: int,
            crs: QgsCoordinateReferenceSystem, oversampling: int, filename: str = None, format: str = None,
            options: CreationOptions = None, feedback: QgsProcessingFeedback = None
    ) -> RasterWriter:

        info = 'Derive class ids from renderer categories'
        feedback.pushInfo(info)

        # create vector layer with class id attribute (values from 1...n) matching the given categories
        fieldName = 'derived_id'
        tmpFilename = Utils.tmpFilename(filename, 'categorized.gpkg')
        tmpVector, names, colors = cls.categoriesToField(vector, fieldName, extent, crs, tmpFilename, feedback)

        # rasterize class ids
        dataType = Utils.smallesUIntDataType(len(names))
        writer = RasterizeVectorAlgorithm.processQgis(
            tmpVector, extent, width, height, dataType, crs, oversampling, resampleAlg=gdal.GRA_Mode,
            burnAttribute=fieldName, filename=filename, format=format, options=options, feedback=feedback
        )
        writer.setCategoryNames(['unclassified'] + names)
        writer.setCategoryColors([QColor('#000')] + colors)

        # clean up
        gdal.Unlink(tmpFilename)
        return writer

    @classmethod
    def categoriesToField(
            cls, vector: QgsVectorLayer, fieldName: str, extent: QgsRectangle, crs: QgsCoordinateReferenceSystem,
            filename: str = None,
            feedback: QgsProcessingFeedback = None
    ) -> Tuple[QgsVectorLayer, List[str], List[QColor]]:

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
            options.ct = QgsCoordinateTransform(vector.crs(), crs, QgsProject.instance())
        options.filterExtent = extent
        transformContext = QgsProject.instance().transformContext()
        error, message = QgsVectorFileWriter.writeAsVectorFormatV2(vector, filename, transformContext, options)
        assert error == QgsVectorFileWriter.NoError, f'Fail error {error}:{message}'

        # calculate class ids [1..nCategories]
        vector2 = QgsVectorLayer(filename)
        fieldIndex = vector2.fields().indexOf(classFieldName)

        def idOfValue(value):
            for id, v in enumerate(values, 1):
                if v == value:
                    return id
            return 0

        n = vector2.featureCount()
        with edit(vector2):
            vector2.addAttribute(QgsField(fieldName, QVariant.Int))
            vector2.updateFields()
            for i, feature in enumerate(vector2.getFeatures()):
                feedback.setProgress(i / n)
                feature.setAttribute(feature.fieldNameIndex(fieldName), idOfValue(feature[fieldIndex]))
                vector2.updateFeature(feature)

        return vector2, names, colors
