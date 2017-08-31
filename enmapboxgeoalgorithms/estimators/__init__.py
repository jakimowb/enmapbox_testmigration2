import os

def parseFolder(package):
    estimators = dict()
    exec 'import ' + package
    dir = eval('os.path.dirname({package}.__file__)'.format(package=package))
    for basename in os.listdir(dir):
        if basename.startswith('_'): continue
        if basename.endswith('.pyc'): continue
        name = basename.replace('.py', '')
        with open(os.path.join(dir, basename)) as f:
            lines = f.readlines()
            lines = ''.join(lines)
        estimators[name] = lines
    return estimators

def parseRegressors():
    return parseFolder(package='enmapboxgeoalgorithms.estimators.regressors')

def parseClassifiers():
    return parseFolder(package='enmapboxgeoalgorithms.estimators.classifiers')

if __name__ == '__main__':
    from tempfile import gettempdir
    import hymaptestdata
    from hubflow.types import *
    aImage = Image(hymaptestdata.aImage)
    aTrain = Classification(hymaptestdata.aTrain)
    aSample = aImage.sampleByClassification(classification=aTrain).classifyByProbability()

    bImage = Image(hymaptestdata.bImage)
    bTrain = Regression(hymaptestdata.bTrain)
    bSample = bImage.sampleByRegression(regression=bTrain)

    outdir = os.path.join(gettempdir(), 'eb_test')
    for Type, estimators, image, sample in [(Regressor, parseRegressors(), bImage, bSample), (Classifier, parseClassifiers(), aImage, aSample)]:
        for name, code in estimators.items():
            try: del sklEstimator
            except: pass

            print('##############')
            print(name)
            #print(code)
            try:
                exec code
                sklEstimator = eval('estimator')
            except:
                print('can not evaluate '+name)

            #print(sklEstimator)
            predictionFilename = os.path.join(outdir, name+'.img')
            if not os.path.exists(predictionFilename):
                estimator = Type(sklEstimator=sklEstimator)
                estimator.fit(sample=sample)
                estimator.predict(predictionFilename=predictionFilename, image=image)
    print('output dir: '+outdir)
