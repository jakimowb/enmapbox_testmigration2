from hubdc import ApplierOperator
from datetime import date, timedelta
from numpy import float32, int16, full, nan, isfinite, iinfo, any, equal

class TSGapFiller(ApplierOperator):

    def ufunc(self, start, end, stddevs, workTempRes, outTempRes):

        assert outTempRes % workTempRes == 0, 'output resolution must by a multiple of working resolution '

        evi = lambda blue, nir, red: 2.5*(nir-red)/(nir+6.*red-7.5*blue+1.)
        ysize, xsize = self.grid.getDimensions()

        # arrange irregularly distributed obvervations into a evenly spaced temporal grid
        bands = (end-start).days // workTempRes+1
        ts = full((bands, ysize, xsize), fill_value=nan, dtype=float32)
        for cfmask, blue, red, nir, acqDate in zip(self.getDatas('cfmask'),
                                                   self.getDatas('blue', dtype=float32, scale=1e-5),
                                                   self.getDatas('red', dtype=float32, scale=1e-5),
                                                   self.getDatas('nir', dtype=float32, scale=1e-5),
                                                   self.getAcquisitionDates()):

            valid = equal(cfmask, 0)
            if not any(valid): continue
            index = (acqDate-start).days // workTempRes
            if index < 0 or index > bands-1: continue
            ts[index][valid[0]] = evi(blue[valid], red[valid], nir[valid])

        da = isfinite(ts).astype(float32) # need to convert to float32, otherwise convolve will produce a float64

        self.noDataTS = iinfo(int16).min
        for i, stddev in enumerate(stddevs):
            fTS, fDA = self.filter(ts, da, stddev, workTempRes)
            self.setData(('filteredTS', i), array=fTS[::outTempRes], replace=[nan, self.noDataTS], scale=1e5, dtype=int16)
            self.setData(('filteredDA', i), array=fDA[::outTempRes], scale=1e5, dtype=int16)

    def umeta(self, start, end, stddevs, workTempRes, outTempRes):

        def decimalYear(d):
            from calendar import isleap
            doy = (d - date(d.year, 1, 1)).days + 1
            dyear = d.year + doy / (365.+isleap(d.year))
            return dyear

        bandNames = list()
        wavelength = list()
        for days in range((end-start).days+1):
            d = start+timedelta(days=days)
            bandNames.append(str(d))
            wavelength.append(decimalYear(d))

        for i in range(len(stddevs)):
            self.setMetadataItem(('filteredTS', i), key='band names', value=bandNames[::outTempRes], domain='ENVI')
            self.setMetadataItem(('filteredDA', i), key='band names', value=bandNames[::outTempRes], domain='ENVI')
            self.setMetadataItem(('filteredTS', i), key='wavelength', value=wavelength[::outTempRes], domain='ENVI')
            self.setMetadataItem(('filteredDA', i), key='wavelength', value=wavelength[::outTempRes], domain='ENVI')
            self.setNoDataValue(('filteredTS', i), value=self.noDataTS)

    def filter(self, ts, da, stddev, workingTemporalResolution):
        from astropy.convolution.kernels import Gaussian1DKernel
        from astropy.convolution import convolve

        stddev = stddev / workingTemporalResolution
        kernel = Gaussian1DKernel(stddev).array.reshape((-1, 1, 1))
        fTS = convolve(ts, kernel, boundary='fill', fill_value=nan, normalize_kernel=True)
        fDA = convolve(da, kernel, boundary='fill', fill_value=0, normalize_kernel=True)
        return fTS, fDA

    def getAcquisitionDates(self):
        from os.path import basename

        for name in self.getSubnames(name='cfmask'):
            dataset = self._applier.inputDatasets[name]
            sceneID = basename(dataset.gdalDataset.GetFileList()[0])[:21]
            year, doy = int(sceneID[9:13]), int(sceneID[13:16])
            yield date(year=year, month=1, day=1) + timedelta(days=doy-1)
