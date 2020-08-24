# -*- coding: utf-8 -*-


import sys
import os
from qgis.PyQt.QtWidgets import *
from osgeo import gdal
import lmuvegetationapps.VIT.VIT_core
from lmuvegetationapps import APP_DIR

pathUI_vit = os.path.join(APP_DIR, 'Resources/UserInterfaces/VIT.ui')
pathUI_nodat = os.path.join(APP_DIR, 'Resources/UserInterfaces/Nodat.ui')
pathUI_prgbar = os.path.join(APP_DIR, 'Resources/UserInterfaces/ProgressBar.ui')

from enmapbox.gui.utils import loadUi

class VIT_GUI(QDialog):
    def __init__(self, parent=None):
        super(VIT_GUI, self).__init__(parent)
        loadUi(pathUI_vit, self)

class Nodat_GUI(QDialog):
    def __init__(self, parent=None):
        super(Nodat_GUI, self).__init__(parent)
        loadUi(pathUI_nodat, self)

class PRG_GUI(QDialog):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        loadUi(pathUI_prgbar, self)

        self.allow_cancel = False

    def closeEvent(self, event): # window may only be closed, if self.allow_cancel is TRUE (=Cancel Button hit)
        if self.allow_cancel:
            event.accept()
        else:
            event.ignore()

class VIT:
    def __init__(self, main):
        self.main = main
        self.gui = VIT_GUI()

        self.checkboxes = self.gui.findChildren(QCheckBox) # all Checkboxes in the GUI
        self.dictchecks() # connect checkboxes to dictionary
        self.connections()
        self.initial_values()

    def initial_values(self):
        self.inFile, self.outFileName, self.outExtension, self.outDir = None, None, None, None
        self.IT = 1 # Interpolation type: 1: NN, 2: linear, 3: IDW, 4: Spline (def: 1);
        self.IDW_exp = 2 # exponent of IDW interpolation
        self.outSingle = 1 # 1: output to single file; else: output to individual files
        self.structIndices = [-1]* 13 # preset all indices in groups and set their flags to -1 (off)
        self.chlIndices = [-1] * 26
        self.carIndices = [-1] * 5
        self.watIndices = [-1] * 8
        self.dmIndices = [-1] * 10
        self.flIndices = [-1] * 4
        self.nodat = [None, None] # nodat[0] = in, nodat[1] = out
        self.division_factor = 1.0

    def connections(self):
        self.gui.cmdSelectAll.clicked.connect(lambda: self.check(bool=True))
        self.gui.cmdDeselectAll.clicked.connect(lambda: self.check(bool=False))
        self.gui.cmdOK.clicked.connect(lambda: self.run_VIT())
        self.gui.cmdInput.clicked.connect(lambda: self.Image(IO="in"))
        self.gui.cmdOutput.clicked.connect(lambda: self.Image(IO="out"))
        self.gui.cmdCancel.clicked.connect(lambda: self.exit_gui())

        self.gui.radNN.toggled.connect(lambda: self.toggle_interpol())
        self.gui.radLinear.toggled.connect(lambda: self.toggle_interpol())
        self.gui.radIDW.toggled.connect(lambda: self.toggle_interpol())
        self.gui.spinIDW_exp.valueChanged.connect(lambda: self.toggle_interpol())

        self.gui.radSingle.toggled.connect(lambda: self.toggle_write())
        self.gui.radIndiv.toggled.connect(lambda: self.toggle_write())

        # assign checkboxes to function: select/deselct on click
        for id in self.dict_structural:
            self.dict_structural[id].stateChanged.connect(lambda group, iid=id: self.toggles(group="structural", cid=iid))
        for id in self.dict_chl:
            self.dict_chl[id].stateChanged.connect(lambda group, iid=id: self.toggles(group="chl", cid=iid))
        for id in self.dict_caranth:
            self.dict_caranth[id].stateChanged.connect(lambda group, iid=id: self.toggles(group="caranth", cid=iid))
        for id in self.dict_wat:
            self.dict_wat[id].stateChanged.connect(lambda group, iid=id: self.toggles(group="water", cid=iid))
        for id in self.dict_drymat:
            self.dict_drymat[id].stateChanged.connect(lambda group, iid=id: self.toggles(group="drymat", cid=iid))
        for id in self.dict_fluor:
            self.dict_fluor[id].stateChanged.connect(lambda group, iid=id: self.toggles(group="fluor", cid=iid))

    def toggles(self, group, cid): # *= -1 is a switch on/off
        if group == "structural":
            self.structIndices[cid] *= -1
        elif group == "chl":
            self.chlIndices[cid] *= -1
        elif group == "caranth":
            self.carIndices[cid] *= -1
        elif group == "water":
            self.watIndices[cid] *= -1
        elif group == "drymat":
            self.dmIndices[cid] *= -1
        elif group == "fluor":
            self.flIndices[cid] *= -1

    def dictchecks(self): # a dictionary for all the checkboxes, so they can be adressed in functions
        self.dict_structural = {0: self.gui.box_hndvi_opp, 1: self.gui.box_ndvi_apa, 2: self.gui.box_ndvi_dat, 3: self.gui.box_ndvi_hab,
                             4: self.gui.box_ndvi_zar, 5: self.gui.box_mcari1, 6: self.gui.box_mcari2, 7: self.gui.box_msavi,
                             8: self.gui.box_mtvi1, 9: self.gui.box_mtvi2, 10: self.gui.box_osavi, 11: self.gui.box_rdvi, 12: self.gui.box_spvi}

        self.dict_chl = {0: self.gui.box_csi1, 1: self.gui.box_csi2, 2: self.gui.box_gi, 3: self.gui.box_gitmer1, 4: self.gui.box_gitmer2,
                         5: self.gui.box_gndvi, 6: self.gui.box_mcari, 7: self.gui.box_npqi, 8: self.gui.box_pri, 9: self.gui.box_reip,
                         10: self.gui.box_rep, 11: self.gui.box_srch1, 12: self.gui.box_sr705, 13: self.gui.box_tcari, 14: self.gui.box_tvi,
                         15: self.gui.box_vog1,  16: self.gui.box_vog2, 17: self.gui.box_ztm, 18: self.gui.box_sra, 19: self.gui.box_srb1,
                         20: self.gui.box_srb2, 21: self.gui.box_srtot, 22: self.gui.box_pssra, 23: self.gui.box_pssrb, 24: self.gui.box_lci,
                         25: self.gui.box_mlo}

        self.dict_caranth = {0: self.gui.box_ari, 1: self.gui.box_cri1, 2: self.gui.box_cri2, 3: self.gui.box_pssrc, 4: self.gui.box_sipi}

        self.dict_wat = {0: self.gui.box_dswi, 1: self.gui.box_dswi5, 2: self.gui.box_lwvi1, 3: self.gui.box_lwvi2, 4: self.gui.box_msi,
                         5: self.gui.box_ndwi, 6: self.gui.box_pwi, 7: self.gui.box_srwi}

        self.dict_drymat = {0: self.gui.box_swirvi, 1: self.gui.box_cai, 2: self.gui.box_ndli, 3: self.gui.box_ndni, 4: self.gui.box_bgi,
                         5: self.gui.box_bri, 6: self.gui.box_rgi, 7: self.gui.box_srpi, 8: self.gui.box_npci, 9: self.gui.box_ndi_test}

        self.dict_fluor = {0: self.gui.box_cur, 1: self.gui.box_lic1, 2: self.gui.box_lic2, 3: self.gui.box_lic3}

    def check(self, bool): # select/deselect checkboxes (all)
        for i in range(len(self.dict_structural)):
            self.dict_structural[i].setChecked(bool)
        for i in range(len(self.dict_chl)):
            self.dict_chl[i].setChecked(bool)
        for i in range(len(self.dict_caranth)):
            self.dict_caranth[i].setChecked(bool)
        for i in range(len(self.dict_wat)):
            self.dict_wat[i].setChecked(bool)
        for i in range(len(self.dict_drymat)):
            self.dict_drymat[i].setChecked(bool)
        for i in range(len(self.dict_fluor)):
            self.dict_fluor[i].setChecked(bool)

    def toggle_interpol(self):
        if self.gui.radNN.isChecked():
            self.IT = 1
            self.gui.spinIDW_exp.setDisabled(True)
        elif self.gui.radLinear.isChecked():
            self.IT = 2
            self.gui.spinIDW_exp.setDisabled(True)
        # elif self.gui.radNo.isChecked():
        #     self.IT = 0
        #     self.gui.spinIDW_exp.setDisabled(True)
        else:
            self.IT = 3
            self.gui.spinIDW_exp.setDisabled(False)
            self.IDW_exp = self.gui.spinIDW_exp.value()

    def toggle_write(self):
        if self.gui.radSingle.isChecked():
            self.outSingle = 1
        else:
            self.outSingle = 0

    def Image(self, IO):
        if IO == "in":
            inFile = str(QFileDialog.getOpenFileName(caption='Select Input Image File')[0])
            if not inFile: return # cancel button is hit

            dataset = gdal.Open(inFile)
            if dataset is None:
                QMessageBox.critical(self.gui, "error", 'Image could not be read. Please make sure it is a valid ENVI image')
                return
            nbands = dataset.RasterCount
            try: # get wavelengths from input file
                wavelengths = "".join(dataset.GetMetadataItem('wavelength', 'ENVI').split())
                wavelengths = wavelengths.replace("{", "")
                wavelengths = wavelengths.replace("}", "")
                wavelengths = wavelengths.split(",")
            except:
                QMessageBox.critical(self.gui, "error", 'Wavelengths could not be read from header file')
                return

            # find wavelength unit and set conversion if necessary
            if dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['nanometers', 'nm', 'nanometer']:
                wave_convert = 1
                self.wunit = u'nm'
            elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm', 'micrometer']:
                wave_convert = 1000
                self.wunit = u"\u03bcm"
            else:
                QMessageBox.critical(self.gui, "error", 'No wavelength units supplied in header file')
                return

            self.wl = [float(item) * wave_convert for item in wavelengths] # valid wavelengths of input dataset

            try: # get nodata-Value
                nodata = int("".join(dataset.GetMetadataItem('data_ignore_value', 'ENVI').split()))
                self.nodat[0] = nodata
            except: # open the nodata-dialog if nodata is not supplied
                self.main.nodat_widget.init(image=inFile)
                self.main.nodat_widget.gui.setModal(True)  # parent window is blocked
                self.main.nodat_widget.gui.exec_() # exec instead of "show" to stop python from processing further code

            self.inFile = inFile
            self.gui.lblInputImage.setText(self.inFile)
            self.gui.lblNodatImage.setText(str(self.nodat[0]))

        elif IO == "out":
            #outFile, _filter = QFileDialog.getSaveFileName(None, 'Specify Output File', '.', "ENVI Image(*.bsq)")
            outFile = QFileDialog.getSaveFileName(caption='Select Output File', filter="ENVI Image (*.bsq)")[0]
            if not outFile: return
            self.gui.txtOutput.setText(outFile)
            try:
                self.outFileName = os.path.basename(outFile).split('.')[0]
                self.outExtension = '.' + os.path.basename(outFile).split('.')[1]
            except:
                self.outExtension = '.bsq'
                self.outFileName = os.path.basename(outFile)
            self.outDir = os.path.dirname(outFile) + "/"  # outDir ends with / so that a filename can be string-added

    def exit_gui(self):
        self.gui.close()  # I wonder what this does...

    def run_VIT(self):
        if self.inFile is None:
            QMessageBox.critical(self.gui, "No image selected", "Please select an image to continue!")
            return
        elif self.outFileName is None:
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
            self.division_factor = float(self.gui.txtDivisionFactor.text())
        except:
            QMessageBox.critical(self.gui, "Error", "'%s' is not a valid division factor!" % self.gui.txtDivisionFactor.text())
            return

        # show progressbar - window
        self.main.prg_widget.gui.lblCaption_l.setText("Vegetation Indices Toolbox")
        self.main.prg_widget.gui.lblCaption_r.setText("Reading Input Image...this may take several minutes")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()

        try:
            vit = lmuvegetationapps.VIT.VIT_core.VIT(IT=self.IT, IDW_exp=self.IDW_exp, nodat=self.nodat,
                                                     division_factor=self.division_factor) # initialize VIT
            ImageIn_matrix = vit.read_image2(self.inFile)  # read the image
        except ValueError as e:
            QMessageBox.critical(self.gui, 'error', str(e))
            self.main.prg_widget.gui.allow_cancel = True # The window may be cancelled
            self.main.prg_widget.gui.close()
            return

        if ImageIn_matrix is None:
            QMessageBox.critical(self.gui, "Image unreadable", "The image file could not be read.")
            return

        self.main.prg_widget.gui.lblCaption_r.setText("Preparing Indices")
        self.main.QGis_app.processEvents()

        # check and pass all indices that were selected
        vit.toggle_indices(StructIndices=self.structIndices, ChlIndices=self.chlIndices, CarIndices=self.carIndices,
                           WatIndices=self.watIndices, DmIndices=self.dmIndices, FlIndices=self.flIndices)

        if not vit.n_indices > 0:
            QMessageBox.critical(self.gui, "No index selected", "Please select at least one index to continue!")
            return

        #try: # give it a shot+
        IndexOut_matrix = vit.calculate_VIT(prg_widget=self.main.prg_widget,
                                                QGis_app=self.main.QGis_app)
        # except:
        #     QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
        #     self.main.prg_widget.gui.allow_cancel = True
        #     self.main.prg_widget.gui.close()
        #     return

        self.main.prg_widget.gui.lblCaption_r.setText("Writing Output-File")
        self.main.QGis_app.processEvents()

        #try: # write Output-File
        vit.write_out(IndexOut_matrix=IndexOut_matrix, OutDir=self.outDir, OutFilename=self.outFileName,
                          OutExtension=self.outExtension, OutSingle=self.outSingle)
        # except:
        #     QMessageBox.critical(self.gui, 'error', "An unspecific error occured while trying to write image data")
        #     self.main.prg_widget.gui.allow_cancel = True
        #     #  self.main.prg_widget.gui.close()
        #     return

        self.main.prg_widget.gui.allow_cancel = True
        self.main.prg_widget.gui.close()
        QMessageBox.information(self.gui, "Finish", "Calculation of indices finished")
        self.gui.close()

class Nodat: # GUI-specifications for NoData-Dialog
    def __init__(self, main):
        self.main = main
        self.gui = Nodat_GUI()
        self.connections()
        self.image = None

    def init(self, image):
        topstring = 'Input-Image @ %s' % image
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
                QMessageBox.critical(self.gui, "No number",
                                     "'%s' is not a valid number" % self.gui.txtNodat.text())
                self.gui.txtNodat.setText("")
                return
        self.main.vit.nodat[0] = nodat
        self.gui.close()

class PRG: # GUI specification for progressbar dialog
    def __init__(self, main):
        self.main = main
        self.gui = PRG_GUI()
        self.gui.lblCancel.setVisible(False)
        self.connections()

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())

    def cancel(self):
        self.gui.allow_cancel = True
        self.gui.cmdCancel.setDisabled(True)
        self.gui.lblCancel.setText("-1")

class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication.instance() # the QGIS-Application made accessible within the code
        self.vit = VIT(self)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.vit.gui.show()


if __name__ == '__main__':
    from enmapbox.testing import initQgisApplication
    app = initQgisApplication()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())
