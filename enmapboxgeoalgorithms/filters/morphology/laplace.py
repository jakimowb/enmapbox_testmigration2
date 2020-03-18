from scipy.ndimage.morphology import morphological_laplace
function = lambda array: morphological_laplace(array, size=(3,3))
