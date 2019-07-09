from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies sobel filter to image. See {} for further information on sobel operators',
               links=[Link('https://en.wikipedia.org/wiki/Sobel_operator','Wikipedia')])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.sobel.html',
                            'scipy.ndimage.sobel')
])
