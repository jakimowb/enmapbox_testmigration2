from enum import Enum, IntEnum
from math import inf
from os.path import splitext, join, dirname, basename
from typing import Dict, Any, List, Tuple, Callable

from osgeo import ogr, gdal

from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.typing import QgisDataType, CreationOptions, GdalResamplingAlgorithm
from enmapboxprocessing.utils import Utils
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRectangle,
                        QgsCoordinateReferenceSystem, QgsProcessingParameterField, Qgis, QgsVectorFileWriter,
                        QgsProject, QgsFeature, QgsFields, QgsField, QgsCoordinateTransform, QgsRasterLayer,
                        QgsProcessingException)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class RasterizeVectorAlgorithm(EnMAPProcessingAlgorithm):
    P_VECTOR = 'vector'
    P_GRID = 'grid'
    P_INIT_VALUE = 'initValue'
    P_BURN_VALUE = 'burnValue'
    P_BURN_ATTRIBUTE = 'burnAttribute'
    P_RESAMPLE_ALG = 'resampleAlg'
    P_ALL_TOUCHED = 'allTouched'
    P_ADD_VALUE = 'addValue'
    P_DATA_TYPE = 'dataType'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outraster'

    def displayName(self):
        return 'Rasterize Vector'

    def shortDescription(self):
        return 'Converts vector geometries (points, lines and polygons) into a raster grid.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_VECTOR, self.helpParameterVector()),
            (self.P_GRID, self.helpParameterGrid()),
            (self.P_INIT_VALUE, 'Pre-initialization value for the output raster.'),
            (self.P_BURN_VALUE, 'Fixed value to burn into each pixel, which is touched (point, line) '
                                'or where the center is covered (polygon) by a feature.'),
            (self.P_BURN_ATTRIBUTE, 'Numeric vector field to use as burn values.'),
            (self.P_RESAMPLE_ALG,
             'If selected, burn at a x10 finer resolution and aggregate values back to target resolution. '
             'For categorical attributes use <i>Mode</i> aggregation to burn the '
             'category with highest pixel coverage (i.e. majority voting). '
             'For continuous attributes use <i>Average</i> to calculate a weighted average.'),
            (self.P_ALL_TOUCHED, 'Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or '
                                 'polygons will be updated, not just those on the line render path, or whose center '
                                 'point is within the polygon.'),
            (self.P_ADD_VALUE,
             'Wether to add up existing values instead of replacing them. new values to the existing REPLACE results in overwriting of value, '
             'while ADD adds the new value to the existing raster, '
             'suitable for heatmaps for instance.'),
            (self.P_DATA_TYPE, self.helpParameterDataType()),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_VECTOR, 'Vector')
        self.addParameterRasterLayer(self.P_GRID, 'Grid')
        self.addParameterFloat(self.P_INIT_VALUE, 'Init Value', defaultValue=0)
        self.addParameterFloat(self.P_BURN_VALUE, 'Burn Value', defaultValue=1)
        self.addParameterField(
            self.P_BURN_ATTRIBUTE, 'Burn Attribute', type=QgsProcessingParameterField.Numeric,
            parentLayerParameterName=self.P_VECTOR, optional=True
        )
        self.addParameterResampleAlg(self.P_RESAMPLE_ALG, 'Aggregation Algorithm', optional=True)
        self.addParameterBoolean(self.P_ADD_VALUE, 'Add Value', defaultValue=False)
        self.addParameterBoolean(self.P_ALL_TOUCHED, 'All touched', defaultValue=False)
        self.addParameterDataType(self.P_DATA_TYPE, defaultValue=self.Float32)
        self.addParameterCreationProfile(self.P_CREATION_PROFILE)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        vector = self.parameterAsVectorLayer(parameters, self.P_VECTOR, context)
        dataType = self.parameterAsQgsDataType(parameters, self.P_DATA_TYPE, context)
        initValue = self.parameterAsDouble(parameters, self.P_INIT_VALUE, context)
        burnValue = self.parameterAsDouble(parameters, self.P_BURN_VALUE, context)
        burnAttribute = self.parameterAsField(parameters, self.P_BURN_ATTRIBUTE, context)
        resampleAlg = self.parameterAsGdalResampleAlg(parameters, self.P_RESAMPLE_ALG, context)
        addValue = self.parameterAsBoolean(parameters, self.P_ADD_VALUE, context)
        allTouched = self.parameterAsBoolean(parameters, self.P_ALL_TOUCHED, context)
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        if resampleAlg == gdal.GRA_NearestNeighbour:
            oversampling = 1
        else:
            oversampling = 10
        noDataValue = None
        self.processQgis(
            vector, grid.extent(), grid.width(), grid.height(), dataType, grid.crs(), oversampling, resampleAlg,
            initValue, burnValue, burnAttribute, addValue, allTouched, noDataValue, filename, format, options, feedback
        )
        return {self.P_OUTPUT_RASTER: filename}

    @classmethod
    def processQgis(
            cls, vector: QgsVectorLayer, extent: QgsRectangle, width: int, height: int, dataType: QgisDataType,
            crs: QgsCoordinateReferenceSystem, oversampling: int = None, resampleAlg: GdalResamplingAlgorithm = None,
            initValue: float = 0., burnValue: float = 1., burnAttribute: str = None,
            addValue: bool = None, allTouched=False, noDataValue: float = None, filename: str = None,
            format: str = None,
            options: CreationOptions = None, feedback: QgsProcessingFeedback = None
    ) -> RasterWriter:
        if oversampling is None:
            oversampling = 1
        sourceFilename, layerName = Utils.splitQgsVectorLayerSourceString(vector.source())
        if vector.crs() != crs:
            feedback.pushInfo('Reproject source vector to target crs')
            tmpVectorFilename = Utils.tmpFilename(filename, 'reprojected.gpkg')
            transformContext = QgsProject.instance().transformContext()
            coordinateTransform = QgsCoordinateTransform(vector.crs(), crs, QgsProject.instance())
            saveVectorOptions = QgsVectorFileWriter.SaveVectorOptions()
            saveVectorOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
            saveVectorOptions.ct = coordinateTransform
            saveVectorOptions.filterExtent = extent
            if layerName is not None:
                saveVectorOptions.layerName = layerName
            saveVectorOptions.feedback = feedback
            error, message = QgsVectorFileWriter.writeAsVectorFormatV2(
                vector, tmpVectorFilename, transformContext, saveVectorOptions
            )
            assert error == QgsVectorFileWriter.NoError, f'Fail error {error}:{message}'
        else:
            tmpVectorFilename = sourceFilename

        info = f'Burn geometries with {burnValue if burnAttribute is None else f"{repr(burnAttribute)} field"}'
        feedback.pushInfo(info)

        # oversampled burn
        tmpFilename = Utils.tmpFilename(filename, 'oversampled.tif')
        tmpFormat = cls.GTiffFormat
        tmpCreationOptions = cls.TiledAndCompressedGTiffCreationOptions
        tmpWidth = int(round(width * oversampling))
        tmpHeight = int(round(height * oversampling))
        tmpDriver = Driver(tmpFilename, tmpFormat, tmpCreationOptions, feedback)
        tmpWriter = tmpDriver.create(Qgis.Float32, tmpWidth, tmpHeight, 1, extent, crs)
        tmpWriter.fill(initValue)
        tmpWriter.setNoDataValue(noDataValue)
        callback = Utils.qgisFeedbackToGdalCallback(feedback)
        cls.gdalRasterize(
            tmpWriter.gdalDataset, tmpVectorFilename, burnValue, burnAttribute, allTouched, add=addValue,
            callback=callback
        )
        del tmpWriter

        # for aggregation we use Warp instead of Translate, because it supports more ResamplAlgs!
        resampleAlgString = Utils.gdalResampleAlgToGdalWarpFormat(resampleAlg)  # use string to avoid a bug in gdalwarp
        gdalDataType = Utils.qgisDataTypeToGdalDataType(dataType)
        warpOptions = gdal.WarpOptions(
            width=width, height=height, resampleAlg=resampleAlgString, outputType=gdalDataType,
            format=format, creationOptions=options, callback=callback, multithread=True
        )
        outGdalDataset = gdal.Warp(
            destNameOrDestDS=filename, srcDSOrSrcDSTab=tmpFilename, options=warpOptions
        )
        writer = RasterWriter(outGdalDataset)

        for f in [tmpFilename, tmpVectorFilename]:
            if basename(f).startswith('.tmp'):
                gdal.Unlink(f)

        return writer

    @classmethod
    def gdalRasterize(
            cls, gdalDataset: gdal.Dataset, sourceFilename: str, burnValue: float = 1., burnAttribute: str = None,
            allTouched: bool = None, useZ: bool = None, SQLStatement: str = None, SQLDialect: str = None,
            where: str = None, optim: str = None, add=None,
            callback=None
    ):
        if burnAttribute is None:
            burnValues = [burnValue]
        else:
            burnValues = None
        if callback is None:
            callback = gdal.TermProgress_nocb
        kwds = dict(
            burnValues=burnValues, attribute=burnAttribute, allTouched=allTouched, useZ=useZ,
            SQLStatement=SQLStatement, SQLDialect=SQLDialect, where=where, optim=optim, add=add
        )
        kwds = {k: v for k, v in kwds.items() if v is not None}
        options = gdal.RasterizeOptions(callback=callback, **kwds)
        success = gdal.Rasterize(destNameOrDestDS=gdalDataset, srcDS=sourceFilename, options=options)
        assert success == 1
