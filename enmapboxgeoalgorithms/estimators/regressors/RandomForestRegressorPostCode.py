from os.path import splitext
from hubflow.core import LoggerFlowObject

global estimator, estimatorFilename

filename = '{}.info.txt'.format(splitext(estimatorFilename)[0])
LoggerFlowObject(filename=filename).setSklEstimatorItems(estimator=estimator).logItems()

