from scipy.ndimage.filters import percentile_filter

function = lambda array: percentile_filter(array, percentile=50, size=3)
