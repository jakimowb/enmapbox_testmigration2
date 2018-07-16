from scipy.ndimage.morphology import black_tophat, generate_binary_structure, iterate_structure

structure = generate_binary_structure(rank=2, connectivity=1)
structure = iterate_structure(structure=structure, iterations=1)
function = lambda array: black_tophat(array, structure=structure)
