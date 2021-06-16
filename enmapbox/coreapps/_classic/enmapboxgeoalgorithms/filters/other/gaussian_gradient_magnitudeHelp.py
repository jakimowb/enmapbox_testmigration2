from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies gaussian_gradient_magnitude filter to image.',
               links=[])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_gradient_magnitude.html',
                            'scipy.ndimage.gaussian_gradient_magnitude')
])
