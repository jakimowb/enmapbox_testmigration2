# -*- coding: utf-8 -*-

import os
import numpy as np
import time
from scipy.stats import truncnorm
from math import radians
import SAIL
import prospect
from Spec2Sensor_cl import Spec2Sensor

# Model class
class Call_model:

    def __init__(self,N,cab,cw,cm,LAI,typeLIDF,LIDF,hspot,psoil,tts,tto,psi,car=None,anth=None,cbrown=None):
        self.N = N
        self.cab = cab
        self.cw = cw
        self.cm = cm
        self.LAI = LAI
        self.typeLIDF = typeLIDF
        self.LIDF = LIDF
        self.hspot = hspot
        self.psoil = psoil
        self.tts = tts
        self.tto = tto
        self.psi = psi
        self.car = car
        self.anth = anth
        self.cbrown = cbrown

    def call_prospect4(self):
        prospect_instance = prospect.Prospect()
        self.prospect = prospect_instance.prospect_4(self.N, self.cab, self.cw, self.cm)

        return self.prospect

    def call_prospect5(self):
        prospect_instance = prospect.Prospect()
        self.prospect = prospect_instance.prospect_5(self.N, self.cab, self.car, self.cw, self.cm)

        return self.prospect

    def call_prospect5B(self):
        prospect_instance = prospect.Prospect()
        self.prospect = prospect_instance.prospect_5B(self.N, self.cab, self.car, self.cbrown, self.cw, self.cm)

        return self.prospect

    def call_prospectD(self):
        prospect_instance = prospect.Prospect()
        self.prospect = prospect_instance.prospect_D(self.N, self.cab, self.car, self.anth, self.cbrown, self.cw, self.cm)

        return self.prospect

    def call_4sail(self):

        try:
            self.prospect.any()
        except ValueError:
            raise ValueError("A leaf optical properties model needs to be run first!")

        sail_instance = SAIL.Sail(radians(self.tts), radians(self.tto), radians(self.psi)) # Create Instance of SAIL and initialize angles
        self.sail = sail_instance.Pro4sail(self.prospect[:,1], self.prospect[:,2], self.LIDF, self.typeLIDF, self.LAI, self.hspot, self.psoil) # call 4SAIL from the SAIL instance

        return self.sail

class Setup_multiple:

    def __init__(self, param_input, ns):
        self.whichlogicals = []
        self.nruns_logic_geo, self.nruns_logic_no_geo, self.nruns_logic_total = (1, 1, 1)
        self.npara = 15
        self.para_dict = {0: 'N', 1: 'cab', 2: 'cw', 3: 'cm', 4: 'LAI', 5: 'typeLIDF', 6: 'LIDF', 7: 'hspot',
                          8: 'psoil', 9: 'car', 10: 'anth', 11: 'cbrown', 12: 'tts', 13: 'tto', 14: 'psi'}
        self.param_input = param_input
        self.ns = int(ns)

        self.error_array = []

    def create_grid(self):
        #1 find logically distributed parameters
        for i in xrange(self.npara):
            if len(self.param_input[i]) == 3: # logical distr. = min, max, nsteps
                self.whichlogicals.append(i)

        #2 calculate nruns_logical for each logically distributed parameter
        self.nruns_logic = [int(self.param_input[i][2]) for i in self.whichlogicals]

        #3 calculate total nruns_logical
        for i in xrange(len(self.whichlogicals)):
            if self.whichlogicals[i] >= self.npara - 3:
                self.nruns_logic_geo *= self.nruns_logic[i] # contains only geometry
            else:
                self.nruns_logic_no_geo *= self.nruns_logic[i] # contains everything except geometry
        self.nruns_logic_total = self.nruns_logic_geo * self.nruns_logic_no_geo

        #4 Calculate total nruns
        self.nruns_total = int(self.nruns_logic_total * self.ns)

        #5 Create numpy array to hold all parameter constellations
        self.para_grid = np.empty(shape=(self.nruns_total, self.npara),dtype=np.float32)

        #6 Fill each parameter into numpy array
        k = 0 # iterator for logical order
        for i_para in xrange(self.npara):
            if len(self.param_input[i_para]) == 2: # uniform distribution
                self.para_grid[:,i_para] = self.uniform_distribution(para_name=self.para_dict[i_para],
                                                                     min=self.param_input[i_para][0],
                                                                     max=self.param_input[i_para][1],
                                                                     multiply=self.nruns_logic_total)

            elif len(self.param_input[i_para]) == 4: # gaussian distribution
                self.para_grid[:,i_para] = self.gauss_distribution(para_name=self.para_dict[i_para],
                                                                   min=self.param_input[i_para][0],
                                                                   max=self.param_input[i_para][1],
                                                                   mean=self.param_input[i_para][2],
                                                                   sigma=self.param_input[i_para][3],
                                                                   multiply=self.nruns_logic_total)

            elif len(self.param_input[i_para]) == 1: # fixed parameter
                self.para_grid[:,i_para] = np.tile(self.param_input[i_para][0],self.nruns_total)

            elif len(self.param_input[i_para]) == 3: # logically distributed parameter
                k += 1
                repeat = self.ns # initialize repeat with number of statistical distributions
                for i in xrange(k):
                    if not i==0: repeat *= self.nruns_logic[i-1]

                multiply = self.nruns_total / (repeat*self.nruns_logic[k-1]) # multiply can be calculated instead of iterated

                self.para_grid[:,i_para] = self.logical_distribution(para_name=self.para_dict[i_para],
                                                                     min=self.param_input[i_para][0],
                                                                     max=self.param_input[i_para][1],
                                                                     repeat=repeat,
                                                                     multiply=multiply,
                                                                     nsteps=self.param_input[i_para][2])

        return self.para_grid


    def fixed(self, para_name, value):
        return_list = np.linspace(start=value, stop=value, num=self.nruns_statistical)
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

    def initialize_multiple(self, LUT_dir, LUT_name, ns, tts, tto, psi, N, cab, cw, cm, LAI, LIDF, typeLIDF, hspot,
                            psoil, car=None, cbrown=None, anth=None, max_per_file=2000, testmode=0, prgbar_widget=None,
                            QGis_app=None):
        # Setup multiple runs with l size logical distribution & n size statistical distribution
        param_input = [N, cab, cw, cm, LAI, typeLIDF, LIDF, hspot, psoil, car, anth, cbrown, tts, tto, psi] # update: geometry comes lastly
        if len(tts) > 1 or len(tto) > 1 or len(psi) > 1:
            self.geo_mode = "sort" # LUT-Files are (firstly) sorted by geometry
        else:
            self.geo_mode = "no_geo"

        self.max_filelength = max_per_file
        npara = len(param_input)
        setup = Setup_multiple(param_input, ns=ns)
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

        if crun_pergeo <= max_per_file: # exactly one LUT-file per Geo
            max_per_file = crun_pergeo # lower max_per_file to LUT-members per Geo
            n_ensembles_split = 1
        else: # second split: several files per Geo
            n_ensembles_split = (crun_pergeo - 1) // max_per_file + 1  # number of ensembles (=number of LUT-files to create)


        if not self.s2s == "default":
            self.s2s_I = Spec2Sensor(sensor=self.s2s, nodat=self.nodat)
            self.s2s_I.init_sensor()
            nbands = self.s2s_I.n_wl_sensor
        else:
            nbands = len(prospect.lambd)

        if testmode == 1:
            start = time.time()
            for run in xrange(crun_max):
                self.run_model(parameters=para_grid[run, :])
            return time.time() - start

        # Meta-File:
        if len(tts) == 3:
            tts_fl = np.linspace(start=setup.param_input[-3][0], stop=setup.param_input[-3][1], num=int(setup.param_input[-3][2]))
            tts_str = [tts_fl.astype(str)[i] for i in xrange(len(tts_fl))]
        elif len(tts) == 1:
            tts_str = [str(tts[0])]
        else:
            tts_str = ["NA"]

        if len(tto) == 3:
            tto_fl = np.linspace(start=setup.param_input[-2][0], stop=setup.param_input[-2][1],
                                 num=int(setup.param_input[-2][2]))
            tto_str = [tto_fl.astype(str)[i] for i in xrange(len(tto_fl))]
        elif len(tto) == 1:
            tto_str = [str(tto[0])]
        else:
            tto_str = ["NA"]

        if len(psi) == 3:
            psi_fl = np.linspace(start=setup.param_input[-1][0], stop=setup.param_input[-1][1],
                                 num=int(setup.param_input[-1][2]))
            psi_str = [psi_fl.astype(str)[i] for i in xrange(len(psi_fl))]
        elif len(psi) == 1:
            psi_str = [str(psi[0])]
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
            for i in xrange(len(tts_str)):
                meta.write(tts_str[i] + ";")
            meta.write("\ntto=")
            for i in xrange(len(tto_str)):
                meta.write(tto_str[i] + ";")
            meta.write("\npsi=")
            for i in xrange(len(psi_str)):
                meta.write(psi_str[i] + ";")
            meta.write("\nmultiplication_factor=%i" % self.int_boost)

        if prgbar_widget:
            prgbar_widget.gui.lblCaption_l.setText("Creating LUT")
            QGis_app.processEvents()

        for geo_ensemble in xrange(n_ensembles_geo):

            rest = crun_pergeo
            for split in xrange(n_ensembles_split):

                if rest >= max_per_file:
                    save_array = np.empty((nbands + npara, max_per_file))
                    nruns = max_per_file
                else:
                    nruns = rest
                    save_array = np.empty((nbands + npara, rest))

                for i in xrange(nruns):
                    # run = (crun_max - rest) + i
                    run = geo_ensemble * crun_pergeo + split * max_per_file + i
                    if i % 100 == 0:
                        if prgbar_widget:
                            if prgbar_widget.gui.lblCancel.text()=="-1":
                                prgbar_widget.gui.lblCancel.setText("")
                                prgbar_widget.gui.cmdCancel.setDisabled(False)
                                raise ValueError("LUT creation cancelled!")

                            prgbar_widget.gui.lblCaption_r.setText('File %s of %s' % (str(run), str(crun_max)))
                            QGis_app.processEvents()
                        else:
                            print("LUT ensemble geo #" + str(geo_ensemble) + "; split #" + str(split) + " of " + str(crun_max))
                    else:
                        if prgbar_widget:
                            prgbar_widget.gui.prgBar.setValue(run*100/crun_max)
                            QGis_app.processEvents()

                    save_array[npara:, i] = self.run_model(parameters=para_grid[run, :])
                    save_array[:npara, i] = para_grid[run,:]

                rest -= max_per_file
                np.save("%s_%i_%i" % (LUT_dir+LUT_name, geo_ensemble, split), save_array)

        if prgbar_widget:
            prgbar_widget.gui.lblCaption_r.setText('File %s of %s' % (str(crun_max), str(crun_max)))
            prgbar_widget.gui.prgBar.setValue(100)
            prgbar_widget.gui.close()

    def initialize_single(self, N, cab, cw, cm, LAI, typeLIDF, LIDF, hspot, psoil, tts, tto, psi,
                   car, anth, cbrown):
        param_input = [N, cab, cw, cm, LAI, typeLIDF, LIDF, hspot, psoil, tts, tto, psi, car, anth, cbrown]

        if not self.s2s == "default":
            self.s2s_I = Spec2Sensor(sensor=self.s2s, nodat=self.nodat)
            self.s2s_I.init_sensor()
        return self.run_model(parameters=param_input)

    def run_model(self, parameters):
        iModel = Call_model(N=parameters[0],cab=parameters[1],cw=parameters[2],cm=parameters[3],
                            LAI=parameters[4],typeLIDF=parameters[5],LIDF=parameters[6],
                            hspot=parameters[7],psoil=parameters[8], tts=parameters[9],
                            tto=parameters[10],psi=parameters[11],car=parameters[12],
                            anth=parameters[13],cbrown=parameters[14])

        if self.lop=="prospect4": iModel.call_prospect4()
        elif self.lop=="prospect5": iModel.call_prospect5()
        elif self.lop=="prospect5B": iModel.call_prospect5B()
        elif self.lop=="prospectD": iModel.call_prospectD()
        else:
            print("Unknown Prospect version. Try 'prospect4', 'prospect5', 'prospect5B' or 'prospectD'")
            return

        if self.canopy_arch=="sail":
            result = iModel.call_4sail()*self.int_boost
        else:
            result = iModel.prospect[:,1]*self.int_boost

        if self.s2s == "default":
            return result
        else:
            return self.s2s_I.run_SRF(result)

def example_single():
    tts = 45.0
    tto = 0.0
    psi = 0.0

    N = 1.5
    cab = 55.0
    car = 10.0
    anth = 4.5
    cbrown = 0.1
    cw = 0.03
    cm = 0.0065
    LAI = 5.5
    hspot = 0.1
    psoil = 0.5
    LIDF = 60.0
    typeLIDF = 2

    lop = "prospectD"
    canopy_arch = "sail"
    s2s = "default"
    int_boost = 1000
    nodat = -999

    model_I = Init_Model(lop=lop, canopy_arch=canopy_arch, nodat=nodat, int_boost=int_boost, s2s=s2s)
    return model_I.initialize_single(tts=tts, tto=tto, psi=psi, N=N, cab=cab, cw=cw, cm=cm,
                                    LAI=LAI, LIDF=LIDF, typeLIDF=typeLIDF, hspot=hspot, psoil=psoil, car=car,
                                    cbrown=cbrown, anth=anth)

def example_multi():

    ### Free Part (values later parsed from GUI):
    # Logically distributed parameter: [min, max, nsteps]
    tts = [30, 55, 6]
    tto = [0.0, 30.0, 3]
    psi = [0.0, 180, 7]


    # Statistically distributed parameter [min, max, (mean, sigma)]
    N = [1.0, 2.2, 1.5, 0.3]
    cab = [0.0, 80.0, 45.0, 20.0]
    car = [0.0, 15.0]
    anth = [0.0, 5.0]
    cbrown = [0.0, 1.0]
    cw = [0.0, 0.1]
    cm = [0.0, 0.01]

    LAI = [0.0, 8.0, 4.5, 1.0]
    LIDF = [10.0, 85.0, 47.0, 25.0]  # typeLIDF=1: 0: Plano, 1: Erecto, 2: Plagio, 3: Extremo, 4: Spherical, 5: Uniform
    # typeLIDF=2: LIDF = ALIA
    hspot = [0.0, 0.1]
    psoil = [0.0, 1.0]

    # Fixed parameters
    typeLIDF = [2]  # 1: Beta, 2: Ellipsoidal

    LUT_dir = "D:/ECST_III/Processor/VegProc/results3/"
    LUT_name = "Martin_LUT_r4"
    ns = 20
    int_boost = 1000
    nodat = -999

    lop = "prospectD"
    canopy_arch = "sail"
    s2s = "default"

    model_I = Init_Model(lop=lop, canopy_arch=canopy_arch, nodat=nodat, int_boost=int_boost, s2s=s2s)
    model_I.initialize_multiple(LUT_dir=LUT_dir, LUT_name=LUT_name, ns=ns, tts=tts, tto=tto, psi=psi, N=N, cab=cab, cw=cw, cm=cm,
                                LAI=LAI, LIDF=LIDF, typeLIDF=typeLIDF, hspot=hspot, psoil=psoil, car=car, cbrown=cbrown,
                                anth=anth)

if __name__ == '__main__':
    # print(example_single() / 1000.0)
    # plt.plot(range(len(example_single())), example_single() / 1000.0)
    # plt.show()
    example_multi()




