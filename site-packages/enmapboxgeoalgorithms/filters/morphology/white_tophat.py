from scipy.ndimage.morphology import white_tophat
function = lambda array: white_tophat(array, size=(3,3))
