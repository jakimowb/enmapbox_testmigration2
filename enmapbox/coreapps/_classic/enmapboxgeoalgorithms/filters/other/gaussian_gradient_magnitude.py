from scipy.ndimage.filters import gaussian_gradient_magnitude

function = lambda array: gaussian_gradient_magnitude(array, sigma=1)
