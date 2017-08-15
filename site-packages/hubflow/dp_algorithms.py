import numpy
from hubdc.applier import CUIProgressBar

def getProgressBar(currentProgressBar):
    if currentProgressBar is None:
        return CUIProgressBar()
    else:
        return currentProgressBar

def is2darray(array):
    return isinstance(array, numpy.ndarray) and array.ndim == 2

def matching2dArrays(array1, array2):
    return is2darray(array1) and is2darray(array2) and (array1.shape[1] == array2.shape[1])

def argmaxProbability(probabilities, minOverallCoverage=0, minWinnerCoverage=0, progressBar=None):
    assert is2darray(probabilities)
    progressBar = getProgressBar(progressBar)

    classes, n = probabilities.shape
    labels = numpy.argmax(probabilities, axis=0)[None]+1
    if minOverallCoverage > 0:
        labels[numpy.sum(probabilities, axis=0, keepdims=True) < minOverallCoverage] = 0
    if minWinnerCoverage > 0:
        labels[numpy.max(probabilities, axis=0, keepdims=True) < minWinnerCoverage] = 0

    hist, edges = numpy.histogram(labels, bins=classes, range=[1,classes+1])
    progressBar.setLabelText('argmax probability for N={}; Skipped={}; Classified=[{}]'.format(n, n-hist.sum(), ', '.join(map(str, hist))))
    return labels

def estimatorFitData(estimator, features, labels, progressBar=None):
    assert matching2dArrays(features, labels)
    progressBar = getProgressBar(progressBar)

    progressBar.setLabelText('fit sample (N={}) with {}'.format(features.shape[1], ' '.join(str(estimator).split())))
    X = features.T
    if labels.shape[0] == 1:
        y = labels.ravel()
    else:
        y = labels.T
    estimator.fit(X=numpy.float64(features.T), y=y)

def classifierPredictData(classifier, features, progressBar=None):
    assert is2darray(features)
    progressBar = getProgressBar(progressBar)

    progressBar.setLabelText('predict sample (N={}) with {}'.format(features.shape[1], str(classifier).split()))
    labels = classifier.predict(X=features.T)
    return labels

def classifyNames(names, classNames, indexBase=0):
    assert set(names).issubset(set(classNames))
    return [classNames.index(name)+indexBase for name in names]

def _synthMix(features, labels, classes, endmemberLikelihoods, classLikelihoods, n):
    assert matching2dArrays(features, labels)

    indices = dict()
    for label in range(1,classes+1):
        indices[label] = numpy.where(labels==label)[1]

    def randomLabels():
        return numpy.random.choice(classes, size=len(endmemberLikelihoods) ,p=classLikelihoods, replace=False) + 1

    def randomFractions(size):
        randomWeights = numpy.atleast_2d(numpy.float32(numpy.random.randint(low=1, high=100, size=size)))
        return randomWeights/randomWeights.sum()

    def createEndmember(label):
        nProfiles = numpy.random.choice(len(endmemberLikelihoods), p=endmemberLikelihoods, replace=False) + 1
        targetIndices = numpy.random.choice(indices[label], size=nProfiles, replace=False)
        targetProfiles = features[:, targetIndices]
        return numpy.sum(targetProfiles*randomFractions(size=nProfiles), axis=1)

    def createSyntheticMixture():
        randLabels = randomLabels()
        randEndmembers = numpy.array([createEndmember(label) for label in randLabels]).T
        randFractions = randomFractions(size=len(randLabels))
        mixedProfile = numpy.sum(randEndmembers*randFractions, axis=1)
        labelFractions = numpy.zeros(classes, dtype=numpy.float32)
        labelFractions[randLabels-1] = randFractions
        return mixedProfile, labelFractions

    mixtures, fractions = zip(*[createSyntheticMixture() for i in range(n)])
    return numpy.array(mixtures).T, numpy.array(fractions).T

def synthMix(features, labels, classes, mixingComplexities, classLikelihoods, n):
    assert matching2dArrays(features, labels)
    assert isinstance(mixingComplexities, dict)
    assert isinstance(classLikelihoods, dict)


    # cache label indices and setup 0%/100% fractions from class labels
    indices = dict()
    zeroOneFractions = numpy.zeros((classes, features.shape[1]), dtype=numpy.float32)
    for label in range(1,classes+1):
        indices[label] = numpy.where(labels==label)[1]
        zeroOneFractions[label-1, indices[label]] = 1.

    # create mixtures
    mixtures = list()
    fractions = list()
    for i in range(n):
        complexity = numpy.random.choice(mixingComplexities.keys(), p=mixingComplexities.values())
        drawnLabels = numpy.random.choice(classLikelihoods.keys(), size=complexity, replace=True, p=classLikelihoods.values())
        drawnIndices = [numpy.random.choice(indices[label]) for label in drawnLabels]
        drawnFeatures = features[:, drawnIndices]
        drawnFractions = zeroOneFractions[:, drawnIndices]
        randomWeights = numpy.atleast_2d(numpy.float32(numpy.random.randint(low=1, high=100, size=complexity)))
        randomWeights /= randomWeights.sum()
        mixtures.append(numpy.sum(drawnFeatures*randomWeights, axis=1))
        fractions.append(numpy.sum(drawnFractions*randomWeights, axis=1))

    return numpy.array(mixtures).T, numpy.array(fractions).T
