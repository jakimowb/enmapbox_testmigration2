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

import codecs
import typing
import enum
import uuid

from PyQt5.QtCore import pyqtSignal, QSettings, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QMenu
from qgis.core import QgsCoordinateReferenceSystem, QgsMapLayer
from qgis.gui import QgsMapCanvas

from enmapbox.gui.mapcanvas import MapCanvas, CanvasLink
from qgis.PyQt import QtCore
from qgis.core import QgsVectorLayer

from enmapbox.gui import SpectralLibraryWidget, SpectralLibrary
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *

from enmapbox.externals.qps.externals.pyqtgraph.dockarea import DockArea as pgDockArea
from enmapbox.externals.qps.externals.pyqtgraph.dockarea.DockArea import TempAreaWindow
from enmapbox.externals.qps.externals.pyqtgraph.dockarea.Dock import Dock as pgDock
from enmapbox.externals.qps.externals.pyqtgraph.dockarea.Dock import DockLabel as pgDockLabel
from enmapbox.externals.qps.layerproperties import pasteStyleFromClipboard
from enmapbox.gui.mimedata import MDF_QGIS_LAYER_STYLE
from enmapbox.externals.qps.speclib.core import is_spectral_library


class DockWindow(QMainWindow):
    def __init__(self, area, **kwargs):
        QMainWindow.__init__(self, **kwargs)
        self.setWindowTitle('EnMAPBox')
        import enmapbox.gui.enmapboxgui
        self.setWindowIcon(enmapbox.icon())
        self.setCentralWidget(area)

    def closeEvent(self, *args, **kwargs):
        self.centralWidget().clear()


class Dock(pgDock):
    @staticmethod
    def readXml(elem):

        return None

    '''
    Handle style sheets etc., basic stuff that differs from pyqtgraph dockarea
    '''
    sigTitleChanged = pyqtSignal(str)

    def __init__(self, name='Data View', closable=True, *args, **kwds):
        super().__init__(name=name, closable=closable, *args, **kwds)
        # KeepRefs.__init__(self)
        # ssert enmapboxInstance is not None
        # self.enmapbox = enmapboxInstance
        # self.setStyleSheet('background:#FFF')

        # replace PyQtGraph Label by EnmapBox labels (could be done by inheritances as well)
        title = self.title()
        if True:
            # self.topLayout.addWidget(self.label, 0, 1)
            newLabel = self._createLabel(title=title)
            oldLabel = self.label
            widgetItem = self.topLayout.replaceWidget(oldLabel, newLabel)
            oldLabel.setParent(None)
            assert isinstance(widgetItem, QWidgetItem)
            self.label = newLabel
            if closable:
                self.label.sigCloseClicked.connect(self.close)

        else:
            pass

        self.uuid = uuid.uuid4()

        self.raiseOverlay()

        if False:
            self.hStyle = """
            Dock > QWidget {
                border: 1px solid #000;
                border-radius: 1px;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-top-width: 0px;
            }
            """
            self.vStyle = """
            Dock > QWidget {
                border: 1px solid #000;
                border-radius: 1px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-left-width: 0px;
            }
            """
            self.nStyle = """
            Dock > QWidget {
                border: 1px solid #000;
                border-radius: 1px;
            }"""
            self.dragStyle = """
            Dock > QWidget {
                border: 4px solid #00F;
                border-radius: 1px;
            }"""

            self.widgetArea.setStyleSheet(self.hStyle)
        self.topLayout.update()

    def contextMenu(self, menu: QMenu = None):
        warnings.warn('Use populateContextMenu instead', DeprecationWarning)
        self.populateContextMenu(menu)
        return menu

    def populateContextMenu(self, menu: QMenu) -> QMenu:
        """
        implement this to return a QMenu with context menu properties for this dock.
        :return: None or QMenu
        """
        assert isinstance(menu, QMenu)
        if self.isVisible():
            a = menu.addAction('Hide View')
            a.triggered.connect(lambda: self.setVisible(False))
        else:
            a = menu.addAction('Show View')
            a.triggered.connect(lambda: self.setVisible(True))

        a = menu.addAction('Close View')
        a.triggered.connect(lambda: self.close())
        return menu

    sigVisibilityChanged = pyqtSignal(bool)

    def setVisible(self, b: bool):

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

        old = self.title()
        super(Dock, self).setTitle(title)
        if old != title:
            self.sigTitleChanged.emit(title)

    def _createLabel(self, *args, **kwds):
        """
        Override this function to provide a dock-specific label
        :return:
        """
        return DockLabel(self, *args, **kwds)

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
        return area

    def setOrientation(self, o='auto', force=False):
        """
        Sets the orientation of the title bar for this Dock.
        Must be one of 'auto', 'horizontal', or 'vertical'.
        By default ('auto'), the orientation is determined
        based on the aspect ratio of the Dock.
        """
        # print self.name(), "setOrientation", o, force
        if o == 'auto' and self.autoOrient:
            # if self.container().type() == 'tab':
            if self.container() is None or self.container().type() == 'tab':
                o = 'horizontal'
            elif self.width() > self.height() * 1.5:
                o = 'vertical'
            else:
                o = 'horizontal'
        if force or self.orientation != o:
            self.orientation = o
            self.label.setOrientation(o)
            self.updateStyle()

    def unfloat(self, *args):

        from enmapbox import EnMAPBox
        enmapbox = EnMAPBox.instance()
        if isinstance(enmapbox, EnMAPBox):
            area = enmapbox.ui.dockArea
            assert isinstance(area, DockArea)
            area.moveDock(self, 'left', None)


class DockArea(pgDockArea):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)

    def __init__(self, *args, **kwds):
        super(DockArea, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)

        s = ""

    def makeContainer(self, typ):
        c = super(DockArea, self).makeContainer(typ)
        # c.apoptose = lambda x : DockArea.containerApoptose(c, x)
        # c.apoptose = lambda p : DockArea.containerApoptose(c,p)
        # c.apoptose(True)
        return c

    """
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

    def fixDock(self, dock):

        s = ""
    """

    def floatDock(self, dock):
        """Removes *dock* from this DockArea and places it in a new window."""

        lastArea = dock.area
        super().floatDock(dock)

        if isinstance(lastArea, DockArea):
            lastArea.sigDockRemoved.emit(dock)

        parentWindow = dock.parent()
        while isinstance(parentWindow, QObject) and parentWindow.parent():
            parentWindow = parentWindow.parent()

        if isinstance(parentWindow, TempAreaWindow):

            parentWindow.setWindowTitle('EnMAP-Box')
            parentWindow.setWindowIcon(QIcon(':/enmapbox/gui/ui/icons/enmapbox.svg'))
            # fix for https://bitbucket.org/hu-geomatics/enmap-box/issues/
            parentWindow.resize(QSize(300, 300))
        else:
            s = ""
        if False:
            newArea = dock.area
            if isinstance(newArea, DockArea):
                s2 = QSize(newArea.size().width() + 1, newArea.size().height())
                newArea.resize(s2)

    def apoptose(self):
        try:
            if self.topContainer is not None and self.topContainer.count() == 0:
                self.topContainer = None

            if self.topContainer is None:
                if self.temporary and self.home is not None:
                    self.home.removeTempArea(self)
            else:
                pass
        except:
            pass

    sigDockAdded = pyqtSignal(Dock)
    sigDockRemoved = pyqtSignal(Dock)

    def addDock(self, dock, position='bottom', relativeTo=None, **kwds) -> Dock:
        assert dock is not None

        v = None
        try:
            visibility = dock.isVisible()
            v = super(DockArea, self).addDock(dock=dock, position=position, relativeTo=relativeTo, **kwds)
            dock.setVisible(visibility)
            self.sigDockAdded.emit(dock)
        except:
            pass
        return v

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


class DockLabel(pgDockLabel):
    sigClicked = pyqtSignal(object, object)
    sigCloseClicked = pyqtSignal()
    sigNormalClicked = pyqtSignal()
    sigContextMenuRequest = pyqtSignal(QContextMenuEvent)

    def __init__(self,
                 dock,
                 title: str = None,
                 allow_floating: bool = True,
                 showClosebutton: bool = True,
                 fontSize: int = 8):
        if title is None:
            title = self.dock.title()
        super(DockLabel, self).__init__(title, dock, showClosebutton, fontSize)

        self.mButtons = list()  # think from right to left

        self.setMinimumSize(26, 26)

        closeButton = QToolButton(self)
        closeButton.clicked.connect(self.sigCloseClicked)
        closeButton.setToolTip('Close window')
        closeButton.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.mButtons.append(closeButton)

        if allow_floating:
            floatButton = QToolButton(self)
            # testButton.clicked.connect(self.sigNormalClicked)
            floatButton.setToolTip('Float window')
            floatButton.clicked.connect(self.dock.float)
            floatButton.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarNormalButton))
            self.mButtons.append(floatButton)

            btnUnFloat = QToolButton(self)
            btnUnFloat.setText('U')
            btnUnFloat.setToolTip('Unfloat window')
            btnUnFloat.clicked.connect(self.dock.unfloat)
            self.mButtons.append(btnUnFloat)

        def setUnfloatButtonVisibility(b: bool):
            btnUnFloat.setVisible(b)
            self.update()

        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()
        if isinstance(enmapBox, EnMAPBox):
            dockArea = enmapBox.ui.dockArea
            if isinstance(dockArea, DockArea):
                dockArea.sigDockAdded.connect(lambda *args: setUnfloatButtonVisibility(False))
                dockArea.sigDockRemoved.connect(lambda *args: setUnfloatButtonVisibility(True))
        self.update()

    def contextMenuEvent(self, event):
        assert isinstance(event, QContextMenuEvent)
        self.sigContextMenuRequest.emit(event)

    # def mouseMoveEvent(self, ev):
    #    if not self.startedDrag and hasattr(self, 'pressPos'):
    #        super(DockLabel, self).mouseMoveEvent(ev)
    #    else:
    #        ev.accept()

    def resizeEvent(self, ev: QResizeEvent):
        if self.orientation == 'vertical':
            size = ev.size().width()
        else:
            size = ev.size().height()

        for i, btn in enumerate([b for b in self.mButtons if not b.isHidden()]):
            if self.orientation == 'vertical':
                pos = QtCore.QPoint(0, i * size)
            else:
                pos = QtCore.QPoint(ev.size().width() - (i + 1) * size, 0)
            btn.setFixedSize(QtCore.QSize(size, size))
            btn.move(pos)

        super(DockLabel, self).resizeEvent(ev)


class MimeDataTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(MimeDataTextEdit, self).__init__(*args, **kwargs)
        # self.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.setOverwriteMode(False)
        self.mCurrentMimeData: QMimeData = QMimeData()

    def canInsertFromMimeData(self, QMimeData) -> bool:
        return True

    def currentMimeData(self) -> QMimeData:
        return self.mCurrentMimeData

    def insertFromMimeData(self, mimeData: QMimeData):
        """
        Shows the QMimeData information
        :param mimeData: QMimeData
        """
        assert isinstance(mimeData, QMimeData)
        formats = [str(f) for f in mimeData.formats()]
        self.mCurrentMimeData = mimeData
        self.clear()

        def append(txt):
            self.moveCursor(QTextCursor.End)
            self.insertPlainText(txt + '\n')
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
                data = mimeData.data(format)
                if isinstance(data, QByteArray):
                    self.insertPlainText(str(mimeData.data(format)))
            append('\n')

    def dragEnterEvent(self, event):
        event.setDropAction(Qt.CopyAction)  # copy but do not remove
        event.accept()

    def dropEvent(self, event):
        self.insertFromMimeData(event.mimeData())
        event.setDropAction(Qt.CopyAction)
        event.accept()


class MimeDataDockWidget(QWidget):

    def __init__(self, parent=None):
        super(MimeDataDockWidget, self).__init__(parent=parent)
        loadUi(enmapboxUiPath('mimedatadockwidget.ui'), self)

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
            path, filter = QFileDialog.getSaveFileName(self, 'Save file...', \
                                                       directory=self.mFile,
                                                       filter=TextDockWidget.FILTERS)
            s = ""
            if len(path) > 0:
                self.mFile = path

        if self.mFile is not None and len(self.mFile) > 0:
            ext = os.path.splitext(self.mFile)[-1].lower()
            import codecs
            if ext in ['.txt', '.csv', '.hdr']:

                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.textEdit.toPlainText())
            elif ext in ['.html']:
                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.textEdit.toHtml())


class TextDockWidget(QWidget):
    """
    A widget to display text files
    """
    FILTERS = ';;'.join(["Textfiles (*.txt *.csv *.hdr)", \
                         "HTML (*.html)" \
                         "Any file (*.*)"
                         ])

    sigSourceChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Constructor
        :param parent:
        """
        super(TextDockWidget, self).__init__(parent=parent)
        loadUi(enmapboxUiPath('textdockwidget.ui'), self)

        self.setAcceptDrops(True)
        self.mFile = None
        self.mTitle = self.windowTitle()
        self.mTextEdit.setAcceptDrops(True)
        self.mTextEdit.dragEnterEven = self.dragEnterEvent
        self.mTextEdit.dropEvent = self.dropEvent
        self.nMaxBytes = 80 * 2 * 12000
        self.btnLoadFile.setDefaultAction(self.actionLoadFile)
        self.btnSaveFile.setDefaultAction(self.actionSaveFile)
        self.btnSaveFileAs.setDefaultAction(self.actionSaveFileAs)
        self.actionLoadFile.triggered.connect(self.onOpenFile)
        self.actionSaveFile.triggered.connect(lambda: self.save(saveAs=False))
        self.actionSaveFileAs.triggered.connect(lambda: self.save(saveAs=True))
        self.actionSaveFile.setEnabled(False)
        self.updateTitle()

    def onOpenFile(self):

        path, result = QFileDialog.getOpenFileName(self, 'Open File', directory=self.mFile,
                                                   filter=TextDockWidget.FILTERS)
        if isinstance(path, str) and len(path) > 0:
            self.loadFile(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        :param event: QDragEnterEvent
        """
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)

            event.accept()

    def dropEvent(self, event: QDropEvent):
        """
        :param event: QDropEvent
        """
        if event.mimeData().hasUrls():
            url = [u for u in event.mimeData().urls()][0]
            assert isinstance(url, QUrl)
            if url.isLocalFile():
                self.loadFile(url.toLocalFile())
                event.setDropAction(Qt.CopyAction)
                event.accept()

    def file(self) -> str:
        """
        Returns the path of a file added with `loadFile`
        :return: str
        """
        if self.mFile is None:
            return ''
        else:
            return self.mFile

    def loadFile(self, path, *args):
        """
        Loads a text file from `path`
        :param path: str
        """
        if os.path.isfile(path):
            data = None

            statinfo = os.stat(path)
            if statinfo.st_size > self.nMaxBytes:
                info = 'Files {} is > {} bytes'.format(path, self.nMaxBytes)
                info += '\nDo you really want to load it into this text editor?'
                result = QMessageBox.warning(self, 'Warning', info, QMessageBox.Yes, QMessageBox.Cancel)
                if result != QMessageBox.Yes:
                    return
            try:
                with open(path, 'r', 'utf-8') as file:
                    data = ''.join(file.readlines())
            except:
                with open(path, 'r') as file:
                    data = ''.join(file.readlines())

            ext = os.path.splitext(path)[-1].lower()
            if data is not None:
                if ext in ['.html']:
                    self.mTextEdit.setHtml(data)
                else:
                    self.mTextEdit.setText(data)

                self.mFile = path

        else:
            self.mFile = None
        self.updateTitle()
        self.actionSaveFile.setEnabled(os.path.isfile(self.file()))
        self.sigSourceChanged.emit(str(path))

    def updateTitle(self):
        """
        Updates the widget title
        """
        # title = '{}'.format(self.mTitle)
        title = ''
        if isinstance(self.mFile, str):
            # title += ' | {}'.format(os.path.basename(self.mFile))
            title = os.path.basename(self.mFile)
        self.setWindowTitle(title)

    def setText(self, *args, **kwds):
        """
        Sets text. See
        :param args:
        :param kwds:
        :return:
        """
        self.mTextEdit.setPlainText(*args, **kwds)

    def text(self) -> str:
        """
        Returns the plain text
        :return: str
        """
        return self.mTextEdit.toPlainText()

    def setHtml(self, *args, **kwds):
        """
        Sets thext as HTML
        :param args:
        :param kwds:
        """
        self.mTextEdit.setHtml(*args, **kwds)

    def save(self, saveAs=False):
        """
        Saves the Text
        :param saveAs: bool
        """
        if self.mFile is None or saveAs:
            path, filter = QFileDialog.getSaveFileName(self, 'Save file...', \
                                                       directory=self.mFile,
                                                       filter=TextDockWidget.FILTERS)
            s = ""
            if len(path) > 0:
                self.mFile = path

        if self.mFile is not None and len(self.mFile) > 0:
            ext = os.path.splitext(self.mFile)[-1].lower()
            import codecs
            if ext in ['.txt', '.csv', '.hdr']:

                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.mTextEdit.toPlainText())
            elif ext in ['.html']:
                with codecs.open(self.mFile, 'w', 'utf-8') as file:
                    file.write(self.mTextEdit.toHtml())


class TextDock(Dock):
    """
    A dock to visualize text data
    """

    def __init__(self, *args, **kwds):
        html = kwds.pop('html', None)
        plainTxt = kwds.pop('plainTxt', None)

        super(TextDock, self).__init__(*args, **kwds)

        self.mTextDockWidget = TextDockWidget(self)
        self.mTextDockWidget.windowTitleChanged.connect(self.setTitle)
        if html:
            self.mTextDockWidget.mTextEdit.insertHtml(html)
        elif plainTxt:
            self.mTextDockWidget.mTextEdit.insertPlainText(plainTxt)
        self.layout.addWidget(self.mTextDockWidget)

    def textDockWidget(self) -> TextDockWidget:
        """
        Returns the widget that displays the text
        :return: TextDockWidget
        """
        return self.mTextDockWidget


class WebViewDock(Dock):
    def __init__(self, *args, **kwargs):
        uri = kwargs.pop('uri', None)
        url = kwargs.pop('url', None)
        super(WebViewDock, self).__init__(*args, **kwargs)
        # self.setLineWrapMode(QTextEdit.FixedColumnWidth)

        from PyQt5.QtWebKitWidgets import QWebView
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
        from PyQt5.QtWebKit import QWebSettings
        settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebSettings.AutoLoadImages, True)


class AttributeTableDock(Dock):
    """
    A dock to show a VectorLayer attribute table
    """

    def __init__(self, layer: QgsVectorLayer, *args, **kwds):
        super(AttributeTableDock, self).__init__(*args, **kwds)
        from enmapbox.externals.qps.layerproperties import AttributeTableWidget
        self.attributeTableWidget = AttributeTableWidget(layer)
        self.addWidget(self.attributeTableWidget, 0, 0)
        self.updateTitle(self.attributeTableWidget.windowTitle())
        self.attributeTableWidget.windowTitleChanged.connect(self.updateTitle)

    def updateTitle(self, title: str):
        # we need to get a short name, not the entire title
        self.setTitle(title.split('::')[0])

    def vectorLayer(self) -> QgsVectorLayer:
        return self.attributeTableWidget.mLayer

class MimeDataDock(Dock):
    """
    A dock to show dropped mime data
    """

    def __init__(self, *args, **kwds):
        super(MimeDataDock, self).__init__(*args, **kwds)

        self.mimeDataWidget = MimeDataDockWidget(self)
        self.addWidget(self.mimeDataWidget, 0, 0)


class SpectralLibraryDock(Dock):
    """
    A Dock to show SpectralProfiles
    """
    sigLoadFromMapRequest = pyqtSignal()

    def __init__(self, *args, speclib: QgsVectorLayer = None, **kwds):
        super(SpectralLibraryDock, self).__init__(*args, **kwds)

        if not isinstance(speclib, QgsVectorLayer):
            speclib = SpectralLibrary()

        self.mSpeclibWidget: SpectralLibraryWidget = SpectralLibraryWidget(parent=self, speclib=speclib)
        self.mSpeclibWidget.spectralLibraryPlotWidget().optionShowVisualizationSettings.setChecked(False)
        self.mSpeclibWidget.sigLoadFromMapRequest.connect(self.sigLoadFromMapRequest)
        self.layout.addWidget(self.mSpeclibWidget)

        name = kwds.get('name')
        if isinstance(name, str):
            speclib.setName(name)

        self.setTitle(speclib.name())
        speclib.nameChanged.connect(lambda slib=speclib: self.setTitle(slib.name()))
        self.sigTitleChanged.connect(speclib.setName)

    def speclibWidget(self) -> SpectralLibraryWidget:
        """
        Returns the SpectralLibraryWidget
        :return: SpectralLibraryWidget
        """
        return self.mSpeclibWidget

    def speclib(self) -> SpectralLibrary:
        """Returns the underlying spectral library"""
        return self.mSpeclibWidget.speclib()

    def populateContextMenu(self, menu: QMenu):
        """
        Returns the MapDock context menu
        :return: QMenu
        """
        super(SpectralLibraryDock, self).populateContextMenu(menu)

        # here we might add Spectral Library Widget specific action
        # speclib / vector layer specific ones are accessible via the lower node

        slw = self.speclibWidget()
        if isinstance(slw, SpectralLibraryWidget):
            menu.addSeparator()
            for action in slw.tbSpeclibAction.actions():
                menu.addAction(action)


class MapDockLabel(DockLabel):

    def __init__(self, *args, **kwds):
        super(MapDockLabel, self).__init__(*args, **kwds)

        self.addMapLink = QToolButton(self)
        self.addMapLink.setToolTip('Link with other map(s)')
        self.addMapLink.setIcon(QIcon(':/enmapbox/gui/ui/icons/link_basic.svg'))
        self.mButtons.append(self.addMapLink)

        self.removeMapLink = QToolButton(self)
        self.removeMapLink.setToolTip('Remove links to this map')
        self.removeMapLink.setIcon(QIcon(':/enmapbox/gui/ui/icons/link_open.svg'))
        self.mButtons.append(self.removeMapLink)

class MapDock(Dock):
    """
    A dock to visualize geodata that can be mapped
    """
    # sigCursorLocationValueRequest = pyqtSignal(QgsPoint, QgsRectangle, float, QgsRectangle)
    # sigCursorLocationRequest = pyqtSignal(SpatialPoint)
    # sigSpectrumRequest = pyqtSignal(SpatialPoint)
    sigLayersAdded = pyqtSignal(list)
    sigCrsChanged = pyqtSignal(QgsCoordinateReferenceSystem)

    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)
        super(MapDock, self).__init__(*args, **kwds)
        self.mBaseName = self.title()

        from enmapbox.gui.mapcanvas import MapCanvas
        self.mCanvas: MapCanvas = MapCanvas(self)
        self.mCanvas.setWindowTitle(self.title())
        self.mCanvas.sigNameChanged.connect(self.setTitle)

        self.sigTitleChanged.connect(self.mCanvas.setWindowTitle)
        self.mCanvas.sigLayersAdded.connect(self.sigLayersAdded.emit)
        self.mCanvas.sigCrsChanged.connect(self.sigCrsChanged.emit)

        settings = QSettings()
        assert isinstance(self.mCanvas, QgsMapCanvas)
        self.mCanvas.setCanvasColor(Qt.black)
        self.mCanvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        self.layout.addWidget(self.mCanvas)

        if initSrc is not None:
            from enmapbox.gui.datasources import DataSourceFactory
            dataSources = DataSourceFactory.create(initSrc)
            from enmapbox.gui.datasources.datasources import SpatialDataSource
            lyrs = [ds.asMapLayer() for ds in dataSources if isinstance(ds, SpatialDataSource)]
            if len(lyrs) > 0:
                self.mCanvas.setLayers(lyrs)

    def mapCanvas(self) -> MapCanvas:
        return self.mCanvas

    def populateContextMenu(self, menu: QMenu):
        """
        Returns the MapDock context menu
        :return: QMenu
        """
        super(MapDock, self).populateContextMenu(menu)

        self.mCanvas.populateContextMenu(menu, None)
        return menu

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            s = ""
        else:
            super(MapDock, self).mousePressEvent(event)

    def linkWithMapDock(self, mapDock, linkType) -> CanvasLink:
        assert isinstance(mapDock, MapDock)
        return self.linkWithCanvas(mapDock.mCanvas, linkType)

    def linkWithCanvas(self, canvas, linkType) -> CanvasLink:
        assert isinstance(canvas, QgsMapCanvas)
        return self.mapCanvas().createCanvasLink(canvas, linkType)

    def mapCanvas(self) -> MapCanvas:
        """
        Returns the MapCanvas
        :return: MapCanvas
        """
        return self.mCanvas

    def addLayers(self, layers: typing.List[QgsMapLayer]):
        assert isinstance(layers, list)
        new_set = self.mapCanvas().layers() + layers
        self.mapCanvas().setLayers(new_set)

    def insertLayer(self, idx, layerSource):
        from enmapbox import EnMAPBox
        from enmapbox.gui.dataviews.dockmanager import MapDockTreeNode

        enmapBox = EnMAPBox.instance()
        if enmapBox is not None:
            mapDockTreeNode: MapDockTreeNode
            for mapDockTreeNode in enmapBox.dockManagerTreeModel().mapDockTreeNodes():
                if mapDockTreeNode.dock is self:
                    mapDockTreeNode.insertLayer(idx=idx, layerSource=layerSource)


class DockTypes(object):
    """
    Enumeration that defines the standard dock types.
    """
    MapDock = 'MAP'
    TextDock = 'TEXT'
    MimeDataDock = 'MIME'
    WebViewDock = 'WEBVIEW'
    SpectralLibraryDock = 'SPECLIB'
    AttributeTableDock = 'ATTRIBUTES'


LUT_DOCKTYPES = {DockTypes.MapDock: MapDock,
                 DockTypes.TextDock: TextDock,
                 DockTypes.MimeDataDock: MimeDataDock,
                 DockTypes.WebViewDock: WebViewDock,
                 DockTypes.SpectralLibraryDock: SpectralLibraryDock,
                 DockTypes.AttributeTableDock: AttributeTableDock
                 }

for cls in set(LUT_DOCKTYPES.values()):
    LUT_DOCKTYPES[cls] = cls

