# -*- coding: utf-8 -*-
from hubflow.core import *
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from lmuvegetationapps.Resources.Spec2Sensor.Sensor_Info import get_ndvi_wl


class MLRA_Training:  # Will be used for training new models, not for predictions!
    def __init__(self, main):
        self.m = main

    def ann(self, X, y, activation, solver, alpha, max_iter=500):
        return MLPRegressor(activation=activation, solver=solver, alpha=alpha, max_iter=max_iter).fit(X, y)

class Functions:
    def __init__(self, main):
        self.m = main
        self.para_dict = {"N": 0, "cab": 1, "car": 2, "anth": 3, "cbrown": 4, "cw": 5, "cm": 6, "cp": 7, "ccl": 8,
                          "LAI": 9, "typeLIDF": 10, "LIDF": 11, "hspot": 12, "psoil": 13, "tts": 14, "tto": 15,
                          "psi": 16, "N2_can4": 17}
        self.conv = {  # Name, ylim/xlim, boost
            "N": ["N", [1.0, 2.2], 1],
            "cab": ["chlorophyll", [10, 80], 1],
            "cw": ["EWT_S", [0.01, 0.007], 1000],
            "cm": ["LMA", [0.0025, 0.006], 1000],
            "LAI": ["greenLAI", [0.0, 8.0], 1],
            "typeLIDF": ["typeLIDF", [1.0, 2.0], 1],
            "LIDF": ["ALIA_S", [10, 80], 1],
            "hspot": ["hspot", [0.0, 0.1], 100],
            "psoil": ["psoil", [0.0, 1.0], 10],
            "tts": ["tts"],
            "tto": ["tto"],
            "psi": ["psi"],
            "cp": ["cp", [0.0, 0.002], 1000],
            "cbc": ["ccl", [0.0, 0.005], 1000],
            "car": ["Car", [0.0, 20.0], 1],
            "anth": ["Canth", [0.0, 5.0], 1],
            "cbrown": ["brown_pigments", [0.0, 1.0], 10]}
        self.wl_sensor = {1: 13, 2: 242, 3: 8, 4: 126}

        # 0: 'N', 1: 'cab', 2: 'cw', 3: 'cm', 4: 'LAI', 5: 'typeLIDF', 6: 'LIDF', 7: 'hspot',
        # 8: 'psoil', 9: 'tts', 10: 'tto', 11: 'psi', 12: 'cp', 13: ccl, 14: car, 15: anth, 16: cbrown

    def NDVI(self, bands, in_matrix, thr):
        red, nir = bands[0], bands[1]
        NDVI_out = (in_matrix[nir, :, :] - in_matrix[red, :, :]) / (in_matrix[nir, :, :] + in_matrix[red, :, :])
        NDVI_out = np.nan_to_num(NDVI_out)
        NDVI_out = np.where(NDVI_out > thr, 1, 0)
        return NDVI_out

    def read_image(self, image, dtype=np.float16):  # routine for loading bsq images, no bands are skipped anymore

        # filename = "U:\ECST_III\Konferenzen\ESA_Workshop_2019\SPARC03-Barrax-B-geoSurfRefl_125_bands_EnMap_10B_ML_VHGP_Narea_noise"
        # image = openRasterDataset(filename)
        # meta = image.metadataDict()
        # rasterDriverX = RasterDriver.fromFilename(filename)
        # proj = image.projection()
        #
        # grid = Grid(extent=Extent(xmin=574873, xmax=578920, ymin=4322452, ymax=4325566, projection=proj),
        #             resolution=6)
        # grid = image.grid()

        dataset = openRasterDataset(image)
        in_matrix = dataset.readAsArray().astype(dtype=dtype)
        nbands, nrows, ncols = in_matrix.shape
        grid = dataset.grid()

        return nrows, ncols, nbands, grid, in_matrix  # return a tuple back to the last function (type "dtype")

    def write_image(self, out_matrix, image_out, grid, paras_out, out_mode):

        if out_mode == 'single':
            output = RasterDataset.fromArray(array=out_matrix, filename=image_out, grid=grid,
                                             driver=EnviDriver())
            output.setMetadataItem('data ignore value', self.m.proc_main.nodat[1], 'ENVI')

            for iband, band in enumerate(output.bands()):
                band.setDescription(paras_out[iband])
                band.setNoDataValue(self.m.proc_main.nodat[1])
        else:
            for ipara in range(len(paras_out)):
                image_out_individual = image_out[:-4] + "_" + paras_out[ipara] + image_out[-4:]
                output = RasterDataset.fromArray(array=out_matrix[ipara, :, :], filename=image_out_individual, grid=grid,
                                                 driver=EnviDriver())
                output.setMetadataItem('data ignore value', self.m.proc_main.nodat[1], 'ENVI')
                band = next(output.bands())  # output.bands() is a generator; here only one band
                band.setDescription(paras_out[ipara])
                band.setNoDataValue(self.m.proc_main.nodat[1])

    def read_geometry(self, GeoIn):
        _, georows, geocols, _, geometry_raw = self.read_image(image=GeoIn)

        # Detect data range by inspecting the mean SZA in the image (where SZA > 0)
        mean_SZA = np.mean(geometry_raw[geometry_raw > 0])
        int_boost_geo = 10 ** (np.ceil(np.log10(mean_SZA)) - 2)  # evaluates as 1 for SZA=45, 100 for SZA=4500, ...

        geometry_matrix = np.empty(shape=(3, georows, geocols))  # three "bands" for SZA, OZA, rAA
        geometry_matrix.fill(-999)
        geometry_matrix = geometry_raw / int_boost_geo  # insert all geometries from file into the geometry matrix

        return geometry_matrix

    def which_model(self, geometry_matrix, geo):
        nrows = geometry_matrix.shape[1]
        ncols = geometry_matrix.shape[2]
        tts, tto, psi = geo
        whichModel = np.zeros(shape=((3, nrows, ncols)), dtype=np.int16)

        for row in range(nrows):
            for col in range(ncols):
                # for the supplied geometry: find closest match in LUT
                angles = []
                angles.append(np.argmin(abs(geometry_matrix[0, row, col] - tts)))  # tts
                angles.append(np.argmin(abs(geometry_matrix[1, row, col] - tto)))  # tto
                angles.append(np.argmin(abs(geometry_matrix[2, row, col] - psi)))  # psi
                whichModel[0, row, col] = angles[2] * len(tto) * len(tts) + angles[1] * len(tts) + angles[0]
        return whichModel


class Processor_Training:
    def __init__(self, main):
        self.m = main
        self.para_list = ['LAI', 'LIDF', 'cab', 'cm']

        ## Parameterization
        self.ann_activation, self.ann_solver, self.ann_alpha, self.ann_max_iter = (None, None, None, None)
        self.gpr_alpha_model, self.gpr_alpha, self.gpr_nu, self.gpr_length_scale, self.gpr_kernel = \
            (None, None, None, None, None)
        self.svr_kernel, self.svr_C, self.svr_g = (None, None, None)
        self.rf_n_estimators, self.rf_max_features, self.rf_min_samples_leaf = (None, None, None)
        self.ml_params_dict_ann = None
        self.ml_params_dict_svr = None
        self.ml_params_dict_rforest = None
        self.ml_params_dict_gpr = None

    def training_setup(self, lut_metafile, exclude_bands, npca, model_meta, algorithm='ann'):
        self.exclude_bands = exclude_bands
        self.algorithm = algorithm

        self.get_meta_LUT(lut_metafile=lut_metafile)

        self.splits = int(self.meta_dict['splits'])
        self.conversion_factor = int(self.meta_dict['multiplication_factor'])

        self.lut_metafile = lut_metafile
        self.lut_basepath = os.path.dirname(lut_metafile)
        self.lut_base = self.lut_basepath + "/" + self.meta_dict['name']

        self.model_metafile = model_meta
        self.model_basepath = os.path.dirname(model_meta)
        self.model_name = os.path.splitext(os.path.basename(model_meta))[0]
        self.model_base = self.model_basepath + "/" + self.model_name

        self.tts = [float(i) for i in self.meta_dict['tts'] if i]
        self.tto = [float(i) for i in self.meta_dict['tto'] if i]
        self.psi = [float(i) for i in self.meta_dict['psi'] if i]

        self.ntts = len(self.tts)
        self.ntto = len(self.tto)
        self.npsi = len(self.psi)

        self.npara_in_lut = len(self.meta_dict['parameters'])
        self.subset_bands_lut = [i + self.npara_in_lut for i in range(len(self.meta_dict['wavelengths']))
                                 if i not in self.exclude_bands]

        # Training Values
        self.para_boost = True  # on per default
        self.noise_type = 1  # 0: Off, 1: Additive, 2: Multiplicative
        self.sigma = 4
        self.log_transform = {'LAI': False, 'LIDF': False, 'cab': True, 'cm': False}
        self.scaler = StandardScaler()
        self.pca = PCA(npca)
        self.components = npca

    def train_and_dump(self, prgbar_widget=None, QGis_app=None):
        if any(self.log_transform[para] for para in self.para_list):
            log_transform_flag = True
            np.seterr(divide='ignore', invalid='ignore')
        else:
            log_transform_flag = False

        nmodels_total = self.npsi * self.ntto * self.ntts * len(self.para_list)


        # Train Model
        for rAA in range(self.npsi):
            for OZA in range(self.ntto):
                for SZA in range(self.ntts):

                    geo_ensemble = rAA * self.ntto * self.ntts + OZA * self.ntts + SZA
                    X, y = self.read_LUT(geo=geo_ensemble)

                    if self.noise_type > 0:
                        X = self.add_noise(ref_list=X, type=self.noise_type, sigma=self.sigma,
                                             conversion=self.conversion_factor)

                    if log_transform_flag:
                        log_X = np.log(1/X)
                        log_X[log_X == np.inf] = 0

                    # INIT MODEL per Para
                    for ipara, para in enumerate(self.para_list):

                        if prgbar_widget:
                            if prgbar_widget.gui.lblCancel.text() == "-1":
                                prgbar_widget.gui.lblCancel.setText("")
                                prgbar_widget.gui.cmdCancel.setDisabled(False)
                                raise ValueError("Training cancelled!")

                            model_no = geo_ensemble * len(self.para_list) + ipara + 1
                            prgbar_widget.gui.lblCaption_r.setText('Training model {:d} of {:d}'.format(model_no,
                                                                                                        nmodels_total))
                            QGis_app.processEvents()
                        else:
                            print("Training {} Noise {:d}-{:d} | {} | Geo {:d} of {:d}".format(
                                self.algorithm, self.noise_type, self.sigma, para, geo_ensemble + 1,
                                self.ntts * self.ntto * self.npsi))

                        self.init_model(var=para)

                        if self.scaler:
                            if self.log_transform[para]:
                                self.scaler.fit(log_X)  # fit scaler
                                x = self.scaler.transform(log_X)  # transform scaler
                            else:
                                self.scaler.fit(X)
                                x = self.scaler.transform(X)
                        else:
                            x = np.copy(X)

                        if self.pca:
                            self.pca.fit(x, y[:, ipara])
                            x = self.pca.transform(x)

                        model = self.ml_model(X=x, y=y[:, ipara], **self.ml_params)
                        joblib.dump(model, self.model_base + "_{:d}_{}{}".format(
                            geo_ensemble, para, self.ml_model_ext))

                        if prgbar_widget:
                            prgbar_widget.gui.prgBar.setValue(int(model_no * 100 / nmodels_total))
                            QGis_app.processEvents()


        for para in self.para_list:
            processing_dict = {"scaler": self.scaler,
                               "pca": self.pca,
                               "log_transform": self.log_transform}

            joblib.dump(processing_dict, self.model_base + '_{}.proc'.format(para))


        # Write Model Meta
        with open(self.model_metafile, 'w') as para_file:
            # para_file.write(";".join(self.whichparas))
            para_file.write("alg={}\nnoise_type={:d}\nsigma={:d}\nPCA_components={:d}\nscaler={}"
                            .format(self.algorithm, self.noise_type, self.sigma, self.components, str(self.scaler)))
            para_file.write("\ntts=" + ";".join(str(i) for i in self.tts))
            para_file.write("\ntto=" + ";".join(str(i) for i in self.tto))
            para_file.write("\npsi=" + ";".join(str(i) for i in self.psi))

    def get_meta_LUT(self, lut_metafile):
        with open(lut_metafile, 'r') as meta_file:
            content = meta_file.readlines()
            content = [item.rstrip("\n") for item in content]
        keys, values = list(), list()
        [[x.append(y) for x, y in zip([keys, values], line.split(sep="=", maxsplit=1))] for line in content]
        values = [value.split(';') if ';' in value else value for value in values]
        self.meta_dict = dict(zip(keys, values))
        self.para_dict = dict(zip(self.meta_dict['parameters'], list(range(len(self.meta_dict['parameters'])))))
        for geo in ['tts', 'tto', 'psi']:  # happens when only one angle is provided (no ; split)
            if not isinstance(self.meta_dict[geo], list):
                self.meta_dict[geo] = [self.meta_dict[geo]]

    def read_LUT(self, geo):
        lut = np.hstack([np.load(self.lut_base + '_{:d}_{:d}'.format(geo, split) + ".npy")
                        for split in range(self.splits)])  # load all splits of the current geo_ensembles
        X = np.asarray(lut[self.subset_bands_lut, :]).T
        y = np.zeros(shape=(lut.shape[1], len(self.para_list)))

        for i, para in enumerate(self.para_list):  # extract parameters
            if self.para_boost:
                y[:, i] = lut[self.para_dict[para], :] * self.m.func.conv.get(para)[2]
            else:
                y[:, i] = lut[self.para_dict[para], :]

        return X, y

    def add_noise(self, ref_list, type, sigma, conversion): # Routine to add noise to PROSAIL output; Ref_list are reflectances
        sigma_c = (sigma/100) * conversion  # sigma converted (e.g. 0...1 -> 0...10000)
        if type == 0:    # no noise
            return ref_list
        elif type == 1:  # additive noise
            ref_noisy = np.random.normal(loc=0.0, scale=sigma_c, size=ref_list.shape) + ref_list
        elif type == 2:  # multiplicative noise
            ref_noisy = (1 + np.random.normal(loc=0.0, scale=sigma/100, size=ref_list.shape)) * ref_list
        else:
            return None
        ref_noisy[ref_noisy < 0] = 0  # stochastic process may happen to produce ref < 0 -> set to zero
        return ref_noisy

    def init_model(self, var):
        if self.algorithm == 'ann':
            # ANN
            if not self.ann_activation:
                if var == "LIDF":
                    self.ann_activation = 'tanh'  # logistic, relu, identity, tanh
                    self.ann_solver = 'lbfgs'  # adam, lbfgs, sgd
                    self.ann_alpha = 10.0
                    self.ann_max_iter = 5000
                elif var == "cab":
                    self.ann_activation = 'tanh'  # logistic, relu, identity, tanh
                    self.ann_solver = 'adam'  # adam, lbfgs, sgd
                    self.ann_alpha = 0.01
                    self.ann_max_iter = 2000
                elif var == "cm":
                    self.ann_activation = 'logistic'  # logistic, relu, identity, tanh
                    self.ann_solver = 'lbfgs'  # adam, lbfgs, sgd
                    self.ann_alpha = 0.1
                    self.ann_max_iter = 1000
                else:  # LAI or None
                    self.ann_activation = 'logistic'  # logistic, relu, identity, tanh
                    self.ann_solver = 'lbfgs'  # adam, lbfgs, sgd
                    self.ann_alpha = 1.0
                    self.ann_max_iter = 5000

            self.ml_params = {'activation': self.ann_activation, 'solver': self.ann_solver,
                              'alpha': self.ann_alpha, 'max_iter': self.ann_max_iter}
            self.ml_model_name = 'ann_mlp'
            self.ml_model_ext = '.ann'
            self.ml_model = self.m.mlra_training.ann


class Processor_Prediction:
    def __init__(self, main):
        self.m = main
        self.mlra_meta = {'ann':
                              {'name': 'ann',
                               'file_ext': '.ann',
                               'file_name': 'ann_mlp'},
                          'svr':
                              {'name': 'svr',
                               'file_ext': '.svr',
                               'file_name': 'svr'}}

    def prediction_setup(self, model_meta, ImgIn, ResOut, out_mode, mask_ndvi, ndvi_thr, mask_image, GeoIn,
                        spatial_geo, paras, algorithm='ann', sensor_nr=2, fixed_geos=None, nodat=None):
        self.model_meta = model_meta
        self.model_dir = os.path.dirname(model_meta)
        self.model_name = os.path.splitext(os.path.basename(model_meta))[0]

        self.ImgIn = ImgIn
        self.ResOut = ResOut
        self.out_mode = out_mode
        self.mask_ndvi = mask_ndvi
        self.ndvi_thr = ndvi_thr
        self.mask_image = mask_image
        self.GeoIn = GeoIn
        self.spatial_geo = spatial_geo
        self.paras = paras
        self.algorithm = algorithm
        self.sensor_nr = sensor_nr
        if fixed_geos is None:
            self.tts_unique, self.tto_unique, self.psi_unique = [None, None, None]
        else:
            self.tts_unique, self.tto_unique, self.psi_unique = fixed_geos
        if nodat is None:
            self.nodat = [-999, -999, -999]
        else:
            self.nodat = nodat

    def predict_from_dump(self, prg_widget=None, QGis_app=None):

        if prg_widget:
            prg_widget.gui.lblCaption_r.setText('Reading Input Image...')
            QGis_app.processEvents()

        nrows, ncols, nbands, self.grid, in_matrix = self.m.func.read_image(image=self.ImgIn, dtype=np.int)

        with open(self.model_meta, 'r') as mlra_metafile:
            metacontent = mlra_metafile.readlines()
            metacontent = [line.rstrip('\n') for line in metacontent]
        self.all_tts = [float(i) for i in metacontent[5].split("=")[1].split(";")]
        self.all_tto = [float(i) for i in metacontent[6].split("=")[1].split(";")]
        self.all_psi = [float(i) for i in metacontent[7].split("=")[1].split(";")]

        if prg_widget:
            prg_widget.gui.lblCaption_r.setText('Reading Geometry Image...')
            QGis_app.processEvents()

        if self.GeoIn:
            geometry_matrix = self.m.func.read_geometry(GeoIn=self.GeoIn)
            if not self.spatial_geo:  # get rid of spatial distribution of geometry (tts, tto, psi) within image
                geometry_matrix[geometry_matrix == self.nodat[1]] = np.nan
                geometry_matrix[0, :, :] = np.nanmean(geometry_matrix[0, :, :])
                geometry_matrix[1, :, :] = np.nanmean(geometry_matrix[1, :, :])
                geometry_matrix[2, :, :] = np.nanmean(geometry_matrix[2, :, :])
        else:
            geometry_matrix = np.zeros(shape=(3, nrows, ncols))
            geometry_matrix[0, :, :] = self.tts_unique * 100
            geometry_matrix[1, :, :] = self.tto_unique * 100
            geometry_matrix[2, :, :] = self.psi_unique * 100

        if self.mask_image:
            if prg_widget:
                prg_widget.gui.lblCaption_r.setText('Reading Mask Image...')
                QGis_app.processEvents()
            _, _, _, _, self.mask = self.m.func.read_image(image=self.mask_image, dtype=np.int8)

        if self.mask_ndvi:
            if prg_widget:
                prg_widget.gui.lblCaption_r.setText('Applying NDVI Threshold...')
                QGis_app.processEvents()
            self.ndvi_mask = self.m.func.NDVI(bands=get_ndvi_wl(sensor=self.sensor_nr), in_matrix=in_matrix,
                                              thr=self.ndvi_thr)

        whichModel = self.m.func.which_model(geometry_matrix=geometry_matrix,
                                             geo=(self.all_tts, self.all_tto, self.all_psi))

        self.whichModel_unique = np.unique(whichModel)  # find out, which "whichModels" are actually found in the geo_image
        whichModel_coords = list()

        all_true = np.full(shape=(nrows, ncols), fill_value=True)

        for iwhichModel in self.whichModel_unique:  # Mask depending on constraints
            whichModel_coords.append(np.where((whichModel[0, :, :] == iwhichModel) &  # present Model
                                              (self.mask[0, :, :] > 0 if self.mask_image else all_true) &  # not masked
                                              (self.ndvi_mask > 0 if self.mask_ndvi else all_true) &  # NDVI masked
                                              (~np.all(in_matrix == self.nodat[0], axis=0))))  # not NoDatVal

        nbands, nrows, ncols = in_matrix.shape
        self.out_matrix = np.full(shape=(len(self.paras), nrows, ncols), fill_value=self.nodat[2], dtype=np.float)  # Reihenfolge ändern
        self.out_matrix = self.predict(image=in_matrix, whichModel_coords=whichModel_coords, out_matrix=self.out_matrix,
                                       prg_widget=prg_widget, QGis_app=QGis_app)


    def write_prediction(self):
        self.m.func.write_image(out_matrix=self.out_matrix, image_out=self.ResOut, grid=self.grid,
                                out_mode=self.out_mode, paras_out=self.paras)

    def predict(self, image, whichModel_coords, out_matrix, prg_widget, QGis_app):
        nbands, nrows, ncols = image.shape

        image = image.reshape((nbands, -1))  # collapse rows and cols into 1 dimension
        image = np.swapaxes(image, 0, 1)     # place predictors into the right position

        for ipara, para in enumerate(self.paras):
            if prg_widget:
                prg_widget.gui.lblCaption_r.setText('Predicting {} (parameter {:d} of {:d})...'
                                                    .format(para, ipara+1, len(self.paras)))
                QGis_app.processEvents()
            process_dict = joblib.load(self.model_dir + "/" + self.model_name + "_{}".format(para) + '.proc')
            image_copy = np.copy(image)

            if process_dict['log_transform'][para]:
                image_copy[image_copy > 0] = np.log(1 / image_copy[image_copy > 0])
                image_copy[image_copy == np.inf] = 0

            if process_dict['scaler']:
                image_copy = process_dict['scaler'].transform(image_copy)

            if process_dict['pca']:
                image_copy = process_dict['pca'].transform(image_copy)

            nbands_para = image_copy.shape[1]
            image_copy = image_copy.reshape((nrows, ncols, nbands_para))  # Back into old shape

            n_geo = len(self.all_tts) * len(self.all_tto) * len(self.all_psi)
            mod = list()
            for igeo in range(n_geo):
                mod.append(joblib.load(self.model_dir + "/" + self.model_name + '_{:d}_{}.ann'.format(igeo, para)))

            for i_imodel, imodel in enumerate(self.whichModel_unique):
                if whichModel_coords[i_imodel][0].size == 0:
                    continue  # after masking, not all 'imodels' are present in the image_copy
                result = mod[imodel].predict(image_copy[whichModel_coords[i_imodel][0], whichModel_coords[i_imodel][1], :])
                out_matrix[ipara, whichModel_coords[i_imodel][0], whichModel_coords[i_imodel][1]] = result / self.m.func.conv[para][2]

        return out_matrix


class ProcessorMainFunction:
    def __init__(self):
        self.mlra_training = MLRA_Training(self)
        self.func = Functions(self)
        self.predict_main = Processor_Prediction(self)
        self.train_main = Processor_Training(self)
