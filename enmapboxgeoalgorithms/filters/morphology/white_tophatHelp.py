from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies white_tophat morphology filter to image. See {} for more information on top-hat transformation.',
               links=[Link('https://en.wikipedia.org/wiki/Top-hat_transform', 'Wikipedia')])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.white_tophat.html',
                            'scipy.ndimage.white_tophat')
])
