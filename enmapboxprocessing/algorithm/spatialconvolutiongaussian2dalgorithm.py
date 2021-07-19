from enmapboxprocessing.algorithm.convolutionfilteralgorithmbase import ConvolutionFilterAlgorithmBase
from typeguard import typechecked


@typechecked
class SpatialConvolutionGaussian2DAlgorithm(ConvolutionFilterAlgorithmBase):

    def displayName(self) -> str:
        return 'Spatial convolution gaussian filter'

    def shortDescription(self) -> str:
        return '2D gaussian filter.\n' \
               'The gaussian filter is a filter with great smoothing properties. ' \
               'It is isotropic and does not produce artifacts.'

    def helpParameterCode(self) -> str:
        link = self.htmlLink('http://docs.astropy.org/en/stable/api/astropy.convolution.Gaussian2DKernel.html',
                             'Gaussian2DKernel')
        return f'Python code. See {link} for information on different parameters.'

    def code(cls):
        from astropy.convolution import Gaussian2DKernel
        kernel = Gaussian2DKernel(x_stddev=1, y_stddev=1)
        return kernel
