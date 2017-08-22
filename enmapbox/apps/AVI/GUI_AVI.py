# -*- coding: utf-8 -*-

import sys
from os.path import basename, dirname
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import AVI_core

app = QApplication(sys.argv)
gui = uic.loadUi("AVI.ui")

class UiFunc:

    def __init__(self):
        self.checkboxes = gui.findChildren(QCheckBox)
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

    def connections(self):
        gui.cmdSelectAll.clicked.connect(lambda: self.check(bool=True))
        gui.cmdDeselectAll.clicked.connect(lambda: self.check(bool=False))
        gui.cmdOK.clicked.connect(lambda: self.run_AVI())
        gui.cmdInput.clicked.connect(lambda: self.Image(IO="in"))
        gui.cmdOutput.clicked.connect(lambda: self.Image(IO="out"))
        gui.cmdCancel.clicked.connect(lambda: self.exit_GUI())
        # gui.structural_group.clicked.connect(lambda: self.check(group=2))

        gui.radNN.toggled.connect(lambda: self.toggle_interpol())
        gui.radLinear.toggled.connect(lambda: self.toggle_interpol())
        gui.radIDW.toggled.connect(lambda: self.toggle_interpol())
        gui.spinIDW_exp.valueChanged.connect(lambda: self.toggle_interpol())

        gui.radSingle.toggled.connect(lambda: self.toggle_write())
        gui.radIndiv.toggled.connect(lambda: self.toggle_write())

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
        self.dict_structural = {0: gui.box_hndvi_opp, 1: gui.box_ndvi_apa, 2: gui.box_ndvi_dat, 3: gui.box_ndvi_hab,
                             4: gui.box_ndvi_zar, 5: gui.box_mcari1, 6: gui.box_mcari2, 7: gui.box_msavi,
                             8: gui.box_mtvi1, 9: gui.box_mtvi2, 10: gui.box_osavi, 11: gui.box_rdvi, 12: gui.box_spvi}

        self.dict_chl = {0: gui.box_csi1, 1: gui.box_csi2, 2: gui.box_gi, 3: gui.box_gitmer1, 4: gui.box_gitmer2,
                         5: gui.box_gndvi, 6: gui.box_mcari, 7: gui.box_npqi, 8: gui.box_pri, 9: gui.box_reip,
                         10: gui.box_rep, 11: gui.box_srch1, 12: gui.box_sr705, 13: gui.box_tcari, 14: gui.box_tvi,
                         15: gui.box_vog1,  16: gui.box_vog2, 17: gui.box_ztm, 18: gui.box_sra, 19: gui.box_srb1,
                         20: gui.box_srb2, 21: gui.box_srtot, 22: gui.box_pssra, 23: gui.box_pssrb, 24: gui.box_lci,
                         25: gui.box_mlo}

        self.dict_caranth = {0: gui.box_ari, 1: gui.box_cri1, 2: gui.box_cri2, 3: gui.box_pssrc, 4: gui.box_sipi}

        self.dict_wat = {0: gui.box_dswi, 1: gui.box_dswi5, 2: gui.box_lwvi1, 3: gui.box_lwvi2, 4: gui.box_msi,
                         5: gui.box_ndwi, 6: gui.box_pwi, 7: gui.box_srwi}

        self.dict_drymat = {0: gui.box_swirvi, 1: gui.box_cai, 2: gui.box_ndli, 3: gui.box_ndni, 4: gui.box_bgi,
                         5: gui.box_bri, 6: gui.box_rgi, 7: gui.box_srpi, 8: gui.box_npci}

        self.dict_fluor = {0: gui.box_cur, 1: gui.box_lic1, 2: gui.box_lic2, 3: gui.box_lic3}

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
        if gui.radNN.isChecked():
            self.IT = 1
            gui.spinIDW_exp.setDisabled(True)
        elif gui.radLinear.isChecked():
            self.IT = 2
            gui.spinIDW_exp.setDisabled(True)
        else:
            self.IT = 3
            gui.spinIDW_exp.setDisabled(False)
            self.IDW_exp = gui.spinIDW_exp.value()

    def toggle_write(self):
        if gui.radSingle.isChecked():
            self.outSingle = 1
        else:
            self.outSingle = 0

    def Image(self, IO):
        if IO == "in":
            self.inFile = str(QFileDialog.getOpenFileName(caption='Select Input Image File'))
            gui.txtInput.setText(self.inFile)
        elif IO == "out":
            outFile = str(QFileDialog.getSaveFileName(caption='Select Output File'))
            gui.txtOutput.setText(outFile)
            try:
                self.outFileName = basename(outFile).split('.')[0]
                self.outExtension = basename(outFile).split('.')[1]
            except:
                self.outExtension = '.bsq'
                self.outFileName = basename(outFile)
            self.outDir = dirname(outFile) + "/"

    def exit_GUI(self):
        gui.close()
        # QCoreApplication.instance().quit()

    def run_AVI(self):

        if self.inFile is None:
            QMessageBox.critical(gui, "No image selected", "Please select an image to continue!")
        elif self.outFileName is None:
            QMessageBox.critical(gui, "No output file selected", "Please select an output file for your image!")
            return

        avi = AVI_core.AVI(IT=self.IT, IDW_exp=self.IDW_exp)
        ImageIn_matrix = avi.read_image(ImgIn=self.inFile, Convert_Refl=1)

        if ImageIn_matrix is None:
            QMessageBox.critical(gui, "Image unreadable", "The image file could not be read.")
            return

        avi.toggle_indices(StructIndices=self.structIndices, ChlIndices=self.chlIndices, CarIndices=self.carIndices,
                           WatIndices=self.watIndices, DmIndices=self.dmIndices, FlIndices=self.flIndices)

        if not avi.n_indices > 0:
            QMessageBox.critical(gui, "No index selected", "Please select at least one index to continue!")
            return

        IndexOut_matrix = avi.calculate_AVI(ImageIn_matrix=ImageIn_matrix)
        avi.write_out(IndexOut_matrix=IndexOut_matrix, OutDir=self.outDir, OutFilename=self.outFileName,
                      OutExtension=self.outExtension, OutSingle=self.outSingle)

        self.exit_GUI()

if __name__ == '__main__':
    myUI = UiFunc()
    gui.show()
    sys.exit(app.exec_())