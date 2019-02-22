from hubflow.core import *
import enmapboxtestdata
from sklearn.ensemble import RandomForestRegressor

enmap = Raster(filename=enmapboxtestdata.enmap)
vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover_polygons, classAttribute='level_2_id',
                                            minOverallCoverage=1., oversampling=5)
fraction = Fraction.fromClassification(filename='/vsimem/fraction.bsq', classification=vectorClassification,
                                       grid=enmap.grid())
sample = RegressionSample(raster=enmap, regression=fraction)
rfr = Regressor(sklEstimator=RandomForestRegressor())
rfr.fit(sample=sample)
prediction = rfr.predict(raster=enmap, filename='/vsimem/rfrRegression.bsq')

if True:
    from enmapbox.__main__ import run
    run(sources=[prediction.filename()])
