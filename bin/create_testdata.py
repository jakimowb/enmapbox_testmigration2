from os.path import join, dirname, basename
import os
import numpy
from osgeo import gdal
from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierOutputRaster, Open
inroot = r'C:\Work\data\gms\landsat'
outroot = r'C:\Work\source\hub-datacube\hubdc\examples\testdata'
for root, dirs, files in os.walk(inroot):
    for f in files:
        if not f.startswith('LT5') or not f.endswith('.img'): continue

        if f[:-5].endswith('sr_band'):
            print(f)

            applier = Applier()
            applier.inputRaster.setRaster(key='in', value=ApplierInputRaster(filename=join(root, f)))
            applier.outputRaster.setRaster(key='out', value=ApplierOutputRaster(filename=join(outroot, f.split('_')[0], f),
                                                                                format='GTiff',
                                                                                creationOptions=['COMPRESS=LZW', 'INTERLEAVE=BAND']))
            applier.controls.setResolution(500, 500)
            class op(ApplierOperator):
                def ufunc(self):
                    array = self.inputRaster.raster(key='in').imageArray(resampleAlg=gdal.GRA_Average)
                    invalid = array == self.inputRaster.raster(key='in').noDataValue()
                    array /= 100
                    array = numpy.clip(array, 0, 100)
                    array = numpy.uint8(array)
                    array[invalid] = 255
                    self.outputRaster.raster(key='out').setImageArray(array=array)
                    self.outputRaster.raster(key='out').setNoDataValue(value=255)
            applier.apply(operatorType=op)

        if f[:-4].endswith('cfmask'):
            print(f)
            ds = Open(filename=join(root, f))
            ds.translate(filename=join(outroot, f.split('_')[0], f), format='GTiff',
                         grid=ds.pixelGrid.newResolution(500, 500),
                         creationOptions=['COMPRESS=LZW', 'INTERLEAVE=BAND'],
                         resampleAlg=gdal.GRA_Mode)