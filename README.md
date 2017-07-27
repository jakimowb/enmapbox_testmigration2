# Welcome to the HUB-Datacube Project

The HUB-Datacube package (_hubdc_) offers a high level interface for integrating heterogeneous raster datasets into a 
user-defined reference pixel grid, resulting in an analysis-ready datacube.
The data model is build on top of [GDAL](http://gdal.org/) and 
was greatly inspired by the [RIOS](http://rioshome.org) project. 

Like RIOS, HUBDC provides functionality which makes it easy to write raster processing code in Python,
but it gives the user more flexibility and has some performance improvements.

###***Simple Example***


    """
    Reads in two input files and adds them together.
    Assumes that they have the same number of bands.
    """
    
    from hubdc import Applier
    
    # Set up input and output filenames.
    applier = Applier()
    applier.setInput('image1', filename='file1.img')
    applier.setInput('image2', filename='file2.img')
    applier.setOutput('outimage', filename='outfile.img')

    # Set up the operator to be applied
    def addThem(operator):
        outimage = operator.getArray('image1') + operator.getArray('image2')
        operator.setArray('outimage', array=outimage)
    
    # Apply the operator to the inputs, creating the outputs.
    applier.apply(addThem)

###***Detailed Sphinx based Documentation***

http://hub-datacube.readthedocs.io
