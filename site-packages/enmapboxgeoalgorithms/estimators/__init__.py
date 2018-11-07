import os
from enmapboxgeoalgorithms.provider import Help

def parseFolder(package):
    estimators = dict()
    exec('import ' + package)
    dir = eval('os.path.dirname({package}.__file__)'.format(package=package))
    for basename in os.listdir(dir):
        if basename.startswith('_'): continue
        if basename.endswith('.pyc'): continue
        if os.path.splitext(basename)[0].endswith('Help'): continue

        name = basename.replace('.py', '')

        # get code snipped
        with open(os.path.join(dir, name+'.py')) as f:
            code = f.readlines()
            code = ''.join(code)

        # get help
        helpFile = os.path.join(dir, name+'Help.py')
        namespace = dict()
        if os.path.exists(helpFile):
            with open(helpFile) as f:
                codeHelp = f.readlines()
                codeHelp = ''.join(codeHelp)
            exec(codeHelp, None, namespace)


        helpAlg = namespace.get('helpAlg', Help('undocumented'))
        helpCode = namespace.get('helpCode', Help('undocumented'))

        estimators[name] = code, helpAlg, helpCode
    return estimators

def parseRegressors():
    return parseFolder(package='enmapboxgeoalgorithms.estimators.regressors')

def parseClassifiers():
    return parseFolder(package='enmapboxgeoalgorithms.estimators.classifiers')

def parseClusterers():
    return parseFolder(package='enmapboxgeoalgorithms.estimators.clusterers')

def parseTransformers():
    return parseFolder(package='enmapboxgeoalgorithms.estimators.transformers')

if __name__ == '__main__':
    from tempfile import gettempdir
    import hymaptestdata
    from hubflow.core import *
    aImage = Raster(hymaptestdata.aImage)
    aTrain = Classification(hymaptestdata.aTrain)
    aSample = aImage.sampleByClassification(classification=aTrain).argmaxProbability()

    bImage = Raster(hymaptestdata.bImage)
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
                exec(code)
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
