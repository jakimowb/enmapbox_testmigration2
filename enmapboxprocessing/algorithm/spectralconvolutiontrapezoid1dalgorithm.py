from enmapboxprocessing.algorithm.convolutionfilteralgorithmbase import ConvolutionFilterAlgorithmBase
from typeguard import typechecked


@typechecked
class SpectralConvolutionTrapezoid1DAlgorithm(ConvolutionFilterAlgorithmBase):

    def displayName(self) -> str:
        return 'Spectral convolution trapezoid filter'

    def shortDescription(self) -> str:
        return '1D trapezoid filter.'

    def helpParameterCode(self) -> str:
        link = self.htmlLink('http://docs.astropy.org/en/stable/api/astropy.convolution.Trapezoid1DKernel.html',
                             'Trapezoid1DKernel')
        return f'Python code. See {link} for information on different parameters.'

    def code(cls):
        from astropy.convolution import Trapezoid1DKernel
        kernel = Trapezoid1DKernel(width=3, slope=1)
        return kernel
