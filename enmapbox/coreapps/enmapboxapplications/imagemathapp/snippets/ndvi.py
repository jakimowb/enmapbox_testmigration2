# select RED and NIR bands
#red = raster[...]
#nir = raster[...]

# calculate NDVI
ndvi = (nir - red) / (nir + red)
