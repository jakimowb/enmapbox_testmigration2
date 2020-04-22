from scipy.ndimage.filters import maximum_filter

function = lambda array: maximum_filter(array, size=3)
