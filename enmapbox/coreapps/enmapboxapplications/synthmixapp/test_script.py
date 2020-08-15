from hubflow.core import *
import enmapboxtestdata
from enmapboxapplications.synthmixapp.script import synthmixRegressionEnsemble
from sklearn.ensemble import RandomForestRegressor

def test1():
    points = VectorClassification(filename=enmapboxtestdata.landcover_points, classAttribute='level_2_id')
    enmap = Raster(filename=enmapboxtestdata.enmap)
    classification = Classification.fromClassification(classification=points, grid=enmap.grid(),
                                                           filename='/vsimem/classification__.bsq')
    sample = ClassificationSample(raster=enmap, classification=classification)
    outdir = r'c:\test'
    speclib = EnviSpectralLibrary.fromSample(sample=sample, filename=join(outdir, 'speclib.sli'))

    raster2 = speclib.raster()
    classification2 = Classification.fromEnviSpectralLibrary(filename='/vsimem/classification2.bsq',
                                                            library=speclib, attribute='id')

    synthmixRegressionEnsemble(
        filename='/vsimem/syntmix',
        classificationSample=ClassificationSample(raster=raster2, classification=classification2),
        targets=[1],
        regressor=Regressor(sklEstimator=RandomForestRegressor()),
        raster=enmap,
        runs=3,
        n=100,
        mixingComplexities={2: 1.})


def run():
    test1()

run()
