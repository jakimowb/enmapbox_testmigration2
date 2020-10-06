import unittest
import os
from osgeo import gdal
import numpy as np
from enmapbox.testing import TestCase, TestObjects

class HUBFlowTests(TestCase):
    def test_wavelength(self):

        # define raster image with ENVI-like metadata
        root = self.createTestOutputDirectory() / 'hubflowtests'
        os.makedirs(root, exist_ok=True)
        pathImg = root / 'testimag.tif'
        # create a dataset with 5 bands, 10 lines and 15 samples
        ds = TestObjects.createRasterDataset(path=pathImg, ns=15, nl=10, nb=5, wlu='nm')
        self.assertIsInstance(ds, gdal.Dataset)

        from enmapbox.gui.utils import parseWavelength
        wl, wlu = parseWavelength(ds)

        enviWL = f"{{{','.join([str(v) for v in wl])}}}"

        print(f'Wavelength: {enviWL}')
        print(f'Wavelength units: {wlu}')

        ds.SetMetadataItem('wavelength', enviWL, 'ENVI')
        ds.SetMetadataItem('wavelength units', wlu, 'ENVI')
        ds.FlushCache()
        del ds

        # 2. read metadata with GDAL
        ds = gdal.Open(pathImg.as_posix())
        # retrieval of Wavelength and Wavelength Unit according to
        # ENVI Headerfile Definition: https://www.harrisgeospatial.com/docs/enviheaderfiles.html
        self.assertEqual(ds.GetMetadataItem('wavelength', 'ENVI'), enviWL)
        self.assertEqual(ds.GetMetadataItem('wavelength units', 'ENVI'), wlu)

        # 3. read metadata with hubflow
        from hubflow.core import Raster
        hubflowRaster = Raster(pathImg.as_posix())

        # HUB Flow Fail
        hubflowWL = hubflowRaster.metadataWavelength()

        for v1, v2 in zip(wl, hubflowWL):
            self.assertEqual(v1, v2)





if __name__ == '__main__':
    unittest.main()
