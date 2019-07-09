from __future__ import print_function
import numpy
from numpy import *
import numpy.random as random
import traceback
from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierInputVector, ApplierOutputRaster, ApplierOptions, ApplierControls
from enmapboxapplications.imagemathapp.routines import *


class Calulator(Applier):
    def applyCode(self, code, options, overlap, outputKeys, overwrite=True):

        assert isinstance(options, dict)
        assert isinstance(outputKeys, list)

        self.apply(operatorType=CalculatorOperator, description='Calculator', overwrite=overwrite,
                   code=code, options=options, overlap=overlap)

        self.controls.progressBar.setPercentage(0)

        if len(list(self.outputRaster.flatRasterKeys())) > 0:
            self.controls.progressBar.setText('\noutputs created:')
            for key in self.outputRaster.flatRasterKeys():
                value = self.outputRaster.raster(key=key)
                self.controls.progressBar.setText('<b>{}</b> = {}'.format(key, value.filename()))
                try:
                    import hubflow.signals
                    hubflow.signals.sigFileCreated.emit(value.filename())
                except:
                    pass

        missingOutputs = [key for key in outputKeys if key not in self.outputRaster.flatRasterKeys()]
        if len(missingOutputs) > 0:
            self.controls.progressBar.setText('')
            self.controls.progressBar.setText(
                '<p style="color:red;">WARNING: missing outputs <b>{}</b></p>'.format(', '.join(missingOutputs)))


class CodeExecutionError(Exception):
    pass


class CalculatorOperator(ApplierOperator):
    def ufunc(self, code, options, overlap):

        global inputRasterByArray, outputRasterByArray, outputNoDataValueByArray, outputMetadataByArray

        namespace = dict()
        for key in self.inputRaster.flatRasterKeys():
            raster = self.inputRaster.raster(key=key)
            namespace['_array'] = raster.array(resampleAlg=options[key]['resampleAlg'], overlap=overlap)
            # noDataValue=options[key]['noDataValue'])
            try:
                exec('{key} = _array'.format(key=key), namespace)
            except:
                raise CodeExecutionError(traceback.format_exc())

            inputRasterByArray[id(namespace['_array'])] = raster

        for key in self.inputVector.flatVectorKeys():
            vector = self.inputVector.vector(key=key)
            namespace['_array'] = vector.array(initValue=options[key]['initValue'],
                                               burnValue=options[key]['burnValue'],
                                               burnAttribute=options[key]['burnAttribute'],
                                               allTouched=options[key]['allTouched'],
                                               filterSQL=options[key]['filterSQL'],
                                               dtype=options[key]['dtype'],
                                               overlap=overlap)
            exec('{key} = _array'.format(key=key), namespace)

        for key in self.outputRaster.flatRasterKeys():
            raster = self.outputRaster.raster(key=key)
            exec('{key} = None'.format(key=key), namespace)

        namespace.pop('_array')

        # add functions to namespace
        exec('from enmapboxapplications.imagemathapp.routines import *', namespace)
        namespace['print'] = self.progressBar.setText

        try:
            exec(code, namespace)
        except:
            raise CodeExecutionError(traceback.format_exc())

        for key in self.outputRaster.flatRasterKeys():
            raster = self.outputRaster.raster(key=key)
            array = namespace[key]
            noData = namespace['outputNoDataValueByArray'].get(id(array), None)
            metadata = outputMetadataByArray.get(id(array), None)
            if array is not None:
                raster.setArray(array=array, overlap=overlap)
                if noData is not None:
                    raster.setNoDataValue(value=noData)
                if metadata is not None:
                    if 'ENVI' in metadata and 'file_compression' in metadata['ENVI']:
                        metadata['ENVI']['file_compression'] = None
                    raster.setMetadataDict(metadataDict=metadata)


def test():
    import enmapboxtestdata
    calculator = Calulator()
    calculator.inputRaster.setRaster(key='enmap', value=ApplierInputRaster(filename=enmapboxtestdata.enmap))
    calculator.inputVector.setVector(key='landCover', value=ApplierInputVector(filename=enmapboxtestdata.landcover))
    calculator.outputRaster.setRaster(key='result', value=ApplierOutputRaster(filename=r'c:\outputs\calcResult.bsq'))
    code = \
'''
result = enmap
result[:, landCover[0] == 0] = noDataValue(enmap)
setNoDataValue(result, noDataValue(enmap))
setMetadata(result, metadata(enmap))
print(numpy.sum(enmap))
'''

    #
    from osgeo import gdal
    options = dict()
    options['enmap'] = dict()
    options['enmap']['resampleAlg'] = gdal.GRA_NearestNeighbour
    options['landCover'] = dict()
    options['landCover']['initValue'] = 0
    options['landCover']['burnValue'] = 1
    options['landCover']['burnAttribute'] = None
    options['landCover']['allTouched'] = False
    options['landCover']['filterSQL'] = None
    options['landCover']['dtype'] = numpy.float32
    calculator.applyCode(code=code, options=options, outputKeys=['result'])


if __name__ == '__main__':
    test()
