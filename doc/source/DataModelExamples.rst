
Data Model Usage Examples
=========================

Imports
-------

.. code:: ipython2

    from hubdc.model import *
    from hubdc.testdata import *
    import numpy as np
    import tempfile
    from os.path import join

Initialze notebook display

.. code:: ipython2

    import hubdc.nbdisplay as nbd
    nbd.output_notebook()

Testdata Overview
-----------------

.. code:: ipython2

    import hubdc.testdata
    print(hubdc.testdata.__doc__)

LT51940232010189KIS01

.. code:: ipython2

    for key, value in sorted(LT51940232010189KIS01.__dict__.items()):
        if not key.startswith('__'):
            print('LT51940232010189KIS01.{}: {}'.format(key, value))

LT51940232010189KIS01

.. code:: ipython2

    for key, value in sorted(LT51940242010189KIS01.__dict__.items()):
        if not key.startswith('__'):
            print('LT51940242010189KIS01.{}: {}'.format(key, value))

BrandenburgDistricts

.. code:: ipython2

    for key, value in sorted(BrandenburgDistricts.__dict__.items()):
        if not key.startswith('__'):
            print('BrandenburgDistricts.{}: {}'.format(key, value))

Open Raster Files
-----------------

.. code:: ipython2

    nir = openRaster(filename=LT51940232010189KIS01.nir)
    swir1 = openRaster(filename=LT51940232010189KIS01.swir1)
    red = openRaster(filename=LT51940232010189KIS01.red)
    cfmask = openRaster(filename=LT51940232010189KIS01.cfmask)
    (nir, swir1, red, cfmask)

Querying Raster Information
---------------------------

.. code:: ipython2

    cfmask.driver()

.. code:: ipython2

    cfmask.description()

.. code:: ipython2

    cfmask.noDataValue()

.. code:: ipython2

    cfmask.dtype()

.. code:: ipython2

    zsize, ysize, xsize = cfmask.shape()
    zsize, ysize, xsize

.. code:: ipython2

    grid = cfmask.grid()

.. code:: ipython2

    grid.extent()

.. code:: ipython2

    grid.resolution()

.. code:: ipython2

    grid.projection()

Create Raster
-------------

Understanding Formats and Drivers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a new raster you have to choose a file format. Most HUB
Datacube raster creation routines use the GDAL MEM format as default,
which does not store the data to disc, but simply holds it in memory.
This is often useful for intermediate results, testing or demonstation
perpouses. Different formats are provided by so called drivers. A driver
can be used to create a new raster of the corresponding format.

.. code:: ipython2

    Driver(name='MEM')

Some drivers are subclassed…

.. code:: ipython2

    MEMDriver() # shortcut for MEM driver

.. code:: ipython2

    ENVIDriver()

.. code:: ipython2

    GTiffDriver()

… and provide functionality to conviniently setup some creation options.

For example, use the GTiffDriver to setup the creation options for a LZW
compressed and tiled GTiff with a block size of 256. Note that the
GTiffDriver exposes some enumerates for selecting appropriate creation
option values (e.g. GTiffDriver.COMPRESS.LZW).

.. code:: ipython2

    driver = GTiffDriver()
    driver

.. code:: ipython2

    options = driver.creationOptions(tiled=GTiffDriver.TILED.YES, blockxsize=256, blockysize=256, 
                                     compress=GTiffDriver.COMPRESS.LZW)
    options

Raster from Array
~~~~~~~~~~~~~~~~~

Raster files are always associated with a pixel grid, which is defined
by an extent, a resolution and a projection.

E.g., define a raster in WGS 84 projection covering the whole world with
a resolution of 1°.

.. code:: ipython2

    grid = Grid(extent=Extent(xmin=-180, xmax=180, ymin=-90, ymax=90), resolution=Resolution(x=1, y=1), 
                projection=Projection.WGS84())
    grid

Create a MEM raster with random noise.

.. code:: ipython2

    array = np.random.randint(0, 255, size=(3, grid.size().y(), grid.size().x()), dtype=np.uint8)
    raster = createRasterFromArray(array=array, grid=grid)
    raster

.. code:: ipython2

    nbd.displayMultibandColor(image=raster, title='Random Colors')

Store the raster as an ENVI file.

.. code:: ipython2

    raster = createRasterFromArray(array=array, grid=grid, filename=join(tempfile.gettempdir(), 'random.img'),
                                  driver=ENVIDriver())
    raster.filenames()

Store the raster as a LZW compressed GTiff file.

.. code:: ipython2

    options = GTiffDriver().creationOptions(compress=GTiffDriver.COMPRESS.LZW)
    options

.. code:: ipython2

    raster = createRasterFromArray(array=array, grid=grid, filename=join(tempfile.gettempdir(), 'random.tif'),
                                  driver=GTiffDriver(), options=options)
    raster.filenames()

Create empty Raster
~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    raster = createRaster(grid=grid, bands=3, gdalType=gdal.GDT_Float32)
    raster

Write Raster Data
~~~~~~~~~~~~~~~~~

Using the empty raster from above.

.. code:: ipython2

    nbd.displayMultibandColor(image=raster)

Write red color values to the whole grid.

.. code:: ipython2

    arrayRed = np.zeros(shape=(3, raster.ysize(), raster.xsize()))
    arrayRed[0] = 255
    raster.writeArray(array=arrayRed)
    nbd.displayMultibandColor(image=raster)

Write blue color values to a raster subset.

.. code:: ipython2

    subgrid = raster.grid().subset(offset=Pixel(x=100, y=100), size=Size(x=50, y=50))
    arrayBlue = np.zeros(shape=(3, subgrid.size().y(), subgrid.size().x()))
    arrayBlue[2] = 255
    raster.writeArray(array=arrayBlue, grid=subgrid)
    nbd.displayMultibandColor(image=raster)

THERE IS A BUG WITH THE Y ORIGIN!!!
===================================

Write to the second rasterband creating…

.. code:: ipython2

    subgrid = raster.grid().subset(offset=Pixel(x=100, y=100), size=Size(x=50, y=50))
    arrayBlue = np.zeros(shape=(3, subgrid.size().y(), subgrid.size().x()))
    arrayBlue[2] = 255
    raster.writeArray(array=arrayBlue, grid=subgrid)
    nbd.displayMultibandColor(image=raster)

Managing Raster Metadata
------------------------

Managing Raster Metadata Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    grid = Grid(extent=Extent(xmin=-180, xmax=180, ymin=-90, ymax=90), resolution=Resolution(x=1, y=1), 
                projection=Projection.WGS84())
    raster = createRaster(grid=grid)
    raster

Set some metadata items.

.. code:: ipython2

    raster.setMetadataItem(key='my string', value='Hello World', domain='MyDomain')
    raster.setMetadataItem(key='my int', value=42, domain='MyDomain')
    raster.setMetadataItem(key='my string list', value=['a', 'b', 'c'], domain='MyDomain')
    raster.setMetadataItem(key='my int list', value=[1, 2, 3], domain='MyDomain')

Query some metadata.

.. code:: ipython2

    raster.metadataDomainList()

.. code:: ipython2

    raster.metadataDict()['MyDomain']

.. code:: ipython2

    raster.metadataItem(key='my int', domain='MyDomain')

Specify a data type if needed.

.. code:: ipython2

    raster.metadataItem(key='my int', domain='MyDomain', dtype=int)

.. code:: ipython2

    raster.metadataItem(key='my int list', domain='MyDomain', dtype=int)

Managing Rasterband Metadata Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    rasterband = raster.band(index=0)
    rasterband

.. code:: ipython2

    rasterband.setMetadataItem(key='my int', value=42, domain='MyDomain')
    rasterband.metadataItem(key='my int', domain='MyDomain', dtype=int)

Managing No Data Values
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    grid = Grid(extent=Extent(xmin=-180, xmax=180, ymin=-90, ymax=90), resolution=Resolution(x=1, y=1), 
                projection=Projection.WGS84())
    raster = createRaster(grid=grid, bands=3)
    raster

Set a single no data value to all raster bands.

.. code:: ipython2

    raster.setNoDataValue(value=-9999)
    raster.noDataValue()

Set different no data values to each band.

.. code:: ipython2

    raster.setNoDataValues(values=[-9999, 0, 255])
    raster.noDataValues()

Set no data values by iterating over the raster bands.

.. code:: ipython2

    for band, noDataValue in zip(raster.bands(), [-1, -2, -3]):
        band.setNoDataValue(value=noDataValue)
        
    noDataValues = [band.noDataValue() for band in raster.bands()]
    noDataValues

Managing Acquisition Time
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    import datetime
    date = datetime.datetime(year=2010, month=12, day=24)
    print(date)
    date

.. code:: ipython2

    raster.setAcquisitionTime(acquisitionTime=date)
    raster.acquisitionTime()

Managing Descriptions
~~~~~~~~~~~~~~~~~~~~~

Set raster description.

.. code:: ipython2

    raster.setDescription(value='This is a raster file')
    raster.description()

Set rasterband description

.. code:: ipython2

    for i, band in enumerate(raster.bands()):
        band.setDescription(value='This is band number {}'.format(i+1))
    [band.description() for band in raster.bands()]

Special Considerations for ENVI Software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a raster is written

Read and Display Raster Data
----------------------------

Landsat Colored-Infrared as Multiband Color Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    stack = np.vstack((nir.readAsArray(), swir1.readAsArray(), red.readAsArray()))
    nbd.displayMultibandColor(image=stack, dataStretches=[(0,50)]*3, title='Landsat ColoredInfraRed', )
    stack.shape

Landsat CFMask as Singleband Grey Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    band = cfmask.readAsArray()
    nbd.displaySinglebandGrey(band=band, dataStretch=(0, 4), title='Landsat CFMask')

Landsat NDVI as Singleband Pseudocolor Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    def ndvi(nir, red): 
        return np.float32(nir-red)/(nir+red)
    
    band = ndvi(nir=nir.readAsArray(), red=red.readAsArray())
    nbd.displaySinglebandPseudocolor(band=band, dataStretch=(0, 0.7), colormap='RdYlGn',
                                     title='Landsat NDVI')

Open Vector Files
-----------------

.. code:: ipython2

    brandenburg = openVector(filename=BrandenburgDistricts.shp)
    brandenburg

Query Vector Information
------------------------

.. code:: ipython2

    brandenburg.filename()

.. code:: ipython2

    brandenburg.featureCount()

.. code:: ipython2

    brandenburg.fieldCount()

.. code:: ipython2

    brandenburg.fieldNames()

.. code:: ipython2

    brandenburg.fieldTypeNames()

.. code:: ipython2

    brandenburg.spatialExtent()

Rasterize and Display Vector Data
---------------------------------

.. code:: ipython2

    brandenburg.spatialExtent()

.. code:: ipython2

    grid = Grid(extent=brandenburg.spatialExtent(), resolution=Resolution(x=0.005, y=0.005))

.. code:: ipython2

    raster = brandenburg.rasterize(grid=grid)
    band = raster.readAsArray()
    nbd.displaySinglebandGrey(band=band, dataStretch=(0, 1), title='Brandenburg')

.. code:: ipython2

    raster = brandenburg.rasterize(grid=grid, burnAttribute='id', initValue=-5)
    band = raster.readAsArray()
    nbd.displaySinglebandGrey(band=band, dataStretch=(np.min, np.max), title='Brandenburg Districts')

Resample and Reproject Raster and Vector Data
---------------------------------------------

Translate Raster Data
~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython2

    targetGrid = Grid(extent=cfmask.grid().spatialExtent(), resolution=Resolution(x=1000, y=1000))
    targetGrid

.. code:: ipython2

    result = cfmask.translate(grid=targetGrid)
    result

.. code:: ipython2

    nbd.displaySinglebandGrey(band=result.readAsArray(), dataStretch=(0, 4), title='CFMask resampled to 1000m resolution')

Warp Raster Data
~~~~~~~~~~~~~~~~

.. code:: ipython2

    targetExtent = cfmask.grid().spatialExtent().reproject(targetProjection=Projection.WGS84())
    targetExtent

.. code:: ipython2

    targetGrid = Grid(extent=targetExtent, resolution=Resolution(x=0.01, y=0.01))
    targetGrid

.. code:: ipython2

    result = cfmask.warp(grid=targetGrid)
    result

.. code:: ipython2

    nbd.displaySinglebandGrey(band=result.readAsArray(), dataStretch=(0, 4), 
                              title='CFMask reprojected into WGS 84 with 0.01° resolution')

Mosaic Example
~~~~~~~~~~~~~~

.. code:: ipython2

    grid = Grid(extent=Extent(xmin=9, xmax=15, ymin=50, ymax=55), 
                resolution=Resolution(x=0.0075, y=0.0075),
                projection=Projection.WGS84())
    grid

.. code:: ipython2

    nir023 = openRaster(filename=LT51940232010189KIS01.nir)
    swir023 = openRaster(filename=LT51940232010189KIS01.swir1)
    red023 = openRaster(filename=LT51940232010189KIS01.red)
    nir024 = openRaster(filename=LT51940242010189KIS01.nir)
    swir024 = openRaster(filename=LT51940242010189KIS01.swir1)
    red024 = openRaster(filename=LT51940242010189KIS01.red)
    brandenburg = openVector(filename=BrandenburgDistricts.shp)

.. code:: ipython2

    r = nir023.warp(grid=grid).readAsArray()
    r[r == 255] = nir024.warp(grid=grid).readAsArray()[r == 255]
    g = swir023.warp(grid=grid).readAsArray()
    g[g == 255] = swir024.warp(grid=grid).readAsArray()[g == 255]
    b = red023.warp(grid=grid).readAsArray()
    b[b == 255] = red024.warp(grid=grid).readAsArray()[b == 255]
    rgb = np.vstack([r, g, b])
    mask = brandenburg.rasterize(grid=grid).readAsArray() == 1
    rgb[:, mask[0]] = 255
    
    nbd.displayMultibandColor(image=rgb, dataStretches=[(0, 50)]*3, 
                              title='Landsat ColoredInfrared Mosaick without Brandenburg')
