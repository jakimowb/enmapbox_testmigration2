import os, sys, fnmatch, six, subprocess, re
from PyQt4.QtSvg import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyQt4.QtXmlPatterns import *
ROOT = os.path.dirname(os.path.dirname(__file__))
jp = os.path.join


def getDOMAttributes(elem):
    assert isinstance(elem, QDomElement)
    values = dict()
    attributes = elem.attributes()
    for a in range(attributes.count()):
        attr = attributes.item(a)
        values[attr.nodeName()] = attr.nodeValue()
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


def make():

    #compile Qt resource files
    resourcefiles = file_search(ROOT, 'resource*.qrc', recursive=True)
    assert len(resourcefiles) > 0
    for f in resourcefiles:
        dn = os.path.dirname(f)
        bn = os.path.basename(f)
        bn = os.path.splitext(bn)[0]
        pathPy2 = os.path.join(dn, bn+'_py2.py' )
        pathPy3 = os.path.join(dn, bn+'_py3.py' )
        print('Make {}'.format(pathPy2))
        subprocess.call(['pyrcc4','-py2','-o',pathPy2, f])
        print('Make {}'.format(pathPy3))
        subprocess.call(['pyrcc4','-py3','-o',pathPy3, f])


def svg2png(pathDir, overwrite=False, mode='INKSCAPE'):
    assert mode in ['INKSCAPE', 'WEBKIT', 'SVG']
    from PyQt4.QtWebKit import QWebPage

    svgs = file_search(pathDir, '*.svg')
    app = QApplication([], True)

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
            dirInkscape = r'C:\Program Files\Inkscape'
            assert os.path.isdir(dirInkscape)
            cmd = [jp(dirInkscape,'inkscape')]
            cmd.append('--file={}'.format(pathSvg))
            cmd.append('--export-png={}'.format(pathPng))
            subprocess.call(cmd)

            s = ""


def png2qrc(icondir, pathQrc):
    pathQrc = os.path.abspath(pathQrc)
    dirQrc = os.path.dirname(pathQrc)
    app = QApplication([])
    assert os.path.exists(pathQrc)
    doc = QDomDocument()
    doc.setContent(QFile(pathQrc))

    query = QXmlQuery()
    #query.setQuery("doc('{}')/RCC/qresource/file".format(pathQrc))
    query.setQuery("doc('{}')/RCC/qresource[@prefix=\"enmapbox/png\"]/file".format(pathQrc))
    query.setQuery("for $x in doc('{}')/RCC/qresource[@prefix=\"enmapbox/png\"] return data($x)".format(pathQrc))
    assert query.isValid()
    #elem = doc.elementsByTagName('qresource')print
    pngFiles = [r.strip() for r in str(query.evaluateToString()).split('\n')]
    pngFiles = set([f for f in pngFiles if os.path.isfile(jp(dirQrc,f))])

    for f in  file_search(icondir, '*.png'):
        xmlPath = os.path.relpath(f, dirQrc).replace('\\','/')
        pngFiles.add(xmlPath)

    pngFiles = sorted(list(pngFiles))
    resourceNodes = doc.elementsByTagName('qresource')
    for i in range(resourceNodes.count()):
        resourceNode = resourceNodes.item(i).toElement()
        if resourceNode.hasAttribute('prefix') and resourceNode.attribute('prefix') == "enmapbox/png":
            childs = resourceNode.childNodes()
            while not childs.isEmpty():
                node = childs.item(0)
                node.parentNode().removeChild(node)

            for pngFile in pngFiles:
                node = doc.createElement('file')
                node.appendChild(doc.createTextNode(pngFile))
                resourceNode.appendChild(node)
    f = open(pathQrc, "w")
    f.write(doc.toString())
    f.close()
    s = ""



if __name__ == '__main__':
    icondir = jp(ROOT, *['enmapbox','gui','icons'])
    pathQrc = jp(ROOT, *['enmapbox','gui','ui','resources.qrc'])
    if False:
        #convert SVG to PNG and add link them into the resource file
        svg2png(icondir, overwrite=True)
        png2qrc(icondir, pathQrc)
    if True: make()
    print('Done')

