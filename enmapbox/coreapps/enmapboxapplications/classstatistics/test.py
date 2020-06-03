import numpy as np

from enmapbox.testing import initQgisApplication
from enmapboxapplications.widgets.core import *
from enmapboxapplications.classstatistics.core import ClassStatistics
from hubdsm.core.gdalraster import GdalRaster

if __name__ == '__main__':

    qgsApp = initQgisApplication()

    try:
        import qgisresources.images

        qgisresources.images.qInitResources()
    except:
        pass

    filename1='/vsimem/raster1.bsq'
    gdalRaster1 = GdalRaster.createFromArray(array=np.array([[[10, 11, 412]]]), filename=filename1)
    del gdalRaster1
    filename2 = '/vsimem/raster2.bsq'
    gdalRaster2 = GdalRaster.createFromArray(array=np.array([[[10, 10, 10, 15, 15, 412]]]), filename=filename2)
    del gdalRaster2

    enmapBox = EnMAPBox(None)
    enmapBox.run()
    enmapBox.addSource(source=r'C:\Users\janzandr\Desktop\classification.bsq', name='classification.bsq')
    enmapBox.addSource(source=filename1, name='raster1.bsq')
    enmapBox.addSource(source=filename2, name='raster2.bsq')

    try:
        widget = ClassStatistics()
        widget.show()
    except:
        import traceback
        traceback.print_exc()

    qgsApp.exec_()
    qgsApp.exitQgis()
