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
    progressBar.setLabelText('argmax probability (N={}, Classes={})'.format(n, classes))
    labels = numpy.argmax(probabilities, axis=0)[None]+1
    if minOverallCoverage > 0:
        labels[numpy.sum(probabilities, axis=0, keepdims=True) < minOverallCoverage] = 0
    if minWinnerCoverage > 0:
        labels[numpy.max(probabilities, axis=0, keepdims=True) < minWinnerCoverage] = 0
    return labels

def classifierFitData(classifier, features, labels, progressBar=None):
    assert matching2dArrays(features, labels)
    progressBar = getProgressBar(progressBar)

    progressBar.setLabelText('fit classification sample (N={}) with {}'.format(features.shape[1], ' '.join(str(classifier).split())))
    classifier.fit(X=features.T, y=labels.ravel())

def classifierPredictData(classifier, features, progressBar=None):
    assert is2darray(features)
    progressBar = getProgressBar(progressBar)

    progressBar.setLabelText('predict sample (N={}) with {}'.format(features.shape[1], str(classifier).split()))
    labels = classifier.predict(X=features.T)
    return labels