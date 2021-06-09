from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies Tophat2DKernel to image.')

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('http://docs.astropy.org/en/stable/api/astropy.convolution.Tophat2DKernel.html',
                            'astropy.convolution.Tophat2DKernel')])
