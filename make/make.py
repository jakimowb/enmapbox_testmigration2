import os, sys, fnmatch, six, subprocess, re

from qgis.core import *

from PyQt4.QtSvg import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyQt4.QtXmlPatterns import *
ROOT = os.path.dirname(os.path.dirname(__file__))
from enmapbox import DIR_UI
jp = os.path.join
import gdal, ogr

def getDOMAttributes(elem):
    assert isinstance(elem, QDomElement)
    values = dict()
    attributes = elem.attributes()
    for a in range(attributes.count()):
        attr = attributes.item(a)
        values[str(attr.nodeName())] = attr.nodeValue()
    return values

def file_search(rootdir, wildcard, recursive=False, ignoreCase=False):
    assert rootdir is not None
    if not os.path.isdir(rootdir):
        six.print_("Path is not a directory:{}".format(rootdir), file=sys.stderr)

    results = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if (ignoreCase and fnmatch.fnmatch(file.lower(), wildcard.lower())) \
                    or fnmatch.fnmatch(file, wildcard):
                results.append(os.path.join(root, file))
        if not recursive:
            break
    return results




def make(ROOT):
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
    for root_dir, f in resourcefiles:
        #dn = os.path.dirname(f)
        pathQrc = os.path.normpath(jp(root_dir, f))
        assert os.path.exists(pathQrc), pathQrc
        bn = os.path.basename(f)
        bn = os.path.splitext(bn)[0]
        pathPy2 = os.path.join(DIR_UI, bn+'_py2.py' )
        pathPy3 = os.path.join(DIR_UI, bn+'_py3.py' )
        print('Make {}'.format(pathPy2))
        subprocess.call(['pyrcc4','-py2','-o',pathPy2, pathQrc])
        print('Make {}'.format(pathPy3))
        subprocess.call(['pyrcc4','-py3','-o',pathPy3, pathQrc])


def fileNeedsUpdate(file1, file2):
    if not os.path.exists(file2):
        return True
    else:
        if not os.path.exists(file1):
            return True
        else:
            return os.path.getmtime(file1) > os.path.getmtime(file2)

def createTestData(dirSrc, dirDst, BBOX, drv=None):

    import tempfile, random
    from qgis.core import QgsRectangle, QgsPoint, QgsPointV2, QgsCoordinateReferenceSystem
    from enmapbox.utils import SpatialExtent
    max_offset = 0 #in %


    assert isinstance(BBOX, SpatialExtent)
    from enmapbox.utils import SpatialExtent

    drvMEM = gdal.GetDriverByName('MEM')
    UL = QgsPoint(*BBOX.upperLeft())
    LR = QgsPoint(*BBOX.lowerRight())
    LUT_EXT = {'ENVI': '.bsq'}
    files = file_search(dirSrc, '*', recursive=True)
    for file in files:
        bn = os.path.basename(file)


        if re.search('(bsq|bip|bil|tiff?)$', bn, re.I):
            dsRasterSrc = gdal.Open(file)
            assert isinstance(dsRasterSrc, gdal.Dataset)
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

            drvDst = gdal.GetDriverByName(drv) if drv is not None else dsRasterSrc.GetDriver()
            #try to retrieve an extension
            pathDst = os.path.join(dirDst, os.path.splitext(os.path.basename(file))[0])
            ext = drvDst.GetMetadata_Dict().get('DMD_EXTENSION','')
            if ext == '':
                ext = LUT_EXT.get(drvDst.ShortName, '')
            if not pathDst.endswith(ext):
                pathDst += ext
            print('Write {}'.format(pathDst))
            drvDst.CreateCopy(pathDst, dsDst)

        elif re.search('(kmz|kml|shp?)$', bn, re.I):

            s = ""
        else:

            s = ""


def svg2png(pathDir, overwrite=False, mode='INKSCAPE'):
    assert mode in ['INKSCAPE', 'WEBKIT', 'SVG']
    from PyQt4.QtWebKit import QWebPage

    svgs = file_search(pathDir, '*.svg')
    app = QApplication([], True)
    buggySvg = []


    for pathSvg in svgs:
        dn = os.path.dirname(pathSvg)
        bn, _ = os.path.splitext(os.path.basename(pathSvg))
        pathPng = jp(dn, bn+'.png')

        if mode == 'SVG':
            renderer = QSvgRenderer(pathSvg)
            doc_size = renderer.defaultSize() # size in px
            img = QImage(doc_size, QImage.Format_ARGB32)
            #img.fill(0xaaA08080)
            painter = QPainter(img)
            renderer.render(painter)
            painter.end()
            if overwrite or not os.path.exists(pathPng):
                img.save(pathPng, quality=100)
            del painter, renderer
        elif mode == 'WEBKIT':
            page = QWebPage()
            frame = page.mainFrame()
            f = QFile(pathSvg)
            if f.open(QFile.ReadOnly | QFile.Text):
                textStream = QTextStream(f)
                svgData = textStream.readAll()
                f.close()

            qba = QByteArray(str(svgData))
            frame.setContent(qba,"image/svg+xml")
            page.setViewportSize(frame.contentsSize())

            palette = page.palette()
            background_color = QColor(50,0,0,50)
            palette.setColor(QPalette.Window, background_color)
            brush = QBrush(background_color)
            palette.setBrush(QPalette.Window, brush)
            page.setPalette(palette)

            img = QImage(page.viewportSize(), QImage.Format_ARGB32)
            img.fill(background_color) #set transparent background
            painter = QPainter(img)
            painter.setBackgroundMode(Qt.OpaqueMode)
            #print(frame.renderTreeDump())
            frame.render(painter)
            painter.end()

            if overwrite or not os.path.exists(pathPng):
                print('Save {}...'.format(pathPng))
                img.save(pathPng, quality=100)
            del painter, frame, img, page
            s  =""
        elif mode == 'INKSCAPE':
            if fileNeedsUpdate(pathSvg, pathPng):
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

    qgsApp = QgsApplication([], True)

    qgsApp.initQgis()


    icondir = jp(ROOT, *['enmapbox','gui','icons'])
    pathQrc = jp(ROOT, *['enmapbox','gui','ui','resources.qrc'])
    if True:
        #convert SVG to PNG and add link them into the resource file
        svg2png(icondir, overwrite=True)
        png2qrc(icondir, pathQrc)
        if True: make(DIR_UI)
    if False:
        dirSrc = r'E:\_EnMAP\Project_EnMAP-Box\SampleData\urbangradient_data'
        dirDst = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapbox\testdata\UrbanGradient'

        from qgis.core import *
        from enmapbox.utils import SpatialExtent

        UL = QgsPoint(383851.349,5819308.225)
        LR = QgsPoint(384459.867,5818407.722)
        crs = QgsCoordinateReferenceSystem('EPSG:32633')
        ext = SpatialExtent(crs, UL, LR)
        createTestData(dirSrc, dirDst, ext)
        s = ""

    print('Done')

