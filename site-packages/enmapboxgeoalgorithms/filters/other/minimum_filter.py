from scipy.ndimage.filters import minimum_filter

function = lambda array: minimum_filter(array, size=3)
