from scipy.ndimage.filters import prewitt

function = lambda array: prewitt(array, axis=0)
