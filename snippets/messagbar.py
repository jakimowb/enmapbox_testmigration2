from __future__ import absolute_import
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from enmapbox.gui.sandbox import initQgisEnvironment
qApp = initQgisEnvironment()



w = QWidget()

w.setLayout(QVBoxLayout())
global nMsg, mbar
mbar = QgsMessageBar(parent=w)
assert isinstance(mbar, QgsMessageBar)

nMsg = 0

def showError(*arg):
    msg, tag, level = arg
    v = QgsMessageViewer()
    v.setMessage(msg, QgsMessageOutput.MessageText)
    v.showMessage(True)

def onMessage(*arg):
    msg, tag, level = arg
    duration = 2

    widget = mbar.createMessage(msg, tag)
    button = QPushButton(widget)
    button.setText("Show")
    button.pressed.connect(lambda : showError(*arg))
    widget.layout().addWidget(button)
    mbar.pushWidget(widget, QgsMessageBar.WARNING, 10)


def onMessageRequest():
    l = QgsMessageLog.instance()
    global nMsg
    nMsg += 1
    l.logMessage('Message {}'.format(nMsg), tag='TAG', level=QgsMessageLog.WARNING)

log = QgsMessageLog.instance()
log.messageReceived.connect(onMessage)

btn = QPushButton(w)
btn.clicked.connect(lambda : onMessageRequest())
w.layout().addWidget(mbar)
w.layout().addWidget(btn)
w.layout().addWidget(QFrame(w))
w.show()
btn.clicked.emit(True)
qApp.exec_()