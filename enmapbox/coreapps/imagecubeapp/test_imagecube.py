
import unittest
from osgeo import gdal, gdal_array, osr
from enmapbox.testing import initQgisApplication, TestObjects

QGIS_APP = initQgisApplication(loadProcessingFramework=False, loadEditorWidgets=False)

SHOW_GUI = True

from .imagecube import *
class VTest(unittest.TestCase):

    def createImageCube(self, nb=150, ns=400, nl=1000, crs='EPSG.32633')->QgsRasterLayer:


        path = '/vsimem/imagecube.tiff'

        array = np.fromfunction(lambda i,j,k: i+j+k, (nb, nl, ns), dtype=np.uint32)

        drv = gdal.GetDriverByName('GTiff')
        assert isinstance(drv, gdal.Driver)
        eType = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
        ds = drv.Create(path, ns, nl, bands=nb, eType=eType)
        assert isinstance(ds, gdal.Dataset)
        if isinstance(crs, str):
            c = QgsCoordinateReferenceSystem(crs)
            ds.SetProjection(c.toWkt())
        ds.SetGeoTransform([0, 1.0, 0, \
                            0, 0, -1.0])

        assert isinstance(ds, gdal.Dataset)
        for b in range(nb):
            band = ds.GetRasterBand(b+1)
            band.WriteArray(array[b,:,:])

        ds.FlushCache()

        assert isinstance(ds, gdal.Dataset)

        lyr = QgsRasterLayer(path, 'image_cube', 'gdal')
        assert lyr.isValid()
        return lyr


    def test_widget(self):

        W = ImageCubeWidget()
        W.show()


        from enmapboxtestdata import enmap as pathEnMAP
        from enmapboxtestdata import hires as pathHyMap

        pathTS = r'R:\temp\temp_bj\Cerrado\cerrado_evi.vrt'


        layers = [self.createImageCube()]
        pathes = [pathEnMAP, pathHyMap]
        if False:
            pathes.append(pathTS)
        for p in pathes:
            if os.path.isfile(p):
                layers.append(QgsRasterLayer(p, os.path.basename(p)))

        QgsProject.instance().addMapLayers(layers)

        if True:
            lyr = layers[0]
            self.assertIsInstance(lyr, QgsRasterLayer)
            W.setRasterLayer(lyr)
            self.assertEqual(lyr, W.rasterLayer())

            x = int(lyr.width() * 0.5)
            y = int(lyr.height() * 0.5)
            z = int(lyr.bandCount() * 0.5)
            W.setX(x)
            W.setY(y)
            W.setZ(z)

            #W.setZSCale(2)
            #self.assertEqual(W.zScale(), 2)
            #W.setZSCale(2)
            self.assertEqual(W.x(), x)
            self.assertEqual(W.y(), y)
            self.assertEqual(W.z(), z)

            W.setZScale(1.8)
            self.assertEqual(1.8, W.zScale())
            W.setZScale(1.9)
            self.assertEqual(1.9, W.zScale())
            W.setZScale(2)
            self.assertEqual(2, W.zScale())
            W.setZScale(1)
            self.assertIsInstance(W.sliceRenderer(), QgsRasterRenderer)
            self.assertIsInstance(W.topPlaneRenderer(), QgsRasterRenderer)

            W.onLoadData()

        if SHOW_GUI:
            QGIS_APP.exec_()