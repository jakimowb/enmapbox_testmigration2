from os.path import dirname, join

enmap = join(dirname(__file__), 'enmap_berlin.bsq')
hires = join(dirname(__file__), 'hires_berlin.bsq')
landcover_polygons = join(dirname(__file__), 'landcover_berlin_polygon.shp')
landcover_points = join(dirname(__file__), 'landcover_berlin_point.shp')
library = join(dirname(__file__), 'library_berlin.sli')

def createEnmapClassification(filename='/vsimem/enmap_classification_{level}', level='level_2_id',
                              minOverallCoverage=1.0, minDominantCoverage=0.5, oversampling=5):
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

def createEnmapFraction(filename='/vsimem/enmap_fraction_{level}', level='level_2_id',
                        minOverallCoverage=1., oversampling=5):
    from hubflow.core import VectorClassification, Fraction, Raster
    vectorClassification = VectorClassification(filename=landcover_polygons, classAttribute=level,
                                                minOverallCoverage=minOverallCoverage, oversampling=oversampling)

    try:
        filename.format(level=level)
    except:
        pass

    return Fraction.fromClassification(filename=filename, classification=vectorClassification,
                                       grid=Raster(filename=enmap).grid())
