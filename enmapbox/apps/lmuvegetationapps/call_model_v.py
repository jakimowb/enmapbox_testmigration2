# -*- coding: utf-8 -*-
# Temporary Call Model routine for hierarchical approach

import os
import numpy as np
from scipy.stats import truncnorm
import lmuvegetationapps.SAIL_v as SAIL_v
import lmuvegetationapps.INFORM_v as INFORM_v
import lmuvegetationapps.prospect_v as prospect_v
from lmuvegetationapps.Spec2Sensor_cl_v import Spec2Sensor
import warnings
import time
warnings.filterwarnings('ignore')

# Model class
class Call_model:

    def __init__(self, soil, paras):
        self.par = paras
        self.ninputs = self.par['cab'].shape[0]  # cab is always part of self.par
        self.soil = soil

    def call_prospect4(self):
        prospect_instance = prospect_v.Prospect()
        self.prospect = prospect_instance.prospect_4(self.par["N"], self.par["cab"], self.par["cw"], self.par["cm"])

        return self.prospect

    def call_prospect5(self):
        prospect_instance = prospect_v.Prospect()
        self.prospect = prospect_instance.prospect_5(self.par["N"], self.par["cab"], self.par["car"], self.par["cw"],
                                                     self.par["cm"])

        return self.prospect

    def call_prospect5B(self):
        prospect_instance = prospect_v.Prospect()
        self.prospect = prospect_instance.prospect_5B(self.par["N"], self.par["cab"], self.par["car"],
                                                      self.par["cbrown"], self.par["cw"], self.par["cm"])

        return self.prospect

    def call_prospectD(self):
        prospect_instance = prospect_v.Prospect()
        self.prospect = prospect_instance.prospect_D(self.par["N"], self.par["cab"], self.par["car"], self.par["anth"],
                                                     self.par["cbrown"], self.par["cw"], self.par["cm"])

        return self.prospect

    def call_prospectCp(self):
        prospect_instance = prospect_v.Prospect()
        self.prospect = prospect_instance.prospect_Cp(self.par["N"], self.par["cab"], self.par["car"], self.par["anth"],
                                                      self.par["cp"], self.par["ccl"], self.par["cbrown"],
                                                      self.par["cw"], self.par["cm"])
        return self.prospect

    def call_prospectPro(self):
        prospect_instance = prospect_v.Prospect()
        self.prospect = prospect_instance.prospect_Pro(self.par["N"], self.par["cab"], self.par["car"],
                                                      self.par["anth"],
                                                      self.par["cp"], self.par["cbc"], self.par["cbrown"],
                                                      self.par["cw"])
        return self.prospect

    def call_4sail(self):

        try:
            self.prospect.any()
        except ValueError:
            raise ValueError("A leaf optical properties model needs to be run first!")
        sail_instance = SAIL_v.Sail(np.deg2rad(self.par["tts"]), np.deg2rad(self.par["tto"]), np.deg2rad(self.par["psi"]))  # Create Instance of SAIL and initialize angles
        self.sail = sail_instance.Pro4sail(self.prospect[:, :, 1], self.prospect[:, :, 2], self.par["LIDF"],
                                           self.par["typeLIDF"], self.par["LAI"], self.par["hspot"], self.par["psoil"],
                                           self.soil)  # call 4SAIL from the SAIL instance

        # Mit Skyl, temporär deaktiviert
        # self.sail = sail_instance.Pro4sail(self.prospect[:,1], self.prospect[:,2], self.par["LIDF"],
        #                                    self.par["typeLIDF"], self.par["LAI"], self.par["hspot"], self.par["psoil"],
        #                                    self.soil, self.par["skyl"])  # call 4SAIL from the SAIL instance

        return self.sail

    def call_inform(self):

        try:
            self.prospect.any()
        except ValueError:
            raise ValueError("A leaf optical properties model needs to be run first!")
        sail_instance = SAIL_v.Sail(np.deg2rad(self.par["tts"]), np.deg2rad(self.par["tto"]), np.deg2rad(self.par["psi"])) # Create Instance of SAIL and initialize angles
        # call Pro4sail to calculate understory reflectance
        self.sail_understory_refl = sail_instance.Pro4sail(self.prospect[:, :, 1], self.prospect[:, :, 2], self.par["LIDF"],
                                           self.par["typeLIDF"], self.par["LAIu"], self.par["hspot"], self.par["psoil"],
                                           self.soil)  # call 4SAIL from the SAIL instance
        # call Pro4sail with understory as soil to calculate infinite crown reflectance
        inform_temp_LAI = np.asarray([15]*self.ninputs).T
        inform_temp_hspot = np.asarray([0]*self.ninputs).T
        self.sail_inf_refl = sail_instance.Pro4sail(self.prospect[:, :, 1], self.prospect[:, :, 2], self.par["LIDF"],
                                                    self.par["typeLIDF"], inform_temp_LAI, self.par["hspot"],
                                                    psoil=None, soil=None, understory=self.sail_understory_refl)

        self.sail_tts_trans = sail_instance.Pro4sail(self.prospect[:, :, 1], self.prospect[:, :, 2], self.par["LIDF"],
                                                     self.par["typeLIDF"], self.par["LAI"], inform_temp_hspot,
                                                     psoil=None, soil=None, understory=self.sail_understory_refl,
                                                     inform_trans='tts')

        self.sail_tto_trans = sail_instance.Pro4sail(self.prospect[:, :, 1], self.prospect[:, :, 2], self.par["LIDF"],
                                                     self.par["typeLIDF"], self.par["LAI"], inform_temp_hspot,
                                                     psoil=None, soil=None, understory=self.sail_understory_refl,
                                                     inform_trans='tto')

        inform_instance = INFORM_v.INFORM(sail_instance.costts, sail_instance.costto, sail_instance.cospsi)
        inform = inform_instance.inform(self.par["cd"], self.par["sd"], self.par["h"], self.sail_understory_refl,
                                        self.sail_inf_refl, self.sail_tts_trans, self.sail_tto_trans)

        return inform

class Setup_multiple:

    def __init__(self, ns, paras, depends):
        self.whichlogicals = []
        self.nruns_logic_geo, self.nruns_logic_no_geo, self.nruns_logic_total = (1, 1, 1)
        # self.para_nums = {"N": 0, "cab": 1, "car": 2, "anth": 3, "cbrown": 4, "cw": 5, "cm": 6, "cp": 7, "ccl": 8,
        #                   "LAI": 9, "typeLIDF": 10, "LIDF": 11, "hspot": 12, "psoil": 13, "tts": 14, "tto": 15,
        #                   "psi": 16}  # Outdated! Might cause trouble
        self.para_nums = {"N": 0, "cab": 1, "car": 2, "anth": 3, "cbrown": 4, "cw": 5, "cm": 6, "cp": 7, "cbc": 8,
                          "LAI": 9, "typeLIDF": 10, "LIDF": 11, "hspot": 12, "psoil": 13, "tts": 14, "tto": 15,
                          "psi": 16, "LAIu": 17, "cd": 18, "sd": 19, "h": 20}
        self.npara = len(self.para_nums)
        self.depends = depends
        self.paras = paras
        self.ns = int(ns)
        self.error_array = []


    def create_grid(self):
        # 1 find logically distributed parameters
        for para_key in self.paras:
            try:
                if len(self.paras[para_key]) == 3:  # logical distr. = min, max, nsteps
                    self.whichlogicals.append(para_key)
            except:
                print(para_key)
                exit()
        #2 calculate nruns_logical for each logically distributed parameter
        self.nruns_logic = dict(zip(self.whichlogicals, [int(self.paras[para_key][2]) for para_key in self.whichlogicals]))

        # 3 calculate total nruns_logical
        for para_key in self.whichlogicals:
            if para_key in ["tts", "tto", "psi"]:
                self.nruns_logic_geo *= self.nruns_logic[para_key]  # contains only geometry
            else:
                self.nruns_logic_no_geo *= self.nruns_logic[para_key]  # contains everything except geometry
        self.nruns_logic_total = self.nruns_logic_geo * self.nruns_logic_no_geo

        # 4 Calculate total nruns
        self.nruns_total = int(self.nruns_logic_total * self.ns)

        # 5 Create numpy array to hold all parameter constellations
        self.para_grid = np.empty(shape=(self.nruns_total, self.npara), dtype=np.float32)

        # 6 Fill each parameter into numpy array
        k = 0  # iterator for logical order
        self.repeat_accum = self.ns

        for para_key in self.paras:
            if len(self.paras[para_key]) == 2:  # uniform distribution
                self.para_grid[:, self.para_nums[para_key]] = self.uniform_distribution(para_name=para_key,
                                                                                        min=self.paras[para_key][0],
                                                                                        max=self.paras[para_key][1],
                                                                                        multiply=self.nruns_logic_total)

            elif len(self.paras[para_key]) == 4:  # gaussian distribution
                self.para_grid[:, self.para_nums[para_key]] = self.gauss_distribution(para_name=para_key,
                                                                                      min=self.paras[para_key][0],
                                                                                      max=self.paras[para_key][1],
                                                                                      mean=self.paras[para_key][2],
                                                                                      sigma=self.paras[para_key][3],
                                                                                      multiply=self.nruns_logic_total)

            elif len(self.paras[para_key]) == 1:  # fixed parameter
                self.para_grid[:, self.para_nums[para_key]] = np.tile(self.paras[para_key][0], self.nruns_total)

            elif len(self.paras[para_key]) == 3:  # logically distributed parameter
                k += 1
                self.repeat_accum *= self.nruns_logic[para_key]
                multiply = self.nruns_total // self.repeat_accum
                self.para_grid[:, self.para_nums[para_key]] = self.logical_distribution(para_name=para_key,
                                                                                        min=self.paras[para_key][0],
                                                                                        max=self.paras[para_key][1],
                                                                                        repeat=self.repeat_accum /
                                                                                               self.nruns_logic[
                                                                                                   para_key],
                                                                                        multiply=multiply,
                                                                                        nsteps=self.paras[para_key][2])

            if self.depends == 1 and para_key == 'car':
                    self.para_grid[:, self.para_nums[para_key]] = self.car_cab_dependency(
                        grid=self.para_grid[:, self.para_nums['cab']])

        return self.para_grid


    def fixed(self, para_name, value):
        return_list = np.linspace(start=value, stop=value, num=self.ns)
        return return_list

    def logical_distribution(self,para_name,min,max,repeat,multiply,nsteps,increment=None):
        return_list = np.tile(np.repeat(np.linspace(start=min,stop=max,num=int(nsteps)), repeat), multiply)
        return return_list

    def gauss_distribution(self,para_name,min,max,mean,sigma,multiply):
        try:
            return_list = np.tile(truncnorm((min-mean)/sigma, (max-mean)/sigma, loc=mean, scale=sigma).rvs(self.ns),multiply)
        except:
            raise ValueError("Cannot create gaussian distribution for parameter %s. Check values!" % para_name)

        return return_list

    def uniform_distribution(self, para_name, min, max, multiply):
        try:
            return_list = np.tile(np.random.uniform(low=min, high=max, size=self.ns), multiply)
        except:
            raise ValueError("Cannot create uniform distribution for parameter %s. Check values!" % para_name)

        return return_list

    def car_cab_dependency(self, grid):

        def truncated_noise(y, lower, upper):
            while True:
                y_noise = np.random.laplace(loc=0, scale=spread, size=1) + y
                if upper > y_noise > lower:
                    return y_noise

        def refine_noise(y, y_lin_noise, lower, upper):
            for i in range(len(y_lin_noise)):
                if upper[i] < y_lin_noise[i] or lower[i] > y_lin_noise[i]:
                    y_lin_noise[i] = truncated_noise(y[i], lower[i], upper[i])
            return y_lin_noise

        # constants from ANGERS03 Leaf Optical Data
        slope = 0.2234
        intercept = 0.9861
        spread = 4.6839
        car_lin = slope * grid + intercept
        lower_car = slope / spread * 3 * grid
        upper_car = slope * spread / 3 * grid + 2 * intercept

        car_lin_noise = np.random.laplace(loc=0, scale=spread, size=len(car_lin)) + car_lin
        car_lin_noise = refine_noise(car_lin, car_lin_noise, lower_car, upper_car)
        car_lin_noise = refine_noise(car_lin, car_lin_noise, lower_car, upper=np.tile(26, len(grid)))

        return car_lin_noise

class Init_Model:

    def __init__(self, lop="prospectD", canopy_arch=None, int_boost=1, nodat=-999, s2s="default"):

        # get current directory
        self._dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(self._dir)
        self.lop = lop
        self.canopy_arch = canopy_arch
        self.int_boost = int_boost
        self.nodat = nodat
        self.s2s = s2s
        self.geo_mode = None
        self.soil = None
        self.para_names = ["N", "cab", "car", "anth", "cbrown", "cw", "cm", "cp", "cbc",
                          "LAI", "LAIu", "typeLIDF", "LIDF", "hspot", "psoil", "tts", "tto",
                          "psi", "sd", "h", "cd"]

    def initialize_multiple_simple(self, soil=None, **paras):
        self.soil = soil
        nparas = len(paras['LAI'])
        para_grid = np.empty(shape=(nparas, len(paras.keys())))
        for run in range(nparas):
            for ikey, key in enumerate(self.para_names):
                para_grid[run, ikey] = paras[key][run]


        self.run_model(paras=dict(zip(self.para_names, para_grid.T)))




    def initialize_vectorized(self, LUT_dir, LUT_name, ns, max_per_file=5000, soil=None,
                            prgbar_widget=None, QGis_app=None, depends=False, testmode=False, **paras):

        self.soil = soil

        # Setup multiple runs with l size logical distribution & n size statistical distribution
        # param_input = [N, cab, cw, cm, LAI, typeLIDF, LIDF, hspot, psoil, car, anth, cbrown, tts, tto, psi] # update: geometry comes lastly


        if len(paras["tts"]) > 1 or len(paras["tto"]) > 1 or len(paras["psi"]) > 1:
            self.geo_mode = "sort"  # LUT-Files are (firstly) sorted by geometry
        else:
            self.geo_mode = "no_geo"

        self.max_filelength = max_per_file
        npara = len(self.para_names)
        setup = Setup_multiple(ns=ns, paras=paras, depends=depends)
        para_grid = setup.create_grid()

        crun_max = setup.nruns_total
        crun_pergeo = setup.ns * setup.nruns_logic_no_geo

        # Get number of files
        # Geo_mode "sort" (at least one LUT-file per Geo)

        n_ensembles_split, n_ensembles_geo = (1, 1)  # initialize ensembles

        if self.geo_mode == "sort":
            n_ensembles_geo = setup.nruns_logic_geo
        elif self.geo_mode == "no_geo":
            n_ensembles_geo = 1

        # print("n_ensembles_geo: ", n_ensembles_geo)
        # print("max_per_file: ", max_per_file)

        if crun_pergeo <= max_per_file:  # exactly one LUT-file per Geo
            # max_per_file = crun_pergeo # lower max_per_file to LUT-members per Geo ## why? Causes trouble for ns < max_per_file
            n_ensembles_split = 1
        else:  # second split: several files per Geo
            n_ensembles_split = (
                                            crun_pergeo - 1) // max_per_file + 1  # number of ensembles (=number of LUT-files to create)

        # print("max_per_file: ", max_per_file)
        # print("n_ensembles_split: ", n_ensembles_split)

        if not self.s2s == "default":
            self.s2s_I = Spec2Sensor(sensor=self.s2s, nodat=self.nodat)
            self.s2s_I.init_sensor()
            nbands = self.s2s_I.n_wl_sensor
        else:
            nbands = len(prospect_v.lambd)

        if testmode == True:
            start = time.time()
            _ = self.run_model(paras=dict(zip(self.para_names, para_grid.T))).T
            # for run in range(crun_max):
            #     self.run_model(paras=dict(zip(self.para_names, para_grid[run, :])))  # Vek anpassen?

            return time.time() - start

        struct_ensemble = 0
        n_struct_ensembles = 1
        # Meta-File:
        if len(paras["tts"]) == 3:
            tts_fl = np.linspace(start=setup.paras["tts"][0], stop=setup.paras["tts"][1],
                                 num=int(setup.paras["tts"][2]))
            tts_str = [tts_fl.astype(str)[i] for i in range(len(tts_fl))]
        elif len(paras["tts"]) == 1:
            tts_str = [str(paras["tts"][0])]
        else:
            tts_str = ["NA"]

        if len(paras["tto"]) == 3:
            tto_fl = np.linspace(start=setup.paras["tto"][0], stop=setup.paras["tto"][1],
                                 num=int(setup.paras["tto"][2]))
            tto_str = [tto_fl.astype(str)[i] for i in range(len(tto_fl))]
        elif len(paras["tto"]) == 1:
            tto_str = [str(paras["tto"][0])]
        else:
            tto_str = ["NA"]

        if len(paras["psi"]) == 3:
            psi_fl = np.linspace(start=setup.paras["psi"][0], stop=setup.paras["psi"][1],
                                 num=int(setup.paras["psi"][2]))
            psi_str = [psi_fl.astype(str)[i] for i in range(len(psi_fl))]
        elif len(paras["psi"]) == 1:
            psi_str = [str(paras["psi"][0])]
        else:
            psi_str = ["NA"]

        with open("%s_00meta.lut" % (LUT_dir + LUT_name), "w") as meta:
            meta.write("name=%s\n" % LUT_name)
            meta.write("n_total=%i\n" % setup.nruns_total)
            meta.write("ns=%i\n" % setup.ns)
            meta.write("lop_model=%s\n" % self.lop)
            meta.write("canopy_architecture_model=%s\n" % self.canopy_arch)
            meta.write("geo_mode=%s\n" % self.geo_mode)
            meta.write("geo_ensembles=%i\n" % n_ensembles_geo)
            meta.write("splits=%i\n" % n_ensembles_split)
            meta.write("max_file_length=%i\n" % self.max_filelength)
            meta.write("tts=")
            for i in range(len(tts_str)):
                meta.write(tts_str[i] + ";")
            meta.write("\ntto=")
            for i in range(len(tto_str)):
                meta.write(tto_str[i] + ";")
            meta.write("\npsi=")
            for i in range(len(psi_str)):
                meta.write(psi_str[i] + ";")
            meta.write("\nmultiplication_factor=%i" % self.int_boost)
            meta.write("\nparameters=")
            for i in self.para_names:
                meta.write(i + ";")

        if prgbar_widget:
            prgbar_widget.gui.lblCaption_l.setText("Creating LUT")
            QGis_app.processEvents()

        for geo_ensemble in range(n_ensembles_geo):

            rest = crun_pergeo
            for split in range(n_ensembles_split):

                if rest >= max_per_file:
                    save_array = np.empty((nbands + npara, max_per_file))
                    nruns = max_per_file # Anzahl Runs im Split
                else:
                    nruns = rest
                    save_array = np.empty((nbands + npara, rest))

                # run = geo_ensemble * crun_pergeo + split * max_per_file + i
                run = geo_ensemble * crun_pergeo + split * max_per_file # current run (first of the current split)

                if prgbar_widget:
                    if prgbar_widget.gui.lblCancel.text() == "-1":
                        prgbar_widget.gui.lblCancel.setText("")
                        prgbar_widget.gui.cmdCancel.setDisabled(False)
                        raise ValueError("LUT creation cancelled!")

                    prgbar_widget.gui.lblCaption_r.setText('Split %s of %s' % (str(split), str(crun_pergeo)))
                    QGis_app.processEvents()
                else:
                    print(
                        "LUT ensemble struct #{:d} of {:d}; ensemble geo #{:d} of {:d}; split #{:d} of {:d}; total #{:d} of {:d}"
                        .format(struct_ensemble, n_struct_ensembles - 1, geo_ensemble,
                                n_ensembles_geo - 1, split, n_ensembles_split - 1, run, crun_max))

                if prgbar_widget:
                    prgbar_widget.gui.prgBar.setValue(run * 100 / crun_max)
                    QGis_app.processEvents()


                save_array[npara:, :] = self.run_model(paras=dict(zip(self.para_names, para_grid[run : run+nruns, :].T))).T
                save_array[:npara, :] = para_grid[run : run+nruns, :].T

                rest -= max_per_file
                np.save("{}_{:d}_{:d}".format(LUT_dir + LUT_name, geo_ensemble, split), save_array)

        if prgbar_widget:
            prgbar_widget.gui.lblCaption_r.setText('File {:d} of {:d}'.format(crun_max, crun_max))
            prgbar_widget.gui.prgBar.setValue(100)
            prgbar_widget.gui.close()


    def initialize_multiple(self, LUT_dir, LUT_name, ns, max_per_file=5000, soil=None,
                            build_step2=0, prgbar_widget=None, QGis_app=None, **paras):

        self.soil = soil

        # Setup multiple runs with l size logical distribution & n size statistical distribution
        # param_input = [N, cab, cw, cm, LAI, typeLIDF, LIDF, hspot, psoil, car, anth, cbrown, tts, tto, psi] # update: geometry comes lastly

        # LAI_step2 = [[0, 0.5], [0.5, 1.0], [1.0, 1.5], [1.5, 2.0], [2.0, 2.5], [2.5, 3.0], [3.0, 3.5], [3.5, 4.0],
        #              [4.0, 4.5], [4.5, 5.0], [5.0, 5.5], [5.5, 6.0], [6.0, 6.5], [6.5, 7.0], [7.0, 7.5], [7.5, 8.0]] # len 16
        # LIDF_step2 = [[20, 30], [30, 40], [40, 50], [50, 60], [60, 70], [70, 80]]

        LAI_step2 = [[0, 1.0], [1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0], [5.0, 6.0], [6.0, 7.0], [7.0, 8.0]] # len: 8
        LIDF_step2 = [[20, 30], [30, 40], [40, 50], [50, 60], [60, 70], [70, 80]] # len 6

        for ALIA_i in range(len(LIDF_step2)):
            for LAI_i in range(len(LAI_step2)):

        # # Reset nach Absturz:
        # for ALIA_i in [5]:
        #     for LAI_i in xrange(8, 16):

                if build_step2 == 1:
                    LAI = LAI_step2[LAI_i]
                    LIDF = LIDF_step2[ALIA_i]
                    struct_ensemble = ALIA_i * len(LAI_step2) + LAI_i
                    n_struct_ensembles = len(LAI_step2) * len(LIDF_step2)
                else:
                    struct_ensemble = 0
                    n_struct_ensembles = 1

                if len(paras["tts"]) > 1 or len(paras["tto"]) > 1 or len(paras["psi"]) > 1:
                    self.geo_mode = "sort"  # LUT-Files are (firstly) sorted by geometry
                else:
                    self.geo_mode = "no_geo"

                self.max_filelength = max_per_file
                npara = len(self.para_names)
                setup = Setup_multiple(ns=ns, paras=paras)
                para_grid = setup.create_grid()

                crun_max = setup.nruns_total
                crun_pergeo = setup.ns * setup.nruns_logic_no_geo

                # Get number of files
                # Geo_mode "sort" (at least one LUT-file per Geo)

                n_ensembles_split, n_ensembles_geo = (1, 1) # initialize ensembles

                if self.geo_mode == "sort":
                    n_ensembles_geo = setup.nruns_logic_geo
                elif self.geo_mode == "no_geo":
                    n_ensembles_geo = 1

                # print("n_ensembles_geo: ", n_ensembles_geo)
                # print("max_per_file: ", max_per_file)

                if crun_pergeo <= max_per_file: # exactly one LUT-file per Geo
                    # max_per_file = crun_pergeo # lower max_per_file to LUT-members per Geo ## why? Causes trouble for ns < max_per_file
                    n_ensembles_split = 1
                else: # second split: several files per Geo
                    n_ensembles_split = (crun_pergeo - 1) // max_per_file + 1  # number of ensembles (=number of LUT-files to create)

                # print("max_per_file: ", max_per_file)
                # print("n_ensembles_split: ", n_ensembles_split)

                if not self.s2s == "default":
                    self.s2s_I = Spec2Sensor(sensor=self.s2s, nodat=self.nodat)
                    self.s2s_I.init_sensor()
                    nbands = self.s2s_I.n_wl_sensor
                else:
                    nbands = len(prospect_v.lambd)

                if build_step2 == 0 or (build_step2 > 0 and struct_ensemble == 0):
                    struct_ensemble = 0
                    # Meta-File:
                    if len(paras["tts"]) == 3:
                        tts_fl = np.linspace(start=setup.paras["tts"][0], stop=setup.paras["tts"][1],
                                             num=int(setup.paras["tts"][2]))
                        tts_str = [tts_fl.astype(str)[i] for i in range(len(tts_fl))]
                    elif len(paras["tts"]) == 1:
                        tts_str = [str(paras["tts"][0])]
                    else:
                        tts_str = ["NA"]

                    if len(paras["tto"]) == 3:
                        tto_fl = np.linspace(start=setup.paras["tto"][0], stop=setup.paras["tto"][1],
                                             num=int(setup.paras["tto"][2]))
                        tto_str = [tto_fl.astype(str)[i] for i in range(len(tto_fl))]
                    elif len(paras["tto"]) == 1:
                        tto_str = [str(paras["tto"][0])]
                    else:
                        tto_str = ["NA"]

                    if len(paras["psi"]) == 3:
                        psi_fl = np.linspace(start=setup.paras["psi"][0], stop=setup.paras["psi"][1],
                                             num=int(setup.paras["psi"][2]))
                        psi_str = [psi_fl.astype(str)[i] for i in range(len(psi_fl))]
                    elif len(paras["psi"]) == 1:
                        psi_str = [str(paras["psi"][0])]
                    else:
                        psi_str = ["NA"]

                    with open("%s_00meta.lut" % (LUT_dir+LUT_name), "w") as meta:
                        meta.write("name=%s\n" % LUT_name)
                        meta.write("n_total=%i\n" % setup.nruns_total)
                        meta.write("ns=%i\n" % setup.ns)
                        meta.write("lop_model=%s\n" % self.lop)
                        meta.write("canopy_architecture_model=%s\n" % self.canopy_arch)
                        meta.write("geo_mode=%s\n" % self.geo_mode)
                        meta.write("geo_ensembles=%i\n" % n_ensembles_geo)
                        meta.write("splits=%i\n" % n_ensembles_split)
                        meta.write("max_file_length=%i\n" % self.max_filelength)
                        meta.write("tts=")
                        for i in range(len(tts_str)):
                            meta.write(tts_str[i] + ";")
                        meta.write("\ntto=")
                        for i in range(len(tto_str)):
                            meta.write(tto_str[i] + ";")
                        meta.write("\npsi=")
                        for i in range(len(psi_str)):
                            meta.write(psi_str[i] + ";")
                        meta.write("\nmultiplication_factor=%i" % self.int_boost)
                        meta.write("\nparameters=")
                        for i in self.para_names:
                            meta.write(i + ";")
												
                if prgbar_widget:
                    prgbar_widget.gui.lblCaption_l.setText("Creating LUT")
                    QGis_app.processEvents()

                for geo_ensemble in range(n_ensembles_geo):

                    rest = crun_pergeo
                    for split in range(n_ensembles_split):

                        if rest >= max_per_file:
                            save_array = np.empty((nbands + npara, max_per_file))
                            nruns = max_per_file
                        else:
                            nruns = rest
                            save_array = np.empty((nbands + npara, rest))

                        for i in range(nruns):
                            run = geo_ensemble * crun_pergeo + split * max_per_file + i
                            if i % 100 == 0:
                                if prgbar_widget:
                                    if prgbar_widget.gui.lblCancel.text() == "-1":
                                        prgbar_widget.gui.lblCancel.setText("")
                                        prgbar_widget.gui.cmdCancel.setDisabled(False)
                                        raise ValueError("LUT creation cancelled!")

                                    prgbar_widget.gui.lblCaption_r.setText('File %s of %s' % (str(run), str(crun_max)))
                                    QGis_app.processEvents()
                                else:
                                    print("LUT ensemble struct #{:d} of {:d}; ensemble geo #{:d} of {:d}; split #{:d} of {:d}; total #{:d} of {:d}"
                                          .format(struct_ensemble, n_struct_ensembles-1, geo_ensemble,
                                                  n_ensembles_geo-1, split, n_ensembles_split-1, run+1, crun_max))
                                    # print("LUT ensemble struct #" + str(struct_ensemble) + " of " +
                                    #       str(n_struct_ensembles-1) + "; ensemble geo #" + str(geo_ensemble) + " of "
                                    #       + str(n_ensembles_geo-1) + "; split #" + str(split) + " of " +
                                    #       str(n_ensembles_split-1)) + "; total #" + str(run+1) + " of " + str(crun_max)
                            else:
                                if prgbar_widget:
                                    prgbar_widget.gui.prgBar.setValue(run*100/crun_max)
                                    QGis_app.processEvents()

                            save_array[npara:, i] = self.run_model(paras=dict(zip(self.para_names, para_grid[run, :])))
                            save_array[:npara, i] = para_grid[run, :]

                        rest -= max_per_file
                        np.save("%s_%i_%i_%i" % (LUT_dir+LUT_name, geo_ensemble, struct_ensemble, split), save_array)

                if prgbar_widget:
                    prgbar_widget.gui.lblCaption_r.setText('File %s of %s' % (str(crun_max), str(crun_max)))
                    prgbar_widget.gui.prgBar.setValue(100)
                    prgbar_widget.gui.close()

                if build_step2 == 0:
                    break # for regular LUT creation, this is the finish line
            if build_step2 == 0:
                break

    def initialize_single(self, **paras):
        self.soil = paras["soil"]
        if not self.s2s == "default":
            self.s2s_I = Spec2Sensor(sensor=self.s2s, nodat=self.nodat)
            self.s2s_I.init_sensor()

        # para_grid
        para_grid = np.empty(shape=(1, len(paras.keys())))
        for ikey, key in enumerate(self.para_names):
            para_grid[0, ikey] = paras[key]
        return self.run_model(paras=dict(zip(self.para_names, para_grid.T)))

    def run_model(self, paras):
        iModel = Call_model(soil=self.soil, paras=paras)
        if self.lop == "prospect4":
            iModel.call_prospect4()
        elif self.lop == "prospect5":
            iModel.call_prospect5()
        elif self.lop == "prospect5B":
            iModel.call_prospect5B()
        elif self.lop == "prospectD":
            iModel.call_prospectD()
        elif self.lop == "prospectCp":
            iModel.call_prospectCp()
        elif self.lop == "prospectPro":
            iModel.call_prospectPro()
        else:
            print("Unknown Prospect version. Try 'prospect4', 'prospect5', 'prospect5B' or 'prospectD' or ProspectPro")
            return

        if self.canopy_arch=="sail":
            result = iModel.call_4sail()*self.int_boost
        elif self.canopy_arch == "inform":
            result = iModel.call_inform() * self.int_boost
        else:
            result = iModel.prospect[:, :, 1]*self.int_boost

        if self.s2s == "default":
            return result
        else:
            return self.s2s_I.run_SRF(result)


def build_vectorized():
    # tts = [22.8, 22.8, 1] # HM
    # tto = [0.0, 32.0, 17] # HM
    # psi = [87.7, 92.3, 2] # HM
    #
    # tts = [10, 70, 7] # Future EM
    # tto = [0,  40, 5]
    # psi = [0, 180, 19]

    tts = [30]  # Test EM
    tto = [0]
    psi = [0]


    # Statistically distributed parameter [min, max, (mean, sigma)]
    # N = [1.0, 2.5, 1.5, 0.4] # bislang
    N = [1.0, 2.0]
    cab = [0.0, 80.0]
    # car = [0.0, 15.0] # bislang
    car = [0.0, 15.0]
    # anth = [0.0, 5.0] # bislang
    anth = [0.0, 2.0]
    # cbrown = [0.0, 1.0] # bislang
    cbrown = [0.1]
    cw = [0.001, 0.02]
    #cm = [0.0, 0.01, 0.004, 0.002]
    cm = [0.0]
    cp = [0.001, 0.0025, 0.0015, 0.0005]
    cbc = [0.001, 0.01]

    # LAI = [0.0, 8.0] # bislang
    LAI = [0.0, 7.0, 3.0, 2.0]
    # LIDF = [10.0, 85.0, 47.0, 25.0]  # bislang
    LIDF = [45]  # typeLIDF=1: 0: Plano, 1: Erecto, 2: Plagio, 3: Extremo, 4: Spherical, 5: Uniform
    # LIDF = [4]  # typeLIDF=1: 0: Plano, 1: Erecto, 2: Plagio, 3: Extremo, 4: Spherical, 5: Uniform
    typeLIDF = [2] # LIDF = ALIA
    # hspot = [0.0, 0.1] # bislang
    hspot = [0.01, 0.5]
    # psoil = [0.0, 1.0] # bislang
    psoil = [0.0, 1.0]

    LUT_dir = r"E:\Testdaten\Strathmann\LUT/"
    LUT_name = "LUT_ProSailPro_ALA45"
    ns = 5000
    int_boost = 1
    nodat = -999

    lop = "prospectPro"
    canopy_arch = "sail"
    # s2s = "HyMap"
    s2s = "default"
    # s2s = "default"
    soil = float(psoil[0])*Rsoil1+(1-float(psoil[0]))*Rsoil2
    # with open("E:\ECST_III\Processor\ML\Spectral\WW_Soil_2017.txt", 'r') as soil_file:
    #     soil = soil_file.readlines()
    # soil = [float(i.rstrip()) for i in soil]


    # model_I = Init_Model(lop=lop, canopy_arch=None, nodat=nodat, int_boost=int_boost, s2s=s2s)
    # model_I.initialize_vectorized(LUT_dir=LUT_dir, LUT_name=LUT_name, ns=ns, tts=tts, tto=tto, psi=psi, N=N,
    #                             cab=cab, cw=cw, cm=cm, LAI=LAI, LIDF=LIDF, typeLIDF=typeLIDF, hspot=hspot,
    #                             psoil=psoil, car=car, cbrown=cbrown, anth=anth, soil=soil, max_per_file=2000)

    model_I = Init_Model(lop=lop, canopy_arch=canopy_arch, nodat=nodat, int_boost=int_boost, s2s=s2s)
    model_I.initialize_vectorized(LUT_dir=LUT_dir, LUT_name=LUT_name, ns=ns, tts=tts, tto=tto, psi=psi, N=N,
                                cab=cab, cw=cw, cm=cm, cp=cp, cbc=cbc, LAI=LAI, LIDF=LIDF, typeLIDF=typeLIDF, hspot=hspot,
                                psoil=psoil, car=car, cbrown=cbrown, anth=anth, soil=soil, max_per_file=5000)

def example_multi_simple():
    npara = 1

    tts = [30] * npara
    tto = [10.0] * npara
    psi = [50.0] * npara

    # Statistically distributed parameter [min, max, (mean, sigma)]
    N = [1.5] * npara
    cab = [50.0] * npara
    car = [10.0] * npara
    anth = [3.0] * npara
    cbrown = [0.5] * npara
    cw = [0.03] * npara
    cm = [0.004] * npara

    cp = [0.001] * npara
    cbc = [0.002] * npara

    LAI = [4.0] * npara
    LIDF = [40.0] * npara  # typeLIDF=1: 0: Plano, 1: Erecto, 2: Plagio, 3: Extremo, 4: Spherical, 5: Uniform
    typeLIDF = [2] * npara
    hspot = [0.02] * npara
    psoil = [0.5] * npara
    int_boost = 10000
    nodat = -999

    LAIu = [3.0] * npara
    sd = [300] * npara
    h = [20] * npara
    cd = [3] * npara

    lop = "prospectPro"
    canopy_arch = "sail"
    s2s = "default"
    soil = None
    # with open("E:\ECST_III\Processor\ML\Spectral\WW_Soil_2017.txt", 'r') as soil_file:
    #     soil = soil_file.readlines()
    # soil = [float(i.rstrip()) for i in soil]

    model_I = Init_Model(lop=lop, canopy_arch=canopy_arch, nodat=nodat, int_boost=int_boost, s2s=s2s)

    # Mehrere Einzelruns
    model_I.initialize_multiple_simple(tts=tts, tto=tto, psi=psi, N=N, cp=cp, cbc=cbc,
                                cab=cab, cw=cw, cm=cm, LAI=LAI, LAIu=LAIu, LIDF=LIDF, typeLIDF=typeLIDF, hspot=hspot,
                                psoil=psoil, car=car, cbrown=cbrown, anth=anth, soil=soil, sd=sd, h=h, cd=cd)



if __name__ == '__main__':
    from lmuvegetationapps.dataSpec import Rsoil1, Rsoil2
    # results = []
    # for skyl in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
    #     res = example_single(skyl=skyl)
    #     results.append(res)
    #     plt.plot(range(len(res)), res, label="skyl = {:3.1f}".format(skyl))
    # plt.legend(frameon=False)
    # plt.savefig(r"D:\ECST_III\Papers\2017_ISD\5th submission RS\Figures\skyl_sensitivity.png", dpi=700)
    # plt.show()
    #

    build_vectorized()
    #example_multi_simple()