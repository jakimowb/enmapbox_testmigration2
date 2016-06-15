from __future__ import absolute_import
#import xml.etree.ElementTree, os, gzip, numpy, copy
import xml.etree.ElementTree, os, numpy, copy
import hub.collections
import gzip

def vrt2mos(vrtfile, hdr={}):
    root = xml.etree.ElementTree.parse(vrtfile).getroot()
    samples = root.attrib['rasterXSize']
    lines = root.attrib['rasterYSize']
    result = 'ENVI MOSAIC TEMPLATE (G)'
    result += '\nOutput Size: '+samples+' x '+lines
    result += '\n'

    VRTRasterBands = root.findall('VRTRasterBand')
    bands = str(len(VRTRasterBands))
    for SimpleSource in VRTRasterBands[0].findall('SimpleSource'):
        SourceFilename = SimpleSource.find('SourceFilename')
        if SourceFilename.attrib['relativeToVRT'] == '1':
            filename = os.path.join(os.path.dirname(vrtfile), SourceFilename.text)
        else:
            filename = SourceFilename.text

        SourceProperties = SimpleSource.find('SourceProperties')
        DstRect = SimpleSource.find('DstRect')
        xoff = str(int(DstRect.attrib['xOff'])+1)
        yoff = str(int(DstRect.attrib['yOff'])+1)

        result += '\nFile : '+filename
        result += '\nBands: 1-'+bands
        result += '\nDims : 1-'+SourceProperties.attrib['RasterXSize']+',1-'+SourceProperties.attrib['RasterYSize']
        result += '\nInfo : ('+xoff+','+yoff+') {0} [ {0}] {}'
        result += '\n'

    mosfile = vrtfile[:-4]+'.mos'
    with open(mosfile, 'w') as file:
        file.write(result)

    # create header file
    hdrfinal = {'description' : '{Virtual Mosaic File}',
                'samples': samples,
                'lines' : lines,
                'bands' : bands,
                'file type' : 'ENVI Virtual Mosaic',
                'read procedures' : '{envi_read_spatial_sm, envi_read_spectral_sm}',
                'subset procedure' : 'envi_read_scroll_sm'}
    hdrfinal.update(hdr)

    hdrfile = vrtfile[:-4]+'.hdr'
    writeHeader(hdrfile, hdrfinal)

    print('ENVI Virtual Mosaic created: '+mosfile)

def readHeader(hdrfile):
    with open(hdrfile, 'r') as file: lines = file.readlines()

    result = hub.collections.Bunch()
    i = 0
    while i < len(lines):
        if lines[i].find('=') == -1:
            i += 1
            continue

        (key, val) = lines[i].split("=", 1)

        key = key.strip()
        val = val.strip()
        if val[0] == '{':
            str = val
            while str[-1] != '}':
                i += 1
                str += lines[i][:-1].strip()
            result[key] = str[1:-1].split(',')
        else:
            result[key] = val
        i += 1
    return result

def writeHeader(hdrfile, hdr_):

    hdr = copy.deepcopy(hdr_)
    sortedKeys = ['description','samples','lines','bands','header offset','file type','data type','interleave','data ignore value',
                  'sensor type','byte order','map info','projection info','coordinate system string','acquisition time',
                  'wavelength units','wavelength','band names']

    with open(hdrfile, 'w') as file:
        def writeKeyValue(key, value):
            if not value: return
            if isinstance(value, list) or isinstance(value, numpy.ndarray):
                value = [str(elem) for elem in value]
            if isinstance(value, list) or isinstance(value, numpy.ndarray):
                file.writelines(key+' = {'+','.join(value)+'}\n')
            else:
                file.writelines(key+' = '+str(value)+'\n')

        file.write('ENVI\n')
        for key in sortedKeys: writeKeyValue(key, hdr.pop(key,None))
        for key, value in zip(hdr.keys(),hdr.values()): writeKeyValue(key, value)

def updateHeader(hdrfile, hdr):
    hdr1 = readHeader(hdrfile)
    hdr1.update(hdr)
    writeHeader(hdrfile, hdr1)

def compress(infile, outfile=None):
    if not outfile: outfile = infile

    hdr = readHeader(infile[:-4]+'.hdr')

    f_in = open(infile, 'rb')
    data = f_in.readlines()
    f_in.close()

    f_out = gzip.open(outfile, 'wb')
    f_out.writelines(data)
    f_out.close()

    hdr['file compression'] = '1'
    writeHeader(outfile[:-4]+'.hdr', hdr)

if __name__ == '__main__':

    infile = r'F:\Geomultisens\data\smallCaseExample\myClearObs\tiles\UL_50000_-4250000\clearObs2005.img'
    outfile = r't:\compressed.img'
  #  compress(infile)#, outfile)