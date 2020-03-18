from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies prewitt filter to image. See {} for further information on prewitt operators.',
               links=[Link('https://en.wikipedia.org/wiki/Prewitt_operator','Wikipedia')])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.prewitt.html',
                            'scipy.ndimage.prewitt')
])
