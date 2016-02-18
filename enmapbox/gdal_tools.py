from osgeo import gdal, ogr, osr
import sys

def initializeGDAL(requiredGDALDrivers=None,requiredOGRDrivers=None):
    registerErrorHandler()
    errors = list()

    if isinstance(requiredGDALDrivers, list):
        missing = [name for name in requiredGDALDrivers if gdal.GetDriverByName(name) is None]
        if len(missing) > 0:
            errors.append('Missing raster/ GDAL driver(s):')
            errors.extend(missing)

    if isinstance(requiredOGRDrivers, list):
        missing = [name for name in requiredOGRDrivers if ogr.GetDriverByName(name) is None]
        if len(missing) > 0:
            errors.append('Missing vector / OGR driver(s):')
            errors.extend(missing)

    if len(errors) > 0:
        raise Exception('\n'.join(errors))

def registerErrorHandler():
    print('Register GDAL error handler')
    gdal.UseExceptions()
    gdal.PushErrorHandler(gdal_error_handler)

def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.gdalconst.CE_None:'None',
            gdal.gdalconst.CE_Debug:'Debug',
            gdal.gdalconst.CE_Warning:'Warning',
            gdal.gdalconst.CE_Failure:'Failure',
            gdal.gdalconst.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    info = ['GDAL Message:']
    info.append('  {} Number: {}'.format(err_class, err_num))
    info.append('  {} Message: {}'.format(err_class, err_msg))
    info = '\n'.join(info)
    if err_class in ['None','Debug']:
        print(info)
    elif err_class in ['Warning']:
        print(info, file=sys.stderr)
    else:
        raise Exception(info)


