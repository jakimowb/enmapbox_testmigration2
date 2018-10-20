import matplotlib
matplotlib.use('QT5Agg')
from matplotlib import pyplot

from os.path import join
from unittest import TestCase
from hubdc.core2 import *
from hubdc.inputformat import force, generic


gdal.UseExceptions()

from sklearn.ensemble import RandomForestClassifier

folderForce = r'C:\Work\data\FORCE\berlin'
folderL2 = join(folderForce, 'level2')

outdir = r'c:\output\force'

tilingScheme = TilingScheme()
if 0:
    tilingScheme.addTile(Tile(name='x1_y1', extent=Extent(xmin=13, xmax=13.5, ymin=52.5, ymax=53, projection=Projection.WGS84())))
    tilingScheme.addTile(Tile(name='x2_y1', extent=Extent(xmin=13.5, xmax=14, ymin=52.5, ymax=53, projection=Projection.WGS84())))
    tilingScheme.addTile(Tile(name='x1_y2', extent=Extent(xmin=13, xmax=13.5, ymin=52, ymax=52.5, projection=Projection.WGS84())))
    tilingScheme.addTile(Tile(name='x2_y2', extent=Extent(xmin=13.5, xmax=14, ymin=52, ymax=52.5, projection=Projection.WGS84())))
else:
    tilingScheme.addTile(Tile(name='x1_y1', extent=Extent(xmin=13.0, xmax=14, ymin=52, ymax=53, projection=Projection.WGS84())))

def computeKwds(basename, noDataValues=None, categoryNames=None):
    return {'tilingScheme': tilingScheme,
            'resolution': 0.001,
            'filename': join(outdir, basename),
            'noDataValues': noDataValues,
            'categoryNames': categoryNames}


Projection.UTM(zone=33, north=True)
class Test(TestCase):


    def test_david(self):

        raster = force.collections(folder=folderL2, ext='.tif').l8.first()\
                    .select(('NIR', 'RED', 'BLUE', 'GREEN'))\
                    .cache() # cached die benötigten Bänder

        indexCollection = List((('NIR', 'RED'), ('NIR', 'BLUE'), ('NIR', 'GREEN')))\
                             .map(function=lambda bandNames: raster.normalizedDifference(bandNames))

        indexRaster = indexCollection\
                         .toBands()\
                         .compute(**computeKwds('stack.tif'))

        a=indexRaster


    def test_arrays(self):
        raster = force.collections(folder=folderL2, ext='.tif').l8.first()
        a,m = raster.band(name='NIR').arrays(grid=Grid(extent=tilingScheme.extent(name='x1_y1'), resolution=0.01))
        print(a.shape)
        print(m.shape)

        a,m = raster.arrays(grid=Grid(extent=tilingScheme.extent(name='x1_y1'), resolution=0.001))
        print(np.shape(a))
        print(np.shape(m))

    def test_computeRaster(self):

        raster = force.collections(folder=folderL2, ext='.tif').l8.first()\
                      .compute(**computeKwds('landsat-NIR-SWIR1-Red.tif'))

    def test_cache(self):

        raster = force.collections(folder=folderL2, ext='.tif').l8.first().multiply(1).multiply(1).multiply(1) #.compute(**computeKwds('raster.bsq'))
        raster = force.collections(folder=folderL2, ext='.tif').l8.first()
        raster = raster.cache()
        a = raster.select(force.BAND_Red)
        b = raster.select(force.BAND_Green)
        ca = a.compute(**computeKwds('red.tif'))
        cb = b.compute(**computeKwds('green.tif'))
        #assert 0

    def test_computeRasterUpdateMask(self):

        raster = force.collections(folder=folderL2, ext='.tif').l8.first()
        raster = (raster.select(bandNames=[force.BAND_NearInfrared,
                                           force.BAND_ShortwaveInfrared1,
                                           force.BAND_Red])
                        .updateMask(mask=raster.select(force.BAND_CloudAndCloudShadowDistance).not_equal(0).cache())
                        .compute(**computeKwds('landsat-NIR-SWIR1-Red.tif', noDataValues=[-1]*3)))

    def test_computeNDVI(self):

        raster = force.collections(folder=folderL2, ext='.tif').l8.first()
        ndvi = (raster.select(bandNames=[force.BAND_NearInfrared, force.BAND_Red])
                      .updateMask(mask=raster.select(force.BAND_CloudAndCloudShadowDistance).not_equal(0))
                      .normalizedDifference()#bandNames=['NIR', 'Red'])
                      .compute(**computeKwds('ndvi.tif', noDataValues=[-1])))

    def test_computeMedian(self):
        l8 = force.collections(folder=folderL2, ext='.tif').l8
        median = (l8.filterDate(start='2017', end='2018')
                    #.slice(0,5)
                    .map(lambda raster: raster.select(bandNames=[force.BAND_NearInfrared,
                                                                 force.BAND_ShortwaveInfrared1,
                                                                 force.BAND_Red])
                                              .updateMask(mask=raster.select(force.BAND_CloudAndCloudShadowDistance).not_equal(0)))
                    .median() #bandNames=['NIR', 'SWIR1', 'Red'])
                    .compute(**computeKwds(basename='2017_median.tif', noDataValues=[-9999]*3)))

        a=median

    def test_sampleRegions(self):

        points = openVectorDataset(filename=r'C:\Work\data\gms\lucas\eu27_lucas_2012_subset1.shp')
        bandNames = [force.BAND_NearInfrared, force.BAND_ShortwaveInfrared1, force.BAND_Red]

        l8 = force.collections(folder=folderL2, ext='.tif').l8
        median = (l8.filterDate(start='201711', end='2018')
                    .map(lambda raster: raster.select(bandNames=bandNames)
                                              .updateMask(mask=raster.select(force.BAND_CloudAndCloudShadowDistance).not_equal(0)))
                    .median(bandNames=bandNames).rename(bandNames=bandNames)
                    #.compute(*computeKwds(basename='2017_median.tif', noDataValues=[-9999] * 3))
                  )

        training = median.sampleRegions(vectorDataset=points, idProperty='POINT_ID',
                                        tilingScheme=tilingScheme, resolution=0.001)

        classifier = Classifier(sklClassifier=RandomForestClassifier())
        classifier.fit(features=training, classProperty='LC4_ID', inputProperties=bandNames)
        classification = median.predict(estimator=classifier)\
                               .compute(**computeKwds(basename='rfcClassification.bsq'))


    def test_forceQAI(self):
        raster = force.collections(folder=folderL2, ext='.tif').l8.first()
        cloudState = raster.inflate(offsets=[1], nbits=[2], bandName=force.BAND_QualityAssuranceInformation) \
                           .rename('Cloud state') \
                           .compute(**computeKwds(basename='qai_cloudState.tif'))
        cloudShadowFlag = raster.inflate(offsets=[3], nbits=[1], bandName=force.BAND_QualityAssuranceInformation) \
                                .rename('Cloud shadow flag') \
                                .compute(**computeKwds(basename='qai_cloudShadowFlag.tif'))

        allInflated = raster.inflate(bandName=force.BAND_QualityAssuranceInformation,
                                     offsets=(0, 1, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15),
                                     nbits=(1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1))\
                            .rename(('Valid data', 'Cloud state', 'Cloud shadow flag', 'Snow flag', 'Water flag',
                                     'Aerosol state', 'Subzero flag', 'Saturation flag', 'High sun zenith flag',
                                     'Illumination state', 'Slope flag', 'Water vapor flag', 'Empty'))\
                            .compute(**computeKwds(basename='qai_inflated.tif'))


    def test_rasterNoneTiled(self):
        from enmapboxtestdata import enmap

        from hubdc.inputformat import generic
        raster = generic.raster(filename=enmap).select([2,1,0])
        raster.compute(filename=join(outdir, 'hymap.tif'))

    def test_select(self):

        sentinel2 = force.collections(folder=folderL2, ext='.tif').s2.first()

        print(sentinel2.select(0).bandNames())      # by index
        print(sentinel2.select('Blue').bandNames()) # by name
        print(sentinel2.select(492.).bandNames())   # by wavelength






    def test_median(self):

        medianNDVI = (force.collections(folder=folderL2, ext='.tif').l8
                           .filterDate('2017', '2018')
                           .map(lambda raster: (raster.normalizedDifference(['NIR', 'Red'])
                                                      .updateMask(mask=raster.select('CLD')).not_equal(0)))
                           .median()
                           .compute(**computeKwds(basename='medianNDVI.bsq', noDataValues=[-1])))

#        mask = raster.select('CLD').not_equal(0)
#        nir = raster.select('NIR').updateMask(mask=mask).compute(**computeKwds('nir.bsq', [-1]))


    def test_pipeline(self):

        raster = force.collections(folder=folderL2, ext='.tif').l8.first()

        ndvi = (raster
                  .multiply(1)
                  .select(bandNames=['NIR', 'Red']).compute(**computeKwds('NIR_Red.bsq'))
                  .normalizedDifference(bandNames=['NIR', 'Red'])
                  .where(condition=raster.select('CLD').equal(0), raster2=-1)
                  #.multiply(raster2=raster.select('CLD').not_equal(0))

                .compute(**computeKwds('ndvi.bsq')))

    def test_collectionForce(self):

        #print(force.tilingScheme.tiles()['X0070_Y0043'].projection())
        #return


        point = Geometry(wkt='POINT(13.7 52.5)', projection=Projection.WGS84())




        forceCollections = force.collections(folder=folderL2, ext='.tif')
        filtered = (forceCollections.l8
                        .filterDate('20170101', '20171231')
                        .filterBounds(point)
                        .map(lambda raster: raster.side(print))
                        .map(lambda raster: raster.normalizedDifference(bandNames=['NIR', 'Red'], filename=r'c:\ndvi.bsq' )))




        print(len(filtered))

        #for raster in filtered.rasters():
        #    print(raster)
        #    break

    def test_Raster(self):

        # get the first landsat 8 raster in the collection
        raster = force.collections(folder=folderL2, ext='.tif').l8.first()

        # define output tiling scheme
        tilingScheme = TilingScheme()
        tilingScheme.addTile(name='x1_y1', extent=Extent(xmin=13, xmax=13.5, ymin=52, ymax=52.5, projection=Projection.WGS84()))
        tilingScheme.addTile(name='x2_y1', extent=Extent(xmin=13.5, xmax=14, ymin=52, ymax=52.5, projection=Projection.WGS84()))
        tilingScheme.addTile(name='x1_y2', extent=Extent(xmin=13, xmax=13.5, ymin=52.5, ymax=53, projection=Projection.WGS84()))
        tilingScheme.addTile(name='x2_y2', extent=Extent(xmin=13.5, xmax=14, ymin=52.5, ymax=53, projection=Projection.WGS84()))



        # define cloud / cloud shadow mask
        onTheFly = True
        cld = raster.select(bandNames=['CLD'])
        if onTheFly:
            mask = cld.updateTransform(function=lambda cld: cld == 0)
        else:
            mask = cld.expression(expression='cld == 0', variables={'cld': cld},
                                  tilingScheme=tilingScheme, resolution = 0.001,
                                  filename = join(outdir, 'ndvi.bsq'))

        raster = raster.updateMask(mask=mask)

        ndvi = raster.normalizedDifference(bandNames=['NIR', 'Red'],
                                           tilingScheme=tilingScheme, resolution=0.001,
                                           filename=join(outdir, 'ndvi.bsq'))

        a= ndvi

    def test_collectionNDVI(self):

        l2Collections = force.collections(folder=folderL2, ext='.tif')
        l8 = l2Collections.l8
        s2 = l2Collections.s2
        all = l8 #.merge(s2)

        def addNDVI(raster):
            assert isinstance(raster, Raster)
            return (raster.multiply(1).addRaster(raster.normalizedDifference(bandNames=['NIR', 'Red']).rename(['NDVI'])))

        all = (all.filterDate(start='2017-01-01', end='2017-12-31')
                  .map(function=addNDVI))

        #median = all.median(bandNames=['Red', 'NIR', 'SWIR1', 'NDVI'])
        #cmean = median.compute(**computeKwds('mean'))
        a=1



if __name__ == '__main__':
    print('output directory: ' + outdir)
