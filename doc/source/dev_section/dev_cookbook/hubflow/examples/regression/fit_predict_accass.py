from hubdc.docutils import createDocPrint, createReportSaveHTML
from hubflow.report import Report
print = createDocPrint(__file__)
#Report.saveHTML = createReportSaveHTML()

# START
import enmapboxtestdata
from hubflow.core import *

# create (multi tagret) regression sample (labels are landcover class fractions)
raster = Raster(filename=enmapboxtestdata.enmap)
regression = Regression(filename=enmapboxtestdata.createFraction(gridOrResolution=raster.grid(), level='level_1_id', oversampling=5))
sample = RegressionSample(raster=raster, regression=regression)

# fit regressor
from sklearn.ensemble import RandomForestRegressor
regressor = Regressor(sklEstimator=RandomForestRegressor(n_estimators=10))
regressor.fit(sample=sample)

# regress a raster
prediction = regressor.predict(filename='randonForestRegression.bsq', raster=raster)

# asses accuracy
performance = RegressionPerformance.fromRaster(prediction=prediction, reference=regression)
performance.report().saveHTML(filename='RegressionPerformance.html')
# END
MapViewer().addLayer(prediction.dataset().mapLayer()).save(basename(__file__).replace('.py', '.png'))
