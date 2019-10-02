# -*- coding: utf-8 -*-

import sys
import os
from qgis.PyQt.QtWidgets import *
from osgeo import gdal
from lmuvegetationapps.PWR_core import PWR_core
import time

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_PWR.ui')
pathUI2 = os.path.join(os.path.dirname(__file__),'GUI_Nodat.ui')
pathUI_prg = os.path.join(os.path.dirname(__file__),'GUI_ProgressBar.ui')

from enmapbox.gui.utils import loadUIFormClass

class PWR_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(PWR_GUI, self).__init__(parent)
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

class PWR:

    def __init__(self, main):
        self.main = main
        self.gui = PWR_GUI()
        self.initial_values()
        self.connections()

    def initial_values(self):
        self.image = None
        self.nodat = [-999]*2
        self.division_factor = 1.0
        self.NDWI_th = -0.9

    def connections(self):
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))

        self.gui.SpinNDWI.valueChanged.connect(lambda: self.NDWI_th_change())

        self.gui.pushRun.clicked.connect(lambda: self.run_pwr())
        self.gui.pushClose.clicked.connect(lambda: self.gui.close())

    def open_file(self, mode):
        if mode == "image":
            bsq_input, _filter = QFileDialog.getOpenFileName(None, 'Select Input Image', '.', "ENVI Image (*.bsq)")
            if not bsq_input: return
            self.image = bsq_input
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
                self.gui.lblInputImage.setText(bsq_input)
                self.gui.lblNodatImage.setText(str(meta[0]))
                self.nodat[0] = meta[0]
        elif mode == "output":
            #result, _filter = QFileDialog.getSaveFileName(None, 'Specify Output File', '.', "ENVI Image(*.bsq)")
            result = QFileDialog.getSaveFileName(caption='Specify Output File', filter="ENVI Image (*.bsq)")[0]
            if not result:
                raise ImportError('Input file could not be read.  Please make sure it is a valid ENVI image')
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

    def NDWI_th_change(self):
        self.NDWI_th = self.gui.SpinNDWI.value()

    def run_pwr(self):
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
        try:
            self.division_factor = float(self.gui.spinDivisionFactor.text())
        except:
            QMessageBox.critical(self.gui, "Error", "'%s' is not a valid division factor!" % self.gui.spinDivisionFactor.text())
            return


        # show progressbar - window
        self.main.prg_widget.gui.lblCaption_l.setText("Plant Water Retrieval")
        self.main.prg_widget.gui.lblCaption_r.setText("Reading Input Image...this may take several minutes")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()

        try:
            iPWR = PWR_core(nodat_val=self.nodat, division_factor=self.division_factor)
            iPWR.initialize_PWR(input=self.image, output=self.out_path, lims=[930, 1060], NDVI_th=self.NDWI_th)
        except MemoryError:
            QMessageBox.critical(self.gui, 'error', "File too large to read. More RAM needed")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
        except ValueError as e:
            QMessageBox.critical(self.gui, 'error', str(e))
            self.main.prg_widget.gui.allow_cancel = True  # The window may be cancelled
            self.main.prg_widget.gui.close()
            return

        try:  # give it a shot
            result = iPWR.execute_PWR(prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)

        except:
            QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
            return

        self.main.prg_widget.gui.lblCaption_r.setText("Writing Output-File")
        self.main.QGis_app.processEvents()

        iPWR.write_image(result=result)
        # try:
        #
        # except:
        #     #QMessageBox.critical(self.gui, 'error', "An unspecific error occured while trying to write image data")
        #     self.main.prg_widget.gui.allow_cancel = True
        #     self.main.prg_widget.gui.close()
        #     return

        self.main.prg_widget.gui.allow_cancel = True
        self.main.prg_widget.gui.close()

        QMessageBox.information(self.gui, "Finish", "Calculation of PWR finished successfully")
        #self.gui.close()

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
        self.pwr = PWR(self)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.pwr.gui.show()

if __name__ == '__main__':
    from enmapbox.testing import initQgisApplication
    app = initQgisApplication()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())
