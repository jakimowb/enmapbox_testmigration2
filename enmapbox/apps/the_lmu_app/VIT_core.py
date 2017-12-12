# -*- coding: utf-8 -*-
# This script is the successor of AVI Agricultural Vegetation Index
# New: the user can choose how to select wavelengths (nearest neighbor, linear, IDW, Spline)

import numpy as np
from scipy.interpolate import interp1d, splrep
import gdal
from gdalconst import *
import struct

class VIT:
    def __init__(self, IT, nodat, IDW_exp=None):

        self.nodat = nodat # set no data value (0: in, 1: out)
        self.IT = IT # Interpolation type: 1: NN, 2: linear, 3: IDW, 4: Spline
        self.IDW_exp = IDW_exp # In case of IT = IDW, set power of IDW 

    def norm_diff1(self, a, b):  # Normalized Difference Index: ARRAYS as input
        return (a - b) / (a + b)

    def norm_diff2(self, a, b):  # Normalized Difference Index: BAND NUMBER as input
        return (self.ImageIn_matrix[:,:,a] - self.ImageIn_matrix[:,:,b]) / (self.ImageIn_matrix[:,:,a] + self.ImageIn_matrix[:,:,b])

    def division(self, a, b): # Simple Division: BAND NUMBER as input
        return self.ImageIn_matrix[:,:,a] / self.ImageIn_matrix[:,:,b]

    def toggle_indices(self, StructIndices, ChlIndices, CarIndices, WatIndices, DmIndices, FlIndices): # Prepare Indices

        # Boolean list for index groups
        self.StructIndices = StructIndices
        self.ChlIndices = ChlIndices
        self.CarIndices = CarIndices
        self.WatIndices = WatIndices
        self.DmIndices = DmIndices
        self.FlIndices = FlIndices

        # How many & which indices are calculated?
        CollapseIndices = StructIndices + ChlIndices + CarIndices + WatIndices + DmIndices + FlIndices
        self.n_indices = sum(CollapseIndices[i] for i in xrange(len(CollapseIndices)) if CollapseIndices[i] > 0)

        all_labels = ["hNDVI_Opp", "NDVI_Apr", "NDVI_Dat", "NDVI_Hab", "NDVI_Zar", "MCARI1", "MCARI2", "MSAVI", "MTVI1",
                      "MTVI2",
                      "OSAVI", "RDVI", "SPVI", "CSI1", "CSI2", "G", "GM1", "GM2", "gNDVI", "MCARI", "NPQI", "PRI",
                      "REIP1",
                      "REP", "SRchl", "SR705", "TCARI", "TVI", "VOG1", "VOG2", "ZTM", "SRa", "SRb", "SRb2",
                      "SRtot",
                      "PSSRa", "PSSRb", "LCI", "MLO", "ARI", "CRI", "CRI2", "PSSRc", "SIPI", "DSWI", "DWSI5",
                      "LMVI1", "LMVI2",
                      "MSI", "NDWI", "PWI", "SRWI", "SMIRVI", "CAI", "NDLI", "NDNI", "BGI", "BRI", "RGI", "SRPI",
                      "NPCI", "CUR", "LIC1", "LIC2", "LIC3"]

        self.labels = [all_labels[i] for i in xrange(len(all_labels)) if CollapseIndices[i] == 1]

        
        # List of wavelengths [nm] used for the indices. Append for new index!
        wl_list = [415, 420, 430, 435, 440, 445, 450, 500, 510, 528, 531, 547, 550, 554, 567, 645, 650, 665, 668, 670, 672, 675,
                   677, 680, 682, 683, 690, 695, 700, 701, 705, 708, 710, 715, 720, 724, 726, 734, 740, 745, 747, 750, 760, 774,
                   780, 800, 802, 820, 827, 831, 850, 858, 860, 900, 970, 983, 1094, 1205, 1240, 1510, 1600, 1657, 1660,
                   1680, 2015, 2090, 2106, 2195, 2208, 2210]

        self.loc_b(wl_list=wl_list) # Assign required wavelengths to sensor wavelengths

    def read_image(self, ImgIn, Convert_Refl=1.0):

        ### Reading the spectral image
        dataset = gdal.Open(ImgIn)
        if dataset is None: raise ValueError("Input Image not found!")
        nbands = dataset.RasterCount

        self.nodat[0] = dataset.GetMetadataItem('data_ignore_value', 'ENVI')
        string_chaos = dataset.GetMetadataItem('wavelength', 'ENVI')
        string_chaos = "".join(string_chaos.split())
        string_chaos = string_chaos.replace("{","")
        string_chaos = string_chaos.replace("}", "")
        string_chaos = string_chaos.split(",")

        if dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['nanometers', 'nm']:
            wave_convert = 1
        elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm']:
            wave_convert = 1000
        else:
            raise ValueError("No wavelength units provided in ENVI header file")

        self.wl = [float(item) * wave_convert for item in string_chaos]  # Wavelengths of the Image Input

        exclude = [] # initialize list for excluded bands
        # Check for EnMAP-Band anomaly
        if self.wl[89] < self.wl[88]:
            exclude = range(89, 98)
            self.wl = [self.wl[i] for i in xrange(len(self.wl)) if not i in exclude]

        self.n_wl = len(self.wl)  # number of wavelengths (=no of sensor bands)
        self.nrows = dataset.RasterYSize
        self.ncols = dataset.RasterXSize

        # Read data
        band_range = [i for i in range(nbands) if i not in exclude] # list of valid bands
        nbands_clean = len(band_range)

        # Create Image Input & Index Output Matrices
        ImageIn_matrix = np.zeros((self.nrows, self.ncols, nbands_clean),
                                  dtype=float)  # float is necessary for divisions

        for band_no, band_in in enumerate(band_range):
            band = dataset.GetRasterBand(band_in + 1)
            scancol = band.ReadRaster(0, 0, self.ncols, self.nrows, self.ncols, self.nrows,
                                      GDT_Float32)  # reads values as binary into single list
            # logic: ReadRaster(xoff, yoff, xsize, ysize, buf_xsize = None, buf_ysize = None, buf_type = None, band_list = None, Datatype)
            scancol = struct.unpack('f' * self.nrows * self.ncols, scancol)  # conversion from binary into float
            in_array = np.asarray(scancol, dtype=float)  # conversion into numpy array
            in_array = [in_array[i] * Convert_Refl if not in_array[i] == self.nodat[0] else in_array[i] for i in
                        xrange(len(in_array))]
            ImageIn_matrix[:,:,band_no] = np.reshape(in_array, (self.nrows, self.ncols))  # reshape into ImageIn_matrix (band per band)

        self.dict_band = dict(zip(self.wl, band_range)) # maps wavelengths to (valid) sensor bands
        self.mask = np.all(ImageIn_matrix == int(self.nodat[0]), axis=2)
        self.ImageIn_matrix = ImageIn_matrix

        return ImageIn_matrix

    def loc_b(self, wl_list): # creates a dict that zips each index-wavelength to a sensor band

        band_out = []

        for wl_in in wl_list:

            if self.IT == 1:  # nearest neighbor
                distances = [abs(wl_in - self.wl[i]) for i in
                             xrange(self.n_wl)]  # Get distances of input WL to all sensor WLs
                Val_target = self.dict_band[self.wl[distances.index(min(distances))]]

            elif self.IT == 2:  # linear
                if wl_in in self.wl:  # if wl_in is actually available, do not interpolate
                    Val_target = self.dict_band[wl_in]
                else:
                    distances = [wl_in - self.wl[i] for i in
                                 xrange(self.n_wl)]  # Get difference (+/-) values of input WL to all sensor WLs
                    try:  # if the input wavelength does not have a left AND right neighbor, perform Nearest Neighbor int instead
                        wl_left = distances.index(min([n for n in distances if n > 0]))
                        wl_right = distances.index(max([n for n in distances if n < 0]))
                        Ref_left = self.dict_band[self.wl[wl_left]]
                        Ref_right = self.dict_band[self.wl[wl_right]]

                        Val_target = (Ref_right - Ref_left) * (wl_in - self.wl[wl_left]) / (
                            self.wl[wl_right] - self.wl[wl_left]) + Ref_left
                    except:
                        distances = [abs(wl_in - self.wl[i]) for i in
                                     xrange(self.n_wl)]  # Get distances of input WL to all sensor WLs
                        Val_target = self.dict_band[self.wl[distances.index(min(distances))]]

            elif self.IT == 3:  # IDW
                if wl_in in self.wl:  # if wl_in is actually available, do not interpolate
                    Val_target = self.dict_band[wl_in]
                else:
                    distances = [wl_in - self.wl[i] for i in
                                 xrange(self.n_wl)]  # Get difference (+/-) values of input WL to all sensor WLs
                    try:  # if the input wavelength does not have a left AND right neighbor, perform Nearest Neighbor int instead
                        dist_left = min([n for n in distances if n > 0])
                        dist_right = max([n for n in distances if n < 0])
                        wl_left = distances.index(dist_left)
                        wl_right = distances.index(dist_right)

                        Ref_left = self.dict_band[self.wl[wl_left]]
                        Ref_right = self.dict_band[self.wl[wl_right]]
                        weights = [0] * 2
                        weights[0] = 1 / (dist_left ** self.IDW_exp)
                        weights[1] = 1 / (abs(dist_right) ** self.IDW_exp)

                        Val_target = (Ref_left * weights[0] + Ref_right * weights[1]) / sum(weights)
                    except:
                        distances = [abs(wl_in - self.wl[i]) for i in
                                     xrange(self.n_wl)]  # Get distances of input WL to all sensor WLs
                        Val_target = self.dict_band[self.wl[distances.index(min(distances))]]

            elif self.IT == 4:  # Spline
                if wl_in in self.wl:  # if wl_in is actually available, do not interpolate
                    Val_target = self.dict_band[wl_in]
                else:
                    if wl_in < self.wl[0]:
                        wl_in = self.wl[0]
                    elif wl_in > self.wl[-1]:
                        wl_in = self.wl[-1]

                    Val_target = self.spline(wl_in)

            # band_out contains the sensor-available wavelengths that are needed for the indices
            band_out.append(Val_target)
            band_out = [int(band_out[i]) for i in xrange(len(band_out))]

        self.dict_senswl = dict(zip(wl_list, band_out)) # maps index wavelengths with sensor bands

    def prgbar_process(self, index_no):
        if self.prg:
            if self.prg.gui.lblCancel.text() == "-1": # Cancel has been hit shortly before
                self.prg.gui.lblCancel.setText("")
                self.prg.gui.cmdCancel.setDisabled(False)
                raise ValueError("Calculation of Indices canceled")
            self.prg.gui.prgBar.setValue(index_no*100 // self.n_indices) # progress value is index-orientated
            self.QGis_app.processEvents() # mach ma neu

    def calculate_VIT(self, ImageIn_matrix, prg_widget=None, QGis_app=None):
        self.prg = prg_widget
        self.QGis_app = QGis_app

        old_settings = np.seterr(all='ignore') # override numpy-settings: math errors will be ignored (nodata will remain in matrix)

        temp_val = np.zeros(shape=(self.nrows, self.ncols, 11), dtype=np.float16)  # initialize temp values dumper
        index_no = 0 # intialize index_counter
        IndexOut_matrix = np.full(shape=(self.nrows, self.ncols, self.n_indices), fill_value=self.nodat[1], dtype=float)

        #         if self.IT == 4:
        #             self.spline = interp1d(self.wl, ImageIn_matrix[row, col, :], kind='cubic')  # Generate spline
        #
        #         if np.mean(ImageIn_matrix[row, col, :]) == self.nodat[0]:  # in case of NoData in the Image, skip Indices
        #             IndexOut_matrix[row, col, :] = self.nodat[1]
        #             continue

        if sum(self.StructIndices) > 0:
            if self.StructIndices[0] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[827], self.dict_senswl[668])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[1] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[900], self.dict_senswl[680])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[2] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[800], self.dict_senswl[680])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[3] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[800], self.dict_senswl[670])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[4] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[774], self.dict_senswl[677])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[5] == 1:
                temp_val[:,:,0] = 2.5 * (self.ImageIn_matrix[:,:,self.dict_senswl[800]] - self.ImageIn_matrix[:,:,self.dict_senswl[670]])
                temp_val[:,:,1] = 1.3 * (self.ImageIn_matrix[:,:,self.dict_senswl[800]] - self.ImageIn_matrix[:,:,self.dict_senswl[550]])
                IndexOut_matrix[:,:,index_no] = 1.2 * (temp_val[:,:,0] - temp_val[:,:,1])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[6] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[550]]
                temp_val[:,:,3] = np.sqrt(self.ImageIn_matrix[:, :, self.dict_senswl[680]])
                temp_val[:,:,4] = 1.5 * (2.5 * (temp_val[:,:,0] - temp_val[:,:,1]) - 1.3 * (temp_val[:,:,0] - temp_val[:,:,2]))
                temp_val[:,:,5] = (2 * temp_val[:,:,0] + 1) ** 2
                temp_val[:,:,6] = 6 * temp_val[:,:,0] - 5 * temp_val[:,:,3]
                temp_val[:,:,7] = np.sqrt(temp_val[:,:,5] - temp_val[:,:,6] - 0.5)
                IndexOut_matrix[:,:,index_no] = temp_val[:,:,4] / temp_val[:,:,7]
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[7] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = 2 * temp_val[:,:,0] + 1
                temp_val[:,:,3] = temp_val[:,:,2] ** 2
                temp_val[:,:,4] = 8 * (temp_val[:,:,0] - temp_val[:,:,1])
                temp_val[:,:,5] = np.sqrt(temp_val[:,:,3] - temp_val[:,:,4])
                IndexOut_matrix[:,:,index_no] = 0.5 * (temp_val[:,:,2] - temp_val[:,:,5])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[8] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[550]]
                temp_val[:,:,3] = 1.2 * (temp_val[:,:,0] - temp_val[:,:,2])
                temp_val[:,:,4] = 2.5 * (temp_val[:,:,1] - temp_val[:,:,2])
                IndexOut_matrix[:,:,index_no] = 1.2 * (temp_val[:,:,3] - temp_val[:,:,4])
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[9] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[550]]
                temp_val[:,:,3] = 1.2 * (temp_val[:,:,0] - temp_val[:,:,2])
                temp_val[:,:,4] = 2.5 * (temp_val[:,:,1] - temp_val[:,:,2])
                temp_val[:,:,5] = 1.5 * (temp_val[:,:,3] - temp_val[:,:,4])
                temp_val[:,:,6] = (2 * temp_val[:,:,0] + 1) ** 2
                temp_val[:,:,7] = 6 * temp_val[:,:,0]
                temp_val[:,:,8] = 5 * np.sqrt(temp_val[:,:,1])
                temp_val[:,:,9] = temp_val[:,:,7] - temp_val[:,:,8]
                temp_val[:,:,10] = np.sqrt(temp_val[:,:,6] - temp_val[:,:,9] - 0.5)
                IndexOut_matrix[:,:,index_no] = temp_val[:,:,5] / temp_val[:,:,10]
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[10] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = 1.16 * (temp_val[:,:,0] - temp_val[:,:,1])
                temp_val[:,:,3] = temp_val[:,:,0] + temp_val[:,:,1] + 0.16
                IndexOut_matrix[:,:,index_no] = temp_val[:,:,2] / temp_val[:,:,3]
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[11] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = temp_val[:,:,0] - temp_val[:,:,1]
                temp_val[:,:,3] = np.sqrt(temp_val[:,:,0] + temp_val[:,:,1])
                IndexOut_matrix[:,:,index_no] = temp_val[:,:,2] / temp_val[:,:,3]
                index_no += 1
                self.prgbar_process(index_no)
            if self.StructIndices[12] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[531]]
                temp_val[:,:,3] = 3.7 * (temp_val[:,:,0] - temp_val[:,:,1])
                temp_val[:,:,4] = 1.2 * (temp_val[:,:,2] - temp_val[:,:,1])
                IndexOut_matrix[:,:,index_no] = 0.4 * (temp_val[:,:,3] - temp_val[:,:,4])
                index_no += 1
                self.prgbar_process(index_no)

        if sum(self.ChlIndices) > 0:
            if self.ChlIndices[0] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[695], self.dict_senswl[420])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[1] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[695], self.dict_senswl[760])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[2] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[554], self.dict_senswl[677])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[3] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[750], self.dict_senswl[550])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[4] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[750], self.dict_senswl[700])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[5] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[750], self.dict_senswl[550])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[6] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[700]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[550]]
                IndexOut_matrix[:,:,index_no] = ((temp_val[:,:,0] - temp_val[:,:,1]) - 0.2 *
                                                 (temp_val[:,:,0] - temp_val[:,:,2])) * (temp_val[:,:,0] / temp_val[:,:,1])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[7] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[415], self.dict_senswl[435])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[8] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[528], self.dict_senswl[567])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[9] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[780]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[740]]
                temp_val[:,:,3] = self.ImageIn_matrix[:,:,self.dict_senswl[701]]
                IndexOut_matrix[:,:,index_no] = 700 + (740 / 700) * ((temp_val[:,:,0] / temp_val[:,:,1]) -
                                                temp_val[:,:,0]) / (temp_val[:,:,2] + temp_val[:,:,3])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[10] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[780]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[740]]
                temp_val[:,:,3] = self.ImageIn_matrix[:,:,self.dict_senswl[700]]
                IndexOut_matrix[:,:,index_no] = 700 + 40 * (((temp_val[:,:,1] + temp_val[:,:,0]) / 2 -
                                                temp_val[:,:,3]) / (temp_val[:,:,2] + temp_val[:,:,3]))
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[11] == 1:
                IndexOut_matrix[:,:,index_no] = self.ImageIn_matrix[:,:,self.dict_senswl[672]] / \
                                                (self.ImageIn_matrix[:,:,self.dict_senswl[550]] *
                                                 self.ImageIn_matrix[:,:,self.dict_senswl[708]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[12] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[750], self.dict_senswl[705])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[13] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[700]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[550]]
                IndexOut_matrix[:,:,index_no] = 3 * ((temp_val[:,:,0] - temp_val[:,:,1]) -
                                                0.2 * (temp_val[:,:,0] - temp_val[:,:,2])) * \
                                                (temp_val[:,:,0] / temp_val[:,:,1])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[14] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[750]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[670]]
                temp_val[:,:,2] = self.ImageIn_matrix[:,:,self.dict_senswl[550]]
                IndexOut_matrix[:,:,index_no] = 0.5 * (120 * (temp_val[:,:,0] - temp_val[:,:,2]) -
                                                       200 * (temp_val[:,:,1] - temp_val[:,:,2]))
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[15] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[740], self.dict_senswl[720])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[16] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[734] - self.dict_senswl[747],
                                                               self.dict_senswl[715] + self.dict_senswl[726])
                index_no += 1
                self.prgbar_process(index_no)
                # former ChlIndices16 is now skipped!

            if self.ChlIndices[17] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[750], self.dict_senswl[710])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[18] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[675], self.dict_senswl[700])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[19] == 1:
                IndexOut_matrix[:,:,index_no] = self.ImageIn_matrix[:,:,self.dict_senswl[672]] / \
                                                (self.ImageIn_matrix[:,:,self.dict_senswl[650]] *
                                                 self.ImageIn_matrix[:,:,self.dict_senswl[700]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[20] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[672], self.dict_senswl[708])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[21] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[760], self.dict_senswl[550])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[22] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[800], self.dict_senswl[675])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[23] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[800], self.dict_senswl[650])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[24] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[745], self.dict_senswl[724])
                index_no += 1
                self.prgbar_process(index_no)
            if self.ChlIndices[25] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[531], self.dict_senswl[645])
                index_no += 1
                self.prgbar_process(index_no)

        if sum(self.CarIndices) > 0:
            if self.CarIndices[0] == 1:
                IndexOut_matrix[:,:,index_no] = (1 / self.ImageIn_matrix[:,:,self.dict_senswl[550]]) \
                                                - (1 / self.ImageIn_matrix[:,:,self.dict_senswl[700]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.CarIndices[1] == 1:
                IndexOut_matrix[:,:,index_no] = (1 / self.ImageIn_matrix[:,:,self.dict_senswl[510]]) \
                                                  - (1 / self.ImageIn_matrix[:,:,self.dict_senswl[550]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.CarIndices[2] == 1:
                IndexOut_matrix[:,:,index_no] = (1 / self.ImageIn_matrix[:,:,self.dict_senswl[510]]) \
                                                  - (1 / self.ImageIn_matrix[:,:,self.dict_senswl[700]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.CarIndices[3] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[800], self.dict_senswl[500])
                index_no += 1
                self.prgbar_process(index_no)
            if self.CarIndices[4] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[800]]
                IndexOut_matrix[:,:,index_no] = (self.ImageIn_matrix[:,:,self.dict_senswl[445]] - temp_val[:,:,0]) / \
                                                (self.ImageIn_matrix[:,:,self.dict_senswl[680]] - temp_val[:,:,0])
                index_no += 1
                self.prgbar_process(index_no)
        if sum(self.WatIndices) > 0:
            if self.WatIndices[0] == 1:
                IndexOut_matrix[:,:,index_no] = (self.ImageIn_matrix[:,:,self.dict_senswl[802]] -
                                                 self.ImageIn_matrix[:,:,self.dict_senswl[547]]) / \
                                                (self.ImageIn_matrix[:,:,self.dict_senswl[1657]] +
                                                 self.ImageIn_matrix[:,:,self.dict_senswl[682]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[1] == 1:
                IndexOut_matrix[:,:,index_no] = (self.ImageIn_matrix[:,:,self.dict_senswl[800]] +
                                                   self.ImageIn_matrix[:,:,self.dict_senswl[550]]) / \
                                                  (self.ImageIn_matrix[:,:,self.dict_senswl[1660]] +
                                                   self.ImageIn_matrix[:,:,self.dict_senswl[680]])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[2] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[1094], self.dict_senswl[983])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[3] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[1094], self.dict_senswl[1205])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[4] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[1600], self.dict_senswl[820])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[5] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[860], self.dict_senswl[1240])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[6] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[970], self.dict_senswl[900])
                index_no += 1
                self.prgbar_process(index_no)
            if self.WatIndices[7] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[858], self.dict_senswl[1240])
                index_no += 1
                self.prgbar_process(index_no)

        if sum(self.DmIndices) > 0:
            if self.DmIndices[0] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[2090]]
                IndexOut_matrix[:,:,index_no] = 37.27 * (self.ImageIn_matrix[:,:,self.dict_senswl[2210]] + temp_val[:,:,0]) + 26.27 * \
                                                        (self.ImageIn_matrix[:,:,self.dict_senswl[2208]] - temp_val[:,:,0]) - 0.57
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[1] == 1:
                IndexOut_matrix[:,:,index_no] = 0.5 * (
                    self.ImageIn_matrix[:,:,self.dict_senswl[2015]] + self.ImageIn_matrix[:,:,self.dict_senswl[2195]]) - \
                                                self.ImageIn_matrix[:,:,self.dict_senswl[2106]]
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[2] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[1094]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[1205]]
                IndexOut_matrix[:,:,index_no] = self.norm_diff1((1 / np.log10(temp_val[:,:,0])),
                                                                (1 / np.log10(temp_val[:,:,1])))
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[3] == 1:
                temp_val[:,:,0] = self.ImageIn_matrix[:,:,self.dict_senswl[1510]]
                temp_val[:,:,1] = self.ImageIn_matrix[:,:,self.dict_senswl[1680]]
                IndexOut_matrix[:,:,index_no] = self.norm_diff1((1 / np.log10(temp_val[:,:,0])),
                                                                (1 / np.log10(temp_val[:,:,1])))
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[4] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[450], self.dict_senswl[550])
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[5] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[450], self.dict_senswl[690])
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[6] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[690], self.dict_senswl[550])
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[7] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[430], self.dict_senswl[680])
                index_no += 1
                self.prgbar_process(index_no)
            if self.DmIndices[8] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[680], self.dict_senswl[430])
                index_no += 1
                self.prgbar_process(index_no)

        if sum(self.FlIndices) > 0:
            if self.FlIndices[0] == 1:
                IndexOut_matrix[:,:,index_no] = (self.ImageIn_matrix[:,:,self.dict_senswl[675]] *
                                                 self.ImageIn_matrix[:,:,self.dict_senswl[550]]) / \
                                                (self.ImageIn_matrix[:,:,self.dict_senswl[683]] ** 2)
                index_no += 1
                self.prgbar_process(index_no)
            if self.FlIndices[1] == 1:
                IndexOut_matrix[:,:,index_no] = self.norm_diff2(self.dict_senswl[800], self.dict_senswl[680])
                index_no += 1
                self.prgbar_process(index_no)
            if self.FlIndices[2] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[440], self.dict_senswl[690])
                index_no += 1
                self.prgbar_process(index_no)
            if self.FlIndices[3] == 1:
                IndexOut_matrix[:,:,index_no] = self.division(self.dict_senswl[440], self.dict_senswl[740])
                index_no += 1
                self.prgbar_process(index_no)

        np.seterr(**old_settings) # restore old numpy settings
        IndexOut_matrix[np.logical_or(np.isnan(IndexOut_matrix), np.isinf(IndexOut_matrix))] = self.nodat[1] # change nan and inf into nodat

        self.mask = np.dstack([self.mask] * self.n_indices) # expand mask to match the shape of the output
        IndexOut_matrix[self.mask == True] = self.nodat[1] # change masked no data values of input to nodat

        return IndexOut_matrix

    def write_out(self, IndexOut_matrix, OutDir, OutFilename, OutExtension, OutSingle):

        driver = gdal.GetDriverByName('ENVI')
        Hdr_deposit = [''] * 2

        if not OutSingle == 1:  # Output to individual files
            for i in xrange(self.n_indices):
                destination = driver.Create(OutDir + OutFilename + '_' + self.labels[i] + OutExtension,
                                            self.ncols, self.nrows, 1,
                                            gdal.GDT_Float32)  # Create output file: Name, Spalten, Reihen, Kanäle, Datentyp
                b = destination.GetRasterBand(1)
                b.SetDescription(self.labels[i])
                b.WriteArray(IndexOut_matrix[:,:,i])
                destination.SetMetadataItem('data ignore value', str(self.nodat[1]), 'ENVI')

        else:  # Output to single file
            try:
                destination = driver.Create(OutDir + OutFilename + '.bsq', self.ncols,
                                            self.nrows, self.n_indices,
                                            gdal.GDT_Float32)  # Create output file: Name, Spalten, Reihen, Kanäle, Datentyp
                for i in xrange(self.n_indices):
                    b = destination.GetRasterBand(i + 1)
                    b.SetDescription(self.labels[i])
                    b.WriteArray(IndexOut_matrix[:,:,i])

                destination.SetMetadataItem('data ignore value', str(self.nodat[1]), 'ENVI')
            except:
                raise ValueError
        dataset = None
        destination = None
