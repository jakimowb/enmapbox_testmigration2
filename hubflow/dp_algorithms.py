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