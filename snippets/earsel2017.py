from enmapbox.processing.types import *
from enmapbox.processing.estimators import *

img = Image('<path spectral image>')
cal = Classification('<path calibration labels>')
val = Classification('<path validation labels>')

rfc = RandomForestClassifier()
rfc.fit(img, cal)
map = rfc.predict(img)
accAssReport = map.assessClassificationPerformance(val)
accAssReport.report().saveHTML('<path report file>')

