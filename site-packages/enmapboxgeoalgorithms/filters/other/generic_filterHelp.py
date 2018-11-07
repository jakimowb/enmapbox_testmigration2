from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies generic_filter to image using a user-specifiable function. This algorithm can perform operations you might know as moving window or focal statistics from some other GIS systems. Mind that depending on the function this algorithms can take some time to process.',
               links=[])

helpCode = Help(text='Python code. The function argument can take any callable function that expects a 1D array as input and returns a single value. You should alter the preset in the code window and define your own function. See {} for information on different parameters.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generic_filter.html',
                            'scipy.ndimage.generic_filter')
])
