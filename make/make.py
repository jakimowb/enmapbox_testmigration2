import os, sys, fnmatch, six, subprocess
from PyQt4.QtSvg import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

ROOT = os.path.dirname(os.path.dirname(__file__))
jp = os.path.join

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


def svg2png(pathDir, overwrite=False):

    from PyQt4.QtWebKit import QWebPage

    svgs = file_search(pathDir, '*.svg')
    app = QApplication([], True)

    for path in svgs:
        dn = os.path.dirname(path)
        bn, _ = os.path.splitext(os.path.basename(path))
        pathNew = jp(dn, bn+'.png')

        if False:
            renderer = QSvgRenderer(path)
            doc_size = renderer.defaultSize() # size in px
            img = QImage(doc_size, QImage.Format_ARGB32)
            #img.fill(0xaaA08080)
            painter = QPainter(img)
            renderer.render(painter)
            painter.end()
            if overwrite or not os.path.exists(pathNew):
                img.save(pathNew, quality=100)
            del painter, renderer
        else:


            # img.fill(0xaaA08080)

            page = QWebPage()

            frame = page.mainFrame()

            #textStream = QTextStream(QString(path))
            #svgData = textStream.readAll()
            f = QFile(path)
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

            if overwrite or not os.path.exists(pathNew):
                print('Save {}...'.format(pathNew))
                img.save(pathNew, quality=100)
            del painter, frame, img, page
            s  =""


if __name__ == '__main__':
    icondir = jp(ROOT, *['enmapbox','gui','icons'])
    if True: svg2png(icondir, overwrite=True)
    if False: make()
    print('Done')

