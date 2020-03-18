from scipy.ndimage.filters import generic_filter
import numpy as np

def filter_function(invalues):

    # do whatever you want to create the output value, e.g. np.nansum
    # outvalue = np.nansum(invalues)
    return outvalue

function = lambda array: generic_filter(array, function=filter_function, size=3)
