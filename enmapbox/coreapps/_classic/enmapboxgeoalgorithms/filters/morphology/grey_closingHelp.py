from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies grey_closing morphology filter to image. See {} for general information about closing morphology.',
               links=[Link('https://en.wikipedia.org/wiki/Closing_(morphology)', 'Wikipedia')])

helpCode = Help(text='Python code. See {} for information on different parameters. At first, the structuring element will be defined ({}). By default, its dimensions are always equal to 3. The connectivity parameter defines the type of neighborhood. In order create a bigger structuring element, the parameters in {} have to be altered (e.g. iterations=2 will increase the size to 5). Alternatively, a custom numpy array can be used as structural element.',
                links=[Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.grey_closing.html',
                            'scipy.ndimage.grey_closing'),
                       Link(
                           'https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html',
                           'scipy.ndimage.generate_binary_structure'),
                       Link('https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html',
                            'iterate_structure')
                       ])