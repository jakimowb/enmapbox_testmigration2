# -*- coding: utf-8 -*-

import numpy as np
import time
import gdal
from gdalconst import *
from osgeo import gdal
import struct
import os
from lmuvegetationapps.Sensor_Info import get_wl
from hubflow.core import *
from matplotlib import pyplot as plt

class RTM_Inversion:

    def __init__(self):
        self.error = None
        self.ctype = 0
        self.nbfits = 0
        self.noisetype = 0
        self.noiselevel = 0
        self.nodat = [0]*3 # 0: input image, 1: geometry image, 2: output image
        self.exclude_bands, self.exclude_bands_model = (None, None)
        self.wl_sensor = None
        self.fwhm_sensor = None
        self.wl_compare = None
        self.n_wl = None
        self.offset = 0
        self.image = None
        self.image_out = None
        self.npara = None
        self.conversion_factor = None

        self.nrows, self.ncols, self.nbands = (None, None, None)
        self.geometry_matrix = None
        self.whichLUT = None
        self.LUT_base = None
        self.exclude_pixels = None
        self.whichpara = None

        # LUT:
        self.ntotal = None
        self.ns = None
        self.tts_LUT, self.tto_LUT, self.psi_LUT, self.nangles_LUT = (None, None, None, None)

        # self.para_dict = {0: 'N', 1: 'cab', 2: 'car', 3: 'cm', 4: 'LAI', 5: 'typeLIDF', 6: 'LIDF', 7: 'hspot',
        #                   8: 'psoil', 9: 'car', 10: 'anth', 11: 'cbrown', 12: 'tts', 13: 'tto', 14: 'psi', }
        self.para_dict = {'N': 0, 'cab': 1, 'car': 2, 'anth': 3, 'cw': 4, 'cbrown': 5, 'cm': 6, 'cp': 7, 'ccl': 8,
                          'LAI': 9, 'typeLIDF': 10, 'LIDF': 11, 'hspot': 12, 'psoil': 13, 'tts': 14, 'tto': 15,
                          'psi': 16, 'LAIu': 17, 'cd': 18, 'sd': 19, 'h': 20}
        self.para_names = self.para_dict.keys()
        self.max_npara = len(self.para_dict)
        #print(self.max_npara)

    def read_image(self, image, nodat, dtype=np.float16, exclude_bands=[]):

        dataset = gdal.Open(image)
        nbands = dataset.RasterCount
        nrows = dataset.RasterYSize
        ncols = dataset.RasterXSize

        in_matrix = np.zeros((nrows, ncols, nbands-len(exclude_bands)))
        skip = 0

        for band_no in range(nbands):
            if band_no in exclude_bands:
                skip += 1
                continue
            band = dataset.GetRasterBand(band_no+1)
            scancol = band.ReadRaster(0,0, ncols, nrows, ncols, nrows, GDT_Float32)
            in_matrix[:, :, band_no-skip] = np.reshape(np.asarray(struct.unpack('f' * nrows * ncols, scancol),
                                                             dtype=dtype), (nrows, ncols))
        return nrows, ncols, nbands, in_matrix

    def get_geometry(self, geo_fixed, geo_image=None):

        #0: Generate geometry matrix
        self.geometry_matrix = np.empty(shape=(self.nrows, self.ncols, 3))
        self.geometry_matrix.fill(self.nodat[2])

        #1: import geometry-file from read_image or

        if geo_image:
            geometry_raw = self.read_image(geo_image, nodat=self.nodat[1])
            if not geometry_raw[0] == self.nrows or not geometry_raw[1] == self.ncols:
                raise ValueError("Geometry image and Sensor image do not match")
            self.geometry_matrix = geometry_raw[3]

        if geo_fixed:
            if not any(geo_fixed[i] is None for i in range(len(geo_fixed))):
                try:
                    for angle in range(3):
                        self.geometry_matrix[:,:,angle] = geo_fixed[angle]
                except: raise ValueError("Problem with reading fixed angles")

        self.whichLUT = np.zeros(shape=(self.nrows, self.ncols),dtype=np.int16)

        if self.geo_mode == "sort":
            for row in range(self.nrows):
                for col in range(self.ncols):
                    angles = []
                    angles.append(np.argmin(abs(self.geometry_matrix[row, col, 0] - self.tts_LUT)))  # tts
                    angles.append(np.argmin(abs(self.geometry_matrix[row, col, 1] - self.tto_LUT)))  # tto
                    angles.append(np.argmin(abs(self.geometry_matrix[row, col, 2] - self.psi_LUT)))  # psi
                    self.whichLUT[row, col] = angles[2]*self.nangles_LUT[1]*self.nangles_LUT[0] + angles[1]*self.nangles_LUT[0] + angles[0]
        else:
            self.whichLUT[:, :] = 0 # take first available (there should be no more than 1 anyway)
            self.geometry_matrix[:, :, :] = 911 # a value that is unlikely to be chosen for no data. In case of geo_mode != 'sort', the matrix is unused

    def add_noise(self, Ref_list, type, sigma):
        n_entries = len(Ref_list)
        sigma_c = (sigma/100) * self.conversion_factor  # sigma converted

        if type == 0: # no noise
            return Ref_list

        elif type == 1:  # additive noise
            # Ref_noisy = [Ref_list[i] + np.random.normal(loc=0.0, scale=sigma_c) for i in range(n_entries)]
            Ref_noisy = np.random.normal(loc=0.0, scale=sigma_c, size=n_entries) + Ref_list

        elif type == 2:  # multiplicative noise
            # Ref_noisy = [Ref_list[i] * (1 + np.random.normal(loc=0.0, scale=sigma / 100)) for i in range(n_entries)]
            Ref_noisy = (1 + np.random.normal(loc=0.0, scale=sigma/100, size=n_entries)) * Ref_list

        elif type == 3:  # inverse multiplicative noise
            # Ref_noisy = [1 - ((1 - Ref_list[i]) * (1 + np.random.normal(loc=0.0, scale=sigma / 100))) for i in
            #              range(n_entries)]
            Ref_noisy = 1 - (1 - Ref_list) * (1 + np.random.normal(loc=0.0, scale=sigma/100))

        # Ref_noisy = [Ref_noisy[i] if Ref_noisy[i] > 0.0 else 0.1 for i in range(n_entries)]

        Ref_noisy[Ref_noisy<0] = 0
        return Ref_noisy

    def cost_fun(self, image_Ref, model_Ref, type):

        if type == 1: # RMSE
            delta = np.linalg.norm(model_Ref - image_Ref) / np.sqrt(self.n_wl)  # Numpy-Solution für RMSE (fast)
        elif type == 2: # MAE
            delta = sum(abs(image_Ref - model_Ref))
        elif type == 3: # mNSE
            delta = 1.0 - ((sum(abs(image_Ref - model_Ref))) /
                           (sum(abs(image_Ref - (np.mean(image_Ref))))))
        else:
            exit("wrong cost function type. Expected 1, 2 or 3; got %i instead" %type)

        return delta

    def inversion_setup(self, image, image_out, LUT_path, ctype, nbfits, nbfits_type, noisetype, noiselevel,
                        exclude_bands, out_mode, geo_image=None, geo_fixed=[None]*3, sensor=2,
                        nodat=[None]*3, mask_image=None):

        self.ctype = ctype
        self.nbfits = nbfits
        self.nbfits_type = nbfits_type
        self.noisetype = noisetype
        self.noiselevel = noiselevel
        self.exclude_bands = exclude_bands

        self.nodat = nodat
        self.out_mode = out_mode


        self.image_out = image_out
        self.get_meta(LUT_path)
        self.sensor_setup(sensor=sensor)
        self.nrows, self.ncols, self.nbands, self.image = self.read_image(image=image, nodat=nodat[1], dtype=np.float16,
                                                                          exclude_bands=self.exclude_bands)
        if mask_image is None:
            self.exclude_pixels = []
        else:
            self.masking(img=mask_image)
            if self.exclude_pixels is None: # Error within self.masking -> self.exclude_pixels is still None
                return self.error

        self.npara = len(self.whichpara)
        self.get_geometry(geo_image=geo_image, geo_fixed=geo_fixed)  # generate list of LUT-names for each pixel

        self.out_matrix = np.empty(shape=(self.nrows, self.ncols, len(self.whichpara)))

    def masking(self, img):
        mask = self.read_image(img, nodat=-999)
        if not self.nrows == mask[0] or not self.ncols == mask[1]:
            self.error = "Input Image and Mask Image must have same dimensions! Input Image has [%ir, %ic], " \
                         "Mask Image has [%ir, %ic]" % (self.nrows, self.ncols, mask[0], mask[1])
            return
        self.exclude_pixels = np.squeeze(mask[3], axis=2) # turns [r,c,1] (1 band) into [r,c]

    def sensor_setup(self, sensor):
        self.wl_sensor, self.fwhm_sensor = get_wl(sensor=sensor)

        if sensor == 1: # ASD
            self.offset = 400 - self.wl_sensor[0]  # 400nm as first wavelength in the PROSAIL model family
            self.exclude_bands = list(range(0, 51)) + list(range(1009, 1129)) + \
                            list(range(1371, 1650)) + list(range(2050, 2151))
            # self.exclude_bands = range(0, self.offset) + range(1009, 1129) + range(1371, 1650) # 350-400nm, 1359-1479nm, 1721-200nm
            self.exclude_bands_model = list(range(self.max_npara)) + [((i - self.offset)) + self.max_npara for i in self.exclude_bands[self.offset:]]
        elif sensor == 2: # EnMAP
            # self.exclude_bands = range(78, 88) + range(128, 138) + range(161, 189) # Überlappung VNIR, Water1, Water2
            self.exclude_bands_model = list(range(self.max_npara)) + [i + self.max_npara for i in self.exclude_bands]
        elif sensor == 3: # Sentinel-2
            # self.exclude_bands = [10]
            self.exclude_bands_model = list(range(self.max_npara)) + [i + self.max_npara for i in self.exclude_bands]

        self.wl_compare = [self.wl_sensor[i] for i in range(len(self.wl_sensor)) if i not in self.exclude_bands]
        self.n_wl = len(self.wl_compare)

    def get_meta(self, file):

        with open(file, 'r') as metafile:
            metacontent = metafile.readlines()
            metacontent = [line.rstrip('\n') for line in metacontent]

        self.LUT_base = os.path.dirname(file) + "/" + metacontent[0].split("=")[1]
        self.ntotal = int(metacontent[1].split("=")[1])
        self.ns = int(metacontent[2].split("=")[1])
        self.lop = metacontent[3].split("=")[1]
        self.canopy_arch = metacontent[4].split("=")[1]
        self.geo_mode = metacontent[5].split("=")[1]
        self.geo_ensembles = int(metacontent[6].split("=")[1])
        self.splits = int(metacontent[7].split("=")[1])
        self.max_file_length = int(metacontent[8].split("=")[1])
        temp = metacontent[9].split("=")[1].split(";")
        if not "NA" in temp:
            self.tts_LUT = [float(angle) for angle in temp[:-1]]
        else:
            self.tts_LUT = []
        temp = metacontent[10].split("=")[1].split(";")
        if not "NA" in temp:
            self.tto_LUT = [float(angle) for angle in temp[:-1]]
        else:
            self.tto_LUT = []
        temp = metacontent[11].split("=")[1].split(";")
        if not "NA" in temp:
            self.psi_LUT = [float(angle) for angle in temp[:-1]]
        else:
            self.psi_LUT = []
        self.conversion_factor = int(metacontent[12].split("=")[1])
        self.para_names = metacontent[13].split("=")[1].split(";")[:-1]

        self.nangles_LUT = [len(self.tts_LUT), len(self.tto_LUT), len(self.psi_LUT)]
        if self.nbfits_type == "rel":
            self.nbfits = int(self.ns * (self.nbfits/100.0))

        self.whichpara = []
        if self.lop == "prospect4":
            self.whichpara.append(["N", "cab", "cw", "cm"])
        elif self.lop == "prospect5":
            self.whichpara.append(["N", "cab", "cw", "cm", "car"])
        elif self.lop == "prospect5B":
            self.whichpara.append(["N", "cab", "cw", "cm", "car", "cbrown"])
        elif self.lop == "prospectD":
            self.whichpara.append(["N", "cab", "cw", "cm", "car", "cbrown", "anth"])
        elif self.lop == "prospectCp":
            self.whichpara.append(["N", "cab", "cw", "cm", "car", "cbrown", "anth", "cp", "ccl"])
        if self.canopy_arch == "sail":
            self.whichpara.append(["LAI", "typeLIDF", "LIDF", "hspot", "psoil", "tts", "tto", "psi"])
        if self.canopy_arch == "inform":
            self.whichpara.append(['LAI', 'typeLIDF', 'LIDF', 'hspot', 'psoil', 'tts', 'tto', 'psi', 
                                   'LAIu', 'cd', 'sd', 'h'])
        self.whichpara = [item for sublist in self.whichpara for item in sublist] # flatten list back
        self.whichpara_num = [self.para_dict[para_key] for para_key in self.whichpara]
        #print(self.whichpara_num)
        #print(self.whichpara)

    def visualize(self, image_Ref, model_Ref):

        # cmap = plt.get_cmap('gnuplot')
        # colors = [cmap(i) for i in np.linspace(0.0, 0.9, len(in_raster))
        # fig = plt.figure(figsize=(10, 5))
        plt.plot(image_Ref, color='b')
        plt.show()
        plt.plot(model_Ref, color='r')
        # plt.plot(all_x + 450 + r_diff, all_y, 'k+')
        # plt.xlabel('Wavelength [nm]')
        # plt.ylabel('Reflectance [-]')
        # plt.xlim(350, 2500)
        # plt.xticks(np.arange(400, 2500, 200))
        #plt.ylim(0, 0.7)
        plt.show()
        # 1: get wl and array with reflectances
        # 2: 1dim array: plot single; 2dim: plot multiple
        pass

    def run_inversion(self, prg_widget=None, QGis_app=None):

        pix_total = self.nrows * self.ncols
        nbands_valid = len(self.image[0,0,:])

        for r in range(self.nrows):
            for c in range(self.ncols):

                pix_current = r*self.ncols + c + 1

                # Check if process shall be aborted
                if prg_widget:
                    if prg_widget.gui.lblCancel.text() == "-1":
                        prg_widget.gui.lblCancel.setText("")
                        prg_widget.gui.cmdCancel.setDisabled(False)
                        raise ValueError("Inversion canceled")

                # Check if Pixel shall be excluded
                if len(self.exclude_pixels) > 0 and self.exclude_pixels[r,c] < 1:
                    self.out_matrix[r,c,:] = self.nodat[2]
                    continue

                # Check if Pixel is NoData or Geometry is not available
                if all(self.image[r, c, j] == self.nodat[0] for j in range(nbands_valid)) or \
                        any(self.geometry_matrix[r, c, i] == self.nodat[0] for i in range(3)):
                    self.out_matrix[r,c,:] = self.nodat[2]
                    # print "skipping: ", r, c
                    continue

                estimates = np.zeros(self.ns)
                lut = np.hstack(np.load(self.LUT_base + "_" + str(self.whichLUT[r, c]) + "_" + str(split) + ".npy")
                                for split in range(self.splits))  # load all splits of the current geo_ensembles

                LUT_params = lut[self.whichpara_num, :]  # extract parameters

                lut = np.delete(lut, self.exclude_bands_model, axis=0)  # delete exclude_bands_model - members

                for run in range(self.ns):

                    #print(self.ns)
                    if np.sum(lut[:, run]) < 1: continue
                    estimates[run] = self.cost_fun(self.image[r, c, :],
                                                   self.add_noise(Ref_list=lut[:,run], type=self.noisetype, sigma=self.noiselevel),
                                                   type=self.ctype)
                L1_subset = np.argpartition(estimates, self.nbfits)[0:self.nbfits]  # get n best performing LUT-entries
                #if r==0 and c==0:
                    #for s in L1_subset:
                        #self.visualize(self.image[r, c, :],
                         #       self.add_noise(Ref_list=lut[:, s], type=self.noisetype, sigma=self.noiselevel))
                L1_subset = L1_subset[np.argsort(estimates[L1_subset])]
                result = np.median([LUT_params[:, i] for i in L1_subset], axis=0)

                self.out_matrix[r, c, :] = result
                #print(self.out_matrix.shape)
                if prg_widget:
                    prg_widget.gui.lblCaption_r.setText('Inverting pixel #%i of %i' % (pix_current, pix_total))
                    prg_widget.gui.prgBar.setValue(pix_current*100 // pix_total)
                    QGis_app.processEvents()



    def write_image(self):
        driver = gdal.GetDriverByName('ENVI')

        if self.out_mode == "single":

            #try:
            out_matrix = np.transpose(self.out_matrix, [2, 0, 1])
            #print(out_matrix.shape)
            output = Raster.fromArray(array=out_matrix, filename=self.image_out)

            output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

            for i, band in enumerate(output.dataset().bands()):
                band.setDescription(self.whichpara[i])
                band.setNoDataValue(self.nodat[1])

            # destination = driver.Create(self.image_out, self.ncols, self.nrows, self.npara, gdal.GDT_Float32)
            # for i, para_key in enumerate(self.whichpara):
            #     band = destination.GetRasterBand(i+1)
            #     band.SetDescription(para_key)
            #     band.WriteArray(self.out_matrix[:, :, i])
            # destination.SetMetadataItem('data ignore value', str(self.nodat[2]), 'ENVI')

        elif self.out_mode == "individual":
            for i, para_key in enumerate(self.whichpara):
                out_matrix = np.transpose(self.out_matrix, [2, 0, 1])
                out_array = np.zeros((1, self.nrows, self.ncols))
                out_array[0, :, :] = out_matrix[i, :, :]
                output = Raster.fromArray(array=out_array, filename=os.path.splitext(
                    self.image_out)[0] + "_" + para_key + os.path.splitext(self.image_out)[1])
                output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')
                for band in output.dataset().bands():
                    #print(i)
                    band.setDescription(para_key)
                    band.setNoDataValue(self.nodat[1])

        
def example():
    ImageIn = "U:/ECST_III/EnMAP_Workshop/Berlin 2019/Data/spectra/WW_0_2015_2017_2018_new_AVG.bsq"
    ResultsOut = "Z:\Matthias\LUT_test/results.bsq"
    #GeometryIn = "D:/ECST_II/Cope_BroNaVI/Felddaten/Parameter/Geometry_DJ_w.bsq"
    LUT_dir = "Z:\Matthias\LUT_test/"
    LUT_name = "mini2"
    
    # global Inversion input:
    costfun_type = 1
    nbest_fits = 2
    nbfits_type = "rel"  # "rel" or "abs"
    out_mode = "single"  # "single" or "individual"
    noisetype = 2
    noiselevel = 1.0 # percent
    sensor = 0 # ASD
    nodat_Geo = -999
    nodat_Image = -999
    nodat_Out = -999
    inversion_range = None

    if sensor == 0:  # ASD
        exclude_bands = list(range(0, 51)) + list(range(1009, 1129)) + \
                        list(range(1371, 1650)) + list(range(2050, 2151))
        # 350-400nm, 1359-1479nm, 1721-200nm, #2450-2500
    elif sensor == 2:  # EnMAP
        exclude_bands = list(range(78, 88)) + list(range(128, 138)) + list(
        range(161, 189))  # Überlappung VNIR, Water1, Water2
    elif sensor == 1:  # Sentinel-2
        exclude_bands = [10]

    # LUT-Path
    LUT_path = LUT_dir + LUT_name + "_00meta.lut"

    # Fixed Geometry
    tts = None
    tto = None
    psi = None
    geometry_fixed = [tts, tto, psi]


    
    rtm = RTM_Inversion()
    rtm.inversion_setup(image=ImageIn, image_out=ResultsOut, LUT_path=LUT_path, ctype=costfun_type,
                     nbfits=nbest_fits, nbfits_type=nbfits_type, noisetype=noisetype, noiselevel=noiselevel,
                     geo_image=None, geo_fixed=geometry_fixed, sensor=sensor,
                     nodat=[nodat_Geo, nodat_Image, nodat_Out], out_mode=out_mode, exclude_bands=exclude_bands)
    
    rtm.run_inversion()
    rtm.write_image()


if __name__ == '__main__':
    # print(example_single() / 1000.0)
    # plt.plot(range(len(example_single())), example_single() / 1000.0)
    # plt.show()
    example()

