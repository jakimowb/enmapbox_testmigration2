# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    docks.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from __future__ import absolute_import, unicode_literals

import itertools, codecs
import os
import uuid
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *

import pyqtgraph.dockarea.Dock
from pyqtgraph.widgets.VerticalLabel import VerticalLabel




class DockWindow(QMainWindow):
    def __init__(self, area, **kwargs):
        QMainWindow.__init__(self, **kwargs)
        self.setWindowTitle('EnMAPBox')
        import enmapbox.gui.enmapboxgui
        self.setWindowIcon(enmapbox.gui.enmapboxgui.getIcon())
        self.setCentralWidget(area)

    def closeEvent(self, *args, **kwargs):
        self.centralWidget().clear()

class DockArea(pyqtgraph.dockarea.DockArea):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)

    def __init__(self, *args, **kwds):
        super(DockArea, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)

        s = ""

    def closeEvent(self, closeEvent):
        assert isinstance(closeEvent, QCloseEvent)
        s = ""

    def makeContainer(self, typ):
        c = super(DockArea, self).makeContainer(typ)
        #c.apoptose = lambda x : DockArea.containerApoptose(c, x)
        #c.apoptose = lambda p : DockArea.containerApoptose(c,p)
        #c.apoptose(True)
        return c

    #todo: somehow manipulate this to solve issue #21
    #ask user to really close DockArea if more than one dock is opened
    #"Do you really want to close this window and all contents?"
    @staticmethod
    def containerApoptose(self, propagate):
        ##if there is only one (or zero) item in this container, disappear.
        cont = self._container
        c = self.count()
        if c > 1:
            return
        if self.count() == 1:  ## if there is one item, give it to the parent container (unless this is the top)
            if self is self.area.topContainer:
                return
            self.container().insert(self.widget(0), 'before', self)
        # print "apoptose:", self
        self.close()
        if propagate and cont is not None:
            cont.apoptose()

    def apoptose(self):
        #print "apoptose area:", self.temporary, self.topContainer, self.topContainer.count()
        if self.topContainer.count() == 0:
            self.topContainer = None
            from enmapbox.gui.enmapboxgui import EnMAPBoxUI
            if not isinstance(self.topLevelWidget(), EnMAPBoxUI) and \
                len(self.docks) > 0:
                info = 'Do you really want to close these {} windows?'.format(len(self.docks))
                result = QMessageBox.question(self, "Question",info,
                                              buttons = QMessageBox.Yes | QMessageBox.No,
                                              defaultButton=QMessageBox.No)
                if result == QMessageBox.No:
                    return
            if self.temporary and self.home is not None:
                self.home.removeTempArea(self)
        else:
            s = ""

    def addDock(self, enmapboxdock, position='bottom', relativeTo=None, **kwds):
        assert enmapboxdock is not None
        assert isinstance(enmapboxdock, Dock)
        return super(DockArea, self).addDock(dock=enmapboxdock, position=position, relativeTo=relativeTo, **kwds)


    def addTempArea(self):
        #overwrites the original method
        if self.home is None:
            area = DockArea(temporary=True, home=self)
            self.tempAreas.append(area)
            win = DockWindow(area)
            area.win = win
            win.show()
        else:
            area = self.home.addTempArea()
        #print "added temp area", area, area.window()
        return area

    # forward to EnMAPBox
    def dragEnterEvent(self, event):
        self.sigDragEnterEvent.emit(event)

    # forward to EnMAPBox
    def dragMoveEvent(self, event):

        self.sigDragMoveEvent.emit(event)

    # forward to EnMAPBox
    def dragLeaveEvent(self, event):

        self.sigDragLeaveEvent.emit(event)

    # forward to EnMAPBox
    def dropEvent(self, event):
        self.sigDropEvent.emit(event)


from enmapbox.gui.utils import KeepRefs
class Dock(pyqtgraph.dockarea.Dock, KeepRefs):
    @staticmethod
    def readXml(elem):


        return None

    '''
    Handle style sheets etc., basic stuff that differs from pyqtgraph dockarea
    '''
    sigTitleChanged = pyqtSignal(str)


    def __init__(self, name='Data View', closable=True, *args, **kwds):
        super(Dock, self).__init__(name=name, closable=False, *args, **kwds)
        KeepRefs.__init__(self)
        #ssert enmapboxInstance is not None
        #self.enmapbox = enmapboxInstance
        self.setStyleSheet('background:#FFF')

        #replace PyQtGraph Label by EnmapBox labels (could be done by inheritances as well)
        title = self.title()
        self.topLayout.removeWidget(self.label)
        del self.label
        self.label = self._createLabel(title=title)
        self.label.setMinimumHeight(50)
        self.topLayout.addWidget(self.label, 0, 1)
        self.uuid = uuid.uuid4()
        if closable:
            self.label.sigCloseClicked.connect(self.close)

        self.raiseOverlay()


        self.hStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top-width: 0px;
        }
        """
        self.vStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-left-width: 0px;
        }
        """
        self.nStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
        }"""
        self.dragStyle = """
        Dock > QWidget {
            border: 4px solid #00F;
            border-radius: 5px;
        }"""

        self.widgetArea.setStyleSheet(self.hStyle)
        self.topLayout.update()

    def contextMenu(self):
        """
        implement this to return a QMenu with context menue properties for this dock.
        :return: None or QMenu
        """

        menu = QMenu()

        if self.isVisible():
            a = menu.addAction('Hide Dock')
            a.triggered.connect(lambda : self.setVisible(True))
        else:
            a = menu.addAction('Show Dock')
            a.triggered.connect(lambda : self.setVisible(False))

        return menu

    sigVisibilityChanged = pyqtSignal(bool)
    def setVisible(self, b):

        i = self.isVisible()
        super(Dock, self).setVisible(b)
        if i != self.isVisible():
            self.sigVisibilityChanged.emit(self.isVisible())


    def setTitle(self, title):
        """
        Override setTitle to emit a signal after title was changed
        :param title:
        :return:
        """
        super(Dock, self).setTitle(title)
        self.sigTitleChanged.emit(title)

    def _createLabel(self, *args, **kwds):
        """
        Overide this function to provide a dock-specific label
        :return:
        """
        return DockLabel(self,  *args, **kwds)

    def append_hv_style(self, stylestr):
        obj_name = type(self).__name__
        style = ' \n{} {{\n{}\n}} '.format(obj_name, stylestr)
        self.hStyle += style
        self.vStyle += style

    def addTempArea(self):
        if self.home is None:
            area = DockArea(temporary=True, home=self)
            self.tempAreas.append(area)
            win = DockWindow(area)
            area.win = win
            win.show()
        else:
            area = self.home.addTempArea()
        #print "added temp area", area, area.window()
        return area





class DockLabel(VerticalLabel):
    sigClicked = pyqtSignal(object, object)
    sigCloseClicked = pyqtSignal()
    sigNormalClicked = pyqtSignal()
    sigContextMenuRequest = pyqtSignal(QContextMenuEvent)
    def __init__(self, dock, title=None, allow_floating=True):
        assert isinstance(dock, Dock)
        self.dim = False
        self.fixedWidth = False
        self.dock = dock
        self.buttons = list()  # think from right to left
        if title is None:
            title = self.dock.title()
        VerticalLabel.__init__(self, title, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.updateStyle()
        self.setAutoFillBackground(False)
        self.startedDrag = False

        #adjust minimum size
        self.setMinimumSize(50,50)

        self.pressPos = QtCore.QPoint()

        closeButton = QToolButton(self)
        closeButton.clicked.connect(self.sigCloseClicked)
        closeButton.setToolTip('Close window')
        closeButton.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.buttons.append(closeButton)

        if allow_floating:
            floatButton = QToolButton(self)
            #testButton.clicked.connect(self.sigNormalClicked)
            floatButton.setToolTip('Float window')
            floatButton.clicked.connect(lambda : self.dock.float())
            floatButton.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarNormalButton))
            self.buttons.append(floatButton)

    def sizeHint(self):
        s_min = 50
        if self.orientation == 'vertical':
            if hasattr(self, 'hint'):
                return QtCore.QSize(self.hint.height(), self.hint.width())
            else:
                return QtCore.QSize(s_min, 50)
        else:
            if hasattr(self, 'hint'):
                return QtCore.QSize(self.hint.width(), self.hint.height())
            else:
                return QtCore.QSize(50, s_min)

    def minimumSizeHint(self):
        h = super(DockLabel, self).minimumSizeHint()
        m = min([h.width(), h.height()])
        return QSize(m,m)

    def contextMenuEvent(self, event):
        assert isinstance(event, QContextMenuEvent)
        self.sigContextMenuRequest.emit(event)

    def updateStyle(self):

        r = '3px'

        if self.dim:#inactive tab
            fg = '#aaa'
            #bg = '#44a'
            #border = '#339'
            bg = '#666'
            border = '#444'
        else:#active tab
            fg = '#fff'
            bg = '#66c'
            border = '#55B'

        if self.orientation == 'vertical':
            pad = '{}px'.format(3 + len(self.buttons)* self.height())

            self.vStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-bottom: 3px;
                padding-top: %s;
            }""" % (bg, fg, r, r, border, pad)
            self.setStyleSheet(self.vStyle)
        else:
            pad = '{}px'.format(3 + len(self.buttons) * self.width())
            pad = '{}px'.format(10* len(self.buttons))

            self.hStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: %s;
            }""" % (bg, fg, r, r, border, pad)
            self.setStyleSheet(self.hStyle)


    def setDim(self, d):
        if self.dim != d:
            self.dim = d
            self.updateStyle()

    def setOrientation(self, o):
        VerticalLabel.setOrientation(self, o)
        self.updateStyle()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pressPos = ev.pos()
            self.startedDrag = False
            ev.accept()

    def mouseMoveEvent(self, ev):
        if not self.startedDrag and (
            ev.pos() - self.pressPos).manhattanLength() > QApplication.startDragDistance():
            self.dock.startDrag()
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if not self.startedDrag:
            self.sigClicked.emit(self, ev)
        ev.accept()

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dock.float()

    def resizeEvent(self, ev):
        if self.orientation == 'vertical':
            size = ev.size().width()
        else:
            size = ev.size().height()

        for i, btn in enumerate([b for b in self.buttons if not b.isHidden()]):
            if self.orientation == 'vertical':
                pos = QtCore.QPoint(0, i * size)
            else:
                pos = QtCore.QPoint(ev.size().width() - (i+1)*size, 0)
            btn.setFixedSize(QtCore.QSize(size, size))
            btn.move(pos)

        super(DockLabel, self).resizeEvent(ev)



class CursorLocationValueDock(Dock):

    _instance = None

    """
    A dock to visualize cursor location values
    """

    def __init__(self, *args, **kwds):
        super(CursorLocationValueDock, self).__init__(*args, **kwds)
        from enmapbox.gui.cursorlocationvalue import CursorLocationValueWidget
        self.dataSourceManager = None
        self.w = CursorLocationValueWidget(self)
        self.layout.addWidget(self.w)
        self.setTitle('Cursor Location Values')

    def connectDataSourceManager(self, dataSourceManager):
        self.w.connectDataSourceManager(dataSourceManager)


    def showLocationValues(self, *args):
        self.w.showLocationValues(*args)

class TextDockWidget(QWidget, loadUI('textdockwidget.ui')):

    FILTERS = ';;'.join(["Textfiles (*.txt *.csv *.hdr)", \
                        "HTML (*.html)" \
                        "Any file (*.*)"
                         ])

    sigSourceChanged = pyqtSignal(str)
    def __init__(self, parent=None):
        super(TextDockWidget, self).__init__(parent=parent)
        self.setupUi(self)
        self.mFile = None

        self.btnLoadFile.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.btnLoadFile.clicked.connect(lambda: self.loadFile(
            QFileDialog.getOpenFileName(self, 'Open File', directory=self.mFile, filter=TextDockWidget.FILTERS)))
        self.btnSaveFile.clicked.connect(lambda: self.save(saveAs=False))
        self.btnSaveAs.clicked.connect(lambda :self.save(saveAs=True))

    def loadFile(self, path):
        if os.path.isfile(path):
            data = None
            with codecs.open(path, 'r', 'utf-8') as file:
                data = ''.join(file.readlines())

            ext = os.path.splitext(path)[-1].lower()
            if data is not None:
                if ext in ['.html']:
                    self.textEdit.setHtml(data)
                else:
                    self.textEdit.setText(data)

                self.mFile = path

        else:
            self.mFile = None
        self.sigSourceChanged.emit(str(path))


    def save(self, saveAs=False):
        if self.mFile is None or saveAs:
            path = QFileDialog.getSaveFileName(self, 'Save file...', \
                                        directory=self.mFile,
                                        filter=TextDockWidget.FILTERS)
            s = ""
            if len(path) > 0:
                self.mFile = path

        if self.mFile is not None and len(self.mFile) > 0:
            ext = os.path.splitext(self.mFile)[-1].lower()
            import codecs
            if ext in ['.txt','.csv', '.hdr']:

                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.textEdit.toPlainText())
            elif ext in ['.html']:
                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.textEdit.toHtml())


class MimeDataTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(MimeDataTextEdit,self).__init__(*args, **kwargs)
        #self.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.setOverwriteMode(False)

    def canInsertFromMimeData(self, QMimeData):
        return True

    def insertFromMimeData(self, mimeData):
        assert isinstance(mimeData, QMimeData)
        formats = [str(f) for f in mimeData.formats()]
        self.clear()
        def append(txt):
            self.moveCursor(QTextCursor.End)
            self.insertPlainText(txt+'\n')
            self.moveCursor(QTextCursor.End)

        for format in formats:
            append('####{}####'.format(format))
            if format == 'text/uri-list':
                self.insertPlainText(str(mimeData.data('text/uri-list')))
            if format == 'text/html':
                self.insertHtml(mimeData.html())
            elif format == 'text/plain':
                self.insertPlainText(mimeData.text())
            else:
                append('### (raw data as string) ###')
                self.insertPlainText(str(mimeData.data(format)))
            append('\n')

    def dragEnterEvent(self, event):
        event.setDropAction(Qt.CopyAction)  # copy but do not remove
        event.accept()

    def dropEvent(self, event):
        self.insertFromMimeData(event.mimeData())
        event.setDropAction(Qt.CopyAction)
        event.accept()


class MimeDataDockWidget(QWidget, loadUI('mimedatadockwidget.ui')):


    def __init__(self, parent=None):
        super(MimeDataDockWidget, self).__init__(parent=parent)
        self.setupUi(self)

    def loadFile(self, path):
        if os.path.isfile(path):
            data = None
            with codecs.open(path, 'r', 'utf-8') as file:
                data = ''.join(file.readlines())

            ext = os.path.splitext(path)[-1].lower()
            if data is not None:
                if ext in ['.html']:
                    self.textEdit.setHtml(data)
                else:
                    self.textEdit.setText(data)

                self.mFile = path

        else:
            self.mFile = None
        self.sigSourceChanged.emit(str(path))


    def save(self, saveAs=False):
        if self.mFile is None or saveAs:
            path = QFileDialog.getSaveFileName(self, 'Save file...', \
                                        directory=self.mFile,
                                        filter=TextDockWidget.FILTERS)
            s = ""
            if len(path) > 0:
                self.mFile = path

        if self.mFile is not None and len(self.mFile) > 0:
            ext = os.path.splitext(self.mFile)[-1].lower()
            import codecs
            if ext in ['.txt','.csv', '.hdr']:

                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.textEdit.toPlainText())
            elif ext in ['.html']:
                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.textEdit.toHtml())


class TextDock(Dock):
    """
    A dock to visualize textural data
    """
    def __init__(self, *args, **kwds):
        html = kwds.pop('html', None)
        plainTxt = kwds.pop('plainTxt', None)

        super(TextDock, self).__init__(*args, **kwds)

        self.textDockWidget = TextDockWidget(self)

        if html:
            self.textDockWidget.textEdit.insertHtml(html)
        elif plainTxt:
            self.textDockWidget.textEdit.insertPlainText(plainTxt)
        self.layout.addWidget(self.textDockWidget)


class WebViewDock(Dock):
    def __init__(self, *args, **kwargs):
        uri = kwargs.pop('uri', None)
        url = kwargs.pop('url', None)
        super(WebViewDock,self).__init__(*args, **kwargs)
        #self.setLineWrapMode(QTextEdit.FixedColumnWidth)

        from PyQt4.QtWebKit import QWebView
        self.webView = QWebView(self)
        self.layout.addWidget(self.webView)

        if uri is not None:
            self.load(uri)
        elif url is not None:
            self.load(url)

    def load(self, uri):
        if os.path.isfile(uri):
            url = QUrl.fromLocalFile(uri)
        else:
            url = QUrl(uri)
        self.webView.load(url)
        settings = self.webView.page().settings()
        from PyQt4.QtWebKit import QWebSettings
        settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebSettings.AutoLoadImages, True)


class MimeDataDock(Dock):
    """
    A dock to show dropped mime data
    """
    def __init__(self,*args, **kwds):
        super(MimeDataDock, self).__init__(*args, **kwds)

        self.mimeDataWidget = MimeDataDockWidget(self)
        self.layout.addWidget(self.mimeDataWidget)


class SpectralLibraryDock(Dock):
    sigLoadFromMapRequest = pyqtSignal()
    def __init__(self,*args, **kwds):
        super(SpectralLibraryDock, self).__init__(*args, **kwds)

        from enmapbox.gui.spectrallibraries import SpectralLibraryWidget
        self.speclibWidget = SpectralLibraryWidget(self)
        self.speclibWidget.sigLoadFromMapRequest.connect(self.sigLoadFromMapRequest)
        self.layout.addWidget(self.speclibWidget)
        self.mShowMapInteraction = True


if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py

    from enmapbox.gui.utils import initQgisApplication
    qgsApp = initQgisApplication()
    da = DockArea()
    dock = MimeDataDock()
    da.addDock(dock)
    da.show()
    qgsApp.exec_()
