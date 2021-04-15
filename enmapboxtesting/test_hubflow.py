import unittest
import os
import pathlib
from osgeo import gdal
import pickle
import json
import numpy as np

from enmapbox.gui.datasourcemanager import DataSourceManager, DataSourceManagerTreeModel, DataSourceTreeView
from enmapbox.testing import TestCase, TestObjects
import enmapboxtestdata
from qgis.core import QgsApplication, QgsProcessingRegistry, \
    QgsProcessingAlgorithm, \
    QgsProcessingContext, \
    QgsProcessingFeedback

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


    def test_create_RFC_model(self):

        configuration = {}



        def onFeedbackProgress(v: float):
            print(f'Progress {v}')

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        feedback.progressChanged.connect(onFeedbackProgress)

        from enmapbox import initAll
        initAll()
        procReg = QgsApplication.instance().processingRegistry()
        assert isinstance(procReg, QgsProcessingRegistry)

        DIR_TMP = self.createTestOutputDirectory()
        path_rfc_pkl = DIR_TMP / 'test_rfc.pkl'

        if not path_rfc_pkl.is_file():
            from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import \
                FitRandomForestClassifierAlgorithm
            a = FitRandomForestClassifierAlgorithm()
            aid = f'enmapbox:{a.id()}'
            alg: FitRandomForestClassifierAlgorithm = procReg.algorithmById(aid)
            self.assertIsInstance(alg, QgsProcessingAlgorithm)
            self.assertIsInstance(alg, FitRandomForestClassifierAlgorithm)

            parameters = {FitRandomForestClassifierAlgorithm.P_RASTER: enmapboxtestdata.enmap,
                          FitRandomForestClassifierAlgorithm.P_CLASSIFICATION: enmapboxtestdata.landcover_points,
                          FitRandomForestClassifierAlgorithm.P_OUTPUT_CLASSIFIER: path_rfc_pkl.as_posix()}
            self.assertTrue(alg.checkParameterValues(parameters, context))

            results = alg.processAlgorithm(parameters, context, feedback)
            self.assertIsInstance(results, dict)

            path_pkl = results.get(FitRandomForestClassifierAlgorithm.P_OUTPUT_CLASSIFIER)
            path_pkl = pathlib.Path(path_pkl)
            self.assertEqual(path_pkl, path_rfc_pkl)
        else:
            path_pkl = path_rfc_pkl

        self.assertTrue(path_pkl.is_file())

        ds = DataSourceManager()
        dm = DataSourceManagerTreeModel(None, ds)
        dtv = DataSourceTreeView()
        dtv.setModel(dm)

        path_sample_pkl = DIR_TMP / 'sample.pkl'
        path_D_json = DIR_TMP / 'example.json'
        path_D_pkl = DIR_TMP / 'example.pkl'
        D = {'String': 'A',
             'List': ['b', 'B', {'a': 'subdictionary'}],
             'Tuple': tuple([f'arg {i}' for i in range(26)]),
             }
        # D['Recursive'] = [D]

        D2 = D.copy()
        D2['Array'] = np.ones(shape=(64,24), dtype=float)

        with open(path_D_json, 'w', encoding='utf-8') as f:
            json.dump(D, f)
        with open(path_D_pkl, 'wb') as f:
            pickle.dump(D2, f)

        for p in [path_sample_pkl, path_pkl, path_D_json, path_D_pkl]:
            if p.is_file():
                sources = ds.addSource(p)
                self.assertTrue(len(sources) > 0)

        self.showGui(dtv)


if __name__ == '__main__':
    unittest.main()
