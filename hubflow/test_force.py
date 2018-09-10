import matplotlib
matplotlib.use('QT5Agg')
from matplotlib import pyplot

from unittest import TestCase
from hubflow.force import *

from sklearn.ensemble import RandomForestClassifier

folderForce = r'C:\Work\data\FORCE\crete'
forceDB = ForceDB(folder=folderForce, spatialFilter=SpatialFilter(tileNames=['X0107_Y0102', 'X0107_Y0103']))

outdir = r'c:\output\force'

CUIProgressBar.SILENT = False

class Test(TestCase):

    def test_ForceDB(self):
        print(forceDB.folder())
        print(forceDB.levels())
        print(forceDB.forceL2DB())

    def test_ForceL2DB(self):
        forceL2DB = forceDB.level2()
        for forceTile in forceL2DB.tiles():
            print(forceTile.name())

        forceL2DB.mean(basename='2015_mean.bsq', level='levelRabe',
                       dateRangeFilter=DateRangeFilter(start='20151001', end='20151008'),
                       sensorFilter=SensorFilter(sensors=['LND07', 'LND08']))


    def test_ForceL2Tile(self):
        tile = forceDB.forceL2DB().forceL2Tile(name='X0107_Y0102')
        print(tile.name())
        filters = [DateRangeFilter(start='20151001', end='20151008'),
                   SensorFilter(sensors=['LND07', 'LND08']),
                   ProductFilter(products=['BOA'])]
        collection = tile.collection(filters=filters)
        print(collection)

        mean = tile.mean(filename=r'/vsimem/mean.bsq',
                         dateRangeFilter=DateRangeFilter(start='20151001', end='20151008'),
                         sensorFilter=SensorFilter(sensors=['LND07', 'LND08']))

        mean.plotMultibandColor(rgbindex=(4-1, 5-1, 3-1), rgbvmin=300, rgbpmax=98)


    def test_ForceL2Collection(self):
        filters = [DateRangeFilter(start='20180101', end='20190101'),
                   SensorFilter(sensors=['LND07', 'LND08'])]
        tile = forceDB.level2(filters=filters).tile(name='X0107_Y0102')

        boa = tile.collection(filters=[ProductFilter(products=['BOA'])])
        cld = tile.collection(filters=[ProductFilter(products=['CLD'])])

        print(boa)
        print(cld)

        for raster in boa.rasters():
            print(raster)
        for raster in cld.rasters():
            print(raster)

    def test_ClassificationWorkflow(self):


        # init database for region of interest (i.e. spatial filter)

        forceDB = ForceDB(folder=r'C:\Work\data\FORCE\crete',
                          spatialFilter=SpatialFilter(tileNames=['X0107_Y0102', 'X0107_Y0103']))

        # create mean and std composites for year 2015

        # - use date range and sensor filter

        dateRangeFilter = DateRangeFilter(start='20150101', end='20151231')
        sensorFilter = SensorFilter(sensors=['LND07', 'LND08'])

        # - mean and std methods are called from the "ForceL2Tile" object

        forceDB.level2().mean(basename='2015_mean.bsq', levelName='levelComposites',
                              dateRangeFilter=dateRangeFilter,
                              sensorFilter=sensorFilter)

        forceDB.level2().std(basename='2015_std.bsq', levelName='levelComposites',
                             dateRangeFilter=dateRangeFilter,
                             sensorFilter=sensorFilter)

        # sample lucas points from composites

        lucas = VectorClassification(filename=r'C:/Work/data/gms/lucas/eu27_lucas_2012_subset1.shp',
                                     classAttribute='LC4_ID',
                                     classDefinition=ClassDefinition(classes=12))

        sources = [forceDB.level(levelName='levelComposites',
                                 filters=[FileFilter(extensions=['.bsq'])])] # use all *.bsq files as input

        sample = forceDB.extractClassificationSample(filename=r'c:\output\sample.pkl', locations=lucas, sources=sources)

        # fit and predict

        rfc = Classifier(sklEstimator=RandomForestClassifier())
        rfc.fit(sample)
        forceDB.predict(basename='2015_classification.bsq', levelName='levelClassification', estimator=rfc, sources=sources)


    def test_Report(self):

        print(forceDB)
        tile = forceDB.level2().tile(name='X0107_Y0102')
        result = OrderedDict()
        for raster in tile.collection(filters=[ProductFilter(products=['BOA'])]).rasters():
            y = basename(raster.filename())[:4]
            result[y] = result.get(y, 0) + 1

        for y, n in result.items():
            print('{} = {}'.format(y, n))

    def test_debug(self):

        pass



if __name__ == '__main__':
    print('output directory: ' + outdir)
