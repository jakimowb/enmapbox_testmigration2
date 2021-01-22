from os.path import splitext, basename
from typing import Dict, Any, List, Tuple

from osgeo import gdal

from enmapboxprocessing.rasterwriter import RasterWriter
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRectangle, QgsRasterLayer, Qgis,
                        QgsRasterDataProvider, QgsPoint, QgsPointXY, QgsCoordinateReferenceSystem)

from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import QgisDataType, CreationOptions, GdalResamplingAlgorithm, GdalDataType
from enmapboxprocessing.utils import Utils
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group, AlgorithmCanceledException


@typechecked
class TranslateRasterAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_BAND_LIST = 'bandList'
    P_GRID = 'grid'
    P_EXTENT = 'extent'
    P_SOURCE_WINDOW = 'sourceWindow'
    P_EXCLUDE_BAD_BANDS = 'excludeBadBands'
    P_RESAMPLE_ALG = 'resampleAlg'
    P_DATA_TYPE = 'dataType'
    P_COPY_METADATA = 'copyMetadata'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outraster'

    def displayName(self):
        return 'Translate/Warp Raster'

    def shortDescription(self):
        return 'Convert raster data between different formats, ' \
               'potentially performing some operations like spatial subsetting, spatial resampling, reprojection, ' \
               'band subsettings, band reordering and data type conversion.'

    def helpHeader(self) -> Tuple[str, str]:
        return (
            'Source No Data Value Handling',
            'The used source no data value can be modified by properly setting up the "No Data Value" section in '
            'the "Transparency" tab inside the "Layer Styling" panel. Use one of the following options:'
            '\n1. Check "No data value" to use the source no data value.'
            '\n2. Uncheck "No data value" to not use the source no data value.'
            '\n3. Uncheck "No data value" and set an "Additional no data value" to overwrite the source no data value.'
        )

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, self.helpParameterRaster()),
            (self.P_BAND_LIST, 'Bands to subset and rearrange. '
                               'Note that an empty selection (default) will select all bands in native order.'),
            (self.P_GRID, self.helpParameterGrid()),
            (self.P_EXTENT, 'Spatial extent for clipping the destination grid, '
                            'which is given by the source Raster or the selected Grid. '
                            'In both cases, the extent is aligned with the actual pixel grid '
                            'to avoid subpixel shifts.'),
            (self.P_SOURCE_WINDOW, 'Subwindow in pixels to extract: left_x, top_y, width, height'),
            (self.P_EXCLUDE_BAD_BANDS, 'Wether to exclude bad bands (given by BBL metadata item inside ENVI domain). '
                                       'Also see The ENVI Header Format for more details: '
                                       'https://www.l3harrisgeospatial.com/docs/ENVIHeaderFiles.html '),
            (self.P_COPY_METADATA, 'Wether to copy metadata from source to destination. '),
            (self.P_RESAMPLE_ALG, 'Spatial resample algorithm.'),
            (self.P_OVERSAMPLING, self.helpParameterOversampling()),
            (self.P_DATA_TYPE, self.helpParameterDataType()),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterSourceWindow(parameters, context)

    def parameterAsSourceWindow(
            self, parameters: Dict[str, Any], context: QgsProcessingContext
    ) -> List[int]:
        string = self.parameterAsString(parameters, self.P_SOURCE_WINDOW, context)
        if string in ['', 'Not set']:
            string = '0, 0, 0, 0'
        return [int(v) for v in string.split(',')]

    def parameterAsSourceWindowExtent(
            self, parameters: Dict[str, Any], context: QgsProcessingContext
    ) -> QgsRectangle:
        left_x, top_y, width, height = self.parameterAsSourceWindow(parameters, context)
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        provider: QgsRasterDataProvider = raster.dataProvider()
        ul: QgsPoint = provider.transformCoordinates(
            QgsPoint(left_x, top_y), QgsRasterDataProvider.TransformImageToLayer
        )
        lr: QgsPoint = provider.transformCoordinates(
            QgsPoint(left_x + width, top_y + height), QgsRasterDataProvider.TransformImageToLayer
        )
        return QgsRectangle(QgsPointXY(ul), QgsPointXY(lr))

    def checkParameterSourceWindow(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            values = self.parameterAsSourceWindow(parameters, context)
            assert len(values) == 4
        except:
            return False, f'Invalid source window ({self.parameterDefinition(self.P_SOURCE_WINDOW).description()})'
        return True, ''

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster')
        self.addParameterBandList(
            self.P_BAND_LIST, 'Selected Bands', parentLayerParameterName=self.P_RASTER, optional=True
        )
        self.addParameterRasterLayer(self.P_GRID, 'Grid', optional=True)
        self.addParameterBoolean(self.P_COPY_METADATA, 'Copy Metadata', defaultValue=False)
        self.addParameterExtent(self.P_EXTENT, 'Spatial Extent', optional=True, advanced=True)
        self.addParameterString(
            self.P_SOURCE_WINDOW, 'Source Window', defaultValue='Not set', optional=True, advanced=True
        )
        self.addParameterBoolean(self.P_EXCLUDE_BAD_BANDS, 'Exclude Bad Bands', defaultValue=False, advanced=True)
        self.addParameterResampleAlg(self.P_RESAMPLE_ALG, advanced=True)
        self.addParameterDataType(self.P_DATA_TYPE, defaultValue=-1, optional=True, advanced=True)
        self.addParameterCreationProfile(self.P_CREATION_PROFILE, allowVrt=True, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        bandList = self.parameterAsInts(parameters, self.P_BAND_LIST, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        if grid is None:
            grid = raster
        extent = self.parameterAsExtent(parameters, self.P_EXTENT, context, crs=grid.crs())
        if not extent.isEmpty():
            extent = Utils.snapExtentToRaster(extent, grid)
        sourceWindowExtent = self.parameterAsSourceWindowExtent(parameters, context)
        if not sourceWindowExtent.isEmpty():
            extent = sourceWindowExtent
            grid = raster  # even if grid is specified, use the source raster
        if extent.isEmpty():
            extent = grid.extent()
        excludeBadBands = self.parameterAsBoolean(parameters, self.P_EXCLUDE_BAD_BANDS, context)
        resampleAlg = self.parameterAsGdalResampleAlg(parameters, self.P_RESAMPLE_ALG, context)
        dataType = self.parameterAsQgsDataType(parameters, self.P_DATA_TYPE, context)
        copyMetadata = self.parameterAsBoolean(parameters, self.P_COPY_METADATA, context)
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        width = int(round(extent.width() / grid.rasterUnitsPerPixelX()))
        height = int(round(extent.height() / grid.rasterUnitsPerPixelY()))

        self.processQgis(
            filename, raster, extent, width, height, grid.crs(), resampleAlg, bandList, excludeBadBands, dataType,
            copyMetadata, format, options, feedback
        )
        return {self.P_OUTPUT_RASTER: filename}

    @classmethod
    def processQgis(
            cls, filename: str, raster: QgsRasterLayer, extent: QgsRectangle, width: int, height: int,
            crs: QgsCoordinateReferenceSystem = None, resampleAlg: GdalResamplingAlgorithm = None,
            bandList: List[int] = None, excludeBadBands=False, dataType: QgisDataType = None,
            copyMetadata=False, format: str = None, options: CreationOptions = None,
            feedback=QgsProcessingFeedback(), **kwargs
    ) -> RasterWriter:
        reader = RasterReader(raster)
        if crs is not None:
            assert crs.isValid()
        if resampleAlg is None:
            resampleAlg = gdal.GRA_NearestNeighbour
        if dataType in [None, Qgis.UnknownDataType]:
            dataType = reader.dataType()
        gdalDataType = Utils.qgisDataTypeToGdalDataType(dataType)
        if excludeBadBands and reader.metadataItem('bbl', 'ENVI') is not None:
            bbl = [bool(v) for v in reader.metadataItem('bbl', 'ENVI')]
            if bandList is None:
                bandList = [bandNo for bandNo, isGoodBand in enumerate(bbl, 1) if isGoodBand]
            else:
                bandList = [bandNo for bandNo, isGoodBand in enumerate(bbl, 1) if isGoodBand and bandNo in bandList]
        if bandList is None:
            nBands = raster.bandCount()
        else:
            nBands = len(bandList)
        if reader.sourceHasNoDataValue() and reader.useSourceNoDataValue():
            noDataValue = None  # use default no data value
        else:
            rasterRanges = reader.userNoDataValues()
            if len(rasterRanges) == 1:
                noDataValue = rasterRanges[0].min()  # use user no data value
            else:
                noDataValue = 'none'  # unset no data value

        infoTail = f' [{width}x{height}x{nBands}]({Utils.qgisDataTypeName(dataType)})'
        if format is not None:
            infoTail += f' -of {format}'
        if options is not None:
            infoTail += f' -co {" ".join(options)}'
        infoTail += f' {filename}'

        gdalDataset = gdal.Open(raster.source())
        assert gdalDataset is not None

        callback = Utils.qgisFeedbackToGdalCallback(feedback)
        resampleAlgSupportedByGdalTranslate = resampleAlg not in [gdal.GRA_Min, gdal.GRA_Q1, gdal.GRA_Med,
                                                                  gdal.GRA_Q3, gdal.GRA_Max]
        if raster.crs() == crs and resampleAlgSupportedByGdalTranslate:
            feedback.pushInfo('Translate Raster' + infoTail)
            projWin = (extent.xMinimum(), extent.yMaximum(), extent.xMaximum(), extent.yMinimum())
            translateOptions = gdal.TranslateOptions(
                format=format, width=width, height=height, creationOptions=options, resampleAlg=resampleAlg,
                projWin=projWin, bandList=bandList, outputType=gdalDataType, callback=callback, noData=noDataValue
            )
            outGdalDataset: gdal.Dataset = gdal.Translate(
                destName=filename, srcDS=gdalDataset, options=translateOptions
            )
            assert outGdalDataset is not None

            # need to explicitely set the GeoTransform tuple, because gdal.Translate extent may deviate slightly
            ulx, uly, lrx, lry = projWin
            xres = (lrx - ulx) / width
            yres = (uly - lry) / height
            geoTransform = (ulx, xres, 0., uly, 0., -yres)
            outGdalDataset.SetGeoTransform(geoTransform)
            tmpFilename = ''
        else:
            if bandList is not None:
                tmpFilename = Utils.tmpFilename(filename, 'bandSubset.vrt')
                tmpGdalDataset = gdal.Translate(
                    destName=tmpFilename, srcDS=gdalDataset, format=cls.VrtFormat, bandList=bandList,
                    noData=noDataValue, callback=callback
                )
            else:
                tmpGdalDataset = gdalDataset
                tmpFilename = ''

            feedback.pushInfo('Warp Raster' + infoTail)
            outputBounds = (extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum())
            dstSRS = crs.toWkt()
            resampleAlgString = Utils.gdalResampleAlgToGdalWarpFormat(resampleAlg)
            warpOptions = gdal.WarpOptions(
                format=format, width=width, height=height, creationOptions=options, resampleAlg=resampleAlgString,
                outputBounds=outputBounds, outputType=gdalDataType, dstSRS=dstSRS, srcNodata=noDataValue,
                callback=callback
            )
            outGdalDataset: gdal.Dataset = gdal.Warp(
                filename, tmpGdalDataset, options=warpOptions
            )
            assert outGdalDataset is not None

        writer = RasterWriter(outGdalDataset)
        if copyMetadata:
            cls.copyMetadata(raster, writer, bandList)

        if format != cls.VrtFormat:
            for f in [tmpFilename]:
                if basename(f).startswith('.tmp'):
                    gdal.Unlink(f)

        return writer

    @classmethod
    def copyMetadata(cls, raster: QgsRasterLayer, writer: RasterWriter, bandList: List[int] = None):
        reader = RasterReader(raster)
        if bandList is None:
            bandList = list(range(1, reader.bandCount() + 1))
        # fix ENVI domain
        enviMetadata = Utils.subsetEnviDomainBandwiseMetadata(
            reader.metadataDomain('ENVI'),
            RasterReader(writer.gdalDataset).metadataDomain('ENVI'),
            bandList
        )
        writer.setMetadataDomain(enviMetadata, 'ENVI')
        writer.setMetadataDomain({}, '')
        # fix default domain
        defaultMetadata = reader.metadataDomain('')
        writer.setMetadataDomain({}, '')
        for key, value in defaultMetadata.items():
            if not key.startswith('Band'):
                writer.setMetadataItem(key, value)
        # band metadata
        for i, bandNo in enumerate(bandList):
            writer.setMetadata(reader.metadata(bandNo), i + 1)
        # this needs to come last, otherwise GDAL will mess up the 'Band_*' items!
        for i, bandNo in enumerate(bandList):
            writer.setMetadataItem(f'Band_{i + 1}', defaultMetadata.get(f'Band_{bandNo}'))
