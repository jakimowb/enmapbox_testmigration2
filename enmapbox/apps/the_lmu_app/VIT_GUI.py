# -*- coding: utf-8 -*-


import sys, os
from qgis.gui import *
from os.path import basename, dirname
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from osgeo import gdal
from enmapbox.gui.applications import EnMAPBoxApplication
import VIT_core

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_VIT.ui')
pathUI2 = os.path.join(os.path.dirname(__file__),'GUI_Nodat.ui')
pathUI_Prg = os.path.join(os.path.dirname(__file__),'GUI_ProgressBar.ui')

from enmapbox.gui.utils import loadUIFormClass

class VIT_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(VIT_GUI, self).__init__(parent)
        self.setupUi(self)

class Nodat_GUI(QDialog, loadUIFormClass(pathUI2)):
    def __init__(self, parent=None):
        super(Nodat_GUI, self).__init__(parent)
        self.setupUi(self)

class PRG_GUI(QDialog, loadUIFormClass(pathUI_Prg)):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        self.setupUi(self)

class VIT:
    def __init__(self, main):
        self.main = main
        self.gui = VIT_GUI()

        self.checkboxes = self.gui.findChildren(QCheckBox)
        self.dictchecks()
        self.connections()
        self.initial_values()

    def initial_values(self):
        self.inFile, self.outFileName, self.outExtension, self.outDir = None, None, None, None
        self.IT = 1
        self.IDW_exp = 2
        self.outSingle = 1
        self.structIndices = [-1]*13
        self.chlIndices = [-1] * 26
        self.carIndices = [-1] * 5
        self.watIndices = [-1] * 8
        self.dmIndices = [-1] * 9
        self.flIndices = [-1] * 4
        self.nodat = [None, None]

    def connections(self):
        self.gui.cmdSelectAll.clicked.connect(lambda: self.check(bool=True))
        self.gui.cmdDeselectAll.clicked.connect(lambda: self.check(bool=False))
        self.gui.cmdOK.clicked.connect(lambda: self.run_VIT())
        self.gui.cmdInput.clicked.connect(lambda: self.Image(IO="in"))
        self.gui.cmdOutput.clicked.connect(lambda: self.Image(IO="out"))
        self.gui.cmdCancel.clicked.connect(lambda: self.exit_gui())
        # self.gui.structural_group.clicked.connect(lambda: self.check(group=2))

        self.gui.radNN.toggled.connect(lambda: self.toggle_interpol())
        self.gui.radLinear.toggled.connect(lambda: self.toggle_interpol())
        # self.gui.radNo.toggled.connect(lambda: self.toggle_interpol())
        self.gui.radIDW.toggled.connect(lambda: self.toggle_interpol())
        self.gui.spinIDW_exp.valueChanged.connect(lambda: self.toggle_interpol())


        self.gui.radSingle.toggled.connect(lambda: self.toggle_write())
        self.gui.radIndiv.toggled.connect(lambda: self.toggle_write())

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

    def toggles(self, group, cid):
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

    def dictchecks(self):
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
                         5: self.gui.box_bri, 6: self.gui.box_rgi, 7: self.gui.box_srpi, 8: self.gui.box_npci}

        self.dict_fluor = {0: self.gui.box_cur, 1: self.gui.box_lic1, 2: self.gui.box_lic2, 3: self.gui.box_lic3}

    def check(self, bool):
        for i in xrange(len(self.dict_structural)):
            self.dict_structural[i].setChecked(bool)
        for i in xrange(len(self.dict_chl)):
            self.dict_chl[i].setChecked(bool)
        for i in xrange(len(self.dict_caranth)):
            self.dict_caranth[i].setChecked(bool)
        for i in xrange(len(self.dict_wat)):
            self.dict_wat[i].setChecked(bool)
        for i in xrange(len(self.dict_drymat)):
            self.dict_drymat[i].setChecked(bool)
        for i in xrange(len(self.dict_fluor)):
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
            inFile = str(QFileDialog.getOpenFileName(caption='Select Input Image File'))
            if not inFile: return

            dataset = gdal.Open(inFile)
            if dataset is None:
                QMessageBox.critical(self.gui, "error", 'Image could not be read. Please make sure it is a valid ENVI image')
                return
            nbands = dataset.RasterCount
            try:
                wavelengths = "".join(dataset.GetMetadataItem('wavelength', 'ENVI').split())
                wavelengths = wavelengths.replace("{", "")
                wavelengths = wavelengths.replace("}", "")
                wavelengths = wavelengths.split(",")
            except:
                QMessageBox.critical(self.gui, "error", 'Wavelengths could not be read from header file')
                return

            if dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['nanometers', 'nm', 'nanometer']:
                wave_convert = 1
                self.wunit = u'nm'
            elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm', 'micrometer']:
                wave_convert = 1000
                self.wunit = u"\u03bcm"
            else:
                QMessageBox.critical(self.gui, "error", 'No wavelength units supplied in header file')
                return

            self.wl = [float(item) * wave_convert for item in wavelengths]

            try:
                nodata = int("".join(dataset.GetMetadataItem('data_ignore_value', 'ENVI').split()))
                self.nodat[0] = nodata
            except:
                self.main.nodat_widget.init(image=inFile)
                self.main.nodat_widget.gui.setModal(True)  # parent window is blocked
                self.main.nodat_widget.gui.exec_()  # unlike .show(), .exec_() waits with execution of the code, until the app is closed

            self.inFile = inFile
            self.gui.lblInputImage.setText(self.inFile)
            self.gui.lblNodatImage.setText(str(self.nodat[0]))

        elif IO == "out":
            outFile = str(QFileDialog.getSaveFileName(caption='Select Output File', filter="ENVI Image (*.bsq)"))
            if not outFile: return
            self.gui.txtOutput.setText(outFile)
            try:
                self.outFileName = basename(outFile).split('.')[0]
                self.outExtension = basename(outFile).split('.')[1]
            except:
                self.outExtension = '.bsq'
                self.outFileName = basename(outFile)
            self.outDir = dirname(outFile) + "/"

    def exit_gui(self):
        self.gui.close()

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

        if self.IT == 0:
            question = QMessageBox.question(self.gui, "No Interpolation", "Please note: Only those indices will be calculated, for which wavelengths are directly supported by the sensor. Do you wish to continue without interpolation option?", QMessageBox.Yes | QMessageBox.No)
            if question == QMessageBox.No: return

        self.main.prg_widget.gui.lblCaption_l.setText("Vegetation Indices Toolbox")
        self.main.prg_widget.gui.lblCaption_r.setText("Reading Input Image...")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()

        vit = VIT_core.VIT(IT=self.IT, IDW_exp=self.IDW_exp, nodat=self.nodat)
        ImageIn_matrix = vit.read_image(ImgIn=self.inFile, Convert_Refl=1)

        if ImageIn_matrix is None:
            QMessageBox.critical(self.gui, "Image unreadable", "The image file could not be read.")
            return

        self.main.prg_widget.gui.lblCaption_r.setText("Preparing Indices")
        self.main.QGis_app.processEvents()

        vit.toggle_indices(StructIndices=self.structIndices, ChlIndices=self.chlIndices, CarIndices=self.carIndices,
                           WatIndices=self.watIndices, DmIndices=self.dmIndices, FlIndices=self.flIndices)

        if not vit.n_indices > 0:
            QMessageBox.critical(self.gui, "No index selected", "Please select at least one index to continue!")
            return

        IndexOut_matrix = vit.calculate_VIT(ImageIn_matrix=ImageIn_matrix, prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)

        self.main.prg_widget.gui.lblCaption_r.setText("Writing Output-File")
        self.main.QGis_app.processEvents()
        result_vit = vit.write_out(IndexOut_matrix=IndexOut_matrix, OutDir=self.outDir, OutFilename=self.outFileName,
                      OutExtension=self.outExtension, OutSingle=self.outSingle)

        if result_vit:
            QMessageBox.critical(self.gui, 'error', result_vit)
        else:
            self.main.prg_widget.gui.close()
            QMessageBox.information(self.gui, "Finish", "Inversion finished")
            self.gui.close()

class Nodat:
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

class PRG:
    def __init__(self, main):
        self.main = main
        self.gui = PRG_GUI()
        self.connections()

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())

class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication(sys.argv)
        self.vit = VIT(self)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.vit.gui.show()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())