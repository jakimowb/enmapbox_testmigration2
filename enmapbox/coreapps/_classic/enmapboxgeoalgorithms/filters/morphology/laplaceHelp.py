from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies morphological_laplace filter to image. See {} for more information on laplace filtering.',
               links=[Link('https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Image_Processing', 'Wikipedia')])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphological_laplace.html',
                            'scipy.ndimage.morphological_laplace')
])
