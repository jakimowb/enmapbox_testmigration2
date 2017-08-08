from sklearn.ensemble import RandomForestRegressor
from hubflow.types import *
import enmapboxtestdata

def synthMixWorkflow():

    image = Image(filename=enmapboxtestdata.enmap)
    vmask = VectorMask(filename=enmapboxtestdata.landcover, allTouched=True)
    unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=enmapboxtestdata.speclib)
    classDefinition = ClassDefinition(names=unsupervisedSample.metadata['level 2 class names'][1:],
                                      lookup=unsupervisedSample.metadata['level 2 class lookup'][3:])
    classificationSample = unsupervisedSample.classifyByClassName(names=unsupervisedSample.metadata['level 2 class spectra names'],
                                                                  classDefinition=classDefinition)
    classificationSample.scaleFeaturesInplace(factor=10000.)
    probabilitySample = classificationSample.synthMix(mixingComplexities={2:0.5, 3:0.3, 4:0.2}, classLikelihoods='proportional', n=1000)
    regressor = Regressor(sklEstimator=RandomForestRegressor())
    regressor.fit(sample=probabilitySample)
    regressor.predict(filename=r'c:\output\fractions.img', image=image, vmask=vmask)

if __name__ == '__main__':
    synthMixWorkflow()

