from enmapboxprocessing.algorithm.convolutionfilteralgorithmbase import ConvolutionFilterAlgorithmBase
from typeguard import typechecked


@typechecked
class SpectralConvolutionRickerWavelet1DAlgorithm(ConvolutionFilterAlgorithmBase):

    def displayName(self) -> str:
        return 'Spectral convolution 1D ricker wavelet filter'

    def shortDescription(self) -> str:
        return '1D ricker wavelet filter kernel (sometimes known as a mexican hat kernel).\n' \
               'The ricker wavelet, or inverted gaussian-laplace filter, is a bandpass filter. ' \
               'It smooths the data and removes slowly varying or constant structures (e.g. Background). ' \
               'It is useful for peak or multi-scale detection.'

    def helpParameterCode(self) -> str:
        link = self.htmlLink('http://docs.astropy.org/en/stable/api/astropy.convolution.RickerWavelet1DKernel.html',
                             'RickerWavelet1DKernel')
        return f'Python code. See {link} for information on different parameters.'

    def code(cls):
        from astropy.convolution import RickerWavelet1DKernel
        kernel = RickerWavelet1DKernel(width=1)
        return kernel
