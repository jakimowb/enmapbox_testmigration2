# -*- coding: utf-8 -*-
import numpy as np
import os
import gdal
import time
import math


class Spec2Sensor:
    
    def __init__(self, sensor, nodat):
        
        if sensor == "Sentinel2":
            self.sens_modus = 1
        elif sensor == "EnMAP":
            self.sens_modus = 2
        elif sensor == "Landsat8":
            self.sens_modus = 3
        else:
            exit("Unknown sensor type %s. Please try Sentinel2, EnMAP or Landsat8 instead!" % sensor)
            
        self.wl_sensor, self.fwhm = (None, None)
        self.wl = range(400,2501)
        self.n_wl = len(self.wl)
        self.nodat = nodat
            
    def init_sensor(self):

        path = os.path.dirname(os.path.realpath(__file__))

        if self.sens_modus == 1:
            self.SRF_File = path + "/S2_srf.rsp"
            self.SRFnpy = path + "/S2_srf.npz"
            self.wl_sensor = [442.25, 492.22, 560.31, 663.09, 703.96, 742.38, 781.72, 833.33, 865.82, 942.25,
            1373.67, 1609.43, 2193.89] # Zentrumswellenlängen von Sentinel-2
    
            self.fwhm = [18.00, 63.00, 34.00, 28.00, 14.00, 14.00, 18.00, 103.00, 22.00, 19.00,
            28.00, 87.00, 172.00] # Full Width Half Maxima von Sentinel-2
          
        elif self.sens_modus == 2:
            self.SRF_File = path + "/E_srf.rsp"
            self.SRFnpy = path + "/E_srf.npz"
            self.wl_sensor = [423.00, 429.00, 434.00, 440.00, 445.00, 450.00, 455.00, 460.00, 464.00, 469.00,
            474.00, 479.00, 484.00, 488.00, 493.00, 498.00, 503.00, 508.00, 513.00, 518.00,
            523.00, 528.00, 533.00, 538.00, 543.00, 548.00, 553.00, 559.00, 564.00, 569.00,
            575.00, 580.00, 586.00, 592.00, 597.00, 603.00, 609.00, 615.00, 621.00, 627.00,
            633.00, 639.00, 645.00, 652.00, 658.00, 665.00, 671.00, 678.00, 685.00, 691.00,
            698.00, 705.00, 712.00, 719.00, 726.00, 733.00, 740.00, 748.00, 755.00, 762.00,
            770.00, 777.00, 785.00, 793.00, 800.00, 808.00, 816.00, 823.00, 831.00, 839.00,
            847.00, 855.00, 863.00, 871.00, 879.00, 887.00, 895.00, 903.00, 911.00, 920.00,
            928.00, 936.00, 944.00, 952.00, 961.00, 969.00, 977.00, 985.00, 905.00, 914.00,
            924.00, 934.00, 944.00, 954.00, 965.00, 975.00, 986.00, 996.00, 1007.00, 1018.00,
            1029.00, 1040.00, 1051.00, 1063.00, 1074.00, 1085.00, 1097.00, 1109.00, 1120.00, 1132.00,
            1144.00, 1155.00, 1167.00, 1179.00, 1191.00, 1203.00, 1215.00, 1227.00, 1239.00, 1251.00,
            1263.00, 1275.00, 1287.00, 1299.00, 1311.00, 1323.00, 1335.00, 1347.00, 1359.00, 1370.00,
            1382.00, 1394.00, 1406.00, 1418.00, 1430.00, 1441.00, 1453.00, 1465.00, 1476.00, 1488.00,
            1499.00, 1511.00, 1522.00, 1534.00, 1545.00, 1556.00, 1568.00, 1579.00, 1590.00, 1601.00,
            1612.00, 1623.00, 1634.00, 1645.00, 1656.00, 1667.00, 1678.00, 1689.00, 1699.00, 1710.00,
            1721.00, 1731.00, 1742.00, 1752.00, 1762.00, 1773.00, 1783.00, 1793.00, 1804.00, 1814.00,
            1824.00, 1834.00, 1844.00, 1854.00, 1864.00, 1874.00, 1884.00, 1893.00, 1903.00, 1913.00,
            1922.00, 1932.00, 1942.00, 1951.00, 1961.00, 1970.00, 1979.00, 1989.00, 1998.00, 2007.00,
            2016.00, 2026.00, 2035.00, 2044.00, 2053.00, 2062.00, 2071.00, 2080.00, 2089.00, 2098.00,
            2106.00, 2115.00, 2124.00, 2133.00, 2141.00, 2150.00, 2159.00, 2167.00, 2176.00, 2184.00,
            2193.00, 2201.00, 2209.00, 2218.00, 2226.00, 2234.00, 2243.00, 2251.00, 2259.00, 2267.00,
            2275.00, 2283.00, 2291.00, 2299.00, 2307.00, 2315.00, 2323.00, 2331.00, 2339.00, 2347.00,
            2355.00, 2363.00, 2370.00, 2378.00, 2386.00, 2393.00, 2401.00, 2409.00, 2416.00, 2424.00,
            2431.00, 2439.00]
            self.fwhm = [6.00,   6.00,   6.00,   6.00,   6.00,   4.00,   4.00,   4.00,   4.00,   4.00,
            4.00,   4.00,   4.00,   4.00,   4.00,   4.00,   4.00,   4.00,   4.00,   4.00,
            6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,
            6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,
            6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   6.00,   8.00,   8.00,   8.00,
            8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,
            8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,
            8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,
            8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,  10.00,  10.00,
            10.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,
            12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  14.00,  14.00,
            14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,
            14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  14.00,
            14.00,  14.00,  14.00,  14.00,  14.00,  14.00,  12.00,  12.00,  12.00,  12.00,
            12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,
            12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,
            12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,  12.00,
            12.00,  12.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,
            10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,
            10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,
            10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,  10.00,
            10.00,  10.00,  10.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,
            8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,
            8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,   8.00,
            8.00,   8.00] # Full Width Half Maximum von EnMAP
        
        elif self.sens_modus == 3:
            self.SRF_File = path + "/L8_srf.rsp"
            self.SRFnpy = path + "/L8_srf.npz"
            self.wl_sensor = [442.96, 482.04, 561.41, 654.59, 864.67, 1373.43, 1608.86, 2200.73]
            self.fwhm = [16.00, 60.00, 57.00, 37.00, 28.00, 20.00, 85.00, 187.00]


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

    def run_SRF(self, reflectance):

        if np.any(np.equal(reflectance, None)): return [self.nodat] * self.n_wl_sensor
        hash_getspec = dict(zip(self.wl, reflectance))
        spec_corr = [0] * self.n_wl_sensor

        for sensor_band in range(self.n_wl_sensor):
            wfactor_include = []
            for srf_i in range(self.srf_nbands[sensor_band]):
                wlambda = int(self.srf[srf_i][sensor_band][0]*1000) # Wellenlänge des W-faktors, Umwandlung in nm und Integer
                wfactor = self.srf[srf_i][sensor_band][1] # Wichtungsfaktor
                wfactor_include.append(srf_i)
                spec_corr[sensor_band] += hash_getspec[wlambda]*wfactor # Aufsummieren der korrigierten Spektren

            sum_wfactor = sum(self.srf[i,sensor_band,1] for i in wfactor_include)

            try:
                spec_corr[sensor_band] /= sum_wfactor
            except ZeroDivisionError:
                spec_corr[sensor_band] = self.nodat

        if self.sens_modus == 1: spec_corr[10] = 0

        return spec_corr

if __name__ == '__main__':

    s2s = Spec2Sensor(sensor="EnMAP", nodat=-999)
    s2s.init_sensor()
    # s2s.SRF2npy()

    # spectrum = np.load("test_spec.npy")
    # s2s.run_SRF(reflectance=spectrum)