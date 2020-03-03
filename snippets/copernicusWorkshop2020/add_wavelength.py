# this snippet shows how to add
# wavelength metadata information
# to a GDAL readible raster that will be read by the EnMAP-Box
import pathlib
from osgeo import gdal
root = pathlib.Path(r'R:\Posters & presentations\workshops\EnMAP Workshops\Copernicus Workshop 2020\Ausgangsdaten_clip_rs10m')
paths = [root / 'HH_2016_rs10m.tif',
         root / 'HH_2019_rs10m.tif'
         ]

namesAndWL = [
	("B1","Aerosol (60m)",443),
	("B2","Blue (10m)",490),
	("B3","Green (10m)",560),
	("B4","Red (10m)",665),
	("B5","RedEdge1 (20m)",705),
	("B6","RedEdge2 (20m)",740),
	("B7","RedEdge3 (20m)",783),
	("B8","nIR (10m)", 842),
	("B8a","nIR (20m)", 865),
	("B9","H2Ovapor (60m)",945),
	("B11","SWIR1 (20m)",1610),
	("B12","SWIR2 (20m)",2190),
    ]


for path in paths:
    ds = gdal.Open(path.as_posix())
    assert isinstance(ds, gdal.Dataset)

    assert len(namesAndWL) == ds.RasterCount
    wl = [str(t[2]) for t in namesAndWL]
    ds.SetMetadataItem('wavelength', ','.join(wl))
    ds.SetMetadataItem('wavelength units', 'nm')
    for b, t in enumerate(namesAndWL):
        bandName = '{} {}@{}nm)'.format(t[0], t[1][:-1], t[2])
        band:gdal.Band = ds.GetRasterBand(b+1)
        band.SetDescription(bandName)
    ds.FlushCache()