from enmapboxprocessing.algorithm.convolutionfilteralgorithmbase import ConvolutionFilterAlgorithmBase
from typeguard import typechecked


@typechecked
class SpatialConvolutionTrapezoidDisk2DAlgorithm(ConvolutionFilterAlgorithmBase):

    def displayName(self) -> str:
        return 'Spatial convolution trapezoid filter'

    def shortDescription(self) -> str:
        return '2D trapezoid filter.'

    def helpParameterCode(self) -> str:
        link = self.htmlLink('http://docs.astropy.org/en/stable/api/astropy.convolution.TrapezoidDisk2DKernel.html',
                             'TrapezoidDisk2DKernel')
        return f'Python code. See {link} for information on different parameters.'

    def code(cls):
        from astropy.convolution import TrapezoidDisk2DKernel
        kernel = TrapezoidDisk2DKernel(radius=3, slope=1)
        return kernel
