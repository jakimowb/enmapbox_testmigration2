from os import remove
from typing import Union, List

import numpy as np
from osgeo.gdal_array import GDALTypeCodeToNumericTypeCode

from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.core.gdaldriver import GdalDriver, ENVI_DRIVER
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.raster import Raster


def saveAsEnvi(gdalRaster: GdalRaster, filename: str = None, co: List[str] = None) -> GdalRaster:
    '''
    Save raster as ENVI raster. Takes care that all metadata is correctly stored inside the ENVI header and that the raster can be opened inside the ENVI Software.
    '''
    assert isinstance(gdalRaster, GdalRaster)
    outGdalRaster = gdalRaster.translate(filename=filename, driver=ENVI_DRIVER, gco=co)

    # set ENVI metadata
    outGdalRaster.setMetadataDomain(values=gdalRaster.metadataDomain(domain='ENVI'), domain='ENVI')

    # find header file
    filenameHdr = ''
    filenameXml = ''
    for f in outGdalRaster.filenames:
        if f.endswith('.hdr'):
            filenameHdr = f
        if f.endswith('.aux.xml'):
            filenameXml = f

    assert filenameHdr.endswith('.hdr')
    assert filenameXml.endswith('.aux.xml')

    # close file and delete xml
    del outGdalRaster
    try:
        remove(filenameXml)
    except:
        pass

    # set no data value
    noDataValue = gdalRaster.band(number=1).noDataValue
    if noDataValue is not None:
        with open(filenameHdr, 'a') as file:
            print(f'data ignore value = {noDataValue}', file=file)

    # reopen file
    outGdalRaster = GdalRaster.open(filename)

    return outGdalRaster