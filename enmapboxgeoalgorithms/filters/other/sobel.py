from scipy.ndimage.filters import sobel

function = lambda array: sobel(array, axis=0)
