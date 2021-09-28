from os.path import dirname, join

# raster
enmap_uncompressed = join(dirname(__file__), 'enmap_uncompressed.tif')
landcover_raster_1m = join(dirname(__file__), 'landcover_raster_1m.tif')
landcover_raster_30m = join(dirname(__file__), 'landcover_raster_30m.tif')
landcover_raster_1m_epsg3035 = join(dirname(__file__), 'landcover_raster_1m_EPSG3035.tif')
landcover_raster_30m_epsg3035 = join(dirname(__file__), 'landcover_raster_30m_EPSG3035.tif')
landcover_raster_1m_3classes = join(dirname(__file__), 'landcover_raster_1m_3classes.tif')
landcover_map_l2 = join(dirname(__file__), 'landcover_map_l2.tif')
landcover_map_l3 = join(dirname(__file__), 'landcover_map_l3.tif')

# vector
landcover_polygons_3classes = join(dirname(__file__), 'landcover_berlin_polygon_3classes.gpkg')
landcover_polygons_3classes_id = join(dirname(__file__), 'landcover_berlin_polygon_3classes_id.gpkg')
landcover_polygons_3classes_epsg4326 = join(dirname(__file__), 'landcover_berlin_polygon_3classes_EPSG4326.gpkg')

landcover_points_singlepart_epsg3035 = join(dirname(__file__), 'landcover_berlin_point_singlepart_3035.gpkg')
landcover_points_multipart_epsg3035 = join(dirname(__file__), 'landcover_berlin_point_multipart_3035.gpkg')

# library
library = join(dirname(__file__), 'library.gpkg')

# classification dataset (X, y)
classificationDatasetAsVector = join(dirname(__file__), 'classification_dataset.gpkg')
classificationDatasetAsCsv = join(dirname(__file__), 'classification_dataset.csv')
classificationDatasetAsPkl = join(dirname(__file__), 'classification_dataset.pkl')

# classification dataset (X, y) as dump
classifierDumpPkl = join(dirname(__file__), 'classifier.pkl')
classifierDumpJson = join(dirname(__file__), 'classifier.pkl.json')

# classification dataset (X, y) as FORCE text files
classificationSampleAsCsv = (join(dirname(__file__), 'force_features.csv'), join(dirname(__file__), 'force_labels.csv'))

# spectral response functions
landsat8_sectralResponseFunctionLibrary = join(dirname(__file__), 'landsat8_srf.gpkg')
