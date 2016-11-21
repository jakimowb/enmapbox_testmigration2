import numpy
from hub.timing import tic, toc
import lamos._old_cubebuilder.cube
import lamos._old_cubebuilder.applier


def testCubeIO():
    tic('running testCubeIO')
    # read cube data and metadata
    incube = lamos._old_cubebuilder.cube.Cube(r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR\cubes')
    mgrstiles = ['32UNB', '32UNC', '32UND', '32UPB', '32UPC', '32UPD', '32UQB', '32UQC', '32UQD', '33UTS', '33UTT', '33UTU', '33UUS', '33UUT', '33UUU', '33UVS', '33UVT', '33UVU']
#    mgrstiles = ['32UNB']
    for mgrstile in mgrstiles:
        #print(mgrstile)

        indata, inmeta = incube.readStack(mgrstile, names=['band4','band8'])

        # calculate ndvi
        red = indata['band4']
        nir = indata['band8']
        ndvi = (nir-red).astype(numpy.float32) / (nir+red)

        # write result data cube and metadata
        outdata = {'ndvi':ndvi}
        outmeta = {'ndvi':inmeta['band4'], 'meta':inmeta['meta']}
        outcube = lamos._old_cubebuilder.cube.Cube(r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR\ndvi')
        outcube.writeStack(mgrstile, outdata, outmeta)
    toc()

# Set up the function to be applied
def ndvi(info, inputs, outputs, inmeta, otherArgs=None):
   # prepare inputs
    red = inputs.landsatTimestack.band4.astype(numpy.float32)
    nir = inputs.landsatTimestack.band8.astype(numpy.float32)
    invalid = inputs.landsatTimestack.bandcfmask != 0 # use only clear land observations

    # calculate the NDVI
    ndvi = (nir-red)/(nir+red)

    # mask invalid pixels
    ndvi[invalid] = -1

    # prepare output cubes
    outputs.ndviTimestack.ndvi = ndvi
    outputs.ndviTimestack.ndvi = inputs.landsatTimestack.band4

# Set up the function to specify output metadata
def ndvimeta(inmeta, outmeta, otherArgs=None):

    # set data ignore value
    outmeta.ndviTimestack.ndvi.setNoDataValue(-1)

    # set AcqDates as band names
    bandNames = ['NDVI '+date for date in inmeta.landsatTimestack.band4.getMetadataItem('AcqDate')]
    outmeta.ndviTimestack.ndvi.setBandNames(bandNames)

    # copy some metadata
    for key in ['AcqTime', 'Sensor', 'Satellite', 'SunAzimuth', 'geometric accuracy', 'AcqDate', 'SceneID', 'SunElevation']:
        outmeta.ndviTimestack.ndvi.copyMetadataItem(key, inmeta.landsatTimestack.band4, mapToBands=True)


def testApplier(verbose=True):

    # Set up input and output filenames.
    infiles = lamos._old_cubebuilder.applier.CubenameAssociations()
    outfiles = lamos._old_cubebuilder.applier.CubenameAssociations()
    infiles.landsatTimestack = (r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR\cubes', ['band4','band8','bandcfmask'])
    outfiles.ndviTimestack =   (r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR\ndvi2',  ['ndvi'])

    # Set up tiles to be processed
    mgrstiles = ['32UNB', '32UNC', '32UND', '32UPB', '32UPC', '32UPD', '32UQB', '32UQC', '32UQD', '33UTS', '33UTT', '33UTU', '33UUS', '33UUT', '33UUU', '33UVS', '33UVT', '33UVU']
    mgrstiles = ['32UPB']

    # Set up processing controls (creates ENVI Files per default)
    controls = lamos._old_cubebuilder.applier.ApplierControls(numThreads=1)
    controls.rios.windowysize = 10000

    # Apply the function to the inputs, creating the outputs.
    lamos._old_cubebuilder.applier.apply(ndvi, ndvimeta, infiles, outfiles, mgrstiles, controls=controls, verbose=verbose)


if __name__ == '__main__':
    testApplier(verbose=1)
