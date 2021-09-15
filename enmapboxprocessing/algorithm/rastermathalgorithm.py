import traceback
from collections import OrderedDict, defaultdict
from math import ceil
from os.path import basename, splitext, join, dirname
from random import randint
from re import finditer, Match
from typing import Dict, Any, List, Tuple, Optional, Iterable, Union

import numpy
import numpy as np
from mock import Mock
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException, QgsProcessing,
                        QgsProcessingParameterString, QgsProject, QgsRasterLayer, QgsProcessingParameterField,
                        QgsProcessingParameterVectorLayer, Qgis, QgsMapLayer, QgsVectorLayer, QgsFields)

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.parameter.processingparameterrastermathcodeeditwidget import \
    ProcessingParameterRasterMathCodeEditWidgetWrapper
from enmapboxprocessing.processingfeedback import ProcessingFeedback
from enmapboxprocessing.rasterblockinfo import RasterBlockInfo
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.utils import Utils
from processing import getTempFilename, Processing
from typeguard import typechecked


@typechecked
class RasterMathAlgorithm(EnMAPProcessingAlgorithm):
    P_CODE, _CODE = 'code', 'Code'
    P_GRID, _GRID = 'grid', 'Grid'
    P_OVERLAP, _OVERLAP = 'overlap', 'Block overlap'
    P_MONOLITHIC, _MONOLITHIC = 'monolithic', 'Monolithic processing'
    P_RS, _RS = 'rasters', 'Raster layers '
    P_R1 = 'R1'
    P_R2 = 'R2'
    P_R3 = 'R3'
    P_R4 = 'R4'
    P_R5 = 'R5'
    P_R6 = 'R6'
    P_R7 = 'R7'
    P_R8 = 'R8'
    P_R9 = 'R9'
    P_R10 = 'R10'
    P_V1 = 'V1'
    P_V2 = 'V2'
    P_V3 = 'V3'
    P_V4 = 'V4'
    P_V5 = 'V5'
    P_V6 = 'V6'
    P_V7 = 'V7'
    P_V8 = 'V8'
    P_V9 = 'V9'
    P_V10 = 'V10'
    P_OUTPUT_RASTER = 'outputRaster'

    def displayName(self) -> str:
        return 'Raster math'

    def shortDescription(self) -> str:
        link1 = self.htmlLink('https://numpy.org/doc/stable/reference/', 'NumPy')
        link2 = self.htmlLink('https://numpy.org/doc/stable/reference/arrays.ndarray.html', '3d NumPy arrays')

        return 'Perform mathematical calculations on selected raster layer data. ' \
               f'Use any {link1}-based arithmetic, or even arbitrary Python code.\n' \
               f'Input raster data is mapped to {link2} A, B, ..., Z. ' \
               'Result array variables R1, R2, ..., R10 are written to corresponding destination raster layer.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        linkReader = self.htmlLink(
            'https://bitbucket.org/hu-geomatics/enmap-box/src/develop/enmapboxprocessing/rasterreader.py',
            'RasterReader'
        )
        linkWriter = self.htmlLink(
            'https://bitbucket.org/hu-geomatics/enmap-box/src/develop/enmapboxprocessing/rasterwriter.py',
            'RasterWriter'
        )
        linkFeedback = self.htmlLink(
            'https://qgis.org/api/classQgsProcessingFeedback.html',
            'feedback'
        )
        return [
            (self._CODE, 'The mathematical calculation to be performed on the input arrays '
                         'A, B, ..., Z, creating result arrays R1, R2, ..., R10. '
                         'All arrays are 3d with shape (bandCount, height, width).\n'
                         'When using a simple expression like A + B, the result is automatically assigned to R1.\n'
                         'Alternatively, use a statement to explicitely assign outputs like R1 = A + B.\n'
                         'To correctly handle no data regions use the AM, ..., ZM mask arrays:'
                         '<pre>'
                         'R1 = A + B<br>'
                         'R1[~AM] = -99<br>'  
                         'R1[~BM] = -99<br>'
                         '</pre>'
                         f'To properly set no data values, band names, metadata etc. use the R1_, ... R10_ '
                         f'{linkWriter} handles:'
                         '<pre>'
                         'R1_.setNoDataValue(-99)<br>'
                         "R1_.setBandName('my band', bandNo=1)<br>"
                         "R1_.setMetadataItem('my key', 42, 'MY DOMAIN')<br>"
                         '</pre>'
                         'To query or copy source no data values, band names, metadata etc. use the A_, ..., Z_ '
                         f'{linkReader} handles. E.g., copy all data and metadata:'
                         '<pre>'
                         'R1 = A<br>'
                         'R1_.setMetadata(A_.metadata())<br>'
                         '</pre>'
                         'When using spatial operators, '
                         'make sure to specify an appropriate value for the Block overlap parameter to avoid artifacts at '
                         'block borders, or enable Monolithic processing. '
                         'E.g., when applying this Gaussian filter, the overlap should be set to sigma * truncate:'
                         '<pre>'
                         'from scipy.ndimage import gaussian_filter<br>'
                         'R1 = gaussian_filter(A, sigma=3, truncate=4)<br>'
                         '</pre>'
                         'In some usecases, the main focus is to calculate some statistics that aggregate data over '
                         'the full grid extent. To do that correctly, you also want to enable Monolithic processing '
                         f'and use the {linkFeedback} object to report/log results:'
                         '<pre>'
                         'hist, bin_edges = np.histogram(A, bins=10, range=(0, 10000))<br>'
                         'for a, b, n in zip(bin_edges[:-1], bin_edges[1:], hist):<br>'
                         "    feedback.pushInfo(f'[{a}, {b}]: {n}')<br>"
                         '</pre>'
                         'To allow for arbitrary many inputs, use the INPUTS parameters.'
                         'E.g. averaging a list of raster layer:'
                         '<pre>np.min(INPUTS, axis=0)</pre>'
                         ),
            (self._GRID, 'The target grid. If not specified, the grid of raster layer A is used.'),
            ('A, B, ..., Z', 'Raster layers that are mapped to numpy array variables A, B, ..., Z '
                             'with shape (bandCount, height, width).\n'
                             f'Use the associated {linkReader} objects A_, B_, ..., Z_ to query additional '
                             'information like metadata, no data values, band names, center wavelength '
                             'and so on.\n'
                             f'Additionally, you may use the associated boolean arrays AM, BM, ..., ZM to properly '
                             f'mask no data regions. Note that all no data, inf and nan values evaluate to False, '
                             f'and all other to True.'),
            ('Selected band', 'If specified, only the selected band is mapped with shape (1, height, width).'),
            (self._RS, 'Additional input raster layers arranged as a list of numpy arrays mapped to the '
                           'variable named INPUTS.\n'
                           f'The associated {linkReader} objects are stored in a variable named INPUTS_.'),
            ('R1, R2, ..., R10', 'Raster file destinations for writing the created output variables '
                                 'R1, R2, ..., R10. \n'
                                 f'Use the associated {linkWriter} objects R1_, R2_, ..., R10_ to assign additional '
                                 'information like metadata, no data values, band names, center wavelength '
                                 'and so on.\n'),
            (self._OVERLAP, 'The number of columns and rows to read from the neighbouring blocks. '
                             'Needs to be specified only when performing spatial operations, '
                             'to avoid artifacts at block borders.'),
            (self._MONOLITHIC, 'Whether to read all data for the full extent at once, instead of block-wise processing. '
                               'This may be useful for some spatially unbound operations, '
                               'like segmentation or region growing, when calculating global statistics, '
                               'or if RAM is not an issue at all.')
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def addParameterMathCode(
            self, name: str, description: str, defaultValue=None, optional=False, advanced=False
    ):
        param = QgsProcessingParameterString(name, description, optional=optional)
        param.setMetadata({'widget_wrapper': {'class': ProcessingParameterRasterMathCodeEditWidgetWrapper}})
        param.setDefaultValue(defaultValue)
        self.addParameter(param)
        self.flagParameterAsAdvanced(name, advanced)

    def inputRasterNames(self):
        for i in range(1, 11):
            yield getattr(self, f'P_R{i}'), f'Raster layer mapped to R{i}'

    def inputVectorNames(self):
        for i in range(1, 11):
            yield getattr(self, f'P_V{i}'), f'Vector layer mapped to V{i}'

    def inputRasterListNames(self):
        i = 11  # first R1...R10 are reserved for manual selected raster layers
        while True:
            yield f'R{i}'
            i += 1

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMathCode(self.P_CODE, self._CODE, None)
        self.addParameterRasterLayer(self.P_GRID, self._GRID, optional=True)
        self.addParameterInt(self.P_OVERLAP, self._OVERLAP, None, True, 0)
        self.addParameterBoolean(self.P_MONOLITHIC, self._MONOLITHIC, False, True)
        self.addParameterMultipleLayers(self.P_RS, self._RS, QgsProcessing.TypeRaster, None, True, True)
        for name, description in self.inputRasterNames():
            self.addParameterRasterLayer(name, description, None, True, True)
        for name, description in self.inputVectorNames():
            self.addParameterVectorLayer(name, description, None, None, True, True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, 'Output raster', None, False, True)

    def prepareAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> bool:
        self.mapLayers = {k:v for k,v in QgsProject.instance().mapLayers().items() if k in parameters[self.P_CODE]}
        print('###', self.mapLayers)
        return True

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        code = self.parameterAsString(parameters, self.P_CODE, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        overlap = self.parameterAsInt(parameters, self.P_OVERLAP, context)
        monolithic = self.parameterAsBoolean(parameters, self.P_MONOLITHIC, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            rasters = OrderedDict()  # original rasters
            rasters2 = OrderedDict()  # resampled rasters

            # get all Ri raster layers R1, ..., R10
            for rasterName, _ in self.inputRasterNames():
                raster = self.parameterAsRasterLayer(parameters, rasterName, context)
                if raster is not None:
                    rasters[rasterName] = self.parameterAsRasterLayer(parameters, rasterName, context)

            # get all RS raster layers R11, ...
            rs = self.parameterAsLayerList(parameters, self.P_RS, context)
            if rs is not None:
                for raster, rasterName in zip(rs, self.inputRasterListNames()):
                    assert isinstance(raster, QgsRasterLayer)
                    rasters[rasterName] = raster

            # get all hard coded raster layer from comments
            # <name> := QgsRasterLayer(<uri>)
            for line in code.splitlines():
                if line.strip().startswith('#') and ':=' in line:
                    layerName, value = line.split(':=')
                    layerName = layerName.strip('# ')
                    raster = eval(value.strip())
                    if isinstance(raster, QgsRasterLayer):
                        rasters[layerName] = raster

            # derive grid
            if grid is None:
                for raster in rasters.values():
                    grid = raster
                    break  # use first raster found as grid
            if grid is None:
                raise QgsProcessingException(f'Missing parameter value: {self._GRID}')

            # get all Vi vector layers
            vectors = dict()
            for vectorName, fieldName in self.inputVectorNames():
                vector = self.parameterAsVectorLayer(parameters, vectorName, context)
                if vector is None:
                    continue
                vectors[vectorName] = vector

            # get all hard coded vector layer from comments
            # <name> := QgsVectorLayer(<uri>), <field name>
            for line in code.splitlines():
                if line.strip().startswith('#') and ':=' in line:
                    layerName, value = line.split(':=')
                    layerName = layerName.strip('# ')
                    vector = eval(value.strip())
                    if isinstance(raster, QgsVectorLayer):
                        vectors[layerName] = vector

            # rasterize vectors to grid
            for vectorName in vectors:
                vector = vectors[vectorName]
                fields: QgsFields = vector.fields()
                filenames = list()
                fieldNames = list()
                for fieldName in fields.names() + [None]:
                    if f'{vectorName}@"{fieldName}"' not in code:
                        if fieldName is not None:
                            continue

                    alg = RasterizeVectorAlgorithm()
                    parameters = {
                        alg.P_VECTOR: vector,
                        alg.P_GRID: grid,
                        alg.P_DATA_TYPE: alg.Float32,
                        alg.P_BURN_ATTRIBUTE: fieldName,
                        alg.P_OUTPUT_RASTER: Utils.tmpFilename(
                            filename, f'{vectorName}_{Utils.makeBasename(str(fieldName))}.tif'
                        )
                    }
                    result = self.runAlg(alg, parameters, None, feedback2, context, True)
                    filenames.append(result[alg.P_OUTPUT_RASTER])
                    fieldNames.append(str(fieldName))
                stackFilename = Utils.tmpFilename(filename, f'{vectorName}.vrt')
                ds: gdal.Dataset = gdal.BuildVRT(
                    stackFilename, filenames, separate=True
                )
                writer = RasterWriter(ds)
                for bandNo, fieldName in enumerate(fieldNames, 1):
                    writer.setBandName(fieldName, bandNo)
                del ds, writer
                raster = QgsRasterLayer(stackFilename)
                rasters[vectorName] = raster

            # translate raster layers to grid
            for rasterName, raster in rasters.items():
                if raster.crs() != grid.crs():
                    alg = TranslateRasterAlgorithm()
                    parameters = {
                        alg.P_RASTER: raster,
                        alg.P_GRID: grid,
                        alg.P_CREATION_PROFILE: self.DefaultVrtCreationProfile,
                        alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, f'{rasterName}.vrt')
                    }
                    raster2 = self.runAlg(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_RASTER]
                else:
                    raster2 = raster
                rasters2[rasterName] = raster2

            grid = RasterReader(grid)
            readers = {rasterName: RasterReader(raster) for rasterName, raster in rasters.items()}
            readers2 = {rasterName: RasterReader(raster) for rasterName, raster in rasters2.items()}

            # find alias identifiers and assign reader
            for line in code.splitlines():
                if not line.startswith('#'):
                    continue
                if ' is an alias for ' in line:
                    a, b = line.strip('# ').split(' is an alias for ')
                    readers[a] = readers[b]
                    readers2[a] = readers2[b]

            # init output raster layer
            writers = self.makeWriter(code, filename, grid, readers, readers2, feedback)

            # get block size
            lineMemoryUsage = 0
            for reader in readers.values():
                lineMemoryUsage += grid.lineMemoryUsage(reader.bandCount(), reader.dataTypeSize())
            for writer in writers.values():
                lineMemoryUsage += grid.lineMemoryUsage(writer.bandCount(), writer.dataTypeSize())
            blockSizeY = min(grid.height(), ceil(Utils.maximumMemoryUsage() / lineMemoryUsage))
            blockSizeX = grid.width()
            if monolithic:
                blockSizeY = grid.height()
                blockSizeX = grid.width()

            #blockSizeY = 100

            # process
            if overlap is None:
                overlap = 0
            for block in grid.walkGrid(blockSizeX, blockSizeY, feedback):
                results = self.processBlock(
                    code, block, readers, readers2, writers, overlap, feedback
                )
                for key in results:
                    writer = writers[key]
                    result = results[key]
                    writer.writeArray(result, block.xOffset, block.yOffset, overlap=overlap)

            # prepare results
            result = {self.P_OUTPUT_RASTER: None}
            for key, writer in writers.items():
                if key == splitext(basename(filename))[0]:  # if identifier matches the output basename, ...
                    key = self.P_OUTPUT_RASTER              # ... map the result to the name of the output
                result[key] = writer.source()
            self.toc(feedback, result)

        return result

    def makeWriter(
            self, code: str, filename: str, grid: RasterReader, readers: Dict[str, RasterReader],
            readers2: Dict[str, RasterReader], feedback: ProcessingFeedback
    ) -> Dict[str, Union[RasterWriter, Mock]]:
        # We derive output data types and band counts by executing the code on a minimal extent (i.e. one pixel).
        # We call this a dry-run.

        # Find writer objects by parsing for set-methods.
        writers = dict()  # we have no writers
        for method in RasterWriter.__dict__:
            if method.startswith('set'):
                match: Match
                pattern = r'\w*.' + method
                for match in finditer(pattern, code):
                    substring = code[match.start(): match.end()]
                    identifier = substring.split('.')[0]
                    writers[identifier] = Mock()  # silently ignore all writer interaction

        for block in grid.walkGrid(1, 1, None):
            results = self.processBlock(code, block, readers, readers2, writers, 0, feedback, dryRun=True)
            break  # stop after processing the first pixel

        for name, result in results.items():
            if name == self.P_OUTPUT_RASTER:
                newFilename = filename
            else:
                newFilename = join(dirname(filename), name + '.tif')
            dataType = Utils.numpyDataTypeToQgisDataType(result.dtype)
            bandCount = len(result)
            format, options = self.GTiffFormat, self.DefaultGTiffCreationOptions
            if dataType == Qgis.Float64:
                options = self.DefaultGTiffFloat64CreationOptions
            driver = Driver(newFilename, format, options, feedback)
            writer = driver.createLike(grid, dataType, bandCount)
            writers[name] = writer

        return writers

    def processBlock(
            self, code: str, block: RasterBlockInfo, readers: Dict[str, RasterReader],
            readers2: Dict[str, RasterReader], writers: Dict[str, Union[RasterWriter, Mock]],
            overlap: int, feedback: ProcessingFeedback, dryRun=False
    ) -> Dict[str, np.ndarray]:

        # add modules
        namespace = dict()
        namespace['np'] = np
        namespace['numpy'] = numpy

        # add special variables
        if dryRun:
            namespace['feedback'] = Mock()  # silently ignore all feedback
        else:
            namespace['feedback'] = feedback
        namespace['block'] = block
        namespace['dryRun'] = dryRun

        # add data arrays and readers
        atIdentifiers = list()  # collect all @identifiers that need to be substitution with valid identifier
        for rasterName in readers:
            reader = readers[rasterName]  # used for querying metadata etc.
            reader2 = readers2[rasterName]  # used for reading the resampled data

            # only read all the data if really required, maybe we just need single bands indicated by the usage of'@'
            needAllData = False

            # - check if we use the actual array
            match: Match
            for line in code.splitlines():
                if line.startswith('#'):
                    continue
                line += '    '  # add some space for avoiding index errors when checking
                for match in finditer(rasterName, line):
                    if line[match.end()] in '@.':
                        continue  # not using the actual array, but only a single band or the reader
                needAllData = True

            # - check if we use the actual mask array
            match: Match
            for line in code.splitlines():
                if line.startswith('#'):
                    continue
                line += '    '  # add some space for avoiding index errors when checking
                for match in finditer(rasterName + 'Mask', line):
                    if line[match.end()] in '@':
                        continue  # not using the actual mask array, but only a single band
                needAllData = True

            if needAllData:
                # check if the raster is a rasterized vector ...
                isRasterizedVector = reader.bandName(reader.bandCount()) == 'None'
                if isRasterizedVector: # ... if so, we just assign the 0/1 mask, instead of all burned fields
                    array = np.array(reader2.arrayFromBlock(block, [reader.bandCount()], overlap))
                    namespace[rasterName] = array
                    namespace[rasterName + 'Mask'] = array == 1
                else:
                    array = np.array(reader2.arrayFromBlock(block, None, overlap))
                    namespace[rasterName] = array
                    namespace[rasterName + 'Mask'] = np.array(reader2.maskArray(array, None))

            #  find single band usages indicated by '@'
            atBands: Dict[Tuple, List[str]] = defaultdict(list)
            match: Match
            for line in code.splitlines():
                if line.startswith('#'):
                    continue
                line += '    '  # add some space for avoiding index errors when checking
                matches = list()
                matches.extend(finditer(rasterName + '@"[^"]+"', line))
                matches.extend(finditer(rasterName + '@[0-9:|^]+', line))
                matches.extend(finditer(rasterName + 'Mask@"[^"]+"', line))
                matches.extend(finditer(rasterName + 'Mask@[0-9:|^]+', line))

                for match in matches:
                    text = line[match.start(): match.end()]
                    atIdentifiers.append(text)  # need to make the @identifier a valid identifier later
                    if line[match.end(): match.end() + 2] == 'nm':  # waveband mode
                        unit = 'nm'
                    else:
                        unit = ''
                    if line[match.end() - 1] == '"':  # band name mode
                        bandName = text.split('"')[1]
                        bandNos = (reader.findBandName(bandName), )
                    else:  # band number mode
                        subtext = text.split('@')[1]
                        groups = subtext.split('|')
                        bandsToUse = list()
                        bandsToExclude = list()
                        for group in groups:
                            if ':' in group:
                                a, b = group.split(':')
                            else:
                                a, b = group, None
                            toBeExcluded = a.startswith('^')
                            if toBeExcluded:
                                a = a[1:]
                            a = int(a)
                            if unit == 'nm':
                                a = reader.findWavelength(a)
                                if b is not None:
                                    b = reader.findWavelength(b)
                            if b is None:
                                b = a + 1
                            b = int(b)
                            if toBeExcluded:
                                bandsToExclude.extend(range(a, b))
                            else:
                                bandsToUse.extend(range(a, b))
                        if len(bandsToUse) == 0:
                            bandsToUse = range(1, reader.bandCount() + 1)
                        bandNos = tuple(set(bandsToUse).difference(bandsToExclude))

                    identifier = text.replace('Mask@', '@') + unit
                    atBands[bandNos].append(identifier)  # collect all identifiers for each band

            # add single band data
            for bandNos, identifiers in atBands.items():
                array = np.array(reader2.arrayFromBlock(block, list(bandNos), overlap))
                marray = np.array(reader2.maskArray(array, list(bandNos)))
                for identifier in identifiers:
                    tmp = identifier.split('@')
                    namespace[Utils.makeIdentifier(tmp[0] + 'At' + tmp[1])] = array
                    namespace[Utils.makeIdentifier(tmp[0] + 'MaskAt' + tmp[1])] = marray

            namespace[rasterName + '_'] = reader

        namespace['RS'] = list()
        namespace['RS_'] = list()
        namespace['RSMask'] = list()
        for rasterName in self.inputRasterListNames():
            if rasterName in namespace:
                namespace['RS'].append(namespace[rasterName])
                namespace['RS_'].append(namespace[rasterName + '_'])
                namespace['RSMask'].append(namespace[rasterName + 'Mask'])
            else:
                break

        # add writers
        for rasterName, writer in writers.items():
            namespace[rasterName + '_'] = writer

        # inject writer objects
        for rasterName in writers:
            code = code.replace(rasterName + '.set', rasterName + '_.set', )

        # inject reader objects
        for rasterName in readers:
            for method in RasterReader.__dict__:
                code = code.replace(rasterName + '.' + method, rasterName + '_.' + method)

        # strip empty lines
        code = code.strip()

        # remove all comments
        code = '\n'.join([line for line in code.splitlines() if not line.strip().startswith('#')])

        # substitute all @"<band name>" identifier with valid identifier
        for atIdentifier in set(atIdentifiers):
            code = code.replace(atIdentifier, Utils.makeIdentifier(atIdentifier.replace('@', 'At')))

        # enable single line expressions
        isSingleLineCode = '\n' not in code
        if isSingleLineCode:
            code = self.P_OUTPUT_RASTER + ' = ' + code  # make it a statement

        # replace @
        code = code.replace('@', 'At')

        # execute code
        try:
            exec(code, namespace)
        except Exception as error:
            traceback.print_exc()
            text = traceback.format_exc()
            text = text[text.index('File "<string>"'):]
            feedback.reportError(text)
            raise QgsProcessingException(str(error))

        # prepare output data
        results = dict()
        for key, value in namespace.items():
            if key in readers:  # skip all input arrays
                continue

            removeItem = False
            for reader  in readers:  # skip all input arrays with @ syntax
                if key.startswith(reader + 'At'):
                    removeItem = True
            if removeItem:
                continue

            if key.endswith('Mask') and key[:-4] in readers:  # skip all input mask arrays
                continue
            if 'MaskAt' in key:  # skip all input mask arrays with @ syntax
                continue
            if not isinstance(value, np.ndarray):  # skip all non-arrays
                continue
            if value.ndim == 2:  # if single band array ...
                value = value[None]  # ... add third dimension
            if value.ndim != 3:  # skip all non-3d-arrays
                continue
            if value.shape[1:] != (block.height + 2 * overlap, block.width + 2 * overlap): # skip mismatching arrays
                continue
            results[key] = value

        # Check if single line was already a statement. If so, remove the default output from the results.
        if isSingleLineCode and len(results) > 1:
            results.pop(self.P_OUTPUT_RASTER)
        return results
