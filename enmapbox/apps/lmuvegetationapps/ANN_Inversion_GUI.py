# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from qgis.gui import *
#ensure to call QGIS before PyQtGraph
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt import uic
from osgeo import gdal
from enmapbox.gui.applications import EnMAPBoxApplication
from lmuvegetationapps.Spec2Sensor_cl import Spec2Sensor
import lmuvegetationapps.Processor_Core as processor
from hubflow.core import *

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_ANN_Prozessor.ui')
pathUI2 = os.path.join(os.path.dirname(__file__),'GUI_Nodat.ui')
pathUI_prg = os.path.join(os.path.dirname(__file__), 'GUI_ProgressBar.ui')

from enmapbox.gui.utils import loadUi


class ANN_Inversion_GUI(QDialog):
    
    def __init__(self, parent=None):
        super(ANN_Inversion_GUI, self).__init__(parent)
        loadUi(pathUI, self)


class Nodat_GUI(QDialog):

    def __init__(self, parent=None):
        super(Nodat_GUI, self).__init__(parent)
        loadUi(pathUI2, self)


class PRG_GUI(QDialog):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        loadUi(pathUI_prg, self)
        self.allow_cancel = False


    def closeEvent(self, event):
        if self.allow_cancel:
            event.accept()
        else:
            event.ignore()

class ANN_Inversion:

    def __init__(self, main):
        self.main = main
        self.gui = ANN_Inversion_GUI()
        self.initial_values()
        self.connections()

    def initial_values(self):
        self.nodat = [-999] * 3
        self.n_wl = None
        self.image = None
        self.mask_image = None
        self.mask_ndvi = False
        self.ndvi_thr = 0.37
        self.spatial_geo = False
        self.out_image = None
        self.out_mode = 'single'
        self.flags =[[0,0],[0],[0],[0,0]]  # to be edited!

        self.geo_mode = "file"
        self.geo_file = None
        self.geo_fixed = [None]*3

        self.conversion_factor = None
        self.NDVI_th = -0.9

        self.sensor = 2  # 0 = ASD, 1 = Sentinel2, 2 = EnMAP, 3 = Landsat, 4 = HyMap
        self.wl = None

    def connections(self):

        # Input Images
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdInputMask.clicked.connect(lambda: self.open_file(mode="mask"))

        # Output Images
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))
        self.gui.radOutSingle.clicked.connect(lambda: self.select_outputmode(mode="single"))
        self.gui.radOutIndividual.clicked.connect(lambda: self.select_outputmode(mode="individual"))

        # Geometry
        self.gui.cmdGeoFromFile.clicked.connect(lambda: self.open_file(mode="geo"))
        self.gui.radGeoFromFile.clicked.connect(lambda: self.select_geo(mode="file"))
        self.gui.radGeoFix.clicked.connect(lambda: self.select_geo(mode="fix"))

        self.gui.grpNDVI.clicked.connect(lambda: self.ndvi_thresh())
        self.gui.SpinNDVI.valueChanged.connect(lambda: self.ndvi_th_change())

        self.gui.chkMeanCalc.clicked.connect(lambda: self.geo_mean_calc())

        # Execute
        self.gui.cmdRun.clicked.connect(lambda: self.run_inversion())
        self.gui.cmdClose.clicked.connect(lambda: self.gui.close())

    def open_file(self, mode):
        if mode == "image":
            result = str(QFileDialog.getOpenFileName(caption='Select Input Image')[0])
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

        elif mode == "output":
            result = QFileDialog.getSaveFileName(caption='Specify Output-file(s)', filter="ENVI Image (*.bsq)")[0]
            if not result: return
            self.out_image = result
            self.out_image = self.out_image.replace("\\", "/")
            self.gui.txtOutputImage.setText(result)
        elif mode == "geo":
            result = str(QFileDialog.getOpenFileName(caption='Select Geometry Image')[0])
            if not result:
                return
            self.geo_file = result
            self.geo_file = self.geo_file.replace("\\", "/")
            meta = self.get_image_meta(image=self.geo_file, image_type="Geometry Image")
            if None in meta:
                self.geo_file = None
                self.nodat[1] = None
                self.gui.lblGeoFromFile.setText("")
                return
            else:
                self.gui.lblGeoFromFile.setText(result)
                self.gui.lblNodatGeoImage.setText(str(meta[0]))
                self.gui.chkMeanCalc.setDisabled(False)
                self.gui.chkMeanCalc.setChecked(True)
                self.nodat[1] = meta[0]
        elif mode == "mask":
            result = str(QFileDialog.getOpenFileName(caption='Select Mask Image')[0])
            if not result: return
            self.mask_image = result
            self.mask_image = self.mask_image.replace("\\", "/")
            meta = self.get_image_meta(image=self.mask_image, image_type="Mask Image")
            if meta[1] is None: # No Data is unimportant for mask file, but dimensions must exist (image readable)
                self.mask_image = None
                self.gui.lblInputMask.setText("")
                return
            else:
                self.gui.lblInputMask.setText(result)

    def select_outputmode(self, mode):
        self.out_mode = mode

    def select_geo(self, mode):
        if mode == "file":
            self.gui.lblGeoFromFile.setDisabled(False)
            self.gui.cmdGeoFromFile.setDisabled(False)
            self.gui.txtSZA.setDisabled(True)
            self.gui.txtOZA.setDisabled(True)
            self.gui.txtRAA.setDisabled(True)
        if mode == "fix":
            self.gui.lblGeoFromFile.setDisabled(True)
            self.gui.cmdGeoFromFile.setDisabled(True)
            self.gui.txtSZA.setDisabled(False)
            self.gui.txtOZA.setDisabled(False)
            self.gui.txtRAA.setDisabled(False)
        self.geo_mode = mode

    def ndvi_thresh(self):
        if self.gui.grpNDVI.isChecked():
            self.gui.SpinNDVI.setDisabled(False)
            self.mask_ndvi = True
        else:
            self.gui.SpinNDVI.setDisabled(True)
            self.mask_ndvi = False

    def ndvi_th_change(self):
        self.NDVI_th = self.gui.SpinNDVI.value()

    def geo_mean_calc(self):
        if self.gui.chkMeanCalc.isChecked():
            self.spatial_geo = False
        else:
            self.spatial_geo = True


    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

    def check_and_assign(self):
        # Image In
        if self.image is None: raise ValueError('Input Image missing')
        elif not os.path.isfile(self.image): raise ValueError('Input Image does not exist')

        # Output path
        self.out_image = self.gui.txtOutputImage.text()
        self.out_image = self.out_image.replace("\\", "/")
        if self.out_image is None: raise ValueError('Output file missing')
        else:
            try:
                os.path.splitext(self.out_image)[1]
            except:
                self.out_image += ".bsq"

        # Geometry file:
        if self.geo_mode == "file":
            if self.geo_file is None:
                raise ValueError('Geometry-Input via file selected, but no file specified')
            elif not os.path.isfile(self.geo_file):
                raise ValueError('Geometry-Input file does not exist')
            elif self.nodat[1] >= 0:
                raise ValueError('NoData value for Geometry needs to be < 0 to avoid confusion with valid angles')

        elif self.geo_mode == "fix":
            self.gui.chkMeanCalc.setDisabled(True)
            if self.gui.txtSZA.text() == "" or self.gui.txtOZA.text() == "" or self.gui.txtRAA.text() == "":
                raise ValueError('Geometry-Input via fixed values selected, but angles are incomplete')
            elif not 0 <= float(self.gui.txtSZA.text()) <= 89:
                raise ValueError('SZA out of range [0-89]')
            elif not 0 <= float(self.gui.txtOZA.text()) <= 89:
                raise ValueError('OZA out of range [0-89]')
            elif not 0 < int(self.gui.txtRAA.text()) <= 180:
                raise ValueError('rAA out of range [0-180]')
            else:
                try:
                    self.geo_fixed = [float(self.gui.txtSZA.text()), float(self.gui.txtOZA.text()), float(self.gui.txtRAA.text())]
                except ValueError:
                    raise ValueError('Cannot interpret Geometry angles as numbers')

        # Mask
        if self.mask_image:
            if not os.path.isfile(self.mask_image):
                raise ValueError('Mask Image does not exist')

        if self.gui.txtNodatOutput.text() == "":
            raise ValueError('Please specify no data value for output')
        else:
            try:
                self.nodat[2] = int(self.gui.txtNodatOutput.text())
            except:
                raise ValueError('%s is not a valid no data value for output' % self.gui.txtNodatOutput.text())

        # Parameters
        self.paras = []
        if self.gui.checkLAI.isChecked():
            self.paras.append("LAI")
        if self.gui.checkALIA.isChecked():
            self.paras.append("LIDF")
        if self.gui.checkCab.isChecked():
            self.paras.append("cab")
        if self.gui.checkCm.isChecked():
            self.paras.append("cm")
        if not self.paras:
            raise ValueError("At least one parameter needs to be selected!")

    def get_image_meta(self, image, image_type):
        dataset = openRasterDataset(image)
        if dataset is None:
            raise ValueError(
                '{} could not be read. Please make sure it is a valid ENVI image'.format(image_type))
        else:
            metadict = dataset.metadataDict()

            nrows = int(metadict['ENVI']['lines'])
            ncols = int(metadict['ENVI']['samples'])
            nbands = int(metadict['ENVI']['bands'])
            # if nbands < 2:
            #     raise ValueError("Input is not a multi-band image")
            try:
                nodata = int(metadict['ENVI']['data ignore value'])
                return nodata, nbands, nrows, ncols
            except:
                self.main.nodat_widget.init(image_type=image_type, image=image)
                self.main.nodat_widget.gui.setModal(True)  # parent window is blocked
                self.main.nodat_widget.gui.exec_()  # unlike .show(), .exec_() waits with execution of the code, until the app is closed
                return self.main.nodat_widget.nodat, nbands, nrows, ncols

    def run_inversion(self):

        try:
            self.check_and_assign()
        except ValueError as e:
            self.abort(message=str(e))
            return

        self.prg_widget = self.main.prg_widget
        self.prg_widget.gui.lblCaption_l.setText("ANN Inversion")
        self.prg_widget.gui.lblCaption_r.setText("Setting up inversion...")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.prg_widget.gui.show()

        self.main.QGis_app.processEvents()

        # Temp insertions
        self.model_dir = r"F:\Flugdaten2\20200320/"

        # insert core methods here
        proc = processor.ProcessorMainFunction()

        try:
            proc.proc_main.processor_setup(model_dir=self.model_dir, algorithm='ann', ImgIn=self.image,
                                           ResOut=self.out_image, out_mode=self.out_mode,
                                           sensor_nr=2, mask_ndvi=self.mask_ndvi, ndvi_thr=self.NDVI_th,
                                           mask_image=self.mask_image, GeoIn=self.geo_file, fixed_geos=self.geo_fixed,
                                           spatial_geo=self.spatial_geo, paras=self.paras)
        except ValueError as e:
            self.abort(message="Failed to setup inversion: {}".format(str(e)))
            return

        try:
            proc.proc_main.predict_from_dump(prg_widget=self.prg_widget, QGis_app=self.main.QGis_app)
        except ValueError as e:
            if str(e) == "Inversion canceled":
                self.abort(message=str(e))
            else:
                self.abort(message="An error occurred during inversion: {}".format(str(e)))
            self.prg_widget.gui.lblCancel.setText("")
            self.prg_widget.gui.allow_cancel = True
            self.prg_widget.gui.close()
            return

        self.prg_widget.gui.lblCaption_r.setText('Prediction Finished! Writing Output...')
        self.main.QGis_app.processEvents()

        try:
            proc.proc_main.write_prediction()
        except ValueError as e:
            self.abort(message="An error occurred while trying to write output-image: {}".format(str(e)))
            return

        self.prg_widget.gui.lblCancel.setText("")
        self.prg_widget.gui.allow_cancel = True
        self.prg_widget.gui.close()
        QMessageBox.information(self.gui, "Finish", "Automatic inversion finished")
        self.gui.close()

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
        self.ann_inversion = ANN_Inversion(self)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.ann_inversion.gui.show()

if __name__ == '__main__':
    from enmapbox.testing import initQgisApplication
    app = initQgisApplication()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())

