from os.path import join, abspath

filename = abspath(join(__file__, '../../doc/source/general/glossary.rst'))
baselink = r'C:\source\QGISPlugIns\enmap-box\doc\build\html\general\glossary.html'

glossary = dict()
with open(filename) as file:
    for line in file.readlines():
        if line[:3] == '   ' and line[3] not in ' .:':
            line = line.strip()
            glossary[line] = f'{baselink}#term-{line.replace(" ", "-")}'

def injectGlossaryLinks(text: str):
    terms = list()
    letter = 'abcdefghijklmnopqrstuvwxyz'
    for k in reversed(sorted(glossary.keys(), key=len)):  # longest terms first to avoid short terms corrupting long terms
        url = glossary[k]
        ilast = 0
        while True:
            i0 = text.find(k, ilast)
            if i0 == -1:
                k = k[0].upper() + k[1:]
                i0 = text.find(k, ilast)
            if i0 == -1:
                break
            ilast = i0 + 1
            if (
                    (i0 > 0 and (text[i0 - 1].lower() in letter)) or
                    (i0 < len(k) and text[i0 + len(k)].lower() in letter)
            ):
                continue
            k2 = f'_{len(terms)}_'
            terms.append((k, k2, url))
            text = text[:i0] + k2 + text[i0+len(k):]  # mark term

            break  # only link first appearence

    for k, k2, url in terms:
        url = f'https://scikit-learn.org/stable/glossary.html#term-dimensionality'
        link = f'<a href="{url}">{k}</a>'
        text = text.replace(k2, link)  # inject link

    return text

def test():
    text = 'wavelength is a term that is also included in wavelength units. and again wavelength. \n' \
           'thisisnotawavelength wavelength \n' \
           'wavelengthNO wavelength. \n' \
           'Wavelength \n' \
           'No data value \n' \
           '"No data value"'
    print(injectGlossaryLinks(text))

#test()
