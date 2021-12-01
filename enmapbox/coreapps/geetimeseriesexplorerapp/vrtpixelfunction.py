import numpy as np

def mean(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, radius, gt):

    if len(in_ar) == 0:
        out_ar *= 0
        out_ar -= 9999
    else:
        array = np.array(in_ar, dtype=np.float32)
        array[array == -9999] = np.nan
        tmp = np.nanmean(array, axis=0)
        tmp[np.isnan(tmp)] = -9999
        np.copyto(out_ar, tmp.astype(out_ar.dtype))

def zeros(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, radius, gt):
    out_ar *= 0
