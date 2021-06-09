from enmapboxgeoalgorithms.provider import Help, Link

helpAlg = Help(text='Applies {}.',
               links=[Link('https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter', 'Savitzki Golay Filter')])

helpCode = Help(text='Python code. See {} for information on different parameters.',
                links=[Link('http://scipy.github.io/devdocs/generated/scipy.signal.savgol_coeffs.html#scipy.signal.savgol_coeffs',
                            'scipy.signal.savgol_coeffs')])
