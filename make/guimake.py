import os, sys, fnmatch, six, subprocess, re

from qgis.core import *

from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
from xml.etree import ElementTree
ROOT = os.path.dirname(os.path.dirname(__file__))
from enmapbox.gui.utils import DIR_UIFILES, DIR_ICONS, DIR_REPO, file_search
jp = os.path.join
import gdal, ogr, osr


def migrateBJexternals():
    from enmapbox.gui.utils import DIR_UIFILES

    for uifile in file_search(DIR_UIFILES, '*.ui'):
        f = open(uifile, 'r', encoding='utf-8')
        xml = f.read()
        f.close()

        if re.search(':/timeseriesviewer/', xml, re.I):
            s = ""
            newXML = re.sub(':/timeseriesviewer/', ':/enmapbox/', xml)

            assert re.search(':/timeseriesviewer/', newXML) is None

            f = open(uifile, 'w', encoding='utf-8')
            f.write(newXML)
            f.flush()
            f.close()

    s = ""




def rasterize_vector_labels(pathRef, pathDst, pathShp, label_field, band_ref=1, label_layer=0):
    drvMemory = ogr.GetDriverByName('Memory')
    drvMEM = gdal.GetDriverByName('MEM')

    dsShp = drvMemory.CopyDataSource(ogr.Open(pathShp),'')
    dsRef = gdal.Open(pathRef)

    assert label_layer < dsShp.GetLayerCount()
    lyr_tmp1 = dsShp.GetLayerByIndex(label_layer)
    lyr_name1 = lyr_tmp1.GetName()
    lyr_def1 = lyr_tmp1.GetLayerDefn()
    field_names1 = [lyr_def1.GetFieldDefn(f).GetName() for f  in range(lyr_def1.GetFieldCount())]
    assert label_field in field_names1, 'field {} does not exist. possible names are: {}'.format(label_field, ','.join(field_names1))
    fieldDef = lyr_def1.GetFieldDefn(field_names1.index(label_field))

    IS_CATEGORICAL = fieldDef.GetType() == ogr.OFTString
    label_names = None
    if IS_CATEGORICAL:
        #label_names = dsRef.GetRasterBand(band_ref).GetCategoryNames()
        label_names = set()
        for feat in lyr_tmp1:
            value = str(feat.GetField(label_field)).strip()
            if len(value) > 0:
                label_names.add(value)
            #get label names from values
        lyr_tmp1.ResetReading()
        label_names = sorted(list(label_names))
        if not 'unclassified' in label_names:
            label_names.insert(0, 'unclassified')
        label_values = list(range(len(label_names)))


    # transform geometries into target reference system
    for name in [lyr.GetName() for lyr in dsShp if lyr.GetName() != lyr_name1]:
        dsShp.Delete(name)
    lyr_name2 = lyr_name1 + '2'
    srs = osr.SpatialReference()
    srs.ImportFromWkt(dsRef.GetProjection())

    trans = None
    if not srs.IsSame(lyr_tmp1.GetSpatialRef()):
        trans = osr.CoordinateTransformation(lyr_tmp1.GetSpatialRef(), srs)
    lyr_tmp2 = dsShp.CreateLayer(lyr_name2, srs=srs, geom_type=ogr.wkbPolygon)


    if IS_CATEGORICAL:
        lyr_tmp2.CreateField(ogr.FieldDefn(label_field, ogr.OFTInteger))
        no_data = 0
    else:
        lyr_tmp2.CreateField(ogr.FieldDefn(label_field, fieldDef.GetType()))
        no_data = dsRef.GetRasterBand(band_ref).GetNoDataValue()

    n = 0
    for feature_src in lyr_tmp1:
        value = feature_src.GetField(label_field)
        if value is None:
            continue

        if IS_CATEGORICAL:
            if value in label_names:
                value = label_values[label_names.index(value)]
            elif value not in label_values:
                print('Not found in prediction labels: {}'.format(value))

        if value is not None:
            geom = feature_src.GetGeometryRef().Clone()
            if trans:
                geom.Transform(trans)

            feature_tmp = ogr.Feature(lyr_tmp2.GetLayerDefn())
            feature_tmp.SetGeometry(geom)
            feature_tmp.SetField(label_field, value)
            lyr_tmp2.CreateFeature(feature_tmp)
            lyr_tmp2.SyncToDisk()
            n +=1

    lyr_tmp2.ResetReading()
    ns = dsRef.RasterXSize
    nl = dsRef.RasterYSize



    dsRasterTmp = drvMEM.Create('', ns, nl, eType=gdal.GDT_Int32)
    dsRasterTmp.SetProjection(dsRef.GetProjection())
    dsRasterTmp.SetGeoTransform(dsRef.GetGeoTransform())
    band_ref = dsRasterTmp.GetRasterBand(1)
    assert type(band_ref) is gdal.Band
    if IS_CATEGORICAL:
        band_ref.Fill(0)  # by default = unclassified = 0
    elif no_data is not None:
        band_ref.Fill(no_data)
        band_ref.SetNoDataValue(no_data)

    # print('Burn geometries...')
    # http://www.gdal.org/gdal__alg_8h.html for details on options
    options = ['ATTRIBUTE={}'.format(label_field)
        , 'ALL_TOUCHED=TRUE']
    err = gdal.RasterizeLayer(dsRasterTmp, [1], lyr_tmp2, options=options)
    assert err in [gdal.CE_None, gdal.CE_Warning], 'Something failed with gdal.RasterizeLayer'

    band_ref = dsRasterTmp.GetRasterBand(1)
    validated_labels = band_ref.ReadAsArray()
    if IS_CATEGORICAL:
        #set classification info
        import matplotlib.cm
        label_colors = list()
        cmap = matplotlib.cm.get_cmap('brg', n)
        for i in range(n):
            if i == 0:
                c = (0,0,0, 255)
            else:
                c = tuple([int(255*c) for c in cmap(i)])
            label_colors.append(c)

        CT = gdal.ColorTable()
        names = list()
        for value in sorted(label_values):
            i = label_values.index(value)
            names.append(label_names[i])
            CT.SetColorEntry(value, label_colors[i])

        band_ref.SetCategoryNames(names)
        band_ref.SetColorTable(CT)

        s = ""
    drvDst = dsRef.GetDriver()
    drvDst.CreateCopy(pathDst, dsRasterTmp)


def getDOMAttributes(elem):
    assert isinstance(elem, QDomElement)
    values = dict()
    attributes = elem.attributes()
    for a in range(attributes.count()):
        attr = attributes.item(a)
        values[str(attr.nodeName())] = attr.nodeValue()
    return values


def copyQGISRessourceFile(pathQGISRepo):
    assert os.path.isdir(pathQGISRepo)
    dirTarget = os.path.join(DIR_REPO, *['qgisresources'])
    os.makedirs(dirTarget, exist_ok=True)
    compile_rc_files(pathQGISRepo, targetDir=dirTarget)

def compile_rc_files(ROOT, targetDir=None):
    #find ui files
    ui_files = file_search(ROOT, '*.ui', recursive=True)
    qrcs = set()

    doc = QDomDocument()
    reg = re.compile('(?<=resource=")[^"]+\.qrc(?=")')

    for ui_file in ui_files:
        pathDir = os.path.dirname(ui_file)
        doc.setContent(QFile(ui_file))
        includeNodes = doc.elementsByTagName('include')
        for i in range(includeNodes.count()):
            attr = getDOMAttributes(includeNodes.item(i).toElement())
            if 'location' in attr.keys():
                print((ui_file, str(attr['location'])))
                qrcs.add((pathDir, str(attr['location'])))

    #compile Qt resource files
    #resourcefiles = file_search(ROOT, '*.qrc', recursive=True)
    resourcefiles = list(qrcs)
    assert len(resourcefiles) > 0

    if sys.platform == 'darwin':
        prefix = '/Applications/QGIS.app/Contents/MacOS/bin/'
    else:
        prefix = ''



    for root_dir, f in resourcefiles:
        #dn = os.path.dirname(f)
        pathQrc = os.path.normpath(jp(root_dir, f))
        assert os.path.exists(pathQrc), pathQrc
        bn = os.path.basename(pathQrc)

        if isinstance(targetDir, str):
            dn = targetDir
        else:
            dn = os.path.dirname(pathQrc)
        os.makedirs(dn, exist_ok=True)
        bn = os.path.splitext(bn)[0]
        pathPy = os.path.join(dn, bn+'.py' )

        try:
            subprocess.call(['pyrcc5', '-o', pathPy, pathQrc])
        except Exception as ex:
            print('Failed call: pyrcc5 -o {} {}'.format(pathPy, pathQrc))


def fileNeedsUpdate(file1, file2):
    """
    Returns True if file2 does not exist or is older than file1
    :param file1:
    :param file2:
    :return:
    """
    if not os.path.exists(file2):
        return True
    else:
        if not os.path.exists(file1):
            return True
        else:
            return os.path.getmtime(file1) > os.path.getmtime(file2)

def createResourceIconPackage(dirIcons, pathResourceFile):
    import numpy as np

    pathInit = jp(dirIcons, '__init__.py')
    code = ['#!/usr/bin/env python',
            '"""',
            'This file is auto-generated.',
            'Do not edit manually, as changes might get overwritten.',
            '"""',
            '__author__ = "auto-generated by {}"'.format(os.path.relpath(__file__, DIR_REPO)),
            '__date__ = "{}"'.format(np.datetime64('now')),
            '',
            'import sys, os',
            '',
            'thisDir = os.path.dirname(__file__)',
            '# File path attributes:',
            ]
    files = file_search(dirIcons, '*.png', recursive=True)

    filePathAttributes = set()

    def addFiles(files, comment=None, numberPrefix='File'):
        if len(files) > 0:
            if comment:
                code.append('# ' + comment)
            for f in files:
                an, ext = os.path.splitext(os.path.basename(f))
                if re.search('^\d', an):
                    an = numberPrefix + an
                an = re.sub(r'[-.]', '_', an)

                assert an not in filePathAttributes
                relpath = os.path.relpath(f, dirData)
                code.append("{} = os.path.join(thisDir,r'{}')".format(an, relpath))
                filePathAttributes.add(an)
            code.append('\n')

    raster = [f for f in files if re.search('.*\.(bsq|bip|bil|tif|tiff)$', f)]
    vector = [f for f in files if re.search('.*\.(shp|kml|kmz)$', f)]

    addFiles(raster, 'Raster files:', numberPrefix='Img_')
    addFiles(vector, 'Vector files:', numberPrefix='Shp_')

    # add self-test for file existence
    if len(filePathAttributes) > 0:
        code.extend(
            [
                "",
                "# self-test to check each file path attribute",
                "for a in dir(sys.modules[__name__]):",
                "    v = getattr(sys.modules[__name__], a)",
                "    if type(v) == str and os.path.isabs(v):",
                "        if not os.path.exists(v):",
                "            sys.stderr.write('Missing package attribute file: {}={}'.format(a, v))",
                "",
                "# cleanup",
                "del thisDir ",
            ]
        )

    open(pathInit, 'w').write('\n'.join(code))
    print('Created ' + pathInit)
def createFilePackage(dirData):
    import numpy as np
    from enmapbox.gui.utils import DIR_REPO
    pathInit = jp(dirData, '__init__.py')
    code = ['#!/usr/bin/env python',
            '"""',
            'This file is auto-generated.',
            'Do not edit manually, as changes might get overwritten.',
            '"""',
            '__author__ = "auto-generated by {}"'.format(os.path.relpath(__file__, DIR_REPO)),
            '__date__ = "{}"'.format(np.datetime64('now')),
            '',
            'import sys, os',
            '',
            'thisDir = os.path.dirname(__file__)',
            '# File path attributes:',
            ]
    files = file_search(dirData, '*', recursive=True)

    filePathAttributes = set()
    def addFiles(files, comment=None, numberPrefix='File'):
        if len(files) > 0:
            if comment:
                code.append('# '+comment)
            for f in files:
                attributeName, ext = os.path.splitext(os.path.basename(f))
                #take care of leading numbers
                if re.search('^\d', attributeName):
                    attributeName = numberPrefix+attributeName
                # append extension
                attributeName += ext
                #take care of not allowed characters
                attributeName = re.sub(r'[-.]', '_',attributeName)



                assert attributeName not in filePathAttributes, attributeName
                relpath = os.path.relpath(f, dirData)
                code.append("{} = os.path.join(thisDir,r'{}')".format(attributeName, relpath))
                filePathAttributes.add(attributeName)
            code.append('\n')

    raster = [f for f in files if re.search('.*\.(bsq|bip|bil|tif|tiff)$', f)]
    vector = [f for f in files if re.search('.*\.(shp|kml|kmz)$', f)]

    addFiles(raster, 'Raster files:', numberPrefix='Img_')
    addFiles(vector, 'Vector files:', numberPrefix='Shp_')

    #add self-test for file existence
    if len(filePathAttributes) > 0:
        code.extend(
        [
        "",
        "# self-test to check each file path attribute",
        "for a in dir(sys.modules[__name__]):",
        "    v = getattr(sys.modules[__name__], a)",
        "    if type(v) == str and os.path.isabs(v):" ,
        "        if not os.path.exists(v):",
        "            sys.stderr.write('Missing package attribute file: {}={}'.format(a, v))",
        "",
        "# cleanup",
        "del thisDir ",
        ]
        )

    open(pathInit, 'w').write('\n'.join(code))
    print('Created '+pathInit)


def createTestData(dirSrc, dirDst, BBOX, drv=None, overwrite=False):

    import tempfile, random
    from qgis.core import QgsRectangle, QgsPoint, QgsPointV2, QgsCoordinateReferenceSystem
    from enmapbox.gui.utils import SpatialExtent
    max_offset = 0 #in %


    assert isinstance(BBOX, SpatialExtent)
    if not os.path.exists(dirDst):
        os.makedirs(dirDst)
    drvMEM = gdal.GetDriverByName('MEM')
    UL = QgsPoint(*BBOX.upperLeft())
    LR = QgsPoint(*BBOX.lowerRight())
    LUT_EXT = {'ENVI': '.bsq'}
    files = file_search(dirSrc, '*', recursive=True)
    for pathSrc in files:
        bn = os.path.basename(pathSrc)
        ext = os.path.splitext(bn)[1]
        pathDst = os.path.join(dirDst, os.path.basename(pathSrc))

        #handle raster files
        if re.search('(bsq|bip|bil|tiff?)$', ext, re.I):
            dsRasterSrc = gdal.Open(pathSrc)
            assert isinstance(dsRasterSrc, gdal.Dataset)

            drvDst = gdal.GetDriverByName(drv) if drv is not None else dsRasterSrc.GetDriver()
            # try to retrieve an extension

            ext = drvDst.GetMetadata_Dict().get('DMD_EXTENSION', '')
            if ext == '':
                ext = LUT_EXT.get(drvDst.ShortName, '')
            if not pathDst.endswith(ext):
                pathDst += ext

            if not fileNeedsUpdate(pathSrc, pathDst):
                continue

            proj = dsRasterSrc.GetProjection()
            trans = list(dsRasterSrc.GetGeoTransform())
            trans[0] = UL.x()
            trans[3] = UL.y()

            nsDst = int(BBOX.width() / abs(trans[1]))
            nlDst = int(BBOX.height() / abs(trans[5]))

            dsDst = drvMEM.Create('', nsDst, nlDst, dsRasterSrc.RasterCount, eType = dsRasterSrc.GetRasterBand(1).DataType)
            assert isinstance(dsDst, gdal.Dataset)
            dsDst.SetProjection(proj)
            dsDst.SetGeoTransform(trans)
            wo = gdal.WarpOptions()
            r = gdal.Warp(dsDst, dsRasterSrc)

            assert r > 0


            print('Write {}'.format(pathDst))
            drvDst.CreateCopy(pathDst, dsDst)

        #handle vector files
        elif re.search('(kmz|kml|shp?)$', ext, re.I):
            if not fileNeedsUpdate(pathSrc, pathDst):
                continue
            import ogr
            ds = ogr.Open(pathSrc)
            wkt = ds.GetLayer(0).GetSpatialRef().ExportToWkt()
            srcCrs = QgsCoordinateReferenceSystem(wkt)
            dstBOX = BBOX.toCrs(srcCrs)
            drvName = ds.GetDriver().GetName()
            ds = None
            cmd = ['ogr2ogr']
            cmd.append('-overwrite')
            #cmd.append("-f '{}'".format(drvName))
            #cmd.append('-spat_srs {}'.format(BBOX.crs().authid()))
            #cmd.append('-spat {} {} {} {}'.format(BBOX.xMinimum(), BBOX.yMinimum(),
            #                                      BBOX.xMaximum(), BBOX.yMaximum()))
            cmd.append('-clipsrc {} {} {} {}'.format(
                dstBOX.xMinimum(), dstBOX.yMinimum(),
                dstBOX.xMaximum(), dstBOX.yMaximum()))
            #cmd.append('-clipsrc spat_extent')
            cmd.append('--debug OFF')
            cmd.append('"{}"'.format(pathDst))
            cmd.append('"{}"'.format(pathSrc))
            cmdStr = ' '.join(cmd)
            subprocess.call(cmdStr, shell=True)
            print(cmdStr)

            s = ""
        else:

            s = ""


def svg2png(pathDir, overwrite=False):
    svgs = file_search(pathDir, '*.svg')
    app = QApplication([], True)
    buggySvg = []


    for pathSvg in svgs:
        dn = os.path.dirname(pathSvg)
        bn, _ = os.path.splitext(os.path.basename(pathSvg))
        pathPng = jp(dn, bn+'.png')


        if fileNeedsUpdate(pathSvg, pathPng) or overwrite:
            if sys.platform == 'darwin':
                cmd = ['inkscape']
            else:
                dirInkscape = r'C:\Program Files\Inkscape'
                assert os.path.isdir(dirInkscape)
                cmd = [jp(dirInkscape,'inkscape')]
            cmd.append('--file={}'.format(pathSvg))
            cmd.append('--export-png={}'.format(pathPng))
            from subprocess import PIPE
            p = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            rc = p.returncode
            print('Saved {}'.format(pathPng))
            if err != '':
                buggySvg.append((pathSvg, err))

    if len(buggySvg) > 0:
        six._print('SVG Errors')
        for t in buggySvg:
            pathSvg, error = t
            six._print(pathSvg, error, file=sys.stderr)
    s = ""


def png2qrc(icondir, pathQrc, pngprefix='enmapbox'):
    pathQrc = os.path.abspath(pathQrc)
    dirQrc = os.path.dirname(pathQrc)
    app = QApplication([])
    assert os.path.exists(pathQrc)
    doc = QDomDocument('RCC')
    doc.setContent(QFile(pathQrc))
    if str(doc.toString()) == '':
        doc.appendChild(doc.createElement('RCC'))
    root = doc.documentElement()
    pngFiles = set()
    fileAttributes = {}
    #add files already included in QRC

    fileNodes = doc.elementsByTagName('file')
    for i in range(fileNodes.count()):
        fileNode = fileNodes.item(i).toElement()

        file = str(fileNode.childNodes().item(0).nodeValue())
        if file.lower().endswith('.png'):
            pngFiles.add(file)
            if fileNode.hasAttributes():
                attributes = {}
                for i in range(fileNode.attributes().count()):
                    attr = fileNode.attributes().item(i).toAttr()
                    attributes[str(attr.name())] = str(attr.value())
                fileAttributes[file] = attributes

    #add new pngs in icondir
    for f in  file_search(icondir, '*.png'):
        file = os.path.relpath(f, dirQrc).replace('\\','/')
        pngFiles.add(file)

    pngFiles = sorted(list(pngFiles))

    def elementsByTagAndProperties(elementName, attributeProperties, rootNode=None):
        assert isinstance(elementName, str)
        assert isinstance(attributeProperties, dict)
        if rootNode is None:
            rootNode = doc
        resourceNodes = rootNode.elementsByTagName(elementName)
        nodeList = []
        for i in range(resourceNodes.count()):
            resourceNode = resourceNodes.item(i).toElement()
            for aName, aValue in attributeProperties.items():
                if resourceNode.hasAttribute(aName):
                    if aValue != None:
                        assert isinstance(aValue, str)
                        if str(resourceNode.attribute(aName)) == aValue:
                            nodeList.append(resourceNode)
                    else:
                        nodeList.append(resourceNode)
        return nodeList


    resourceNodes = elementsByTagAndProperties('qresource', {'prefix':pngprefix})

    if len(resourceNodes) == 0:
        resourceNode = doc.createElement('qresource')
        root.appendChild(resourceNode)
        resourceNode.setAttribute('prefix', pngprefix)
    elif len(resourceNodes) == 1:
        resourceNode = resourceNodes[0]
    else:
        raise NotImplementedError('Multiple resource nodes')

    #remove childs, as we have all stored in list pngFiles
    childs = resourceNode.childNodes()
    while not childs.isEmpty():
        node = childs.item(0)
        node.parentNode().removeChild(node)

    #insert new childs
    for pngFile in pngFiles:

        node = doc.createElement('file')
        attributes = fileAttributes.get(pngFile)
        if attributes:
            for k, v in attributes.items():
                node.setAttribute(k,v)
            s = 2
        node.appendChild(doc.createTextNode(pngFile))
        resourceNode.appendChild(node)
        print(pngFile)

    f = open(pathQrc, "w")
    f.write(doc.toString())
    f.close()




if __name__ == '__main__':
    from enmapbox.gui.utils import DIR_TESTDATA, DIR_UIFILES, DIR_ICONS, initQgisApplication


    qgsApp = initQgisApplication()
    icondir = DIR_ICONS
    pathQrc = jp(DIR_UIFILES, 'resources.qrc')

    if False:
        pathQGISRepo = r'C:\Users\geo_beja\Repositories\QGIS'
        copyQGISRessourceFile(pathQGISRepo)

    if False:
        #convert SVG to PNG and add link them into the resource file
        svg2png(icondir, overwrite=False)
        png2qrc(icondir, pathQrc)
    if True:
        migrateBJexternals()
        compile_rc_files(DIR_UIFILES)

    print('Done')

