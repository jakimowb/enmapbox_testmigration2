from rios.applier import FilenameAssociations, OtherInputs, ApplierControls, apply
from hub.gdal.api import GDALMeta

def ufunc_apply_mask(info, inputs, outputs, args):

    mask = inputs.mask[0] == 0
    outputs.result = inputs.image
    for band in outputs.result:
        band[mask] = args.fill_value


def apply_mask(filename_result, filename_image, filename_mask, fill_value):

    infiles = FilenameAssociations()
    infiles.image = filename_image
    infiles.mask = filename_mask

    outfiles = FilenameAssociations()
    outfiles.result = filename_result

    args = OtherInputs()
    args.fill_value = fill_value

    controls = ApplierControls()
    controls.setWindowXsize(256)
    controls.setWindowYsize(256)
    controls.setJobManagerType('multiprocessing')
    controls.setNumThreads(1)
    controls.setOutputDriverName('ENVI')

    # apply the masking ufunc
    apply(ufunc_apply_mask, infiles, outfiles, args, controls)

    # handle metadata
    inmeta = GDALMeta(filename_image)
    outmeta = GDALMeta(filename_result)
    outmeta.copyMetadataDomain(inmeta, domainName='ENVI')
    outmeta.writeMeta()

if __name__ == '__main__':
    filename_image = r'C:\Work\data\Hymap_Berlin-A_Image'
    filename_mask = r'C:\Work\data\Hymap_Berlin-A_Mask'
    filename_result = r'C:\Work\data\_masked_image_'
    apply_mask(filename_result, filename_image, filename_mask, fill_value=0)

