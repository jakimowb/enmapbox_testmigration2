from collections import OrderedDict
from typing import Dict, Union, List

import numpy as np
from osgeo.gdal_array import GDALTypeCodeToNumericTypeCode

from hubdsm.core.gdalrasterdriver import GdalRasterDriver
from hubdsm.core.raster import Raster
from hubdsm.error import GridMismatchError, BandCountMismatchError


def convertRaster(
        raster: Raster, noDataValues: List[Union[float, int]] = None, gdalDataType: int = None, filename: str = None,
        options: List[str] = None
) -> Raster:
    '''
    Convert raster allows to perform several converion tasks at ones:

        a) fill masked areas with given noDataValues

        b) cast to given gdalDataType

    '''
    if noDataValues is None:
        noDataValues = [None] * len(raster.bands)
    if len(noDataValues) != len(raster.bands):
        raise ValueError('incorrect number of noDataValues')

    if gdalDataType is None:
        gdalDataType = raster.band(number=1).gdalBand.gdalDataType

    numpyDataType = GDALTypeCodeToNumericTypeCode(gdalDataType)

    driver = GdalRasterDriver.fromFilename(filename=filename)
    outGdalRaster = driver.create(
        grid=raster.grid, bands=len(raster.bands), gdalDataType=gdalDataType, filename=filename, options=options)

    for outGdalBand, array, maskArray, noDataValue in zip(
            outGdalRaster.bands, raster.iterArrays(), raster.iterMaskArrays(), noDataValues
    ):
        # convert type
        if array.dtype != numpyDataType:
            array = array.astype(dtype=numpyDataType)
        # set noDataValue
        if noDataValue is not None:
            array[np.logical_not(maskArray)] = noDataValue
        # write
        outGdalBand.writeArray(array=array)
        outGdalBand.setNoDataValue(value=noDataValue)

    return Raster.open(outGdalRaster)
