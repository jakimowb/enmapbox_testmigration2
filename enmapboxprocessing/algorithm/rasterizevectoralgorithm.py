from typing import Dict, Any, List, Tuple

from PyQt5.QtCore import QVariant
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsProcessingParameterField, Qgis,
                        QgsVectorFileWriter,
                        QgsProject, QgsCoordinateTransform, QgsField)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class RasterizeVectorAlgorithm(EnMAPProcessingAlgorithm):
    P_VECTOR, _VECTOR = 'vector', 'Vector layer'
    P_GRID, _GRID = 'grid', 'Grid'
    P_INIT_VALUE, _INIT_VALUE = 'initValue', 'Init value'
    P_BURN_VALUE, _BURN_VALUE = 'burnValue', 'Burn value'
    P_BURN_ATTRIBUTE, _BURN_ATTRIBUTE = 'burnAttribute', 'Burn attribute'
    P_BURN_FID, _BURN_FID = 'burnFid', 'Burn feature ID'
    P_RESAMPLE_ALG, _RESAMPLE_ALG = 'resampleAlg', 'Aggregation algorithm'
    P_ALL_TOUCHED, _ALL_TOUCHED = 'allTouched', 'All touched'
    P_ADD_VALUE, _ADD_VALUE = 'addValue', 'Add value'
    P_DATA_TYPE, _DATA_TYPE = 'dataType', 'Data type'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRasterizedVector', 'Output raster layer'

    def displayName(self):
        return 'Rasterize vector layer'

    def shortDescription(self):
        return 'Converts vector geometries (points, lines and polygons) into a raster grid.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._VECTOR, 'A vector layer to be rasterized.'),
            (self._GRID, 'The target grid.'),
            (self._INIT_VALUE, 'Pre-initialization value for the output raster layer.'),
            (self._BURN_VALUE, 'Fixed value to burn into each pixel, which is touched (point, line) '
                               'or where the center is covered (polygon) by a geometry.'),
            (self._BURN_ATTRIBUTE, 'Numeric vector field to use as burn values.'),
            (self._BURN_FID, 'Whether to use the feature ID as burn values. Initial value is set to -1. '
                             'Data type is set to Int32.'),
            (self._RESAMPLE_ALG,
             'If selected, burn at a x10 finer resolution and aggregate values back to target resolution. '
             'For example, use Mode aggregation for categorical attributes to burn the '
             'category with highest pixel coverage (i.e. majority voting). '
             'For continuous attributes use Average to calculate a weighted average.'),
            (self._ALL_TOUCHED, 'Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or '
                                'polygons will be updated, not just those on the line render path, or whose center '
                                'point is within the polygon.'),
            (self._ADD_VALUE, 'Whether to add up existing values instead of replacing them.'),
            (self._DATA_TYPE, 'Output data type.'),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_VECTOR, self._VECTOR)
        self.addParameterRasterLayer(self.P_GRID, self._GRID)
        self.addParameterFloat(self.P_INIT_VALUE, self._INIT_VALUE, defaultValue=0)
        self.addParameterFloat(self.P_BURN_VALUE, self._BURN_VALUE, defaultValue=1)
        self.addParameterField(
            self.P_BURN_ATTRIBUTE, self._BURN_ATTRIBUTE, type=QgsProcessingParameterField.Numeric,
            parentLayerParameterName=self.P_VECTOR, optional=True
        )
        self.addParameterBoolean(self.P_BURN_FID, self._BURN_FID, defaultValue=False)
        self.addParameterResampleAlg(self.P_RESAMPLE_ALG, self._RESAMPLE_ALG, optional=True)
        self.addParameterBoolean(self.P_ADD_VALUE, self._ADD_VALUE, defaultValue=False)
        self.addParameterBoolean(self.P_ALL_TOUCHED, self._ALL_TOUCHED, defaultValue=False)
        self.addParameterDataType(self.P_DATA_TYPE, self._DATA_TYPE, defaultValue=self.Float32)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        vector = self.parameterAsVectorLayer(parameters, self.P_VECTOR, context)
        dataType = self.parameterAsQgsDataType(parameters, self.P_DATA_TYPE, context, default=Qgis.Float32)
        initValue = self.parameterAsDouble(parameters, self.P_INIT_VALUE, context)
        burnValue = self.parameterAsDouble(parameters, self.P_BURN_VALUE, context)
        burnAttribute = self.parameterAsField(parameters, self.P_BURN_ATTRIBUTE, context)
        burnFid = self.parameterAsBoolean(parameters, self.P_BURN_FID, context)
        resampleAlg = self.parameterAsGdalResampleAlg(parameters, self.P_RESAMPLE_ALG, context)
        addValue = self.parameterAsBoolean(parameters, self.P_ADD_VALUE, context)
        allTouched = self.parameterAsBoolean(parameters, self.P_ALL_TOUCHED, context)
        format, options = self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        if resampleAlg == gdal.GRA_NearestNeighbour:
            oversampling = 1
        else:
            oversampling = 10
        noDataValue = None

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # create fid field if needed
            if burnFid:
                field = QgsField('temp_fid', QVariant.LongLong)
                vector.addExpressionField('$id', field)
                tmpFilename = Utils.tmpFilename(filename, 'fid.gpkg')
                saveVectorOptions = QgsVectorFileWriter.SaveVectorOptions()
                saveVectorOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
                saveVectorOptions.attributes = [vector.fields().indexFromName(field.name())]
                saveVectorOptions.feedback = feedback
                transformContext = QgsProject.instance().transformContext()
                error, message = QgsVectorFileWriter.writeAsVectorFormatV2(
                    vector, tmpFilename, transformContext, saveVectorOptions
                )
                assert error == QgsVectorFileWriter.NoError, f'Fail error {error}:{message}'
                vector = QgsVectorLayer(tmpFilename)
                burnAttribute = field.name()
                initValue = -1
                dataType = Qgis.Int32

            # reproject if needed
            sourceFilename, layerName = Utils.splitQgsVectorLayerSourceString(vector.source())
            if vector.crs() != grid.crs():
                feedback.pushInfo('Reproject source vector layer to target crs')
                tmpFilename = Utils.tmpFilename(filename, 'reprojected.gpkg')
                transformContext = QgsProject.instance().transformContext()
                coordinateTransform = QgsCoordinateTransform(vector.crs(), grid.crs(), QgsProject.instance())
                saveVectorOptions = QgsVectorFileWriter.SaveVectorOptions()
                saveVectorOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
                saveVectorOptions.ct = coordinateTransform
                saveVectorOptions.filterExtent = grid.extent()
                if burnAttribute is None:
                    saveVectorOptions.skipAttributeCreation = True
                if layerName is not None:
                    saveVectorOptions.layerName = layerName
                saveVectorOptions.feedback = feedback
                error, message = QgsVectorFileWriter.writeAsVectorFormatV2(
                    vector, tmpFilename, transformContext, saveVectorOptions
                )
                assert error == QgsVectorFileWriter.NoError, f'Fail error {error}:{message}'
                vector = QgsVectorLayer(tmpFilename)

            # oversampled burn
            info = f'Burn vector geometries'
            feedback.pushInfo(info)
            # - init raster
            tmpFilename = Utils.tmpFilename(filename, 'oversampled.tif')
            tmpFormat = self.GTiffFormat
            tmpCreationOptions = self.TiledAndCompressedGTiffCreationOptions
            tmpWidth = int(round(grid.width() * oversampling))
            tmpHeight = int(round(grid.height() * oversampling))
            tmpDriver = Driver(tmpFilename, tmpFormat, tmpCreationOptions, feedback2)
            tmpWriter = tmpDriver.create(Qgis.Float32, tmpWidth, tmpHeight, 1, grid.extent(), grid.crs())
            tmpWriter.fill(initValue)
            tmpWriter.setNoDataValue(noDataValue)
            # - prepare rasterize options and rasterize
            callback = Utils.qgisFeedbackToGdalCallback(feedback2)
            if burnAttribute is None:
                burnValues = [burnValue]
            else:
                burnValues = None
            if callback is None:
                callback = gdal.TermProgress_nocb
            kwds = dict(burnValues=burnValues, attribute=burnAttribute, allTouched=allTouched, add=addValue)
            kwds = {k: v for k, v in kwds.items() if v is not None}
            rasterizeOptions = gdal.RasterizeOptions(callback=callback, **kwds)
            success = gdal.Rasterize(
                destNameOrDestDS=tmpWriter.gdalDataset, srcDS=vector.source(), options=rasterizeOptions
            )
            assert success == 1
            del tmpWriter

            # for aggregation we use Warp instead of Translate, because it supports more ResamplAlgs!
            resampleAlgString = Utils.gdalResampleAlgToGdalWarpFormat(
                resampleAlg)  # use string to avoid a bug in gdalwarp
            gdalDataType = Utils.qgisDataTypeToGdalDataType(dataType)
            warpOptions = gdal.WarpOptions(
                width=grid.width(), height=grid.height(), resampleAlg=resampleAlgString, outputType=gdalDataType,
                format=format, creationOptions=options, callback=callback, multithread=True
            )
            gdal.Warp(destNameOrDestDS=filename, srcDSOrSrcDSTab=tmpFilename, options=warpOptions)

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)
        return result
