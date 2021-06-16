from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies TrapezoidDisk2DKernel to image.')

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('http://docs.astropy.org/en/stable/api/astropy.convolution.TrapezoidDisk2DKernel.html',
                            'astropy.convolution.TrapezoidDisk2DKernel')])
