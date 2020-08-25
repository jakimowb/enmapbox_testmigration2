# -*- coding: utf-8 -*-
import numpy as np
import csv
import os


class Spec2Sensor:
    
    def __init__(self, nodat, sensor):
        self.wl_sensor, self.fwhm = (None, None)
        self.wl = range(400, 2501)
        self.n_wl = len(self.wl)
        self.nodat = nodat
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.sensor = sensor

    def init_sensor(self):
        try:
            SRF_File = np.load(self.path + "/srf/" + self.sensor + ".srf")
        except FileNotFoundError:
            print("File {} not found, please check directories!".format(self.sensor + ".srf"))
            return False
        self.srf = SRF_File['srf']
        self.srf_nbands = SRF_File['srf_nbands']
        self.wl_sensor = SRF_File['sensor_wl']
        self.n_wl_sensor = len(self.wl_sensor)
        # self.fwhm = SRF_File['sensor_fwhm']  # deprecated
        self.ndvi = SRF_File['sensor_ndvi']
        return True

    def run_SRF(self, reflectance, int_factor_wl=1000, int_factor=1):
        hash_getwl = dict(zip(self.wl, list(range(self.n_wl))))
        spec_corr = np.zeros(shape=(reflectance.shape[0], self.n_wl_sensor))

        for sensor_band in range(self.n_wl_sensor):
            wfactor_include = []
            for srf_i in range(self.srf_nbands[sensor_band]):
                try:
                    wlambda = int(self.srf[srf_i][sensor_band][0]*int_factor_wl)  # Wellenlänge des W-faktors, Umwandlung in nm und Integer
                except ValueError:
                    print("sensor_band", sensor_band)
                    print("srf_i", srf_i)
                    exit()
                if wlambda not in self.wl:
                    continue
                wfactor = self.srf[srf_i][sensor_band][1]  # Wichtungsfaktor
                wfactor_include.append(srf_i)
                spec_corr[:, sensor_band] += reflectance[:, hash_getwl[wlambda]] * wfactor  # Aufsummieren der korrigierten Spektren

            sum_wfactor = sum(self.srf[i][sensor_band][1] for i in wfactor_include)

            try:
                spec_corr[:,sensor_band] /= sum_wfactor
                # spec_corr[:,sensor_band] = ((spec_corr[:,sensor_band] / sum_wfactor) * int_factor).astype(np.int32) # for reflectances 0...1
            except ZeroDivisionError:
                spec_corr[:, sensor_band] = self.nodat

        # if self.sensor == "Sentinel2":
        #     spec_corr[:, 10] = 0
        return spec_corr

class Build_SRF:

    def __init__(self, srf_files, wl_file=None, out_file=None, delimiter=None,
                 header_bool=None, wl_convert=None, nodat=-999):
        self.files = srf_files
        self.wl_file = wl_file
        self.out_file = out_file
        self.delimiter = delimiter
        self.header_bool = header_bool
        self.wl_convert = wl_convert
        self.nodat = nodat

    def dframe_from_txt(self):
        # sniff dialect
        sniffer = csv.Sniffer()
        with open(self.files[0], 'r') as raw_file:
            if not self.delimiter:
                dialect = sniffer.sniff(raw_file.readline())
                self.delimiter = dialect.delimiter
            raw_file.seek(0)
            # raw = csv.reader(raw_file, dialect)
            raw = csv.reader(raw_file, delimiter=self.delimiter)
            firstline = [i for i in next(raw) if i]  # removes blank lines in K. Segl SRF files
            secondline = [i for i in next(raw) if i]

            if not self.header_bool:
                try:
                    _ = [float(i) for i in firstline]
                    self.header_bool = False
                except ValueError:
                    self.header_bool = True

            if not self.wl_convert:   # SRF must be stored in µm
                try:
                    wl_testing = secondline[0]
                    if float(wl_testing) < 1:
                        self.wl_convert = 1  # presumably µm
                    else:
                        self.wl_convert = 1000  # presumably nm
                except ValueError:
                    pass

        srf_list = list()
        for i_file, single_file in enumerate(self.files):
            single_filename = os.path.basename(single_file)
            all_lines = list()
            with open(single_file, 'r') as raw_file:
                raw = csv.reader(raw_file, delimiter=self.delimiter)
                for line in raw:
                    all_lines.append([i for i in line if i])
            if self.header_bool:
                header_items = all_lines[0]
                if not len(header_items) == 2:
                    return False, "Error at file {}: Header has {:d} columns. Number of columns " \
                                  "expected is 2 (wavelengths and weights)".format(single_filename, len(header_items))
                skiprows = 1
            else:
                skiprows = 0
                header_items = ['(band {:00d}) wavelengths'.format(i_file + 1), 'weights']  # create new header names

            try:
                wavelengths = [float(all_lines[i][0]) for i in range(skiprows, len(all_lines))]
                weights = [float(all_lines[i][1]) for i in range(skiprows, len(all_lines))]
            except ValueError:
                return False, "Error reading file {}".format(single_filename)

            if not len(all_lines[1]) == 2:
                return False, "Error at file {}: Data has {:d} columns. Number of columns " \
                              "expected is 2 (wavelengths and weights)".format(single_filename, len(all_lines[1]))

            srf_list.append([wavelengths, weights])  # List-dimensions: [Band target sensor][[0: wavelengths, 1: weights][values]

        return True, srf_list

    def srf_from_dframe(self, srf_list):

        nbands_sensor = len(srf_list)
        srf_nbands = [len(srf_list[i][0]) for i in range(nbands_sensor)]
        new_srf = np.full(shape=(np.max(srf_nbands), nbands_sensor, 2), fill_value=self.nodat, dtype=np.float64)

        # nrows = srf_df.shape[0]
        # ncols = srf_df.shape[1]
        # nbands_sensor = ncols // 2
        # srf_nbands = list(nrows - srf_df[srf_df == self.nodat].count())[::2]  # count valid data (!= nodat) and store in new list
        # new_srf = np.full(shape=(np.max(srf_nbands), nbands_sensor, 2), fill_value=self.nodat, dtype=np.float64)

        for band in range(nbands_sensor):
            new_srf[0:srf_nbands[band], band, 0] = np.asarray(srf_list[band][0][:srf_nbands[band]]) / self.wl_convert
            new_srf[0:srf_nbands[band], band, 1] = np.asarray(srf_list[band][1][:srf_nbands[band]])

        try:
            wavelength = np.loadtxt(self.wl_file) / self.wl_convert
        except:
            return False, "Error reading wavelength file! Expected text-file with one float-value " \
                          "per line (i.e. wavelength)"

        if not wavelength.shape[0] == nbands_sensor:
            return False, "Got {:d} bands in wavelength-file, but {:d} bands in SRF-File!"\
                .format(int(wavelength.shape[0]), nbands_sensor)
        ndvi = list()
        ndvi.append(np.argmin(np.abs(wavelength - 0.677)))  # red
        ndvi.append(np.argmin(np.abs(wavelength - 0.837)))  # nir

        np.savez(self.out_file, srf_nbands=srf_nbands, srf=new_srf, sensor_wl=wavelength, sensor_ndvi=ndvi)
        os.rename(self.out_file, os.path.splitext(self.out_file)[0] + ".srf")
        return True, os.path.splitext(os.path.basename(self.out_file))[0]  # returning the filename helps with putting the correct name into the combobox

    # def srf_from_txt(self, file_path):   # fwhm-style depricated
    #     # file_path = self.path + "/srf/" + filename + ".txt"
    #     filename = os.path.splitext(os.path.basename(file_path))[0]  # Get actual filename (i.e. sensor name) w/o ext
    #     content = None
    #     with open(file_path, 'r') as file:
    #         try:
    #             content = np.loadtxt(file)
    #         except ValueError:
    #             _ = file.readline()  # First row may be a header
    #             content = np.loadtxt(file)
    #     # content = np.loadtxt(file_path)
    #     if content is None:
    #         return False
    #     wavelength = content[:, 0]
    #     fwhm = content[:, 1]
    #
    #     # sigma = fwhm / 2.355  # temporarily disabled
    #     x_list = list()
    #     gs_list = list()
    #
    #     for wl in range(len(wavelength)):
    #         x_lower = scipy.stats.norm.ppf(0.105, wavelength[wl], fwhm[wl])
    #         x_upper = scipy.stats.norm.ppf(0.895, wavelength[wl], fwhm[wl])
    #
    #         x = np.arange(x_lower, x_upper+1)
    #         gs = scipy.stats.norm.pdf(x, wavelength[wl], fwhm[wl])
    #         x_list.append(x)
    #         gs_list.append(gs)
    #
    #     for ix, x in enumerate(x_list):
    #         n_invalid = sum(i > 2500 or i < 400 for i in x)  # if outreach of PDF is beyond PROSAIL range, then clip on both sides
    #         if n_invalid > 0:
    #             x_list[ix] = x_list[ix][n_invalid:-n_invalid]
    #             gs_list[ix] = gs_list[ix][n_invalid:-n_invalid]
    #
    #     new_srf_nbands = np.asarray([len(i) for i in x_list])
    #     new_srf = np.full(shape=(np.max(new_srf_nbands), len(wavelength), 2), fill_value=self.nodat, dtype=np.float64)
    #
    #     for wl in range(len(wavelength)):
    #         new_srf[0:new_srf_nbands[wl], wl, 0] = np.around(x_list[wl]/1000, decimals=3)
    #         new_srf[0:new_srf_nbands[wl], wl, 1] = gs_list[wl]
    #
    #     ndvi = list()
    #     ndvi.append(np.argmin(np.abs(wavelength - 677)))  # red
    #     ndvi.append(np.argmin(np.abs(wavelength - 837)))  # nir
    #
    #     np.savez(self.path + "/srf/" + filename, srf_nbands=new_srf_nbands, srf=new_srf, sensor_wl=wavelength,
    #              sensor_fwhm=fwhm, sensor_ndvi=ndvi)
    #     os.rename(self.path + "/srf/" + filename + ".npz", self.path + "/srf/" + filename + ".srf")
    #     return filename  # returning the filename helps with putting the correct name into the combobox

if __name__ == '__main__':
    # s2s = Spec2Sensor(sensor=None, nodat=-999)

    basepath = r'E:\Dokumente und Einstellungen\User_Martin\Eigene Dateien\TextDokumente\Beruf\Uni\Homeoffice\EnMAP\SRF/srf_enmap/'
    # files = os.listdir(basepath)[1:-1]  # EnMAP Temp
    files = os.listdir(basepath)[:-1]
    files = [basepath + i for i in files]
    wl_file = basepath + "wavelengths.rsp"
    out_file = r"/lmuvegetationapps/Resources/srf/EnMAP_new.npz"
    # out_file = r"D:\python\EnMAPBox\enmap-box-lmu-vegetation-apps\lmuvegetationapps\srf/Sentinel2.npz"
    # excel_out = r"E:\Dokumente und Einstellungen\User_Martin\Eigene Dateien\TextDokumente\Beruf\Uni\Homeoffice\EnMAP\SRF/S2_SRF.xlsx"

    build_srf = Build_SRF(srf_files=files, wl_file=wl_file, out_file=out_file, nodat=-999)
    return_flag, srf_list = build_srf.dframe_from_txt()

    if not return_flag:
        print(srf_list)

    _, sensor_name = build_srf.srf_from_dframe(srf_list=srf_list)

    # file_path = r'D:\python\EnMAPBox\enmap-box-lmu-vegetation-apps\lmuvegetationapps\srf\save/Fake_Sensor2.txt'
    # s2s.srf_from_txt(file_path=file_path)
