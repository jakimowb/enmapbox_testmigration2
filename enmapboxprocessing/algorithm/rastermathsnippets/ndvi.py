raster =

# find bands
red = raster@655nm
nir = raster@865nm

# calculate NDVI
ndvi = (nir - red) / nir + red

# clean up temp
del