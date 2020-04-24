from typing import Union, List

import numpy as np
from osgeo import gdal
from osgeo.gdal_array import GDALTypeCodeToNumericTypeCode
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin, ClusterMixin
from sklearn.utils.validation import check_is_fitted

from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.core.gdalrasterdriver import GdalRasterDriver
from hubdsm.core.raster import Raster


def estimatorPredict(
        raster: Raster, estimator: Union[ClassifierMixin, RegressorMixin, ClusterMixin], filename: str = None,
        co: List[str] = None, po=ProcessingOptions(), gdalDataType=None, noDataValue=None
) -> Raster:
    '''Apply estimator predict on a raster.'''
    if isinstance(estimator, (ClassifierMixin, ClusterMixin)):
        bands = 1
        gdalDataType = gdal.GDT_UInt16
    elif isinstance(estimator, RegressorMixin):
        X0 = np.ones(shape=(1, len(raster.bands)), dtype=np.float64)
        y0 = estimator.predict(X=X0)
        bands = max(y0.shape)
        gdalDataType = gdal.GDT_Float64
    else:
        assert 0
    numpyDataType = GDALTypeCodeToNumericTypeCode(gdalDataType)
    if noDataValue is None:
        noDataValue = np.iinfo(numpyDataType).min

    driver = GdalRasterDriver.fromFilename(filename=filename)
    outGdalRaster = driver.create(grid=raster.grid, bands=bands, gdt=gdalDataType, filename=filename, gco=co)
    subgrids = list(raster.grid.subgrids(shape=po.getShape(default=raster.grid.shape)))
    n = len(subgrids)
    i = 1
    t0 = po.callbackStart(estimatorPredict.__name__)
    for subgrid in subgrids:
        po.callbackProgress(i, n)
        i += 1
        array = np.full(shape=(bands, *subgrid.shape), fill_value=noDataValue, dtype=numpyDataType)
        sample, location = raster.readAsSample(
            grid=subgrid, mode=Raster.SampleMode.strict, fieldNames=Raster.SampleFieldNames.bandIndices,
            xPixel='x', yPixel='y'
        )
        X = sample.array().T
        y = estimator.predict(X=X)
        if isinstance(estimator, ClusterMixin):
            y += 1  # start with id=1, because zero is reserved as no data value
        array[:, location.y, location.x] = y.reshape(len(sample), -1).T
        outGdalRaster.writeArray(array=array, grid=subgrid)
    outGdalRaster.setNoDataValue(value=noDataValue)
    po.callbackFinish(estimatorPredict.__name__, t0=t0)
    return Raster.open(outGdalRaster)
