# -*- coding: utf-8 -*-

import sys, os
import numpy as np

from qgis.gui import *
#ensure to call QGIS before PyQtGraph
import pyqtgraph as pg
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import call_model as mod
from enmapbox.gui.applications import EnMAPBoxApplication
from Spec2Sensor_cl import Spec2Sensor

pathUI = os.path.join(os.path.dirname(__file__) ,'GUI_LUT.ui')

#gui = uic.loadUi("GUI_ISD.ui")
#loadUIFormClass allows to load QGIS Widgets and some more...
from enmapbox.gui.utils import loadUIFormClass

class GUI_LUT(QDialog, loadUIFormClass(pathUI)):
    
    def __init__(self, parent=None):
        super(GUI_LUT, self).__init__(parent)
        self.setupUi(self)    

class UiFunc:

    def __init__(self):
        
        self.gui = GUI_LUT()
        self.dictchecks()
        self.initial_values()
        self.connections()
        # self.para_list = []
        # self.update_lineEdit_pos()
        # self.txt_enables()
        # self.para_init()
        # self.select_model()
        # self.mod_interactive()
        # self.mod_exec()

    def initial_values(self):
        self.typeLIDF = 2
        self.lop = "prospectD"
        self.canopy_arch = "sail"

    def dictchecks(self):
        self.dict_objects = {"chl": [self.gui.radio_fix_chl, self.gui.radio_gauss_chl, self.gui.radio_uni_chl,
                                 self.gui.radio_log_chl, self.gui.txt_fix_chl, self.gui.txt_gauss_min_chl,
                                 self.gui.txt_gauss_max_chl, self.gui.txt_gauss_mean_chl, self.gui.txt_gauss_std_chl,
                                 self.gui.txt_log_min_chl, self.gui.txt_log_max_chl, self.gui.txt_log_steps_chl],
                             "cw": [self.gui.radio_fix_cw, self.gui.radio_gauss_cw, self.gui.radio_uni_cw,
                                 self.gui.radio_log_cw, self.gui.txt_fix_cw, self.gui.txt_gauss_min_cw,
                                 self.gui.txt_gauss_max_cw, self.gui.txt_gauss_mean_cw, self.gui.txt_gauss_std_cw,
                                 self.gui.txt_log_min_cw, self.gui.txt_log_max_cw, self.gui.txt_log_steps_cw],
                             "cm": [self.gui.radio_fix_cm, self.gui.radio_gauss_cm, self.gui.radio_uni_cm,
                                 self.gui.radio_log_cm, self.gui.txt_fix_cm, self.gui.txt_gauss_min_cm,
                                 self.gui.txt_gauss_max_cm, self.gui.txt_gauss_mean_cm, self.gui.txt_gauss_std_cm,
                                 self.gui.txt_log_min_cm, self.gui.txt_log_max_cm, self.gui.txt_log_steps_cm],
                             "car": [self.gui.radio_fix_car, self.gui.radio_gauss_car, self.gui.radio_uni_car,
                                 self.gui.radio_log_car, self.gui.txt_fix_car, self.gui.txt_gauss_min_car,
                                 self.gui.txt_gauss_max_car, self.gui.txt_gauss_mean_car, self.gui.txt_gauss_std_car,
                                 self.gui.txt_log_min_car, self.gui.txt_log_max_car, self.gui.txt_log_steps_car],
                             "canth": [self.gui.radio_fix_canth, self.gui.radio_gauss_canth, self.gui.radio_uni_canth,
                                 self.gui.radio_log_canth, self.gui.txt_fix_canth, self.gui.txt_gauss_min_canth,
                                 self.gui.txt_gauss_max_canth, self.gui.txt_gauss_mean_canth, self.gui.txt_gauss_std_canth,
                                 self.gui.txt_log_min_canth, self.gui.txt_log_max_canth, self.gui.txt_log_steps_canth],
                             "cbr": [self.gui.radio_fix_cbr, self.gui.radio_gauss_cbr, self.gui.radio_uni_cbr,
                                 self.gui.radio_log_cbr, self.gui.txt_fix_cbr, self.gui.txt_gauss_min_cbr,
                                 self.gui.txt_gauss_max_cbr, self.gui.txt_gauss_mean_cbr, self.gui.txt_gauss_std_cbr,
                                 self.gui.txt_log_min_cbr, self.gui.txt_log_max_cbr, self.gui.txt_log_steps_cbr],
                             "lai": [self.gui.radio_fix_lai, self.gui.radio_gauss_lai, self.gui.radio_uni_lai,
                                 self.gui.radio_log_lai, self.gui.txt_fix_lai, self.gui.txt_gauss_min_lai,
                                 self.gui.txt_gauss_max_lai, self.gui.txt_gauss_mean_lai, self.gui.txt_gauss_std_lai,
                                 self.gui.txt_log_min_lai, self.gui.txt_log_max_lai, self.gui.txt_log_steps_lai],
                             "hspot": [self.gui.radio_fix_hspot, self.gui.radio_gauss_hspot, self.gui.radio_uni_hspot,
                                 self.gui.radio_log_hspot, self.gui.txt_fix_hspot, self.gui.txt_gauss_min_hspot,
                                 self.gui.txt_gauss_max_hspot, self.gui.txt_gauss_mean_hspot, self.gui.txt_gauss_std_hspot,
                                 self.gui.txt_log_min_hspot, self.gui.txt_log_max_hspot, self.gui.txt_log_steps_hspot],
                             "oza": [self.gui.radio_fix_oza, self.gui.radio_gauss_oza, self.gui.radio_uni_oza,
                                 self.gui.radio_log_oza, self.gui.txt_fix_oza, self.gui.txt_gauss_min_oza,
                                 self.gui.txt_gauss_max_oza, self.gui.txt_gauss_mean_oza, self.gui.txt_gauss_std_oza,
                                 self.gui.txt_log_min_oza, self.gui.txt_log_max_oza, self.gui.txt_log_steps_oza],
                             "sza": [self.gui.radio_fix_sza, self.gui.radio_gauss_sza, self.gui.radio_uni_sza,
                                 self.gui.radio_log_sza, self.gui.txt_fix_sza, self.gui.txt_gauss_min_sza,
                                 self.gui.txt_gauss_max_sza, self.gui.txt_gauss_mean_sza, self.gui.txt_gauss_std_sza,
                                 self.gui.txt_log_min_sza, self.gui.txt_log_max_sza, self.gui.txt_log_steps_sza],
                             "raa": [self.gui.radio_fix_raa, self.gui.radio_gauss_raa, self.gui.radio_uni_raa,
                                 self.gui.radio_log_raa, self.gui.txt_fix_raa, self.gui.txt_gauss_min_raa,
                                 self.gui.txt_gauss_max_raa, self.gui.txt_gauss_mean_raa, self.gui.txt_gauss_std_raa,
                                 self.gui.txt_log_min_raa, self.gui.txt_log_max_raa, self.gui.txt_log_steps_raa],
                             "skyl": [self.gui.radio_fix_skyl, self.gui.radio_gauss_skyl, self.gui.radio_uni_skyl,
                                 self.gui.radio_log_skyl, self.gui.txt_fix_skyl, self.gui.txt_gauss_min_skyl,
                                 self.gui.txt_gauss_max_skyl, self.gui.txt_gauss_mean_skyl, self.gui.txt_gauss_std_skyl,
                                 self.gui.txt_log_min_skyl, self.gui.txt_log_max_skyl, self.gui.txt_log_steps_skyl],
                             "laiu": [self.gui.radio_fix_laiu, self.gui.radio_gauss_laiu, self.gui.radio_uni_laiu,
                                 self.gui.radio_log_laiu, self.gui.txt_fix_laiu, self.gui.txt_gauss_min_laiu,
                                 self.gui.txt_gauss_max_laiu, self.gui.txt_gauss_mean_laiu, self.gui.txt_gauss_std_laiu,
                                 self.gui.txt_log_min_laiu, self.gui.txt_log_max_laiu, self.gui.txt_log_steps_laiu],
                             "sd": [self.gui.radio_fix_sd, self.gui.radio_gauss_sd, self.gui.radio_uni_sd,
                                 self.gui.radio_log_sd, self.gui.txt_fix_sd, self.gui.txt_gauss_min_sd,
                                 self.gui.txt_gauss_max_sd, self.gui.txt_gauss_mean_sd, self.gui.txt_gauss_std_sd,
                                 self.gui.txt_log_min_sd, self.gui.txt_log_max_sd, self.gui.txt_log_steps_sd],
                             "h": [self.gui.radio_fix_h, self.gui.radio_gauss_h, self.gui.radio_uni_h,
                                 self.gui.radio_log_h, self.gui.txt_fix_h, self.gui.txt_gauss_min_h,
                                 self.gui.txt_gauss_max_h, self.gui.txt_gauss_mean_h, self.gui.txt_gauss_std_h,
                                 self.gui.txt_log_min_h, self.gui.txt_log_max_h, self.gui.txt_log_steps_h],
                             "cd": [self.gui.radio_fix_cd, self.gui.radio_gauss_cd, self.gui.radio_uni_cd,
                                 self.gui.radio_log_cd, self.gui.txt_fix_cd, self.gui.txt_gauss_min_cd,
                                 self.gui.txt_gauss_max_cd, self.gui.txt_gauss_mean_cd, self.gui.txt_gauss_std_cd,
                                 self.gui.txt_log_min_cd, self.gui.txt_log_max_cd, self.gui.txt_log_steps_cd]}

    def connections(self):
        # Sensor Type
        self.gui.SType_None_B.clicked.connect(lambda: self.select_s2s(sensor="default"))
        self.gui.SType_Sentinel_B.clicked.connect(lambda: self.select_s2s(sensor="Sentinel2"))
        self.gui.SType_Landsat_B.clicked.connect(lambda: self.select_s2s(sensor="Landsat8"))
        self.gui.SType_Enmap_B.clicked.connect(lambda: self.select_s2s(sensor="EnMAP"))

        # Models
        self.gui.B_Prospect4.clicked.connect(lambda: self.select_model(lop="prospect4"))
        self.gui.B_Prospect5.clicked.connect(lambda: self.select_model(lop="prospect5"))
        self.gui.B_Prospect5b.clicked.connect(lambda: self.select_model(lop="prospect5B"))
        self.gui.B_ProspectD.clicked.connect(lambda: self.select_model(lop="prospectD"))

        self.gui.B_LeafModelOnly.clicked.connect(lambda: self.select_model(canopy_arch="None"))
        self.gui.B_4Sail.clicked.connect(lambda: self.select_model(canopy_arch="sail"))
        self.gui.B_Inform.clicked.connect(lambda: self.select_model(canopy_arch="inform"))

        # Radio Buttons
        self.gui.radio_fix_chl.clicked.connect(lambda: self.txt_enables())


    def txt_enables(self):
        pass

    def any_lineEdit_change(self, textfeld, slider,):
        try:
            my_value = int(float(textfeld.text()) * 10000)
            slider.setValue(my_value)
        except ValueError:
            QMessageBox.critical(self.gui, "Not a number", "'%s' is not a valid number" % textfeld.text())
            textfeld.setText(str(slider.value() / 10000.0))

    def select_s2s(self, sensor, trigger=True):
        self.sensor = sensor
        if not sensor == "default":
            s2s = Spec2Sensor(sensor=sensor, nodat=-999)
            s2s.init_sensor()
            self.wl = s2s.wl_sensor
            self.plot_count += 1
        else:
            self.wl = range(400, 2501)

        if trigger:
            self.mod_exec()

    def select_model(self, lop="prospectD", canopy_arch="sail"):
        self.lop = lop
        if canopy_arch == "None":
            self.canopy_arch = None
        else:
            self.canopy_arch = canopy_arch
        self.mod_exec()

    def select_LIDF(self, index):
        if index > 0:
            self.typeLIDF = 1 # Beta Distribution
            self.para_list[6] = index - 1
            self.gui.LIDFB_Slide.setDisabled(True)
            self.gui.LIDFB_lineEdit.setDisabled(True)
            self.mod_exec()
        else:
            self.typeLIDF = 2 # Ellipsoidal Distribution
            self.mod_exec(self.gui.LIDFB_Slide, item=6)
            self.gui.LIDFB_Slide.setDisabled(False)
            self.gui.LIDFB_lineEdit.setDisabled(False)

    def deactivate_sliders(self):
        self.gui.B_Prospect5b.toggled.connect(lambda: self.model_rb_click(self.gui.B_Prospect5b, self.gui.Canth_Slide, self.gui.Canth_lineEdit, self.gui.Canth_Text))

        self.gui.B_Prospect5.toggled.connect(lambda: self.model_rb_click(self.gui.B_Prospect5, self.gui.Canth_Slide, self.gui.Canth_lineEdit, self.gui.Canth_Text))
        self.gui.B_Prospect5.toggled.connect(lambda: self.model_rb_click(self.gui.B_Prospect5, self.gui.Cbrown_Slide, self.gui.Cbrown_lineEdit, self.gui.Cbrown_Text))

        self.gui.B_Prospect4.toggled.connect(lambda: self.model_rb_click(self.gui.B_Prospect4, self.gui.Canth_Slide, self.gui.Canth_lineEdit, self.gui.Canth_Text))
        self.gui.B_Prospect4.toggled.connect(lambda: self.model_rb_click(self.gui.B_Prospect4, self.gui.Cbrown_Slide, self.gui.Cbrown_lineEdit, self.gui.Cbrown_Text))
        self.gui.B_Prospect4.toggled.connect(lambda: self.model_rb_click(self.gui.B_Prospect4, self.gui.Car_Slide, self.gui.Car_lineEdit, self.gui.Car_Text))

    def model_rb_click(self, rbutton, slider, textfeld, text):
        if rbutton.isChecked():
            slider.setDisabled(True)
            textfeld.setDisabled(True)
            text.setDisabled(True)
        else:
            slider.setDisabled(False)
            textfeld.setDisabled(False)
            text.setDisabled(False)

    def para_init(self):
        self.select_s2s(sensor="default", trigger=False)
        self.para_list.append(float(self.gui.N_lineEdit.text())) #0
        self.para_list.append(float(self.gui.Cab_lineEdit.text())) #1
        self.para_list.append(float(self.gui.Cw_lineEdit.text())) #2
        self.para_list.append(float(self.gui.Cm_lineEdit.text())) #3
        self.para_list.append(float(self.gui.LAI_lineEdit.text())) #4
        self.para_list.append(float(2))  # 5
        self.para_list.append(float(self.gui.LIDFB_lineEdit.text())) #6
        self.para_list.append(float(self.gui.hspot_lineEdit.text())) #7
        self.para_list.append(float(self.gui.psoil_lineEdit.text())) #8
        self.para_list.append(float(self.gui.SZA_lineEdit.text())) #9
        self.para_list.append(float(self.gui.OZA_lineEdit.text())) #10
        self.para_list.append(float(self.gui.rAA_lineEdit.text())) #11
        self.para_list.append(float(self.gui.Car_lineEdit.text())) #12
        self.para_list.append(float(self.gui.Canth_lineEdit.text())) #13
        self.para_list.append(float(self.gui.Cbrown_lineEdit.text())) #14
        self.para_list.append(float(self.gui.skyl_lineEdit.text())) #15
        self.typeLIDF = 2

    def mod_interactive(self):
        self.gui.N_Slide.valueChanged.connect(lambda: self.mod_exec(slider=self.gui.N_Slide, item=0))
        self.gui.Cab_Slide.valueChanged.connect(lambda: self.mod_exec(slider=self.gui.Cab_Slide, item=1))
        self.gui.Cw_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cw_Slide, item=2))
        self.gui.Cm_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cm_Slide, item=3))
        self.gui.LAI_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LAI_Slide, item=4))
        self.gui.LIDFB_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LIDFB_Slide, item=6))
        self.gui.hspot_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.hspot_Slide, item=7))
        self.gui.psoil_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.psoil_Slide, item=8))
        self.gui.SZA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.SZA_Slide, item=9))
        self.gui.OZA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.OZA_Slide, item=10))
        self.gui.rAA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.rAA_Slide, item=11))
        self.gui.Car_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Car_Slide, item=12))
        self.gui.Canth_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Canth_Slide, item=13))
        self.gui.Cbrown_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cbrown_Slide, item=14))
        self.gui.skyl_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.skyl_Slide, item=15))
        self.gui.LAIu_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LAIu_Slide, item=16))
        self.gui.SD_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.SD_Slide, item=17))
        self.gui.TreeH_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.TreeH_Slide, item=18))
        self.gui.CD_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.CD_Slide, item=19))

        self.gui.SType_None_B.clicked.connect(lambda: self.select_s2s(sensor="default"))
        self.gui.SType_Sentinel_B.clicked.connect(lambda: self.select_s2s(sensor="Sentinel2"))
        self.gui.SType_Landsat_B.clicked.connect(lambda: self.select_s2s(sensor="Landsat8"))
        self.gui.SType_Enmap_B.clicked.connect(lambda: self.select_s2s(sensor="EnMAP"))

        self.gui.B_Prospect4.clicked.connect(lambda: self.select_model(lop="prospect4"))
        self.gui.B_Prospect5.clicked.connect(lambda: self.select_model(lop="prospect5"))
        self.gui.B_Prospect5b.clicked.connect(lambda: self.select_model(lop="prospect5B"))
        self.gui.B_ProspectD.clicked.connect(lambda: self.select_model(lop="prospectD"))

        self.gui.B_LeafModelOnly.clicked.connect(lambda: self.select_model(canopy_arch="None"))
        self.gui.B_4Sail.clicked.connect(lambda: self.select_model(canopy_arch="sail"))
        self.gui.B_Inform.clicked.connect(lambda: self.select_model(canopy_arch="inform"))

        self.gui.LIDF_combobox.currentIndexChanged.connect(self.select_LIDF)

        self.gui.pushClearPlot.clicked.connect(self.clear_plot)
        self.gui.Push_LoadInSitu.clicked.connect(self.open_file)
        self.gui.Push_Exit.clicked.connect(self.gui.accept)
        self.gui.Push_ResetInSitu.clicked.connect(self.reset_in_situ)

    def mod_exec(self, slider=None, item=None):

        if slider is not None and item is not None:
            self.para_list[item] = slider.value() / 10000.0 # update para_list

        mod_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=-999, int_boost=1.0, s2s=self.sensor)
        self.myResult = mod_I.initialize_single(tts=self.para_list[9], tto=self.para_list[10], psi=self.para_list[11],
                                           N=self.para_list[0], cab=self.para_list[1], cw=self.para_list[2],
                                           cm=self.para_list[3], LAI=self.para_list[4], LIDF=self.para_list[6],
                                           typeLIDF=self.typeLIDF, hspot=self.para_list[7], psoil=self.para_list[8],
                                           car=self.para_list[12],
                                           cbrown=self.para_list[14], anth=self.para_list[13])

        # self.myResult[960:1021] = np.nan  # set atmospheric water vapour absorption bands to NaN
        # self.myResult[1390:1541] = np.nan
        self.plotting()

    def plotting(self):

        if not self.gui.CheckPlotAcc.isChecked():

            self.clear_plot()
            self.gui.graphicsView.plot(self.wl, self.myResult, pen="g", fillLevel=0, fillBrush=(255, 255, 255, 30),
                                        name='modelled')

            self.gui.graphicsView.setYRange(0, 0.6, padding=0)
            self.gui.graphicsView.setLabel('left', text="Reflectance [%]")
            self.gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")
        else:
            self.plot = self.gui.graphicsView.plot(self.wl, self.myResult,
                                              pen=self.plot_color[self.plot_count % 7])
            self.plot_own_spec()
            self.gui.graphicsView.setYRange(0, 0.6, padding=0)
            self.gui.graphicsView.setLabel('left', text="Reflectance [%]")
            self.gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")

        if self.data_mean is not None and self.gui.SType_None_B.isChecked() and not self.gui.CheckPlotAcc.isChecked():

            self.plot_own_spec()

            mae = np.nansum(abs(self.myResult - self.data_mean)) / len(self.myResult)
            rmse = np.sqrt(np.nanmean((self.myResult - self.data_mean)**2))
            nse = 1.0 - ((np.nansum((self.data_mean - self.myResult)**2)) /
                         (np.nansum((self.data_mean - (np.nanmean(self.data_mean)))**2)))
            mnse = 1.0 - ((np.nansum(abs(self.data_mean - self.myResult))) /
                          (np.nansum(abs(self.data_mean - (np.nanmean(self.data_mean))))))
            r_squared = ((np.nansum((self.data_mean - np.nanmean(self.data_mean)) * (self.myResult - np.nanmean(self.myResult))))
                         / ((np.sqrt(np.nansum((self.data_mean - np.nanmean(self.data_mean))**2)))
                            * (np.sqrt(np.nansum((self.myResult - np.nanmean(self.myResult))**2)))))**2

            errors = pg.TextItem("RMSE: " + str(round(rmse, 6)) +
                                 "\nMAE: " + str(round(mae, 6)) +
                                 "\nNSE: " + str(round(nse, 6)) +
                                 "\nmNSE: " + str(round(mnse, 6)) +
                                 '\n' + u'R²: ' + str(round(r_squared, 6)), (100, 200, 255),
                                 border="w", anchor=(1, 0))
            errors.setPos(2500, 0.55)
            self.gui.graphicsView.addItem(errors)

    def open_file(self):
        # Dialog to open own spectrum, .asc exported by ViewSpecPro as single file
        filename = str(QFileDialog.getOpenFileName(caption='Select Spectrum File'))
        self.data = np.genfromtxt(filename, delimiter="\t", skip_header=True)
        ## "\OSGEO4~1\apps\Python27\lib\site-packages\numpy\lib\npyio.py" changed endswith to endsWith to work:
        self.data = np.delete(self.data, 0, axis=1)
        self.data_mean = np.mean(self.data, axis=1)
        self.data_mean[1010:1071] = np.nan  # set atmospheric water vapour absorption bands to NaN
        self.data_mean[1440:1591] = np.nan
        self.data_mean[2050:2151] = np.nan
        self.data_mean = self.data_mean[50:]
        self.mod_exec()

    def reset_in_situ(self):
        self.data_mean = None
        self.mod_exec()

    def plot_own_spec(self):
        if self.data_mean is not None:
            self.gui.graphicsView.plot(range(400, 2501), self.data_mean, name='observed')

    def clear_plot(self):
        self.gui.graphicsView.clear()
        self.plot_count = 0

    #never ever...
    #def exit_GUI(self):
    #    QCoreApplication.instance().quit()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app =  initQgisEnvironment()
    myUI = UiFunc()
    myUI.gui.show()
    sys.exit(app.exec_())


