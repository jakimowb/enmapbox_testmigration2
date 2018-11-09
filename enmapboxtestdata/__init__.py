from os.path import dirname, join

__version__ = '0.6'

enmap = join(dirname(__file__), 'enmap_berlin.bsq')
hires = join(dirname(__file__), 'hires_berlin.bsq')
landcover_polygons = join(dirname(__file__), 'landcover_berlin_polygon.shp')
landcover_points = join(dirname(__file__), 'landcover_berlin_point.shp')
library = join(dirname(__file__), 'library_berlin.sli')

def createEnmapClassification(filename='/vsimem/enmap_classification_{level}', level='level_2_id',
                              minOverallCoverage=1.0, minDominantCoverage=0.5, oversampling=5):
    '''
    Create a classification map from landcover polygons.

    :param str filename: output path
    :param str level: class id attribute
    :param float minOverallCoverage: passed to VectorClassification
    :param float minDominantCoverage: passed to VectorClassification
    :param int oversampling: passed to VectorClassification
    :return:
    '''
    from hubflow.core import VectorClassification, Classification, Raster
    vectorClassification = VectorClassification(filename=landcover_polygons, classAttribute=level,
                                                minOverallCoverage=minOverallCoverage,
                                                minDominantCoverage=minDominantCoverage,
                                                oversampling=oversampling)

    try:
        filename.format(level=level)
    except:
        pass

    return Classification.fromClassification(filename=filename, classification=vectorClassification,
                                             grid=Raster(filename=enmap).grid())

def createEnmapFraction(
        filename='/vsimem/enmap_fraction', level='level_2_id', minOverallCoverage=1., oversampling=5):
    """
    Create a fraction map from landcover polygons.

    :param str filename: output path
    :param str level: class id attribute
    :param float minOverallCoverage: passed to VectorClassification
    :param int oversampling: passed to VectorClassification
    :rtype: hubflow.core.Fraction
    """
    from hubflow.core import VectorClassification, Fraction, Raster
    vectorClassification = VectorClassification(filename=landcover_polygons, classAttribute=level,
                                                minOverallCoverage=minOverallCoverage, oversampling=oversampling)
    return Fraction.fromClassification(filename=filename, classification=vectorClassification,
                                       grid=Raster(filename=enmap).grid())

def createClassifier(level='level_2_id'):
    '''
    Create a fitted Random Forest Classifier using enmap raster and landcover points.

    :param str level: class id attribute
    :rtype: hubflow.core.Classifier
    '''
    from hubflow.core import VectorClassification, Classification, ClassificationSample, Classifier, Raster
    from sklearn.ensemble import RandomForestClassifier

    raster = Raster(filename=enmap)
    points = VectorClassification(filename=landcover_points, classAttribute=level)
    classification = Classification.fromClassification(
        filename='/vsimem/points.bsq', classification=points, grid=raster.grid())
    sample = ClassificationSample(raster=raster, classification=classification)
    rfc = Classifier(sklEstimator=RandomForestClassifier())
    rfc.fit(sample=sample)
    return rfc

def createRegressor(level='level_2_id'):
    '''
    Create a fitted Random Forest Regressor using enmap raster and landcover polygons.

    :param str level: class id attribute
    :rtype: hubflow.core.Regressor
    '''

    from hubflow.core import VectorClassification, Fraction, RegressionSample, Regressor, Raster
    from sklearn.ensemble import RandomForestRegressor

    raster = Raster(filename=enmap)
    vectorClassification = VectorClassification(filename=landcover_polygons, classAttribute=level,
                                                minOverallCoverage=1., oversampling=5)
    fraction = Fraction.fromClassification(filename='/vsimem/fraction.bsq', classification=vectorClassification,
                                           grid=raster.grid())
    sample = RegressionSample(raster=raster, regression=fraction)
    rfr = Regressor(sklEstimator=RandomForestRegressor())
    rfr.fit(sample=sample)
    return rfr

def createClusterer():
    '''
    Create a fitted KMeans Clusterer using enmap raster.

    :rtype: hubflow.core.Clusterer
    '''

    from hubflow.core import Clusterer, Sample, Raster, VectorMask
    from sklearn.cluster import KMeans

    raster = Raster(filename=enmap)
    sample = Sample(raster=raster, mask=VectorMask(filename=landcover_polygons))
    kmeans = Clusterer(sklEstimator=KMeans())
    kmeans.fit(sample=sample)
    return kmeans

def createTransformer():
    '''
    Create a fitted PCA Transformer using enmap raster.

    :rtype: hubflow.core.Transformer
    '''

    from hubflow.core import Transformer, Sample, Raster, VectorMask
    from sklearn.decomposition import PCA

    raster = Raster(filename=enmap)
    sample = Sample(raster=raster, mask=VectorMask(filename=landcover_polygons))
    pca = Transformer(sklEstimator=PCA())
    pca.fit(sample=sample)
    return pca

