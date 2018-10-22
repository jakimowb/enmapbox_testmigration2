from hubflow.force import *
from sklearn.ensemble import RandomForestClassifier

def run():

    # init database for region of interest (i.e. spatial filter)

    forceDB = ForceDB(folder=r'C:\Work\data\FORCE\crete',
                      spatialFilter=SpatialFilter(tileNames=['X0107_Y0102', 'X0107_Y0103']))

    forceDB.level(levelName=).

    getForce(folder, level='level2', product='BOA')
    l8refl2018 = getForce(folder2\'level2')
    l8refl2018.select(['B1', 'pixel_qa'])




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


if __name__ == '__main__':
    run()