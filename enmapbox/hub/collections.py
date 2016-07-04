__author__ = 'janzandr'

class Bunch(dict):
    def __init__(self, dictionary=None):
        if dictionary is None:
            dict.__init__(self)
        elif isinstance(dictionary, dict):
            dict.__init__(self, dictionary.items())
        else:
            dict.__init__(self, dictionary)
        self.__dict__ = self
