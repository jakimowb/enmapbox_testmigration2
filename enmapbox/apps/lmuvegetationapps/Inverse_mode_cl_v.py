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

    def read_image(self, image, dtype=np.float16, exclude_bands=[]):
        dataset = openRasterDataset(image)
        in_matrix = dataset.readAsArray().astype(dtype=dtype)
        in_matrix = np.delete(in_matrix, exclude_bands, 0)
        nbands, nrows, ncols = in_matrix.shape
        grid = dataset.grid()

        return nrows, ncols, nbands, grid, in_matrix  # return a tuple back to the last function (type "dtype")

    def get_geometry(self, geo_fixed, geo_image=None, spatial_geo=False):
        if geo_image:
            geometry_raw = self.read_image(geo_image)
            geometry_data = geometry_raw[-1]
            if not geometry_raw[0] == self.nrows or not geometry_raw[1] == self.ncols:
                raise ValueError("Geometry image and Sensor image do not match")
            mean_SZA = np.mean(geometry_data[geometry_data > 0])
            int_boost_geo = 10 ** (np.ceil(np.log10(mean_SZA)) - 2)  # evaluates as 1 for SZA=45, 100 for SZA=4500, ...
            self.geometry_matrix = geometry_data / int_boost_geo
            if not spatial_geo:  # get rid of spatial distribution of geometry (tts, tto, psi) within image
                self.geometry_matrix[self.geometry_matrix == self.nodat[1]] = np.nan
                self.geometry_matrix[0, :, :] = np.nanmean(self.geometry_matrix[0, :, :])
                self.geometry_matrix[1, :, :] = np.nanmean(self.geometry_matrix[1, :, :])
                self.geometry_matrix[2, :, :] = np.nanmean(self.geometry_matrix[2, :, :])

        elif geo_fixed:
            self.geometry_matrix = np.empty(shape=(3, self.nrows, self.ncols))
            self.geometry_matrix.fill(self.nodat[2])
            if not any(geo_fixed[i] is None for i in range(len(geo_fixed))):
                try:
                    for angle in range(3):
                        self.geometry_matrix[angle, :, :] = geo_fixed[angle]
                except ValueError:
                    raise ValueError("Problem with reading fixed angles")

        self.whichLUT = np.zeros(shape=(3, self.nrows, self.ncols), dtype=np.int16)

        if self.geo_mode == "sort":
            for row in range(self.nrows):
                for col in range(self.ncols):
                    angles = list()
                    angles.append(np.argmin(abs(self.geometry_matrix[0, row, col] - self.tts_LUT)))  # tts
                    angles.append(np.argmin(abs(self.geometry_matrix[1, row, col] - self.tto_LUT)))  # tto
                    angles.append(np.argmin(abs(self.geometry_matrix[2, row, col] - self.psi_LUT)))  # psi
                    self.whichLUT[0, row, col] = angles[2] * self.nangles_LUT[1] * self.nangles_LUT[0] + \
                                                 angles[1] * self.nangles_LUT[0] + \
                                                 angles[0]
        else:
            self.whichLUT[0, :, :] = 0  # take first available (there should be no more than 1 anyway)
            self.geometry_matrix[:, :, :] = 911  # a value that is unlikely to be chosen for no data. In case of geo_mode != 'sort', the matrix is unused

    def add_noise(self, Ref_array, type, sigma):

        sigma /= 100
        sigma_c = (sigma/100) * self.conversion_factor  # sigma converted

        if type == 1:  # additive noise
            Ref_noisy = np.random.normal(loc=0.0, scale=sigma_c, size=Ref_array.shape) + Ref_array

        elif type == 2:  # multiplicative noise
            Ref_noisy = (1 + np.random.normal(loc=0.0, scale=sigma, size=Ref_array.shape)) * Ref_array

        elif type == 3:  # inverse multiplicative noise
            Ref_noisy = 1 - (1 - Ref_array) * (1 + np.random.normal(loc=0.0, scale=sigma))

        else:
            return None

        Ref_noisy[np.isnan(Ref_noisy)] = 0
        Ref_noisy[Ref_noisy < 0] = 0

        return Ref_noisy

    def cost_fun(self, image_Ref, model_Ref, type):

        if type == 1: # RMSE
            # delta = np.linalg.norm(model_Ref - image_Ref) / np.sqrt(self.n_wl)  # Numpy-Solution für RMSE (fast)
            delta = np.sqrt(np.mean((image_Ref - model_Ref) ** 2, axis=0))
        elif type == 2: # MAE
            delta = np.sum(np.abs(image_Ref - model_Ref), axis=0)
        elif type == 3: # mNSE
            delta = 1.0 - ((np.sum(np.abs(image_Ref - model_Ref), axis=0)) /
                           (np.sum(np.abs(image_Ref - (np.mean(image_Ref))))))
        else:
            delta = None
            exit("wrong cost function type. Expected 1, 2 or 3; got %i instead" %type)

        return delta

    def inversion_setup(self, image, image_out, LUT_path, ctype, nbfits, nbfits_type, noisetype, noiselevel,
                        exclude_bands, out_mode, geo_image=None, geo_fixed=[None]*3, spatial_geo=False, sensor=2,
                        nodat=[-999]*3, mask_image=None):

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

        self.nrows, self.ncols, self.nbands, self.grid, self.image = self.read_image(image=image, dtype=np.float16,
                                                                                     exclude_bands=self.exclude_bands)
        if mask_image is None:
            self.exclude_pixels = []
            self.mask = None
        else:
            mask_rows, mask_cols, _, _, self.mask = self.read_image(image=mask_image, dtype=np.int8)
            if not self.nrows == mask_rows or not self.ncols == mask_cols:
                return "Input Image and Mask Image must have same dimensions! Input Image has [{:d}r, {:d}c], " \
                       "Mask Image has [{:d}r, {:d}c]".format(self.nrows, self.ncols, mask_rows, mask_cols)

        self.npara = len(self.whichpara)
        self.get_geometry(geo_image=geo_image, geo_fixed=geo_fixed, spatial_geo=spatial_geo)  # generate list of LUT-names for each pixel
        self.out_matrix = np.empty(shape=(len(self.whichpara), self.nrows, self.ncols))

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

    def run_inversion(self, prg_widget=None, QGis_app=None):

        self.whichLUT_unique = np.unique(self.whichLUT)  # find out, which "whichLUT" are actually found in the geo_image
        whichLUT_coords = list()

        all_true = np.full(shape=(self.nrows, self.ncols), fill_value=True)
        for iwhichLUT in self.whichLUT_unique:  # Mask depending on constraints
            whichLUT_coords.append(np.where((self.whichLUT[0, :, :] == iwhichLUT) &  # present Model
                                            (self.mask[0, :, :] > 0 if not self.mask is None else all_true) &  # not masked
                                        #   (self.ndvi_mask > 0 if self.mask_ndvi else all_true) &  # NDVI masked # todo
                                            (~np.all(self.image == self.nodat[0], axis=0))))  # not NoDatVal
        pix_current = 0
        npixel_valid = sum([len(whichLUT_coords[i][0]) for i in range(len(self.whichLUT_unique))])


        for i_ilut, ilut in enumerate(self.whichLUT_unique):
            if whichLUT_coords[i_ilut][0].size == 0:
                continue  # after masking, not all 'iluts' are present in the image_copy
            load_objects = [np.load(self.LUT_base + "_" + str(ilut) + "_" + str(split) + ".npy")
                            for split in range(self.splits)]
            lut = np.hstack(load_objects)  # load all splits of the current geo_ensembles

            LUT_params = lut[self.whichpara_num, :]  # extract parameters
            lut = np.delete(lut, self.exclude_bands_model, axis=0)  # delete exclude_bands_model - members
            lut = self.add_noise(Ref_array=lut, type=self.noisetype, sigma=self.noiselevel)/self.conversion_factor

            samples_size = len(whichLUT_coords[i_ilut][0])
            result = np.zeros(shape=(self.npara, samples_size))
            for isample in range(samples_size):
                mydata = self.image[:, whichLUT_coords[i_ilut][0][isample], whichLUT_coords[i_ilut][1][isample]]  # Get current sample
                estimates = self.cost_fun(image_Ref=mydata[:, np.newaxis], model_Ref=lut, type=self.ctype)
                # estimates = np.sqrt(np.mean((mydata[:, np.newaxis] - lut) ** 2, axis=0))
                pix_current += 1
                if isample % 1000 == 0:
                    if prg_widget:
                        prg_widget.gui.lblCaption_r.setText('Inverting pixel #{:d} of {:d}'.format(pix_current, npixel_valid))
                        prg_widget.gui.prgBar.setValue(pix_current*100 // npixel_valid)
                        QGis_app.processEvents()
                    else:
                        print("LUT_unique #{:d} of {:d}: Checking sample {:d} of {:d}".format(i_ilut, len(self.whichLUT_unique), isample, samples_size))
                L1_subset = np.argpartition(estimates, self.nbfits)[0:self.nbfits]  # get n best performing LUT-entries
                L1_subset = L1_subset[np.argsort(estimates[L1_subset])]
                result[:, isample] = np.median(LUT_params[:, L1_subset], axis=1)

            self.out_matrix[:, whichLUT_coords[i_ilut][0], whichLUT_coords[i_ilut][1]] = result


    def write_image(self):
        if self.out_mode == "single":
            output = Raster.fromArray(array=self.out_matrix, filename=self.image_out, grid=self.grid)
            output.dataset().setMetadataItem('data ignore value', self.nodat[2], 'ENVI')
            for i, band in enumerate(output.dataset().bands()):
                band.setDescription(self.whichpara[i])
                band.setNoDataValue(self.nodat[2])

        elif self.out_mode == "individual":
            for i, para_key in enumerate(self.whichpara):
                output = Raster.fromArray(array=self.out_matrix[i, :, :], filename=os.path.splitext(
                    self.image_out)[0] + "_" + para_key + os.path.splitext(self.image_out)[1])
                output.dataset().setMetadataItem('data ignore value', self.nodat[2], 'ENVI')
                for band in output.dataset().bands():
                    band.setDescription(para_key)
                    band.setNoDataValue(self.nodat[2])

def example():
    ImageIn = r"F:\Flugdaten2\Cali\Test_Snippet/BA_mosaic_su_cut_test.bsq"
    ResultsOut = r"F:\Flugdaten2\Cali\Test_Snippet/inverse_out_cut_test.bsq"
    #GeometryIn = "D:/ECST_II/Cope_BroNaVI/Felddaten/Parameter/Geometry_DJ_w.bsq"
    LUT_dir = r"F:\Temp\LUT_debug/"
    LUT_name = "Test_LUT"
    
    # global Inversion input:
    costfun_type = 1
    nbest_fits = 5
    nbfits_type = "rel"  # "rel" or "abs"
    out_mode = "single"  # "single" or "individual"
    noisetype = 1
    noiselevel = 3.0 # percent
    sensor = 2  # EnMAP
    nodat_Geo = -999
    nodat_Image = -999
    nodat_Out = -999

    nodats = [nodat_Geo, nodat_Image, nodat_Out]

    if sensor == 0:  # ASD
        exclude_bands = list(range(0, 51)) + list(range(1009, 1129)) + \
                        list(range(1371, 1650)) + list(range(2050, 2151))
        # 350-400nm, 1359-1479nm, 1721-200nm, #2450-2500
    elif sensor == 2:  # EnMAP
        exclude_bands = list(range(78, 88)) + list(range(128, 138)) + list(
        range(161, 189))  # Überlappung VNIR, Water1, Water2
    elif sensor == 1:  # Sentinel-2
        exclude_bands = [10]
    else:
        exclude_bands = None

    # LUT-Path
    LUT_path = LUT_dir + LUT_name + "_00meta.lut"

    # Fixed Geometry
    tts = 45
    tto = 0
    psi = 0
    geometry_fixed = [tts, tto, psi]
    geo_image = r"F:\Flugdaten2\Cali\Test_Snippet/BA_mosaic_su_cut_geo_test.bsq"
    geo_image = None
    spatial_geo = False

    mask_image = r"F:\Flugdaten2\Cali\Test_Snippet/BA_mosaic_su_cut_mask_test.bsq"
    # mask_image = None

    rtm = RTM_Inversion()
    rtm.inversion_setup(image=ImageIn, image_out=ResultsOut, LUT_path=LUT_path, ctype=costfun_type,
                     nbfits=nbest_fits, nbfits_type=nbfits_type, noisetype=noisetype, noiselevel=noiselevel,
                     geo_image=geo_image, geo_fixed=geometry_fixed, spatial_geo=spatial_geo, sensor=sensor,
                     nodat=nodats, mask_image=mask_image, out_mode=out_mode, exclude_bands=exclude_bands)
    
    rtm.run_inversion()
    rtm.write_image()


if __name__ == '__main__':
    # print(example_single() / 1000.0)
    # plt.plot(range(len(example_single())), example_single() / 1000.0)
    # plt.show()
    example()

