from scipy.ndimage.morphology import morphological_gradient, generate_binary_structure, iterate_structure

structure = generate_binary_structure(rank=2, connectivity=1)
structure = iterate_structure(structure=structure, iterations=1)
function = lambda array: morphological_gradient(array, structure=structure)
