from scipy.ndimage.filters import median_filter

function = lambda array: median_filter(array, size=3)
