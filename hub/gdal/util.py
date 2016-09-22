import numpy, os, hub.file, subprocess, gdal, xml.etree.ElementTree, copy
#from gdalconst import *

def gdal_translate(outfile, infile, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))
    cmd = 'gdal_translate '+options+' '+infile+' '+outfile
    #cmd = r'"C:\Program Files\QGIS Wien\bin\gdal_translate" '+options+' '+infile+' '+outfile

    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)
    return outfile

def gdalwarp(outfile, infile, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdalwarp '+options+' '+infile+' '+outfile
    #cmd = r'"C:\Program Files\QGIS Wien\bin\gdalwarp" '+options+' '+infile+' '+outfile


    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)

    return outfile

def gdalbuildvrt(outfile, infiles, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    # create filelist file
    infiles_file = outfile[:-4]+'.txt'
    numpy.savetxt(infiles_file, infiles, fmt="%s")

    cmd = 'gdalbuildvrt '+options+' -input_file_list '+infiles_file+' '+outfile
    #cmd = r'"C:\Program Files\QGIS Wien\bin\gdalbuildvrt" '+options+' -input_file_list '+infiles_file+' '+outfile

    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)

def gdaldem(outfile, infile, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdaldem '+options+' '+infile+' '+outfile

    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)

def gdal_proximity(outfile, infile, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdal_proximity '+infile+' '+outfile+' '+options

    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)

def gdaltindex(outfile, infiles, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))
    for file in infiles:
        cmd = 'gdaltindex '+options+' '+outfile+' '+file
        if verbose:
            print(cmd)
        else:
            cmd += ' -q'
        subprocess.call(cmd, shell=True)


def gdal_rasterize(outfile, infile, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdal_rasterize '+options+' '+infile+' '+outfile
    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)

def gdal_calc(outfile, infile1, options, verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdal_calc'#+options+' '+ogrfile+' '+rasterfile
#          gdal_calc.py -A input1.tif -B input2.tif --outfile=result.tif --calc="A+B"
    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)


def stack_images(outfile, infiles, options='', verbose=True):

    gdalbuildvrt(outfile, infiles, options+' -separate', verbose)

    bandss = [gdal.Open(infile, gdal.GA_ReadOnly).RasterCount for infile in infiles]

    tree = xml.etree.ElementTree.parse(outfile)
    root = tree.getroot()
    root2 = xml.etree.ElementTree.Element(root.tag)
    for key, value in root.items():
        root2.set(key, value)

    vrtbandindex = 0
    vrtfileindex = 0

    for child in root.getchildren():
        if child.tag == 'VRTRasterBand':
            for band in range(bandss[vrtfileindex]):
                VRTRasterBand = copy.deepcopy(child)
                VRTRasterBand.set('band',str(vrtbandindex+1))
                vrtbandindex += 1
                Source =  VRTRasterBand.find('SimpleSource') if VRTRasterBand.find('SimpleSource') is not None else VRTRasterBand.find('ComplexSource')
                SourceBand = Source.find('SourceBand')
                SourceBand.text = str(band+1)
                root2.append(VRTRasterBand)
            vrtfileindex += 1
        else:
            root2.append(copy.deepcopy(child))

    #xml.etree.ElementTree.dump(root2)
    tree2 = xml.etree.ElementTree.ElementTree(root2)
    tree2.write(outfile)

    return outfile


def stack_bands(outfile, infiles, inbands, options='', verbose=True):

    assert len(infiles) == len(inbands)

    # create VRT stack with band 1 for each input file
    gdalbuildvrt(outfile, infiles, options+' -separate -b 1', verbose)

    # manipulate VRT
    with open(outfile) as f:
        text = f.readlines()

    bandIndex = 0
    for i, line in enumerate(text):
        if line.strip() == '<SourceBand>1</SourceBand>':
            text[i] = '      <SourceBand>' + str(inbands[bandIndex]) + '</SourceBand>\n'
            bandIndex += 1

    with open(outfile, 'w') as f:
        f.writelines(text)


    return outfile


def mosaic(outfile, infiles, options='', verbose=True):
    gdalbuildvrt(outfile, infiles, options, verbose)

'''
def warp(outfile, infile, of='VRT'):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdalwarp -of '+of+' -t_srs EPSG:3575 -tr 30 30 -overwrite -r near -wm 2000 '+infile+' '+outfile
    print(cmd)
    subprocess.call(cmd, shell=True)


def subset(outfile, infile, xmin, ymin, xmax, ymax, of='VRT', verbose=True):

    hub.file.mkdir(os.path.dirname(outfile))

    cmd = 'gdal_translate -of '+of+' -projwin '+xmin+' '+ymin+' '+xmax+' '+ymax+' -eco '+infile+' '+outfile
    if verbose:
        print(cmd)
    else:
        cmd += ' -q'
    subprocess.call(cmd, shell=True)
'''

if __name__ == '__main__':

#    infile = r'H:\EuropeanDataCube\sentinel2\imported_laea\S2A_OPER_PRD_MSIL1C_PDMC_20150812T211957_R065_V20150806T102902_20150806T102902\MSIL1C_20150806T102902_viewstack_mosxx_land.vrt'
#    outfile = r'H:\EuropeanDataCube\sentinel2\imported_laea\S2A_OPER_PRD_MSIL1C_PDMC_20150812T211957_R065_V20150806T102902_20150806T102902\cloudMask\stack_10m_land.img'
    infile = r'H:\EuropeanDataCube\sentinel2\imported_laea\S2A_OPER_PRD_MSIL1C_PDMC_20150812T211957_R065_V20150806T102902_20150806T102902\MSIL1C_20150806T102902_viewstack_mosxx_ldcm.vrt'
    outfile = r'H:\EuropeanDataCube\sentinel2\imported_laea\S2A_OPER_PRD_MSIL1C_PDMC_20150812T211957_R065_V20150806T102902_20150806T102902\cloudMask\stack_10m_ldcm.img'

    gdal_translate(outfile, infile, '-of ENVI')

#    rasterfile = r'H:\EuropeanDataCube\sentinel2\imported_laea\S2A_OPER_PRD_MSIL1C_PDMC_20150812T211957_R065_V20150806T102902_20150806T102902\_lucas_r60.img'
#    ogrfile    = r'H:\EuropeanDataCube\sentinel2\user-consultation\data\lucas\eu27_lucas_2012.shp'
#    gdal_rasterize(rasterfile, ogrfile, '-a LC3 -l eu27_lucas_2012')

