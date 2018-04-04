import re, os


# regular expressions can be used to describe and extract patterns of characters / word

# extract all numbers from a string
print(re.findall('[0123456789]+', 'lore 12 ipsum 32 tralala 211'))
print(re.findall('\d+', 'lore 12 ipsum 32 tralala 211')) #the same, '\d' for digits


# extract all latitude values
a_complicated_string = """[{"type":"polyline","latLngs":[{"lat":52.931796,"lng":13.0189},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.932341,"lng":13.015449},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.933029,"lng":12.972047},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.93315,"lng":12.971325},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.921248,"lng":12.903533},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.92323,"lng":12.857292},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923098,"lng":12.854554},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923069,"lng":12.854014},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923026,"lng":12.853402},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.922774,"lng":12.850958},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.926853,"lng":12.819442},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.927064,"lng":12.814569},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.927102,"lng":12.812133},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.926597,"lng":12.809967},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.926583,"lng":12.808324},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.926414,"lng":12.807165},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.925776,"lng":12.805178},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.925952,"lng":12.804001},{"lat":52.746462,"lng":13.513278}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.92569,"lng":12.802545},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.925619,"lng":12.802111},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.925535,"lng":12.801109},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.9255,"lng":12.800682},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.925475,"lng":12.798277},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923973,"lng":12.791221},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.931796,"lng":13.0189},{"lat":53.309496,"lng":13.849219},{"lat":52.932341,"lng":13.015449}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.933029,"lng":12.972047},{"lat":53.309496,"lng":13.849219},{"lat":52.93315,"lng":12.971325}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.921248,"lng":12.903533},{"lat":53.309496,"lng":13.849219},{"lat":52.92323,"lng":12.857292}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923098,"lng":12.854554},{"lat":53.309496,"lng":13.849219},{"lat":52.923069,"lng":12.854014}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923026,"lng":12.853402},{"lat":53.309496,"lng":13.849219},{"lat":52.922774,"lng":12.850958}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":53.309496,"lng":13.849219},{"lat":52.746462,"lng":13.513278}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.746462,"lng":13.513278},{"lat":53.310092,"lng":13.850617}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":53.310092,"lng":13.850617},{"lat":52.926853,"lng":12.819442}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.927102,"lng":12.812133},{"lat":53.310092,"lng":13.850617},{"lat":52.927064,"lng":12.814569}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.926597,"lng":12.809967},{"lat":53.310092,"lng":13.850617},{"lat":52.926583,"lng":12.808324}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.925952,"lng":12.804001},{"lat":53.310092,"lng":13.850617},{"lat":52.925776,"lng":12.805178}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.926414,"lng":12.807165},{"lat":53.310092,"lng":13.850617}],"color":"#666666"},{"type":"polyline","latLngs":[{"lat":52.746462,"lng":13.513278},{"lat":53.312821,"lng":13.854465}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":53.312821,"lng":13.854465},{"lat":52.92569,"lng":12.802545}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.925535,"lng":12.801109},{"lat":53.312821,"lng":13.854465},{"lat":52.925619,"lng":12.802111}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.925475,"lng":12.798277},{"lat":53.312821,"lng":13.854465},{"lat":52.9255,"lng":12.800682}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.923973,"lng":12.791221},{"lat":53.312821,"lng":13.854465}],"color":"#c38a4a"},{"type":"polyline","latLngs":[{"lat":52.963053,"lng":14.425574},{"lat":52.746462,"lng":13.513278},{"lat":52.962194,"lng":14.430319}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":52.960768,"lng":14.432888},{"lat":52.746462,"lng":13.513278},{"lat":52.960701,"lng":14.435442}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":52.960785,"lng":14.436454},{"lat":52.746462,"lng":13.513278},{"lat":52.960429,"lng":14.438336}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":52.746462,"lng":13.513278},{"lat":53.306483,"lng":13.860793},{"lat":52.963053,"lng":14.425574}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":52.962194,"lng":14.430319},{"lat":53.306483,"lng":13.860793}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":53.307797,"lng":13.859117},{"lat":52.746462,"lng":13.513278},{"lat":53.308603,"lng":13.858075}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":53.310482,"lng":13.857157},{"lat":52.746462,"lng":13.513278},{"lat":53.312821,"lng":13.854465}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":52.962194,"lng":14.430319},{"lat":53.307797,"lng":13.859117},{"lat":52.960768,"lng":14.432888}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":53.307797,"lng":13.859117},{"lat":52.960701,"lng":14.435442},{"lat":53.308603,"lng":13.858075}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":53.308603,"lng":13.858075},{"lat":52.960785,"lng":14.436454},{"lat":53.310482,"lng":13.857157}],"color":"#a24ac3"},{"type":"polyline","latLngs":[{"lat":53.310482,"lng":13.857157},{"lat":52.960429,"lng":14.438336},{"lat":53.312821,"lng":13.854465}],"color":"#a24ac3"}]"""
print(re.findall('"lat":\d+.\d+',a_complicated_string ))

# do the same, but skip the preceding "lat": to return the numbers only
print(re.findall('(?<="lat":)\d+.\d+',a_complicated_string ))

#extract lines from XML (in general it is recommended to parse XML using an XML reader
#however, a regular expression is often the faster way if you like to read small pieces only.
sentinel2_xml_subset = """<        <Product_Info>
            <PRODUCT_START_TIME>2017-03-15T10:10:21.026Z</PRODUCT_START_TIME>
            <PRODUCT_STOP_TIME>2017-03-15T10:10:21.026Z</PRODUCT_STOP_TIME>
            <PRODUCT_URI>S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE</PRODUCT_URI>
            <PROCESSING_LEVEL>Level-1C</PROCESSING_LEVEL>
            <PRODUCT_TYPE>S2MSI1C</PRODUCT_TYPE>
            <PROCESSING_BASELINE>02.04</PROCESSING_BASELINE>
            <GENERATION_TIME>2017-03-15T10:12:14.000000Z</GENERATION_TIME>
            <PREVIEW_IMAGE_URL>Not applicable</PREVIEW_IMAGE_URL>
            <PREVIEW_GEO_INFO>Not applicable</PREVIEW_GEO_INFO>
            <Datatake datatakeIdentifier="GS2A_20170315T101021_009028_N02.04">
        </Product_Info>
"""
print(re.search('<Datatake.*>', sentinel2_xml_subset).group())


#this file stores a long list of file paths.
pathCSV = os.path.join(os.path.dirname(__file__), 'files.csv')
assert os.path.isfile(pathCSV), 'Missing file:' + pathCSV

f = open(pathCSV)
list_of_filenames = f.readlines() #a long list with file name
f.close()


#define a landsat scene identifier like LC82270652015034LGN00 as regular expression
#see https://landsat.usgs.gov/what-are-naming-conventions-landsat-scene-identifiers
#L<sensor><satellite><WRS path><WRS row><year><day-of-year><ground station id><archive version number>
regexLandsatID = re.compile('L[CET][4578]\d{3}\d{3}\d{4}\d{3}[A-Z]{3}\d{2}')

sceneIDs = set(regexLandsatID.findall('\n'.join(list_of_filenames)))
print('found {} different scene IDs'.format(len(sceneIDs)))

#find the FMask files
regexFMask = re.compile(regexLandsatID.pattern + '_cfmask.hdr')

fmaskFiles = [f for f in list_of_filenames if regexFMask.search(f)]
print('found {} FMask files'.format(len(fmaskFiles)))
