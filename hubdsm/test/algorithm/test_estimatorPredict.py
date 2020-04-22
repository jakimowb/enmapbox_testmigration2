from unittest import TestCase

import numpy as np
from osgeo import gdal
from sklearn.ensemble import RandomForestClassifier

from hubdsm.algorithm.estimatorpredict import estimatorPredict
from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.core.gdalrasterdriver import MEM_DRIVER
from hubdsm.core.raster import Raster
from hubdsm.core.rastercollection import RasterCollection


class TestEstimatorPredict(TestCase):

    def test(self):
        raster = Raster.createFromArray(np.array(range(3 * 2 * 2)).reshape((3, 2, 2)))
        classification = Raster.createFromArray(np.reshape([111, 112, 311, 411], (1, 2, 2)))
        samples, location = RasterCollection(
            rasters=(
                classification.withName('classification').rename(['classId']),
                raster.withName('raster')
            )
        ).readAsSample(fieldNames=Raster.SampleFieldNames.bandIndices)

        X = samples['raster'].array(dtype=np.float32).T
        y = samples['classification'].array().ravel()

        estimator = RandomForestClassifier()
        estimator.fit(X=X, y=y)
        prediction = estimatorPredict(raster=raster, estimator=estimator)
        print(prediction.readAsArray())
