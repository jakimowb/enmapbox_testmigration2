from enmapboxprocessing.algorithm.applybandfunctionalgorithmbase import ApplyBandFunctionAlgorithmBase
from enmapboxprocessing.enmapalgorithm import Group
from typeguard import typechecked


@typechecked
class SpatialMorphologicalBlackTophatAlgorithm(ApplyBandFunctionAlgorithmBase):

    def displayName(self) -> str:
        return 'Spatial morphological black top-hat filter'

    def group(self):
        return Group.Test.value + Group.ConvolutionMorphologyAndFiltering.value

    def shortDescription(self) -> str:
        link = self.htmlLink('https://en.wikipedia.org/wiki/Top-hat_transform', 'Wikipedia')
        return f'Spatial morphological black tophat filter. See {link} for general information.'

    def helpParameterCode(self) -> str:
        links = ', '.join([
            self.htmlLink('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.black_tophat.html',
                          'binary_closing'),
            self.htmlLink(
                'https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html',
                'generate_binary_structure'),
            self.htmlLink('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html',
                          'iterate_structure')
        ])
        return f'Python code. See {links} for information on different parameters.'

    def code(cls):
        from scipy.ndimage.morphology import black_tophat, generate_binary_structure, iterate_structure

        structure = generate_binary_structure(rank=2, connectivity=1)
        structure = iterate_structure(structure=structure, iterations=1)
        function = lambda array: black_tophat(array, structure=structure)
        return function
