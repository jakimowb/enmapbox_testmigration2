from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import hubdc
import enmapboxtestdata
import qgis.utils
print(hubdc.__version__)
print(enmapboxtestdata.__version__)
print(qgis.utils.Qgis.QGIS_VERSION)
# END