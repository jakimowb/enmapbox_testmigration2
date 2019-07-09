# -*- coding: utf-8 -*-
"""
***************************************************************************
    drawing
    ---------------------
    Date                 : Februar 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
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
# noinspection PyPep8Naming

import qgis
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
DEBUG = False


def printPen(pen):
    if isinstance(pen, QPen):
        print('QPen: {}, {}'.format(pen.widthF(), pen.color().getRgb()))
    else:
        print(pen)



class PenFrame(QFrame):

    sigPenChanged = pyqtSignal(QPen)

    def __init__(self, *args, **kwds):
        super(PenFrame, self).__init__(*args, **kwds)

        self.setLayout(QVBoxLayout())

        #self.cbPenStyle = OptionComboBox(LUT_PENSTYLES, parent=self, tooltip='Choose pen style')
        #self.cbCapStyle = OptionComboBox(LUT_PENCAPSTYLES, parent=self, tooltip='Choose cap style')
        #self.cbJoinStyle = OptionComboBox(LUT_PENJOINSTYLES, parent=self, tooltip='Choose join style')

        self.cbBrushStyle = QgsBrushStyleComboBox()
        self.cbBrushStyle.setToolTip('Select brush style.')
        self.cbPenStyle = QgsPenStyleComboBox()
        self.cbPenStyle.setToolTip('Select pen style.')
        self.cbCapStyle = QgsPenCapStyleComboBox()
        self.cbCapStyle.setToolTip('Select cap style.')
        self.cbJoinStyle = QgsPenJoinStyleComboBox()
        self.cbJoinStyle.setToolTip('Select join style.')
        self.btnColor = QgsColorButton()
        self.btnColor.setToolTip('Select pen color.')

        self.sbWidth = QDoubleSpinBox()
        self.sbWidth.setToolTip('Specify pen width.')
        self.sbWidth.setMinimum(0)
        self.sbWidth.setMaximum(9999.99999)

        for cb in [self.cbBrushStyle, self.cbPenStyle, self.cbCapStyle, self.cbJoinStyle]:
            assert isinstance(cb, QComboBox)
            cb.currentIndexChanged.connect(self.onUpdate)
        self.btnColor.colorChanged.connect(self.onUpdate)
        self.sbWidth.valueChanged.connect(self.onUpdate)


        l = QHBoxLayout()
        for w in [QLabel('Width'), self.sbWidth, self.btnColor, self.cbPenStyle]:
            l.addWidget(w)
        self.layout().addLayout(l)
        l = QHBoxLayout()
        for w in [self.cbBrushStyle, self.cbCapStyle, self.cbJoinStyle]:
            l.addWidget(w)
        self.layout().addLayout(l)

        self.mLastPen = QPen()

        #set a default pen
        self.setPen(QPen(QBrush(Qt.black, Qt.SolidPattern), 1.0, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin))

    def onUpdate(self, *args, **kwds):
        pen = self.pen()
        if pen != self.mLastPen:
            self.mLastPen = pen
            self.sigPenChanged.emit(pen)

        if DEBUG:
            printPen(pen)

    def pen(self):
        color = self.btnColor.color()
        brush = QBrush(color, self.cbBrushStyle.brushStyle())
        return QPen(brush, self.sbWidth.value(), self.cbPenStyle.penStyle(), self.cbCapStyle.penCapStyle(), self.cbJoinStyle.penJoinStyle())

    def setPen(self, pen):
        currentPen = self.pen()
        if isinstance(pen, QPen) and pen != currentPen:
            widgets = [self.sbWidth, self.cbPenStyle, self.cbBrushStyle, self.cbJoinStyle, self.cbCapStyle, self.btnColor]
            states = [w.blockSignals(True) for w in widgets]
            self.sbWidth.setValue(pen.width())
            self.cbPenStyle.setPenStyle(pen.style())
            self.cbCapStyle.setPenCapStyle(pen.capStyle())
            self.cbJoinStyle.setPenJoinStyle(pen.joinStyle())
            brush = pen.brush()
            assert isinstance(brush, QBrush)
            self.btnColor.setColor(brush.color())
            self.cbBrushStyle.setBrushStyle(brush.style())

            for state, w in zip(states, widgets):
                w.blockSignals(state)

            self.onUpdate()


class PenDialog(QDialog):

    @staticmethod
    def showDialog(parent=None, pen=None):

        d = PenDialog(parent=parent)
        if isinstance(pen, QPen):
            d.setPen(pen)

        d.exec_()

        if d.result() == QDialog.Accepted:

            return d.pen()
        else:
            return None



    sigPenChange = pyqtSignal(QPen)
    def __init__(self, pen=None, *args, **kwds):

        super(QDialog, self).__init__(*args, **kwds)
        self.setWindowTitle('Pen Settings')
        self.setLayout(QVBoxLayout())
        self.mPenFrame = PenFrame(parent=self)
        self.setPen(pen)
        self.mButtonBox = QDialogButtonBox(parent=self)
        self.mButtonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.mButtonBox.button(QDialogButtonBox.Ok).clicked.connect(lambda : self.done(QDialog.Accepted))
        self.mButtonBox.button(QDialogButtonBox.Cancel).clicked.connect(lambda: self.done(QDialog.Rejected))

        self.layout().addWidget(self.mPenFrame)
        self.layout().addWidget(self.mButtonBox)

    def pen(self):
        return self.mPenFrame.pen()

    def setPen(self, pen):
        if isinstance(pen, QPen):
            self.mPenFrame.setPen(pen)

if __name__ == '__main__':
    import site, sys
    from enmapbox.testing import initQgisApplication

    DEBUG = True
    qgsApp = initQgisApplication()

    printPen(PenDialog.showDialog())

    qgsApp.exec_()
