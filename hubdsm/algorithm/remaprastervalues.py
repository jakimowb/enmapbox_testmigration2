from typing import List, Dict, Any, Union

import numpy as np
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode

from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.core.classdefinition import ClassDefinition
from hubdsm.core.gdalrasterdriver import GdalRasterDriver
from hubdsm.core.raster import Raster


def remapRasterValues(
        raster: Raster, sources: np.ndarray, targets: np.ndarray, filename: str = None, co: List[str] = None,
        po=ProcessingOptions()
) -> Raster:
    '''
    Remap raster from source to target values.
    Output data type is derived from target array.
    Output no data value is same as input no data value, if not mapped, otherwise the mapped value is used.
    '''
    assert isinstance(raster, Raster)
    assert isinstance(sources, np.ndarray)
    assert isinstance(targets, np.ndarray)
    assert targets.shape == sources.shape
    mapping = {s: t for s,t in zip(sources, targets)}
    gdalDataType = NumericTypeCodeToGDALTypeCode(targets.dtype)
    driver = GdalRasterDriver.fromFilename(filename=filename)
    outGdalRaster = driver.create(grid=raster.grid, bands=len(raster.bands), gdalDataType=gdalDataType,
        filename=filename, gdalCreationOptions=co
    )

    subgrids = list(raster.grid.subgrids(shape=po.getShape(default=raster.grid.shape)))
    n = len(subgrids) * len(raster.bands)
    i = 1
    t0 = po.callbackStart(remapRasterValues.__name__)

    for band, outGdalBand in zip(raster.bands, outGdalRaster.bands):
        noDataValue = band.gdalBand.noDataValue
        noDataValue = mapping.get(noDataValue, noDataValue)

        for subgrid in subgrids:
            po.callbackProgress(i, n)
            i += 1
            array = np.full(shape=subgrid.shape, fill_value=noDataValue, dtype=targets.dtype)
            sample = band.readAsSample(grid=subgrid)
            for old, new in mapping.items():
                where = sample.values == old
                array[sample.yLocations[where], sample.xLocations[where]] = new
            outGdalBand.writeArray(array=array, grid=subgrid)
        outGdalBand.setNoDataValue(value=noDataValue)

    po.callbackFinish(remapRasterValues.__name__, t0=t0)
    return Raster.open(outGdalRaster)
