# -*- coding: utf-8 -*-
import numpy as np
import os
import gdal
from gdalconst import *
import struct
import time
import math
from matplotlib import pyplot as plt
from lmuvegetationapps.Sensor_Info import get_wl

class Spec2Sensor:
    
    def __init__(self, sensor, nodat):
        
        if sensor == "Sentinel2":
            self.sens_modus = 1
        elif sensor == "EnMAP":
            self.sens_modus = 2
        elif sensor == "Landsat8":
            self.sens_modus = 3
        elif sensor == "HyMap":
            self.sens_modus = 4
        else:
            exit("Unknown sensor type %s. Please try Sentinel2, EnMAP or Landsat8 instead!" % sensor)
            
        self.wl_sensor, self.fwhm = (None, None)
        self.wl = range(400,2501)
        self.n_wl = len(self.wl)
        self.nodat = nodat
            
    def init_sensor(self):

        path = os.path.dirname(os.path.realpath(__file__))
        self.wl_sensor, self.fwhm = get_wl(self.sens_modus)

        if self.sens_modus == 1:
            self.SRF_File = path + "/S2_srf.rsp"
            self.SRFnpy = path + "/S2_srf.npz"

        elif self.sens_modus == 2:
            self.SRF_File = path + "/E_srf.rsp"
            self.SRFnpy = path + "/E_srf.npz"
        
        elif self.sens_modus == 3:
            self.SRF_File = path + "/L8_srf.rsp"
            self.SRFnpy = path + "/L8_srf.npz"

        elif self.sens_modus == 4:
            self.SRFnpy = path + "/H_srf.npz"

        else:
            exit("unkown sensor type")

        self.n_wl_sensor = len(self.wl_sensor)
        SRF_File = np.load(self.SRFnpy) # turn this off, if SRF2npy is to be called
        self.srf = SRF_File['srf'] # turn this off, if SRF2npy is to be called
        self.srf_nbands = SRF_File['srf_nbands'] # turn this off, if SRF2npy is to be called

    def SRF2npy(self):  # creates a numpy array for any further use from K. Segl's .rsp files

        # Einlesen der SRFs (Spectral Response Functions)
        with open(self.SRF_File, 'r') as SRF:
            lines = SRF.readlines()

        # Get number of SRF-Bands per sensor band
        srf_nbands = lines[0].split(' ')
        srf_nbands = [int(srf_nbands[i]) for i in range(0,len(srf_nbands),2)]

        del lines[0] # remove Header
        srf = np.zeros((len(lines),(len(srf_nbands)*2))) # Erstellen der leeren Matrix für alle SRF-Werte

        for line_num in range(len(lines)):
            line_ex = lines[line_num].split(' ') # Aufspalten der Items pro Zeile in Einzel-Werte
            line_ex = [-999 if "NA" in line_ex[i] else float(line_ex[i]) for i in range(len(line_ex))] # Umwandlung Str->Float, bzw. Setzen von NoDataValue
            srf[line_num,:] = line_ex # Einfügen in die fertige SRF-Matrix

        srf = srf.reshape(len(lines),len(srf_nbands),2) # 1. Dim: SRF, 2. Dim: Sensor-Kanal, 3. Dimenson: [0] Wavelength und [1] SRF-Wert

        ### Angepasste SRF, mit Downgrade auf spektrale Auflösung des Input-Bilds (z.B. EnMAP)
        new_srf = np.copy(srf)
        new_srf.fill(-999)

        new_srf_nbands = []

        for sens_band in range(len(srf_nbands)): # für jeden Kanal im Zielsensor
            mask = [] # setze Masken-Liste zurück

            for sens_lambd in range(len(self.wl)): # für jede Wellenlänge des Input-Sensors

                for srf_lambd in range(srf_nbands[sens_band]): # jeder Wert der SRF für die Wellenlänge des Input-Sensors

                    if self.wl[sens_lambd] == int(srf[srf_lambd,sens_band,0]*1000): # Bei Treffer (SRF vorhanden: in nm!)

                        mask.append(srf_lambd) # den Wert zur Maske hinzufügen
                        break

            for i in range(len(mask)): # die Maske in die neue SRF-Matrix ausschütten
                new_srf[i,sens_band,:] = srf[mask[i],sens_band,:]

            new_srf_nbands.append(len(mask)) # Update der srf_nbands (wie viele SRF-Werte pro Kanal, hier: im Output-Sensor)

        np.savez(self.SRFnpy, srf_nbands=new_srf_nbands, srf=new_srf)

    def run_SRF(self, reflectance, int_factor_wl=1000, int_factor=1):

        hash_getwl = dict(zip(self.wl, list(range(self.n_wl))))
        spec_corr = np.zeros(shape=(reflectance.shape[0], self.n_wl_sensor))

        for sensor_band in range(self.n_wl_sensor):
            wfactor_include = []
            for srf_i in range(self.srf_nbands[sensor_band]):
                wlambda = int(self.srf[srf_i][sensor_band][0]*int_factor_wl)  # Wellenlänge des W-faktors, Umwandlung in nm und Integer
                if wlambda not in self.wl:
                    continue
                wfactor = self.srf[srf_i][sensor_band][1]  # Wichtungsfaktor
                wfactor_include.append(srf_i)
                spec_corr[:, sensor_band] += reflectance[:, hash_getwl[wlambda]] * wfactor  # Aufsummieren der korrigierten Spektren

            sum_wfactor = sum(self.srf[i,sensor_band,1] for i in wfactor_include)

            try:
                spec_corr[:,sensor_band] /= sum_wfactor
                # spec_corr[:,sensor_band] = ((spec_corr[:,sensor_band] / sum_wfactor) * int_factor).astype(np.int32) # for reflectances 0...1
            except ZeroDivisionError:
                spec_corr[:, sensor_band] = self.nodat

        if self.sens_modus == 1:
            spec_corr[:,10] = 0

        return spec_corr