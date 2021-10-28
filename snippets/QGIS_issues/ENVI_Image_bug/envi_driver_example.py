import pathlib
from osgeo import gdal
TEST_DATA_DIR = pathlib.Path(__file__).parent
path_uncompressed = TEST_DATA_DIR / 'envi_uncompressed.bsq'
path_compressed = TEST_DATA_DIR / 'envi_compressed.bsq'

print(gdal.VersionInfo(''))
for path in [path_uncompressed.as_posix(),
             path_compressed.as_posix()]:
    print(f'Test {path}')
    assert isinstance(gdal.Open(path), gdal.Dataset), f'Unable to open {path} by gdal.Open()'

    # this fails with compressed ENVI file and thows an error like
    # "ERROR 1: Driver GTM is considered for removal in GDAL 3.5 ..."
    assert isinstance(gdal.OpenEx(path), gdal.Dataset), f'Unable to open {path} by gdal.OpenEx()'
