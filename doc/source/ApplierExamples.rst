================
Applier Examples
================

To honor the similarities of HUBDC with RIOS, we replicate the
`examples known from RIOS <http://rioshome.org/en/latest/applierexamples.html>`_, and add some more HUBDC specific examples.


Simple Example
==============

::

    """
    Reads in two input files and adds them together.
    Assumes that they have the same number of bands.
    """
    
    from hubdc.applier import Applier, ApplierOperator
    
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

Instead of providing the operator as an *user defined function*, you could also pass an *user defined class* which implemets the ``ufunc`` method::

    from hubdc.applier import ApplierOperator

    # Set up the operator to be applied
    class AddThem(ApplierOperator):
        def ufunc(self):
            outimage = self.getArray('image1') + self.getArray('image2')
            self.setArray('outimage', array=outimage)

The program shown above is minimalistic, but complete, and would work, assuming the two input files existed.
The result would be the file called outfile.img.

The user-supplied operator in form of the ``addThem`` function or ``AddThem`` class is passed to the
:meth:`hubdc.applier.Applier.apply` method, which applies it across the image.

The operators :meth:`~hubdc.applier.ApplierOperator.getArray` and :meth:`~hubdc.applier.ApplierOperator.setArray`
methods are used to access and deliver image data from the raster files defined earlier.

The data is presented as numpy arrays, of the datatype corresponding to that in the raster files. 
It is the responsibility of the user to manage all conversions of datatypes.

All blocks of data are 3-d numpy arrays. The first dimension corresponds to the number of layers in the image file, 
and will be present even when there is only one layer.
The second and third dimensions represent the spatial extent (ysize, xsize) of the image block.

The datatype of the output file(s) will be inferred from the datatype of the numpy arrays(s) given in the outputs object. 
So, to control the datatype of the output file, use the numpy astype() function to control the datatype of the output arrays.

Manage Metadata Example
=======================

You can read metadata from input and write metadata to output datasets. This simple example reads the *wavelength* information in
the *ENVI* metadata domain of the input dataset and passes it to the output dataset::

    def ufunc(operator):
        wavelength = operator.getMetadataItem(name='image', key='wavelength', domain='ENVI')
        operator.setArray('outimage', array=operator.getArray('image'))
        operator.setMetadataItem('outimage', key='wavelength', value=wavelength, domain='ENVI')

Metadata management is usually independent of the block that is currently processed. In the above example, the metadata
i/o is done redundantly. This can be prevented by using the operators
:meth:`~hubdc.applier.ApplierOperator.isFirstBlock` or
:meth:`~hubdc.applier.ApplierOperator.isLastBlock` method::

    def ufunc(operator):
    
        if operator.isFirstBlock():
            operator.wavelength = operator.getMetadataItem(name='image', key='wavelength', domain='ENVI')
    
        operator.setArray('outimage', array=operator.getArray('image'))
    
        if operator.isLastBlock():
            operator.setMetadataItem('outimage', key='wavelength', value=operator.wavelength, domain='ENVI')

For more information on the GDAL Data and Metadata Model see the
`GDAL documentation <http://www.gdal.org/gdal_datamodel.html>`_.


Passing Other Data Example
==========================

Use additional arguments for passing other data into the user function,
apart from the raster data itself. This is obviously useful for passing parameters into the processing. 

Use the ``return`` statement to pass information out again.

A simple example, using it to pass in a single parameter, 
might be a program to multiply an input raster by a scale value and add an offset::

    def rescale(operator, scale, offset):
        assert isinstance(operator, ApplierOperator)
        scaled = operator.getArray('img') * scale + offset
        operator.setArray('scaled', array=scaled)
    
    applier.apply(rescale, scale=1, offset=0)

An example of using the ``return`` statement to accumulate information across blocks might be a program
to calculate some statistic (e.g. the mean) across the whole raster::

    def accum(operator):
        img = operator.getArray('img')
        return float(img.sum()), img.size

    results = applier.apply(accum)

    total, count = 0., 0
    for blockTotal, blockCount in results:
        total += blockTotal
        count += blockCount

    print('Average value = ', total / count)
    
The ``total`` and ``count`` values are calculated from the list of ``blockTotal`` and ``blockCount`` values
returned by the :meth:`~hubdc.applier.Applier.apply` method.

The values could be accumulated between blocks, as HUBDC loops sequentially over all blocks in the image,
but this approach would fail if the applier is used with multiprocessing enabled.

Of course, there already exist superior ways of calculating the mean value of an image, 
but the point about using HUBDC to do something like this would be that:
a) opening the input rasters is taken care of; and
b) it takes up very little memory, as only small blocks are in memory at one time. The same mechanism can be used to do more specialized calculations across the images.

Note that there are no output rasters from the last example - this is perfectly valid.

Controlling the Reference Pixel Grid Example
============================================

Normally, HUBDC will raise an exception if the input rasters are on different projections, 
but if requested to do so, it will reproject on-the-fly. 

This is enabled by telling it which of the input rasters should be used as the reference 
(all other inputs will be reprojected onto this reference pixel grid).
This is done as follows::

    filename = 'image.img'
    applier.controls.setReferenceImage(filename=filename)

If the input rasters have the same projection, but differ in their spatial extent and/or pixel resolution,
HUBDC will automatically calculate the pixel grid by deriving the *union* extent and the *minimum* resolution
from all inputs.

To alter this default behaviour, use for example the :meth:`~hubdc.applier.ApplierControls.setAutoFootprint`
methods of the ``applier.controls`` object to change the footprint type to *intersection*::

    applier.controls.setAutoFootprint(footprintType='intersection')

Or use :meth:`~hubdc.applier.ApplierControls.setAutoResolution` to set the resolution type to *average* or *maximum*::

    applier.controls.setAutoResolution(resolutionType='average')

Or explicitly define the reference pixel grid in terms of
pixel resolution (use :meth:`~hubdc.applier.ApplierControls.setResolution`),
spatial footprint (use :meth:`~hubdc.applier.ApplierControls.setFootprint`)
and projection (use :meth:`~hubdc.applier.ApplierControls.setProjection`)::

    applier.controls.setFootprint(xMin=4400000, xMax=450000, yMin=3100000, yMax=3200000)
    applier.controls.setResolution(xRes=30, yRes=30)
    applier.controls.setProjection(projection='EPSG:3035')

Other controls which can be manipulated are detailed in the source code documentation for the 
:class:`~hubdc.applier.ApplierControls` class.

Arbitrary Numbers of Input (and Output) Files Example
=====================================================

Inputs can also be list of filenames, instead of a single filename. 
Use :meth:`~hubdc.applier.Applier.setInputList` and :meth:`~hubdc.applier.Applier.setOutputList` of the *applier* object
to specify lists of input and output filenames::

    applier = Applier()
    applier.setInputList('images', filenames=['image1.img', 'image2.img']
    applier.setOutputList('results', filenames=['result1.img', 'result2.img'])

Inside the user function, individual images can be accessed using the list identifier together with an index into the list.
To access the first, second and third image of a list named ``images`` use the subnames ``('images', 0)``,  ``('images', 1)``,  ``('images', 2)``, ...

For example, to read the image block of the i-th image of an input list and write it to the k-th image of an output list use::

    def ufunc(operator):
        array = operator.getArray(('inputs', i))
        operator.setArray(('outputs', k), array=array)


To loop over all items in an input list use :meth:`~hubdc.applier.ApplierOperator.getInputListSubnames`::

    def ufunc(operator):
        for subname in operator.getInputListSubnames('images'):
            array = operator.getArray(subname) # read image data
            metadata = operator.getMetadataItem(subname, key='wavelength', domain='ENVI') # read metadata item

To loop over all items in an output list use :meth:`~hubdc.applier.ApplierOperator.getOutputListSubnames`::

    def ufunc(operator):
        for subname in operator.getOutputListSubnames('results'):
            operator.setArray(subname, array=array) # write image data
            operator.setMetadataItem(subname, key='wavelength', value=wavelength, domain='ENVI') # write metadata item

An example might be a function to calculate basic statistics (e.g. pixelwise min, max) for a number of raster files,
which should work the same regardless of how many files are to be processed. This could be written as follows::

    def calcMinMax(operator):

        img0 = operator.getArray(('images', 0))
        minimum = img0
        maximum = img0.copy()

        for subname in operator.getInputListSubnames('images'):
            img = operator.getArray(subname)
            numpy.minimum(minimum, img, out=minimum)
            numpy.maximum(maximum, img, out=maximum)

        operator.setArray(('minmax', 0), array=minimum)
        operator.setArray(('minmax', 1), array=maximum)

Filters and Overlap Example
===========================

Because HUBDC operates on a per block basis, care must be taken to set the overlap correctly when working with filters.
The ``overlap`` keyword must be consistently set when using the ``operator`` object data reading methods (
:meth:`~hubdc.applier.ApplierOperator.getArray`,
:meth:`~hubdc.applier.ApplierOperator.getDerivedArray`,
:meth:`~hubdc.applier.ApplierOperator.getRasterization`) and data writing methods (:meth:`~hubdc.applier.ApplierOperator.setArray`).

Here is a simple convolution filter example::

    from hubdc import Applier
    from scipy.ndimage import uniform_filter
    
    applier = Applier()
    applier.setInput('img', filename='image.img')
    applier.setOutput('filtered', filename='filtered.img')
    
    def doFilter(operator):
        # does a 11x11 uniform filter.
        # Note: for a 3x3 the overlap is 1, 5x5 overlap is 2, ..., 11x11 overlap is 5, etc
        img = operator.getArray('img', indicies=0, overlap=5)
        filtered = uniform_filter(img, size=11, mode='constant', cval=-9999)
        operator.setArray('filtered', array=filtered, overlap=5)
    
    applier.apply(doFilter)

Many other Scipy filters are also available and can be used in a similar way.

Derived Raster Inputs Example
=============================

The on-the-fly resampling and reprojection of input rasters into the reference pixel grid is one key feature of the HUBDC applier.
But in some cases this default behaviour can be insufficient in terms of information content preservation, even if the resampling algorithm is carefully choosen.

For example, if the goal is to process a categorical raster, where different categories are coded with different ids,
a simple resampling algorithm will not be able to preserve the information content, when the reference pixel grid is at a coarser resolution.

In the following example a Landsat CFMask image at 30 m is used to calculate cloud fractions at 250 m::

    from osgeo import gdal
    import numpy
    from hubdc.applier import Applier

    applier = Applier()
    applier.controls.setResolution(xRes=250, yRes=250)
    applier.setInput('cfmask', filename='LC81940242015235LGN00_cfmask.img', resampleAlg=gdal.GRA_Average)
    applier.setOutput('cloudFraction', filename=r'c:\output\out.img', format='ENVI')
    applier.apply(operator=ufunc)

    def ufunc(operator):

        def cloudMask(cfmask):
            # make a binary cloud mask and cast to float, which is important for the following resampling step
            return numpy.float32(cfmask==4)

        cloudFraction = self.getDerivedArray('cfmask', ufunc=cloudMask)
        self.setArray('cloudFraction', array=cloudFraction)

Note that the original 30 m CFMask data is passed to the ``cloudMask`` user function, which is called internally by
:meth:`~hubdc.applier.ApplierOperator.getDerivedArray` before the resampling (``resampleAlg=gdal.GRA_Average``) takes place.
This way the binary cloud information is correctly interpreted at 30 m level and afterwards averaged to 250 m target resolution.

Vector Inputs Example
=====================

Vector layers can be included into the processing using the
:meth:`~hubdc.applier.Applier.setVector` method of the ``applier`` object::

    applier = Applier()
    applier.setVector('vector', filename='vector.shp')

Like any input raster file, vector layers can be accessed via the ``operator`` object inside the user function.
Use the ``operator``
:meth:`~hubdc.applier.ApplierOperator.getRasterization` method to get a rasterized version of the vector layer.
The rasterization is a binary mask by default, that is initialized with 0 and all pixels covered by features
are filled (burned) with a value of 1::

    def ufunc(operator):
        array = operator.getRasterization('vector')
        
This behaviour can be altered using the ``initValue`` and ``burnValue`` keywords::

    array = operator.getRasterization('vector', initValue=0, burnValue=1)

Instead of a constant burn value, a burn attribute can be set by using the ``burnAttribute`` keyword::

    array = operator.getRasterization('vector', burnAttribute='ID')
        
Use the ``filterSQL`` keyword to set an attribute query string in form of a SQL WHERE clause.
Only features for which the query evaluates as true will be returned::

        sqlWhere = "Name = 'Vegetation'"
        array=self.getRasterization('vector', initValue=0, burnValue=1, filterSQL=sqlWhere)


Parallel Processing Example
===========================

Each block can be processed on a seperate CPU using Python's multiprocessing module. 
Making use of this facility is very easy and is as simple as setting some more options on the ``applier.controls`` object as below.
Note, that under Windows you need to use the  ``if __name__ == '__main__':`` statement::

    def ufunc(operator):
        ...

    if __name__ == '__main__':
    
        applier = Applier()
        applier.controls.setNumThreads(1)
        applier.apply(ufunc)


Parallel Writing Example
========================

It is possible to have multiple writer processes. Using multiple writers (in case of multiple outputs) makes sense,
because writing outputs is not only limitted by the hard drive, but also by data compression and other CPU intense overhead. 
Making use of this facility is also very easy and is as simple as setting some more options on the ``applier.controls`` object as below::

        applier.controls.setNumWriter(5)


Setting GDAL Options Example
============================

Via the ``applier.controls`` object you can set various GDAL config options
(e.g. :meth:`~hubdc.applier.ApplierControls.setGDALCacheMax`) to handle the trade of between
processing times and memory consumption::

    applier = Applier()
    applier.controls.setGDALCacheMax(bytes=1000*2**20)
    applier.controls.setGDALSwathSize(bytes=1000*2**20)
    applier.controls.setGDALDisableReadDirOnOpen(disable=True)
    applier.controls.setGDALMaxDatasetPoolSize(nfiles=1000)


 .. toctree::
    :maxdepth: 1
    :caption: Contents:

    Downloads.rst
    hubdc.rst