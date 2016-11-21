import multiprocessing
import multiprocessing.pool
import os
import sys
import lamos._old_cubebuilder
import hub.file
import hub.gdal.api
import hub.gdal.util
import hub.rs.virtual
import rios.applier
from hub.collections import Bunch
from hub.timing import tic, toc
import hub.envi

class CubenameAssociations(hub.collections.Bunch):pass

class ApplierControls(rios.applier.ApplierControls):

    def __init__(self, numThreads=1, compress=False):
        self.numThreads = numThreads
        self.compress = compress
        self.rios = rios.applier.ApplierControls()
        self.rios.setNumThreads(1)
        self.rios.setJobManagerType('multiprocessing')
        if self.numThreads > 1:
            self.rios.setWindowXsize(10000)
            self.rios.setWindowYsize(10)
        else:
            self.rios.setWindowXsize(10000)
            self.rios.setWindowYsize(10)
        self.rios.setOutputDriverName("ENVI")
        self.rios.setCreationOptions(["INTERLEAVE=BSQ"])
        self.rios.setCalcStats(False)
        self.rios.setOmitPyramids(True)

def riosapply(riosinfo, riosinputs, riosoutputs, riosotherargs):

    if riosotherargs.verbose:
        sys.stdout.write(str(int(100.*riosinfo.yblock/riosinfo.ytotalblocks))+'..')

    # convert inputs
    info = riosinfo

    # map RIOS list of input images to a nicer Bunch representing the 4D cube
    inputs = Bunch()
    outputs = Bunch()
    for (cubename, stackname) in riosotherargs.outfilekeys:
        if not outputs.has_key(cubename): outputs[cubename] = Bunch()
        outputs[cubename][stackname] = None

    for ((cubename, stackname), i) in zip(riosotherargs.infilekeys,range(len(riosotherargs.infilekeys)+1)):
        if not inputs.has_key(cubename): inputs[cubename] = Bunch()
        inputs[cubename][stackname] = riosinputs.images[i]

    # call the 4D cube applier

    #riosotherargs.ufunc(info, inputs, riosotherargs.outputs, riosotherargs.inmeta, otherArgs=riosotherargs.otherArgs)
    riosotherargs.ufunc(info, inputs, outputs, riosotherargs.inmeta, otherArgs=riosotherargs.otherArgs)

    # map 4D cube applier results back to RIOS list of output images
    riosoutputs.images = [outputs[cubename][stackname] for (cubename, stackname) in riosotherargs.outfilekeys]

def applyToTile((ufunc, ufuncMeta, infiles, outfiles, mgrstile, i, n, controls, otherArgs, verbose)):

    # report progress
    if verbose: print('MGRS Tile: '+mgrstile+' ('+str(i)+'/'+str(n)+')')

    # prepare inputs for the applier function
    outputs = Bunch({cubename:Bunch({stackname:None for stackname in stacknames}) for (cubename, (cubedir, stacknames)) in outfiles.items()})

    inmeta = Bunch()
    for cubename,(filename,stacknames) in infiles.items():
        cube = lamos._old_cubebuilder.cube.Cube(filename)
        inmeta[cubename] = cube.readStackMeta(mgrstile, names=stacknames)


    # set some infos that could be used inside the user function
    info = hub.collections.Bunch()
    info.mgrstile = mgrstile

    ### use RIOS applier ###
    # call user function

    # Set up input and output filenames.
    # Map 4D Cubes stack to rios filelist
    riosinfiles = rios.applier.FilenameAssociations()
    riosoutfiles = rios.applier.FilenameAssociations()

    riosinfiles.images = [os.path.join(cubename, mgrstile[0:2], mgrstile, stackname) for cubename, stacknames in infiles.values() for stackname in stacknames]
    for filename, i in zip(riosinfiles.images,range(len(riosinfiles.images)+1)):
        if os.path.exists(filename+'.img'):
            riosinfiles.images[i] = filename+'.img'
        else:
            riosinfiles.images[i] = filename+'.vrt'

    riosoutfiles.images = [os.path.join(cubename, mgrstile[0:2], mgrstile, stackname+'.img') for cubename, stacknames in outfiles.values() for stackname in stacknames]

    #####
    #riosoutfiles = rios.applier.FilenameAssociations()

    riosotherargs = Bunch()
    riosotherargs.ufunc = ufunc
    riosotherargs.infilekeys = [(cubename, stackname) for (cubename, (cubedir, stacknames)) in infiles.items() for stackname in stacknames]
    riosotherargs.outfilekeys = [(cubename, stackname) for (cubename, (dubedir, stacknames)) in outfiles.items() for stackname in stacknames]
    riosotherargs.inmeta = inmeta
    riosotherargs.outputs = outputs
    riosotherargs.otherArgs = otherArgs
    riosotherargs.verbose = verbose

    # create output folders
    for filename in riosoutfiles.images:
        hub.file.mkfiledir(filename)

    # Apply the function to the inputs, creating the outputs.
    rios.applier.apply(riosapply, riosinfiles, riosoutfiles, otherArgs=riosotherargs, controls=controls.rios)

    # prepare output metadata
    #- read metadata from files produced by RIOS
    outmeta = Bunch()
    for cubename,(filename,stacknames) in outfiles.items():
        cube = lamos._old_cubebuilder.cube.Cube(filename)
        outmeta[cubename] = cube.readStackMeta(mgrstile, names=stacknames)
    #- call user function for metadata specification
    ufuncMeta(inmeta, outmeta, otherArgs=otherArgs)
    #- write metadata
    for cubename,(filename,stacknames) in outfiles.items():
        cube = lamos._old_cubebuilder.cube.Cube(filename)
        cube.writeStackMeta(mgrstile, outmeta[cubename])

    if verbose: print('100')

    # compress files if needed
    if controls.compress:
        if verbose: print('compress files')
        for filename in riosoutfiles.images:
            hub.envi.compress(filename)



def apply(ufunc, ufuncMeta, infiles, outfiles, mgrstiles, controls=ApplierControls(), otherArgs=None, verbose=True):

    tic('applying user function: '+ufunc.func_name)
    args = [(ufunc, ufuncMeta, infiles, outfiles, mgrstile, i, len(mgrstiles), controls, otherArgs, verbose) for mgrstile, i in zip(mgrstiles,range(1,len(mgrstiles)+1))]
    if controls.numThreads == 1:
        for arg in args: applyToTile(arg)
    else:
        pool = multiprocessing.pool.ThreadPool(controls.numThreads)
#        pool = multiprocessing.Pool(controls.numThreads)
        pool.map(applyToTile, args)
        try: pool.terminate()
        except: pass
    toc()


