from math import isnan
from typing import Dict, Any, List, Tuple

from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRectangle, QgsRasterLayer,
                        QgsRasterDataProvider, QgsPoint, QgsPointXY)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class TranslateRasterAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_BAND_LIST, _BAND_LIST = 'bandList', 'Selected bands'
    P_GRID, _GRID = 'grid', 'Grid'
    P_COPY_METADATA, _COPY_METADATA = 'copyMetadata', 'Copy metadata'
    P_COPY_STYLE, _COPY_STYLE = 'copyStyle', 'Copy style'
    P_EXTENT, _EXTENT = 'extent', 'Spatial extent'
    P_SOURCE_COLUMNS, _SOURCE_COLUMNS = 'sourceColumns', 'Column subset'
    P_SOURCE_ROWS, _SOURCE_ROWS = 'sourceRows', 'Row subset'
    P_EXCLUDE_BAD_BANDS, _EXCLUDE_BAD_BANDS = 'excludeBadBands', 'Exclude bad bands'
    P_RESAMPLE_ALG, _RESAMPLE_ALG = 'resampleAlg', 'Resample algorithm'
    P_DATA_TYPE, _DATA_TYPE = 'dataType', 'Data type'
    P_CREATION_PROFILE, _CREATION_PROFILE = 'creationProfile', 'Output options'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputTranslatedRaster', 'Output raster layer'

    def displayName(self):
        return 'Translate raster layer'

    def shortDescription(self):
        return 'Convert raster data between different formats, ' \
               'potentially performing some operations like spatial subsetting, spatial resampling, reprojection, ' \
               'band subsettings, band reordering and data type conversion.'

    def helpHeader(self) -> Tuple[str, str]:
        return (
            'Source no data value handling',
            'The used source no data value can be modified by properly setting up the "No Data Value" section in '
            'the "Transparency" tab inside the "Layer Styling" panel. Use one of the following options:'
            '\n1. Check "No data value" to use the source no data value.'
            '\n2. Uncheck "No data value" to not use the source no data value.'
            '\n3. Uncheck "No data value" and set an "Additional no data value" to overwrite the source no data value.'
        )

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, 'Source raster layer.'),
            (self._BAND_LIST, 'Bands to subset and rearrange. '
                              'An empty selection defaults to all bands in native order.'),
            (self._GRID, 'The target grid.'),
            (self._EXTENT, 'Spatial extent for clipping the destination grid, '
                           'which is given by the source Raster or the selected Grid. '
                           'In both cases, the extent is aligned with the actual pixel grid '
                           'to avoid subpixel shifts.'),
            (self._SOURCE_COLUMNS, 'Column subset range in pixels to extract.'),
            (self._SOURCE_ROWS, 'Rows subset range in pixels to extract.'),
            (self._EXCLUDE_BAD_BANDS, 'Whether to exclude bad bands (given by BBL metadata item inside ENVI domain). '
                                      'Also see The ENVI Header Format for more details: '
                                      'https://www.l3harrisgeospatial.com/docs/ENVIHeaderFiles.html '),
            (self._COPY_METADATA, 'Whether to copy metadata from source to destination. '
                                  'Special care is taken of ENVI list items containing band information. '
                                  'The following list items will be properly subsetted according to the selected '
                                  'bands: band names, bbl, data_gain_values, data_offset_values, '
                                  'data_reflectance_gain_values, data_reflectance_offset_values, fwhm, '
                                  'wavelength.'),
            (self._COPY_STYLE, 'Whether to copy style from source to destination.'),
            (self._RESAMPLE_ALG, 'Spatial resample algorithm.'),
            (self._DATA_TYPE, 'Output data type.'),
            (self._CREATION_PROFILE, 'Output format and creation options.'),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return True, ''

    def parameterAsSourceWindowExtent(
            self, parameters: Dict[str, Any], context: QgsProcessingContext
    ) -> QgsRectangle:

        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        provider: QgsRasterDataProvider = raster.dataProvider()

        xmin, xmax = self.parameterAsRange(parameters, self.P_SOURCE_COLUMNS, context)
        ymin, ymax = self.parameterAsRange(parameters, self.P_SOURCE_ROWS, context)
        skipRangeX = isnan(xmin) and isnan(xmax)
        skipRangeY = isnan(ymin) and isnan(ymax)
        if skipRangeX and skipRangeY:
            return QgsRectangle()

        if isnan(xmin):
            xmin = 0
        if isnan(ymin):
            ymin = 0
        if isnan(xmax):
            xmax = xmin + raster.width() - 1
        if isnan(ymax):
            ymax = ymin + raster.height() - 1
        p1: QgsPoint = provider.transformCoordinates(QgsPoint(xmin, ymin), QgsRasterDataProvider.TransformImageToLayer)
        p2: QgsPoint = provider.transformCoordinates(
            QgsPoint(xmax + 1, ymax + 1), QgsRasterDataProvider.TransformImageToLayer
        )
        return QgsRectangle(QgsPointXY(p1), QgsPointXY(p2))

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterBandList(
            self.P_BAND_LIST, self._BAND_LIST, parentLayerParameterName=self.P_RASTER, optional=True
        )
        self.addParameterRasterLayer(self.P_GRID, self._GRID, optional=True)
        self.addParameterBoolean(self.P_COPY_METADATA, self._COPY_METADATA, defaultValue=False)
        self.addParameterBoolean(self.P_COPY_STYLE, self._COPY_STYLE, defaultValue=False)
        self.addParameterExtent(self.P_EXTENT, self._EXTENT, optional=True, advanced=True)
        self.addParameterIntRange(self.P_SOURCE_COLUMNS, self._SOURCE_COLUMNS, optional=True, advanced=True)
        self.addParameterIntRange(self.P_SOURCE_ROWS, self._SOURCE_ROWS, optional=True, advanced=True)
        self.addParameterBoolean(self.P_EXCLUDE_BAD_BANDS, self._EXCLUDE_BAD_BANDS, defaultValue=False, advanced=True)
        self.addParameterResampleAlg(self.P_RESAMPLE_ALG, self._RESAMPLE_ALG, advanced=True)
        self.addParameterDataType(self.P_DATA_TYPE, self._DATA_TYPE, optional=True, advanced=True)
        self.addParameterCreationProfile(self.P_CREATION_PROFILE, self._CREATION_PROFILE, allowVrt=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        provider: QgsRasterDataProvider = raster.dataProvider()
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
        dataType = self.parameterAsQgsDataType(parameters, self.P_DATA_TYPE, context, default=provider.dataType(1))
        copyMetadata = self.parameterAsBoolean(parameters, self.P_COPY_METADATA, context)
        copyStyle = self.parameterAsBoolean(parameters, self.P_COPY_STYLE, context)
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        width = int(round(extent.width() / grid.rasterUnitsPerPixelX()))
        height = int(round(extent.height() / grid.rasterUnitsPerPixelY()))
        crs = grid.crs()

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            reader = RasterReader(raster)
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
                feedback.pushInfo('Translate raster' + infoTail)
                projWin = (extent.xMinimum(), extent.yMaximum(), extent.xMaximum(), extent.yMinimum())
                translateOptions = gdal.TranslateOptions(
                    format=format, width=width, height=height, creationOptions=options, resampleAlg=resampleAlg,
                    projWin=projWin, bandList=bandList, outputType=gdalDataType, callback=callback, noData=noDataValue
                )
                try:
                    outGdalDataset: gdal.Dataset = gdal.Translate(
                        destName=filename, srcDS=gdalDataset, options=translateOptions
                    )
                except:
                    a=1
                assert outGdalDataset is not None

                # need to explicitely set the GeoTransform tuple, because gdal.Translate extent may deviate slightly
                ulx, uly, lrx, lry = projWin
                xres = (lrx - ulx) / width
                yres = (uly - lry) / height
                geoTransform = (ulx, xres, 0., uly, 0., -yres)
                outGdalDataset.SetGeoTransform(geoTransform)
            else:
                if bandList is not None:
                    tmpFilename = Utils.tmpFilename(filename, 'bandSubset.vrt')
                    tmpGdalDataset = gdal.Translate(
                        destName=tmpFilename, srcDS=gdalDataset, format=self.VrtFormat, bandList=bandList,
                        noData=noDataValue, callback=callback
                    )
                else:
                    tmpGdalDataset = gdalDataset

                feedback.pushInfo('Warp raster' + infoTail)
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

            if copyStyle:
                raster.saveDefaultStyle()

            writer = RasterWriter(outGdalDataset)
            if copyMetadata:
                self.copyMetadata(raster, writer, bandList)

            if copyStyle:
                renderer = raster.renderer().clone()
                outraster = QgsRasterLayer(filename)
                outraster.setRenderer(renderer)
                outraster.saveDefaultStyle()

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result

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
