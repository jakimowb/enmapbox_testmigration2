from scipy.ndimage.morphology import grey_opening, generate_binary_structure, iterate_structure

structure = generate_binary_structure(rank=2, connectivity=1)
structure = iterate_structure(structure=structure, iterations=1)
function = lambda array: grey_opening(array, structure=structure)
