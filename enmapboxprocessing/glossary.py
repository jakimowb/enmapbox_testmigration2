from os.path import join, abspath

filename = abspath(join(__file__, '../../doc/source/general/glossary.rst'))
baselink = r'C:\source\QGISPlugIns\enmap-box\doc\build\html\general\glossary.html'
baselink = 'file:///C:/source/QGISPlugIns/enmap-box/doc/build/html/general/glossary.html'
baselink = 'https://enmap-box.readthedocs.io/en/latest/general/glossary.html'

glossary = dict()
with open(filename) as file:
    for line in file.readlines():
        if line[:4] == '    ' and line[4] not in ' .:':
            line = line.strip()
            glossary[line] = f'{baselink}#term-{line.replace(" ", "-").lower()}'  # term-* anchor needs to be lower case


def injectGlossaryLinks(text: str):
    terms = list()
    letter = '_abcdefghijklmnopqrstuvwxyz'
    letter = letter + letter.upper()
    letterWithoutS = '_abcdefghijklmnopqrtuvwxyz'
    letterWithoutS = letterWithoutS + letterWithoutS.upper()
    for k in reversed(sorted(glossary.keys(), key=len)):  # long terms first to avoid term corruption
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
            if i0 > 0:
                if text[i0 - 1].lower() in letter:
                    continue
            if text[i0 + len(k)].lower() in letterWithoutS:
                continue
            else:
                if len(text) - 1 >= i0 + len(k) + 1:
                    if text[i0 + len(k) + 1].lower() in letter:
                        continue

            # handle some special cases
            if k.lower() == 'output':
                if text[i0:].lower().startswith('output data type'):
                    continue
                if text[i0:].lower().startswith('output format'):
                    continue
                if text[i0:].lower().startswith('output raster'):
                    continue
                if text[i0:].lower().startswith('output report'):
                    continue
                if text[i0:].lower().startswith('output destination'):
                    continue
                if text[i0:].lower().startswith('output category'):
                    continue
                if text[i0:].lower().startswith('output vector'):
                    continue
                if text[i0:].lower().startswith('output _'):
                    continue

            if k.lower() == 'target':
                if text[i0:].lower().startswith('target coordinate reference system'):
                    continue
                if text[i0:].lower().startswith('target extent'):
                    continue
                if text[i0:].lower().startswith('target raster'):
                    continue
                if text[i0:].lower().startswith('target width'):
                    continue
                if text[i0:].lower().startswith('target height'):
                    continue
                if text[i0:].lower().startswith('target grid'):
                    continue

            if k.lower() == 'grid':
                a=1
            k2 = f'_{len(terms)}_'
            terms.append((k, k2, url))
            text = text[:i0] + k2 + text[i0 + len(k):]  # mark term

            break  # only link first appearence

    for k, k2, url in terms:
        link = f'<a href="{url}">{k}</a>'
        text = text.replace(k2, link)  # inject link

    return text


def test():
    text = 'wavelength is a term that is also included in wavelength units. and again wavelength. \n' \
           'thisisnotawavelength wavelength \n' \
           'wavelengthNO wavelength. \n' \
           'Wavelength \n' \
           'No data valueE \n' \
           '"No data values"'

    # text = '"No data value"'
    print(injectGlossaryLinks(text))

# test()
