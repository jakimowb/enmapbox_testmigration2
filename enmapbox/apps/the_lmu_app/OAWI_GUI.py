# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from qgis.gui import *
#ensure to call QGIS before PyQtGraph
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from osgeo import gdal
from OAWI_core import OAWI_core
from enmapbox.gui.applications import EnMAPBoxApplication

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_OAWI.ui')
pathUI2 = os.path.join(os.path.dirname(__file__),'GUI_Nodat.ui')
pathUI_prg = os.path.join(os.path.dirname(__file__),'GUI_ProgressBar.ui')

from enmapbox.gui.utils import loadUIFormClass

class OAWI_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(OAWI_GUI, self).__init__(parent)
        self.setupUi(self)

class Nodat_GUI(QDialog, loadUIFormClass(pathUI2)):
    def __init__(self, parent=None):
        super(Nodat_GUI, self).__init__(parent)
        self.setupUi(self)

class PRG_GUI(QDialog, loadUIFormClass(pathUI_prg)):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        self.setupUi(self)
        self.allow_cancel = False

    def closeEvent(self, event):
        if self.allow_cancel:
            event.accept()
        else:
            event.ignore()

class OAWI:

    def __init__(self, main):
        self.main = main
        self.gui = OAWI_GUI()
        self.initial_values()
        self.connections()

    def initial_values(self):
        self.image = None
        self.nodat = [-999]*2
        self.NDVI_th = 0.37

    def connections(self):
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))

        self.gui.SpinNDVI.valueChanged.connect(lambda: self.NDVI_th_change())

        self.gui.pushRun.clicked.connect(lambda: self.run_oawi())
        self.gui.pushClose.clicked.connect(lambda: self.gui.close())

    def open_file(self, mode):
        if mode=="image":
            result = str(QFileDialog.getOpenFileName(caption='Select Input Image'))
            if not result: return
            self.image = result
            self.image = self.image.replace("\\", "/")
            try:
                meta = self.get_image_meta(image=self.image, image_type="Input Image")
            except ValueError as e:
                self.abort(message=str(e))
                return
            if None in meta:
                self.image = None
                self.nodat[0] = None
                self.gui.lblInputImage.setText("")
                return
            else:
                self.gui.lblInputImage.setText(result)
                self.gui.lblNodatImage.setText(str(meta[0]))
                self.nodat[0] = meta[0]
        elif mode=="output":
            result = str(QFileDialog.getSaveFileName(caption='Specify Output-file(s)', filter="ENVI Image (*.bsq)"))
            if not result: return
            self.out_path = result
            self.out_path = self.out_path.replace("\\", "/")
            self.gui.txtOutputImage.setText(result)

    def get_image_meta(self, image, image_type):
        dataset = gdal.Open(image)
        if dataset is None:
            raise ValueError('%s could not be read. Please make sure it is a valid ENVI image' % image_type)
        else:
            nbands = dataset.RasterCount
            nrows = dataset.RasterYSize
            ncols = dataset.RasterXSize

            try:
                nodata = int("".join(dataset.GetMetadataItem('data_ignore_value', 'ENVI').split()))
                return nodata, nbands, nrows, ncols
            except:
                self.main.nodat_widget.init(image_type=image_type, image=image)
                self.main.nodat_widget.gui.setModal(True)  # parent window is blocked
                self.main.nodat_widget.gui.exec_()  # unlike .show(), .exec_() waits with execution of the code, until the app is closed
                return self.main.nodat_widget.nodat, nbands, nrows, ncols

    def NDVI_th_change(self):
        self.NDVI_th = self.gui.SpinNDVI.value()

    def run_oawi(self):
        if self.image is None:
            QMessageBox.critical(self.gui, "No image selected", "Please select an image to continue!")
            return
        elif self.out_path is None:
            QMessageBox.critical(self.gui, "No output file selected", "Please select an output file for your image!")
            return
        elif self.gui.txtNodatOutput.text()=="":
            QMessageBox.critical(self.gui, "No Data Value", "Please specify No Data Value!")
            return
        else:
            try:
                self.nodat[1] = int(self.gui.txtNodatOutput.text())
            except:
                QMessageBox.critical(self.gui, "Error", "'%s' is not a valid  No Data Value!" % self.gui.txtNodatOutput.text())
                return

        # show progressbar - window
        self.main.prg_widget.gui.lblCaption_l.setText("Plant Water Retrieval")
        self.main.prg_widget.gui.lblCaption_r.setText("Reading Input Image...this may take several minutes")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()

        try:
            iOawi = OAWI_core(nodat_val=self.nodat)
            iOawi.initialize_OAWI(input=self.image, output=self.out_path, lims=[926,1070], NDVI_th=self.NDVI_th)
        except ValueError as e:
            QMessageBox.critical(self.gui, 'error', str(e))
            self.main.prg_widget.gui.allow_cancel = True # The window may be cancelled
            self.main.prg_widget.gui.close()
            return

        try: # give it a shot
            result = iOawi.execute_OAWI(prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)
        except:
            QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
            return

        self.main.prg_widget.gui.lblCaption_r.setText("Writing Output-File")
        self.main.QGis_app.processEvents()

        try:
            iOawi.write_image(result=result)
        except:
            QMessageBox.critical(self.gui, 'error', "An unspecific error occured while trying to write image data")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
            return

        self.main.prg_widget.gui.allow_cancel = True
        self.main.prg_widget.gui.close()

        QMessageBox.information(self.gui, "Finish", "Calculation of OAWI finished successfully")
        self.gui.close()

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

class Nodat:
    def __init__(self, main):
        self.main = main
        self.gui = Nodat_GUI()
        self.connections()
        self.image = None

    def init(self, image_type, image):
        topstring = '%s @ %s' % (image_type, image)
        self.gui.lblSource.setText(topstring)
        self.gui.txtNodat.setText("")
        self.image = image
        self.nodat = None

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())
        self.gui.cmdOK.clicked.connect(lambda: self.OK())

    def OK(self):
        if self.gui.txtNodat.text() == "":
            QMessageBox.critical(self.gui, "No Data", "A no data value must be supplied for this image!")
            return
        else:
            try:
                nodat = int(self.gui.txtNodat.text())
            except:
                QMessageBox.critical(self.gui, "No number", "'%s' is not a valid number" % self.gui.txtNodat.text())
                self.gui.txtNodat.setText("")
                return
        self.nodat = nodat
        self.gui.close()

class PRG:
    def __init__(self, main):
        self.main = main
        self.gui = PRG_GUI()
        self.gui.lblCancel.setVisible(False)
        self.connections()

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.cancel())

    def cancel(self):
        self.gui.allow_cancel = True
        self.gui.cmdCancel.setDisabled(True)
        self.gui.lblCancel.setText("-1")

class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication.instance()
        self.oawi = OAWI(self)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.oawi.gui.show()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    m = MainUiFunc()
    m.show()
    app.exec_()