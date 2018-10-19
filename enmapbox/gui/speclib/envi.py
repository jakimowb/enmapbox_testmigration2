# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    envi.py
    Reading and writing spectral profiles to ENVI Spectral Libraries
    ---------------------
    Date                 : Okt 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This file is part of the EnMAP-Box.                                   *
*                                                                         *
*   The EnMAP-Box is free software; you can redistribute it and/or modify *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   The EnMAP-Box is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with the EnMAP-Box. If not, see <http://www.gnu.org/licenses/>. *
*                                                                         *
***************************************************************************
"""



class EnviSpectralLibraryIO(AbstractSpectralLibraryIO):
    """
    IO of ENVI Spectral Libraries
    see http://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html for format description
    Additional profile metadata is written to/read from a *.csv of same base name as the ESL
    """

    REQUIRED_TAGS = ['byte order', 'data type', 'header offset', 'lines', 'samples', 'bands']
    SINGLE_VALUE_TAGS = REQUIRED_TAGS + ['description', 'wavelength', 'wavelength units']

    @staticmethod
    def canRead(pathESL):
        """
        Checks if a file can be read as SpectraLibrary
        :param pathESL: path to ENVI Spectral Library (ESL)
        :return: True, if pathESL can be read as Spectral Library.
        """
        assert isinstance(pathESL, str)
        if not os.path.isfile(pathESL):
            return False
        hdr = EnviSpectralLibraryIO.readENVIHeader(pathESL, typeConversion=False)
        if hdr is None or hdr['file type'] != 'ENVI Spectral Library':
            return False
        return True

    @staticmethod
    def readFrom(pathESL, tmpVrt=None):
        """
        Reads an ENVI Spectral Library (ESL).
        :param pathESL: path ENVI Spectral Library
        :param tmpVrt: (optional) path of GDAL VRT that is used internally to read the ESL
        :return: SpectralLibrary
        """
        assert isinstance(pathESL, str)
        md = EnviSpectralLibraryIO.readENVIHeader(pathESL, typeConversion=True)

        data = None

        createTmpFile = tmpVrt == None
        if createTmpFile:
            tmpVrt = tempfile.mktemp(prefix='tmpESLVrt', suffix='.esl.vrt', dir='/vsimem/')

        ds = EnviSpectralLibraryIO.esl2vrt(pathESL, tmpVrt)
        data = ds.ReadAsArray()

        #remove the temporary VRT, as it was created internally only
        if createTmpFile:
            ds.GetDriver().Delete(ds.GetFileList()[0])
            ds = None

        #check for additional CSV to enhance profile descriptions
        pathCSV = os.path.splitext(pathESL)[0] + '.csv'
        hasCSV = os.path.isfile(pathCSV)

        nSpectra, nbands = data.shape
        yUnit = None
        xUnit = md.get('wavelength units')
        xValues = md.get('wavelength')
        if xValues is None:
            xValues = list(range(1, nbands + 1))
            xUnit = 'index'

        #get offical ENVI Spectral Library standard values
        spectraNames = md.get('spectra names', ['Spectrum {}'.format(i+1) for i in range(nSpectra)])

        SLIB = SpectralLibrary()
        SLIB.startEditing()

        profiles = []
        for i in range(nSpectra):
            p = SpectralProfile(fields=SLIB.fields())
            p.setXValues(xValues)
            p.setYValues(data[i,:])
            p.setXUnit(xUnit)
            p.setYUnit(yUnit)
            p.setName(spectraNames[i])
            profiles.append(p)
        SLIB.addProfiles(profiles)

        if hasCSV: #we have a CSV with additional metadata. Let's add it to the profiles

            SL_CSV = CSVSpectralLibraryIO.readFrom(pathCSV)

            assert len(SL_CSV) == len(SLIB), 'Inconsistent CSV: number of rows not equal to number of spectra in *.hdr {}. '.format(pathCSV)

            #update fields
            SLIB.addMissingFields(SL_CSV.fields())

            #update feature field values

            fieldNamesToUpdate = [n for n in SL_CSV.fieldNames() if not n.startswith(HIDDEN_ATTRIBUTE_PREFIX)]


            for p1, p2 in zip(SLIB.profiles(), SL_CSV.profiles()):
                assert isinstance(p1, SpectralProfile)
                assert isinstance(p2, SpectralProfile)

                assert p1.id() == p2.id()

                p1.setGeometry(p2.geometry())
                for n in fieldNamesToUpdate:
                    p1.setAttribute(n, p2.attribute(n))
                SLIB.updateFeature(p1)

            if False:
                drv = ogr.GetDriverByName('CSV')
                assert isinstance(drv, ogr.Driver)

                ds = drv.Open(pathCSV)
                assert isinstance(ds, ogr.DataSource)
                lyr = ds.GetLayer(0)
                assert isinstance(lyr, ogr.Layer)
                assert lyr.GetFeatureCount() == nSpectra

                fieldData = {}
                for i in range(lyr.GetLayerDefn().GetFieldCount()):
                    fieldData[lyr.GetLayerDefn().GetFieldDefn(i).GetName()] = []
                fieldNames = list(fieldData.keys())
                fieldList = []

                feature = lyr.GetNextFeature()
                while isinstance(feature, ogr.Feature):
                    for name in fieldNames:
                        fieldData[name].append(feature.GetFieldAsString(name).strip())
                    feature = lyr.GetNextFeature()

                #replace empty values by None and convert values to most-likely basic python data type
                for fieldName in fieldNames:
                    if fieldName in ['WKT']:
                        continue
                    values = fieldData[fieldName]
                    qgsField = None
                    for v in values:
                        if len(v) > 0:
                            t = findTypeFromString(v)
                            v = toType(t, v)
                            qgsField = createQgsField(fieldName, v)
                            break
                    if qgsField == None:
                        qgsField = createQgsField(fieldName, '')

                    values = [toType(t, v) if len(v) > 0 else None for v in values]
                    fieldList.append(qgsField)
                    fieldData[fieldName] = values

                #add the fields to the speclib
                SLIB.addMissingFields(fieldList)
                addGeometryWKT = 'WKT' in fieldNames

                for i, feature in enumerate(SLIB.getFeatures()):
                    assert isinstance(feature, QgsFeature)

                    if addGeometryWKT:
                        wkt = fieldData['WKT'][i]
                        g = QgsGeometry.fromWkt(wkt)
                        feature.setGeometry(g)

                    for field in fieldList:
                        fn = field.name()
                        feature.setAttribute(fn, fieldData[fn][i])

                SLIB.updateFeature(feature)

        SLIB.commitChanges()
        assert SLIB.featureCount() == nSpectra
        return SLIB

    @staticmethod
    def write(speclib, path, ext='sli'):
        """
        Writes a SpectralLibrary as ENVI Spectral Library (ESL).
        See http://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html for ESL definition

        Additional attributes (coordinate, user-defined attributes) will be written into a CSV text file with same basename

        For example the path myspeclib.sli leads to:

            myspeclib.sli <- ESL binary file
            myspeclib.hdr <- ESL header file
            myspeclib.csv <- CSV text file, tabulator separated columns (for being used in Excel)


        :param speclib: SpectralLibrary
        :param path: str
        :param ext: str, ESL file extension of, e.g. .sli (default) or .esl
        """
        assert isinstance(path, str)
        assert ext != 'csv'
        dn = os.path.dirname(path)
        bn = os.path.basename(path)

        writtenFiles = []

        if bn.lower().endswith(ext.lower()):
            bn = os.path.splitext(bn)[0]

        if not os.path.isdir(dn):
            os.makedirs(dn)

        def value2hdrString(values):
            """
            Converts single values or a list of values into an ENVI header string
            :param values: valure or list-of-values, e.g. int(23) or [23,42]
            :return: str, e.g. "23" in case of a single value or "{23,42}" in case of list values
            """
            s = None
            maxwidth = 75

            if isinstance(values, list):
                lines = ['{']
                values = ['{}'.format(v).replace(',','-') for v in values]
                line = ' '
                l = len(values)
                for i, v in enumerate(values):
                    line += v
                    if i < l-1: line += ', '
                    if len(line) > maxwidth:
                        lines.append(line)
                        line = ' '
                line += '}'
                lines.append(line)
                s = '\n'.join(lines)

            else:
                s = '{}'.format(values)

            return s

        initialSelection = speclib.selectedFeatureIds()

        for iGrp, grp in enumerate(speclib.groupBySpectralProperties().values()):

            if len(grp) == 0:
                continue

            wl = grp[0].xValues()
            wlu = grp[0].xUnit()

            fids = [p.id() for p in grp]

            # stack profiles
            pData = [np.asarray(p.yValues()) for p in grp]
            pData = np.vstack(pData)

            #convert array to data types GDAL can handle
            if pData.dtype == np.int64:
                pData = pData.astype(np.int32)

            pNames = [p.name() for p in grp]

            if iGrp == 0:
                pathDst = os.path.join(dn, '{}.{}'.format(bn, ext))
            else:
                pathDst = os.path.join(dn, '{}.{}.{}'.format(bn, iGrp, ext))

            drv = gdal.GetDriverByName('ENVI')
            assert isinstance(drv, gdal.Driver)


            eType = gdal_array.NumericTypeCodeToGDALTypeCode(pData.dtype)
            """Create(utf8_path, int xsize, int ysize, int bands=1, GDALDataType eType, char ** options=None) -> Dataset"""
            ds = drv.Create(pathDst, pData.shape[1], pData.shape[0], 1, eType)
            band = ds.GetRasterBand(1)
            assert isinstance(band, gdal.Band)
            band.WriteArray(pData)

            #ds = gdal_array.SaveArray(pData, pathDst, format='ENVI')

            assert isinstance(ds, gdal.Dataset)
            ds.SetDescription(speclib.name())
            ds.SetMetadataItem('band names', 'Spectral Library', 'ENVI')
            ds.SetMetadataItem('spectra names',value2hdrString(pNames), 'ENVI')
            ds.SetMetadataItem('wavelength', value2hdrString(wl), 'ENVI')
            ds.SetMetadataItem('wavelength units', wlu, 'ENVI')

            fieldNames = ds.GetMetadata_Dict('ENVI').keys()
            fieldNames = [n for n in speclib.fields().names() if n not in fieldNames and not n.startswith(HIDDEN_ATTRIBUTE_PREFIX)]

            for a in fieldNames:
                v = value2hdrString([p.metadata(a) for p in grp])
                ds.SetMetadataItem(a, v, 'ENVI')

            pathHDR = ds.GetFileList()[1]
            pathCSV = os.path.splitext(pathHDR)[0]+'.csv'
            ds = None

            # re-write ENVI Hdr with file type = ENVI Spectral Library
            file = open(pathHDR)
            hdr = file.readlines()
            file.close()

            for iLine in range(len(hdr)):
                if re.search('file type =', hdr[iLine]):
                    hdr[iLine] = 'file type = ENVI Spectral Library\n'
                    break

            file = open(pathHDR, 'w', encoding='utf-8')
            file.writelines(hdr)
            file.flush()
            file.close()

            # write none-spectral data into CSV
            speclib.selectByIds(fids)
            fieldNames = [n for n in speclib.fieldNames() if not n.startswith(HIDDEN_ATTRIBUTE_PREFIX)]
            fieldIndices = [grp[0].fieldNameIndex(n) for n in fieldNames]

            sep = '\t'
            fwc = CSVWriterFieldValueConverter(speclib)
            fwc.setSeparatorCharactersToReplace([sep, ','], ' ') #replaces the separator in string by ' '

            #test ogr CSV driver options
            drv = ogr.GetDriverByName('CSV')
            optionXML = drv.GetMetadataItem('DMD_CREATIONOPTIONLIST')

            canWriteTAB = '<Value>TAB</Value>' in optionXML
            canWriteXY = '<Value>AS_XY</Value>' in optionXML
            co = []
            if canWriteTAB:
                co.append('SEPARATOR=TAB')
            if canWriteXY:
                co.append('GEOMETRY=AS_XY')
            else:
                co.append('GEOMETRY=AS_WKT')

            exitStatus, error = QgsVectorFileWriter.writeAsVectorFormat(speclib, pathCSV, 'utf-8', speclib.crs(), 'CSV',
                                                         fieldValueConverter=fwc,
                                                         onlySelected=True,
                                                         datasourceOptions=co,
                                                         attributes=fieldIndices)

            if False and not all([canWriteTAB, canWriteXY]):
                file = open(pathCSV,'r',encoding='utf-8')
                lines = file.readlines()
                file.close()

                if not canWriteTAB:
                    lines = [l.replace(',', sep) for l in lines]

                if not canWriteXY:
                    pass
                file = open(pathCSV, 'w', encoding='utf-8')
                file.writelines(lines)
                file.close()

            writtenFiles.append(pathDst)

        #restore initial feature selection
        speclib.selectByIds(initialSelection)

        return writtenFiles


    @staticmethod
    def esl2vrt(pathESL, pathVrt=None):
        """
        Creates a GDAL Virtual Raster (VRT) that allows to read an ENVI Spectral Library file
        :param pathESL: path ENVI Spectral Library file (binary part)
        :param pathVrt: (optional) path of created GDAL VRT.
        :return: GDAL VRT
        """

        hdr = EnviSpectralLibraryIO.readENVIHeader(pathESL, typeConversion=False)
        assert hdr is not None and hdr['file type'] == 'ENVI Spectral Library'

        if hdr.get('file compression') == '1':
            raise Exception('Can not read compressed spectral libraries')

        eType = LUT_IDL2GDAL[int(hdr['data type'])]
        xSize = int(hdr['samples'])
        ySize = int(hdr['lines'])
        bands = int(hdr['bands'])
        byteOrder = 'LSB' if int(hdr['byte order']) == 0 else 'MSB'

        if pathVrt is None:
            id = uuid.UUID()
            pathVrt = '/vsimem/{}.esl.vrt'.format(id)
            #pathVrt = tempfile.mktemp(prefix='tmpESLVrt', suffix='.esl.vrt')


        ds = describeRawFile(pathESL, pathVrt, xSize, ySize, bands=bands, eType=eType, byteOrder=byteOrder)
        for key, value in hdr.items():
            if isinstance(value, list):
                value = u','.join(v for v in value)
            ds.SetMetadataItem(key, value, 'ENVI')
        ds.FlushCache()
        return ds


    @staticmethod
    def readENVIHeader(pathESL, typeConversion=False):
        """
        Reads an ENVI Header File (*.hdr) and returns its values in a dictionary
        :param pathESL: path to ENVI Header
        :param typeConversion: Set on True to convert values related to header keys with numeric
        values into numeric data types (int / float)
        :return: dict
        """
        assert isinstance(pathESL, str)
        if not os.path.isfile(pathESL):
            return None

        pathHdr = EnviSpectralLibraryIO.findENVIHeader(pathESL)
        if pathHdr is None:
            return None


        #hdr = open(pathHdr).readlines()
        file = open(pathHdr, encoding='utf-8')
        hdr = file.readlines()
        file.close()

        i = 0
        while i < len(hdr):
            if '{' in hdr[i]:
                while not '}' in hdr[i]:
                    hdr[i] = hdr[i] + hdr.pop(i + 1)
            i += 1

        hdr = [''.join(re.split('\n[ ]*', line)).strip() for line in hdr]
        # keep lines with <tag>=<value> structure only
        hdr = [line for line in hdr if re.search('^[^=]+=', line)]

        # restructure into dictionary of type
        # md[key] = single value or
        # md[key] = [list-of-values]
        md = dict()
        for line in hdr:
            tmp = line.split('=')
            key, value = tmp[0].strip(), '='.join(tmp[1:]).strip()
            if value.startswith('{') and value.endswith('}'):
                value = [v.strip() for v in value.strip('{}').split(',')]
            md[key] = value

        # check required metadata tegs
        for k in EnviSpectralLibraryIO.REQUIRED_TAGS:
            if not k in md.keys():
                return None

        if typeConversion:
            to_int = ['bands','lines','samples','data type','header offset','byte order']
            to_float = ['fwhm','wavelength', 'reflectance scale factor']
            for k in to_int:
                if k in md.keys():
                    md[k] = toType(int, md[k])
            for k in to_float:
                if k in md.keys():
                    md[k] = toType(float, md[k])


        return md

    @staticmethod
    def findENVIHeader(pathESL):
        paths = [os.path.splitext(pathESL)[0] + '.hdr', pathESL + '.hdr']
        pathHdr = None
        for p in paths:
            if os.path.exists(p):
                pathHdr = p
        return pathHdr