
import unittest
from osgeo import gdal, gdal_array, osr
from enmapbox.testing import initQgisApplication, TestObjects

QGIS_APP = initQgisApplication(loadProcessingFramework=False, loadEditorWidgets=False)

SHOW_GUI = True

from .imagecube import *
class VTest(unittest.TestCase):

    def createImageCube(self, nb=10, ns=20, nl=30, crs='EPSG.32633')->QgsRasterLayer:


        path = '/vsimem/imagecube.tiff'

        array = np.fromfunction(lambda i,j,k: i+j+k, (nb, nl, ns), dtype=np.uint32)
        #array = array * 10
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


    def test_samplingGrid(self):

        from enmapboxtestdata import enmap as pathEnMAP
        lyr = QgsRasterLayer(pathEnMAP)

        ext1 = lyr.extent()
        ns, nl = lyr.width(), lyr.height()
        cache = 1024**4
        nnl, nns = samplingGrid(lyr, ext1, ncb=3, max_size=cache)
        self.assertIsInstance(nnl, int)
        self.assertIsInstance(nns, int)
        self.assertTrue(nnl >= 0 and nns >= 0)
        self.assertTrue(nnl == nl and nns == ns)

        #reduce cache
        nnl, nns = samplingGrid(lyr, ext1, ncb=3, max_size=1024*2)
        self.assertTrue(nnl < nl and nns < ns)

        f1 = ext1.width() / ext1.height()
        f2 = nns / nnl
        self.assertAlmostEqual(f1, f2, 1)
        s = ""

    def test_renderJob(self):
        lyr = self.createImageCube()
        job = ImageCubeRenderJob('JOB', lyr, lyr.renderer())

        self.assertEqual(job.id(), 'JOB')
        from enmapbox.externals.qps.layerproperties import showLayerPropertiesDialog, rendererFromXml, rendererToXml
        xml1 = rendererToXml(lyr.renderer()).toString()
        xml2 = rendererToXml(job.renderer()).toString()
        self.assertEqual(xml1, xml2)
        self.assertEqual(job.extent(), lyr.extent())

    def test_widget(self):

        W = ImageCubeWidget()
        W.show()


        from enmapboxtestdata import enmap as pathEnMAP
        from enmapboxtestdata import hires as pathHyMap

        pathLargeImage = r'R:\temp\temp_bj\Cerrado\cerrado_evi.vrt'
        pathLargeImage = r'Q:\Processing_BJ\01_Data\level2\X0016_Y0046\20140803_LEVEL2_LND07_BOA.tif'

        layers = [self.createImageCube()]
        pathes = [pathEnMAP, pathHyMap, pathLargeImage]
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


            ext1 = lyr.extent()
            self.assertEqual(ext1, W.extent())
            self.assertEqual(lyr.crs(), W.crs())
            ext2 = QgsRectangle(ext1)
            ext2.setXMinimum(ext2.xMinimum()-5)

            W.setExtent(ext2)
            self.assertEqual(W.extent(), ext2)


        if True:
            W.setRasterLayer(layers[1])
            W.startDataLoading()

        if SHOW_GUI:
            QGIS_APP.exec_()