__author__ = 'janzandr'
#from enmapbox.processing.types import *
import os
import PyQt4.QtCore
from enmapbox.processing.environment import Environment


MODEL_URIS = []
MODEL_NAMES = []

_SIGNALS = None

class _ProcessingSignals(PyQt4.QtCore.QObject):
    """
    Object to bind QtSignals. Only to be used in this package definition.
    """
    sigFileCreated = PyQt4.QtCore.pyqtSignal(str)
    sigFileDeleted = PyQt4.QtCore.pyqtSignal(str)
    sigModelCreated = PyQt4.QtCore.pyqtSignal(str)
    sigModelDeleted = PyQt4.QtCore.pyqtSignal(str)

    def __init__(self):
        super(_ProcessingSignals, self).__init__()
        global _SIGNALS
        assert _SIGNALS is None, '_ProcessingSignals instance already created'

_SIGNALS = _ProcessingSignals()

#forwared PyQtSignals emitted by enmapbox.processing package
sigModelCreated = _SIGNALS.sigModelCreated
sigModelDeleted = _SIGNALS.sigModelDeleted
sigFileCreated = _SIGNALS.sigFileCreated
sigFileDeleted = _SIGNALS.sigFileDeleted


def registerModel(uri, name=None):
    """
    Tell
    :param uri: path / uri of model file
    :param name: model name. Basename by default
    :return: uri, if model did not exist in model list, None if it was already there
    """
    if uri not in MODEL_URIS:
        if name is None:
            name = os.path.basename(uri)
        MODEL_NAMES.append(name)
        MODEL_URIS.append(uri)
        sigModelCreated.emit(uri) #specific: it is a model
        sigFileCreated.emit(uri)  #unspecific: it is a file
        return uri
    else:
        return None

def deregisterModel(uri):
    """
    Removes the model from the package list of models MODEL_URIS
    :param uri: uri of model to be removed
    :return: uri of removed model or None if it did not exist
    """
    if uri in MODEL_URIS:
        i = MODEL_URIS.index(uri)
        MODEL_NAMES.remove(i)
        MODEL_URIS.remove(i)
        sigModelDeleted.emit(uri)
        sigFileDeleted.emit(uri) #tell others that a file was removed from the internal list
        return uri
    else:
        return None



