from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies percentile filter to image.',
               links=[])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.percentile_filter.html',
                            'scipy.ndimage.percentile_filter')
])
