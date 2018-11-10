from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies Moffat2DKernel to image.')

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('http://docs.astropy.org/en/stable/api/astropy.convolution.Moffat2DKernel.html',
                            'astropy.convolution.Moffat2DKernel')])
