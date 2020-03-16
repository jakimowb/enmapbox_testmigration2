from unittest import TestCase

import enmapboxtestdata
from hubdc.algorithm.sampling import sample_points, sample_polygons
from hubdc.core import openRasterDataset, openVectorDataset

class Test(TestCase):

    def test_sample_points(self):
        raster = openRasterDataset(filename=enmapboxtestdata.enmap)
        vector = openVectorDataset(filename=enmapboxtestdata.landcover_points)
        samples = sample_points(raster=raster, vector=vector, idField='level_1')
        print(samples)

    def test_sample_polygons(self):
        raster = openRasterDataset(filename=enmapboxtestdata.enmap)
        vector = openVectorDataset(filename=enmapboxtestdata.landcover_points)#lygons)
        samples = sample_polygons(raster=raster, vector=vector, fieldNames=['level_2', 'level_2_id'], oversampling=1, allTouched=False)
        for sample in samples:
            print(sample.fid, sample.fieldValues, sample.profiles.shape)

        samples = sample_polygons(raster=raster, vector=vector, fieldNames=['level_2', 'level_2_id'], oversampling=5, allTouched=False)
        for sample in samples:
            print(sample.fid, sample.fieldValues, sample.profiles.shape)


        samples = sample_polygons(raster=raster, vector=vector, fieldNames=['level_2', 'level_2_id'], oversampling=10, allTouched=False)
        for sample in samples:
            print(sample.fid, sample.fieldValues, sample.profiles.shape)
