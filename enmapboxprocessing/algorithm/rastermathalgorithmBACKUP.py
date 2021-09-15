import traceback
from math import ceil
from random import randint
from re import finditer, Match
from typing import Dict, Any, List, Tuple, Optional

import numpy
import numpy as np
from mock import Mock
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException, QgsProcessing,
                        QgsProcessingParameterString, QgsProject, QgsRasterLayer)

from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.parameter.processingparameterrastermathcodeeditwidget import \
    ProcessingParameterRasterMathCodeEditWidgetWrapper
from enmapboxprocessing.rasterblockinfo import RasterBlockInfo
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from processing import getTempFilename
from typeguard import typechecked


@typechecked
class RasterMathAlgorithm(EnMAPProcessingAlgorithm):
    P_A = 'A'
    P_B = 'B'
    P_C = 'C'
    P_D = 'D'
    P_E = 'E'
    P_F = 'F'
    P_G = 'G'
    P_H = 'H'
    P_I = 'I'
    P_J = 'J'
    P_K = 'K'
    P_L = 'L'
    P_M = 'M'
    P_N = 'N'
    P_O = 'O'
    P_P = 'P'
    P_Q = 'Q'
    P_R = 'R'
    P_S = 'S'
    P_T = 'T'
    P_U = 'U'
    P_V = 'V'
    P_W = 'W'
    P_X = 'X'
    P_Y = 'Y'
    P_Z = 'Z'
    P_A_BAND = 'bandA'
    P_B_BAND = 'bandB'
    P_C_BAND = 'bandC'
    P_D_BAND = 'bandD'
    P_E_BAND = 'bandE'
    P_F_BAND = 'bandF'
    P_G_BAND = 'bandG'
    P_H_BAND = 'bandH'
    P_I_BAND = 'bandI'
    P_J_BAND = 'bandJ'
    P_K_BAND = 'bandK'
    P_L_BAND = 'bandL'
    P_M_BAND = 'bandM'
    P_N_BAND = 'bandN'
    P_O_BAND = 'bandO'
    P_P_BAND = 'bandP'
    P_Q_BAND = 'bandQ'
    P_R_BAND = 'bandR'
    P_S_BAND = 'bandS'
    P_T_BAND = 'bandT'
    P_U_BAND = 'bandU'
    P_V_BAND = 'bandV'
    P_W_BAND = 'bandW'
    P_X_BAND = 'bandX'
    P_Y_BAND = 'bandY'
    P_Z_BAND = 'bandZ'
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
    P_CODE, _CODE = 'code', 'Code'
    P_GRID, _GRID = 'grid', 'Grid'
    P_OVERLAP, _OVERLAP = 'overlap', 'Block overlap'
    P_MONOLITHIC, _MONOLITHIC = 'monolithic', 'Monolithic processing'
    P_INPUTS, _INPUTS = 'inputs', 'INPUTS'


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
            (self._INPUTS, 'Additional input raster layers arranged as a list of numpy arrays mapped to the '
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

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMathCode(self.P_CODE, self._CODE, None)
        self.addParameterMultipleLayers(self.P_INPUTS, self._INPUTS, QgsProcessing.TypeRaster, None, True)
        self.addParameterRasterLayer(self.P_GRID, self._GRID, optional=True)
        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for letter in self.letters:
            self.addParameterRasterLayer(letter, letter, None, True, False)
            self.addParameterBand('band' + letter, 'Selected band', None, letter, True, False, False)
        for i in range(1, 11):
            self.addParameterRasterDestination(f'R{i}', f'R{i}', None, True, True)
        self.addParameterInt(self.P_OVERLAP, self._OVERLAP, None, True, 0)
        self.addParameterBoolean(self.P_MONOLITHIC, self._MONOLITHIC, False, True)

    def prepareAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> bool:
        self.mapLayers = {k:v for k,v in QgsProject.instance().mapLayers().items() if k in parameters[self.P_CODE]}
        print('###', self.mapLayers)
        return True

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        self.code = self.parameterAsString(parameters, self.P_CODE, context)
        self.rasters = [self.parameterAsRasterLayer(parameters, letter, context) for letter in self.letters]
        self.bandLists = [self.parameterAsInt(parameters, 'band' + letter, context) for letter in self.letters]
        rasterList = self.parameterAsLayerList(parameters, self.P_INPUTS, context)
        if rasterList is not None:
            self.rasters.extend(rasterList)
            self.bandLists.extend([None] * len(rasterList))
        self.grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        self.filenames = [self.parameterAsFileOutput(parameters, f'R{i}', context) for i in range(1, 11)]
        self.overlap = self.parameterAsInt(parameters, self.P_OVERLAP, context)
        self.monolithic = self.parameterAsBoolean(parameters, self.P_MONOLITHIC, context)

        if self.grid is None:
            for raster in self.rasters:
                if raster is not None:
                    self.grid = raster

        if self.grid is None:  # use first mapped GUI layers
            for line in self.code.split('\n'):
                if ' is mapped to ' in line:
                    registryName, identifier = line[2:].split(' is mapped to ')
                    layer = self.mapLayers[registryName]
                    self.grid = layer
                    break

        if self.grid is None:
            message = 'Select either a Grid or at least one input A, ..., Z or INPUTS.'
            feedback.reportError(message, True)
            raise QgsProcessingException()

        self.grid = RasterReader(self.grid)

        self.format, self.options = self.GTiffFormat, self.DefaultGTiffCreationOptions
        self.maximumMemoryUsage = Utils.maximumMemoryUsage()

        logFilename = None
        for filename in self.filenames:
            if filename is not None:
                logFilename = filename + '.log'
                break
        if logFilename is None:
            logFilename = getTempFilename(ext='log')

        with open(logFilename, 'w') as logfile:
            self.feedback, self.feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(self.feedback, parameters, context)

            self.initReader()

            # prepare code snippet
            lines = self.code.split('\n')
            lines = [line for line in lines if line.strip() != '']
            if len(lines) == 1:
                lines[-1] = '_result = ' + lines[-1]  # this allows for simple expressions
            self.code = '\n'.join(lines)

            self.initWriter()

            # get block size
            blockSizeY = min(self.grid.height(), ceil(self.maximumMemoryUsage / self.lineMemoryUsage))
            blockSizeX = self.grid.width()
            if self.monolithic:
                blockSizeY = self.grid.height()
                blockSizeX = self.grid.width()

            # process
            for block in self.grid.walkGrid(blockSizeX, blockSizeY, self.feedback):

                results = self.processBlock(block)

                for result, writer in zip(results, self.writers):
                    if result is not None:
                        writer.writeArray(result, block.xOffset, block.yOffset, overlap=self.overlap)

            result = dict()
            for i, (filename, writer) in enumerate(zip(self.filenames, self.writers), 1):
                key = f'R{i}'
                if writer is not None:
                    result[key] = filename
            self.toc(self.feedback, result)

        return result

    def initReader(self):

        self.readers = list()  # original
        self.readers2 = list()  # resampled to target grid
        self.lineMemoryUsage = 0
        i=0
        for raster, bandList in zip(self.rasters, self.bandLists):
            i += 1
            if raster is None:
                reader = None
                reader2 = None
            else:
                reader = RasterReader(raster)
                # resample to target grid
                if self.grid.crs() == raster.crs():
                    reader2 = reader
                else:
                    alg = TranslateRasterAlgorithm()
                    parameters = {
                        alg.P_RASTER: raster,
                        alg.P_GRID: self.grid.source(),
                        alg.P_RESAMPLE_ALG: self.NearestNeighbourResampleAlg,
                        alg.P_CREATION_PROFILE: self.DefaultVrtCreationProfile,
                        alg.P_OUTPUT_RASTER: f'/vsimem/RasterMathAlgorithm/{i}.vrt'
                    }
                    raster2 = self.runAlg(
                        alg, parameters, None, self.feedback2, self.context, True
                    )[alg.P_OUTPUT_RASTER]
                    reader2 = RasterReader(raster2)
                if bandList is None:
                    self.lineMemoryUsage += reader2.lineMemoryUsage()
                else:
                    self.lineMemoryUsage += reader2.lineMemoryUsage(1)
            self.readers.append(reader)
            self.readers2.append(reader2)

        # add mapped gui layer
        self.readersGui = dict()  # original
        self.readers2Gui = dict()  # resampled to target grid

        for registryName, layer in self.mapLayers.items():
            i += 1
            if isinstance(layer, QgsRasterLayer):
                raster = layer
                reader = RasterReader(layer)
                # resample to target grid
                if self.grid.crs() == raster.crs():
                    reader2 = reader
                else:
                    alg = TranslateRasterAlgorithm()
                    parameters = {
                        alg.P_RASTER: raster,
                        alg.P_GRID: self.grid.source(),
                        alg.P_RESAMPLE_ALG: self.NearestNeighbourResampleAlg,
                        alg.P_CREATION_PROFILE: self.DefaultVrtCreationProfile,
                        alg.P_OUTPUT_RASTER: f'/vsimem/RasterMathAlgorithm/{i}.vrt'
                    }
                    raster2 = self.runAlg(
                        alg, parameters, None, self.feedback2, self.context, True
                    )[alg.P_OUTPUT_RASTER]
                    reader2 = RasterReader(raster2)
            else:
                assert 0
            self.lineMemoryUsage += reader2.lineMemoryUsage()
            self.readersGui[registryName] = reader
            self.readers2Gui[registryName] = reader2

    def initWriter(self):
        # derive output data types, bandCount und output size,
        # by executing the code on a minimal extent (i.e. one pixel),
        # and create output raster
        self.writers = list()
        for block in self.grid.walkGrid(1, 1, None):
            results = self.processBlock(block, dryRun=True)
            for result, filename in zip(results, self.filenames):
                if result is None:
                    writer = None
                else:
                    dataType = Utils.numpyDataTypeToQgisDataType(result.dtype)
                    bandCount = len(result)
                    driver = Driver(filename, self.format, self.options, self.feedback)
                    writer = driver.createLike(self.grid, dataType, result.shape[0])
                    self.lineMemoryUsage += self.grid.lineMemoryUsage(bandCount, writer.dataTypeSize())
                self.writers.append(writer)
            break

    def processBlock(self, block: RasterBlockInfo, dryRun=False) -> List[Optional[np.ndarray]]:

        # load data into namespace
        namespace = dict()
        namespace['np'] = np
        namespace['numpy'] = numpy
        namespace['INPUTS'] = list()
        namespace['INPUTS_'] = list()
        namespace['INPUT_MASKS'] = list()

        if dryRun:
            namespace['feedback'] = Mock()  # silently ignore all feedback
        else:
            namespace['feedback'] = self.feedback
        for i, (reader, reader2, bandList) in enumerate(zip(self.readers, self.readers2, self.bandLists)):
            if reader is None:
                continue
            if bandList is not None:
                bandList = [bandList]
            # add data from input widgets
            array = np.array(reader2.arrayFromBlock(block, bandList, self.overlap))
            if i < len(self.letters):
                letter = self.letters[i]
                if letter in self.code:
                    namespace[letter] = array
                    namespace[letter + '_'] = reader
                # add mask
                if letter + 'M' in self.code:
                    namespace[letter + 'M'] = np.array(reader2.maskArray(array, bandList))
            else:
                namespace['INPUTS'].append(array)
                namespace['INPUTS_'].append(reader)
                if 'INPUT_MASKS' in self.code:
                    namespace['INPUT_MASKS'].append(np.array(reader2.maskArray(array, bandList)))

        code = self.code

        # add data from mapped GUI layers
        # - the mapping is coded in special comments like "# <registryName> is mapped to <identifier>"
        for line in code.split('\n'):
            if ' is mapped to ' in line:
                registryName, identifier = line[2:].split(' is mapped to ')
                reader = self.readersGui[registryName]
                reader2 = self.readers2Gui[registryName]
                # load all bands if required
                loadAll = self.code.count(identifier) - self.code.count(identifier + '@') > 1
                if loadAll:
                    array = np.array(reader.arrayFromBlock(block, None, self.overlap))
                    namespace[identifier] = array
                    namespace[identifier + '_'] = reader
                    namespace[identifier + 'Mask'] = np.array(reader2.maskArray(array))

                # replace wavebands by normal band
                match: Match
                for match in finditer(identifier + '@[0-9.]*nm', self.code):
                    aliasIdentifier = self.code[match.start(): match.end()]
                    wavelength = float(self.code[match.start(): match.end() - 2].split('@')[1])
                    bandNo = reader.findWavelength(wavelength)
                    code = code.replace(aliasIdentifier, identifier + f'@{bandNo}')
                # load normal band
                match: Match
                for match in finditer(identifier + '@[0-9]*', code):
                    bandNo = int(code[match.start(): match.end()].split('@')[1])
                    bandIdentifier = identifier + f'At{bandNo}'
                    if not 0 < bandNo <= reader.bandCount():
                        raise QgsProcessingException(f'invalid band number ({bandNo}): expected 1 <= bandNo <= {reader.bandCount()}')
                    if not bandIdentifier in namespace:
                        if identifier in namespace:  # if all bands already read, index the band
                            array = namespace[identifier][bandNo - 1][None]
                        else:
                            array = np.array(reader.arrayFromBlock(block, [bandNo], self.overlap))
                        namespace[bandIdentifier] = array
                        namespace[bandIdentifier + 'Mask'] = np.array(reader2.maskArray(array, [bandNo]))

                if loadAll:
                    array = np.array(reader.arrayFromBlock(block, None, self.overlap))
                    namespace[identifier] = array
                    namespace[identifier + '_'] = reader

        # add writer
        for i in range(1, 11):
            if dryRun:
                namespace[f'R{i}_'] = Mock()  # silently ignore all writer interaction
            else:
                namespace[f'R{i}_'] = self.writers[i - 1]

        # remove all comments (also the implicite mapping comments)
        code = '\n'.join([line for line in code.split('\n') if not line.startswith('#')])

        # add default assignment to R1, if code is single line
        if not '\n' in code:
            code = 'R1 = ' + code

        # execute code
        try:
            code = code.replace('@', 'At')
            exec(code, namespace)
        except Exception as error:
            traceback.print_exc()
            text = traceback.format_exc()
            text = text[text.index('File "<string>"'):]
            self.feedback.reportError(text)
            raise QgsProcessingException(str(error))

        # prepare output data
        isExpression = True
        isExpression &= self.code.count('\n') == 0  # only single line code can be an expression
        results = list()
        for i in range(1, 11):
            key = f'R{i}'
            if key in namespace:
                result = np.array(namespace[key])
                isExpression = False
            else:
                result = None
            results.append(result)
        if isExpression:
            results[0] = np.array(namespace['_result'])
        # check outputs
        for i, result in enumerate(results):
            if result is None:
                continue
            if result.ndim != 3:
                message = f'expected 3d array-like, got ndim(R{i + 1}) = {result.ndim}'
                self.feedback.reportError(message, True)
                raise QgsProcessingException(message)
            if self.overlap is None:
                expected = (block.height, block.width)
            else:
                expected = (block.height + 2 * self.overlap, block.width + 2 * self.overlap)

            if result.ndim != 3 or result.shape[1:] != expected:
                message = f'spatial shape mismatch for result R{i + 1} with shape {result.shape[1:]}, ' \
                          f'expected {expected}'
                self.feedback.reportError(message, True)
                raise QgsProcessingException(message)

        return results
