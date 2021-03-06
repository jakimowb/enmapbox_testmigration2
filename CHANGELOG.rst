CHANGELOG
=========

Version 3.9
-----------
*This release was tested under QGIS 3.18 and 3.20.*

*Note that we are currently in a transition phase, where we're overhauling all processing algorithms.
Already overhauled algorithms are placed in groups prefixed by an asterisk, e.g. "*Classification".*


**GUI**

* added drag&drop functionality for opening external products (PRISMA, DESIS, Sentinel-2, Landsat) by simply dragging and dropping the product metadata file from the system file explorer onto the map view area.
* added map view context menu *Set background color* option

* new *Save as* options in data source and data view panel context menus:

  * opens *Translate raster layer* dialog for raster sources
  * opens *Save Features* dialog for vector sources

* added data sources context menu *Append ENVI header* option: opens *Append ENVI header to GeoTiff raster layer* algorithm dialog
* added single pixel movement in map view using <Ctrl> + <Arrow> keys, <Ctrl> + S to save a selected profile in a Spectral Library

* revised Data Source Panel and Data Source handling (#430)
* revised Spectral Library concept:

  * each vector layer that allows storing binary data can become a spectral library
    (e.g. Geopackage, PostGIS, in-memory layers)
  * spectral libraries can define multiple spectral profile fields

* revised Spectral Profile Source panel:

  * tree view defines how spectral profile features will be generated when using the Identify
    map tool with activated pixel profile option
  * allows to extract spectral profiles from different raster sources into different
    spectral profile fields of the same feature or into different features
  * values of extracted spectral profiles can be scaled by an (new) offset and a multiplier
  * other attributes of new features, e.g. for text and numeric fields, can be
    added by static values or expressions

* revised Spectral Library Viewer:

  * each vector layer can be opened in a Spectral Library Viewer
  * spectral profile visualizations allow to define colors, lines styles and
    profile labels
  * spectral profile visualizations are applied to individual sets of spectral profiles,
    e.g. all profiles of a spectral profile field, or only to profiles that match
    filter expressions like ``"name" = 'vegetation'``
  * profile colors can be defined as static color, attribute value or expression
  * profile plot allows to select multiple data points, e.g. to compare individual
    bands between spectral profiles
  * dialog to add new fields shows data type icons for available field types



**Renderer**

We started to introduced new raster renderer into the EnMAP-Box / QGIS.
Unfortunately, QGIS currently doesn't support registering custom Python raster renderer.
Because of this, our renderers aren't visible in the *Renderer type* list inside the *Layer Properties* dialog under *Symbology > Band Rendering*.

To actually use one of our renderers, you need to choose it from the *Custom raster renderer* submenu inside the raster layer context menu in the *Date Views* panel.

* added custom *Class fraction/probability* raster renderer: allows to visualize arbitrary many fraction/probability bands at the same time; this will replace the *Create RGB image from class probability/fraction layer* processing algorithm
* added custom *Decorrelation stretch* raster renderer: remove the high correlation commonly found in optical bands to produce a more colorful color composite image; this will replace the *Decorrelation stretch* processing algorithm

**Processing algorithms**

* added PRISMA L1 product import
* added Landsat 4-8 Collection 1-2 L2 product import
* added Sentinel-2 L2A product import
* added custom processing widget for selecting classification datasets from various sources; improves consistency and look&feel in algorithm dialogs and application GUIs
* added custom processing widget for Python code with highlighting
* added custem processing widget for building raster math expressions and code snippets
* improved raster math algorithms dialog and provided comprehensive cookbook usage recipe on ReadTheDocs
* added *Layer to mask layer* processing algorithm
* added *Create mask raster layer* processing algorithm
* overhauled all spatial and spectral filter algorithms
* added *Spatial convolution 2D Savitzki-Golay filter* processing algorithm
* overhauled all spectral resampling algorithms; added more custom sensors for spectral resampling: we now support EnMAP, DESIS, PRISMA, Landsat 4-8 and Sentinel-2; predefined sensor response functions are editable in the algorithm dialog
* added *Spectral resampling (to response function library)* processing algorithm: allows to specify the target response functions via a spectral library
* added *Spectral resampling (to spectral raster layer wavelength and FWHM)* processing algorithm: allows to specify the target response functions via a spectral raster layer
* added *Spectral resampling (to custom sensor)* processing algorithm: allows to specify the target response function via Python code
* improved *Translate raster layer* processing algorithm: 1) improved source and target no data handling, 2) added option for spectral subsetting to another spectral raster layer, 3) added options for setting/updating band scale and offset values, 4) added option for creating an ENVI header sidecar file for better compatibility to ENVI software
* added *Save raster layer as* processing algorithm: a slimmed down version of "Translate raster layer"
* added *Append ENVI header to GeoTiff raster layer* processing algorithm: places a \*.hdr ENVI header file next to a GeoTiff raster to improve compatibility to ENVI software
* added *Geolocate raster layer* processing algorithm: allows to geolocate a raster given in sensor geometry using X/Y location bands; e.g. usefull for geolocating PRISMA L1 Landcover into PRISMA L2 pixel grid using the Lat/Lon location bands

**Miscellaneous**

* added EnMAP spectral response function library as example dataset
* change example data vector layer format from Shapefile to GeoPackage
* added example data to enmapbox repository
* added unittest data to enmapbox repository


Version 3.8
-----------
* introduced a Glossary explaining common terms
* added processing algorithm for creating default style (QML sidecar file) with given categories
* overhauled Classification Workflow app; old version is still available as Classification Workflow (Classic)
* overhauled several processing algorithms related to classification fit, predict, accuracy accessment and random sub-sampling
* overhauled processing algorithms show command line and Python commands for re-executing the algorithms with same inputs
* added a processing algorithm for calculating a classification change map from two classifications
* overhauled existing and introduced new processing algorithms for prepare classification (training/testing) datasets;
  currently we support classification data from raster/vector layers, from table; from text file; from spectral library
* added processing algorithm for supervised classifier feature ranking using permutation importances
* added processing algorithm for unsupervised feature clustering
* overhauled processing algorithm for creating RGB images from class probability or class fraction layer
* added processing algorithm for creating a grid (i.e. an empty raster layer) by specifying target CRS, extent and size
* added processing algorithm for doing raster math with a list of input raster layers
* added processing algorithm for rasterizing categoriezed vector layers
* overhauled processing algorithm for rasterizing vector layers (improved performance)
* added processing algorithm for translating categorized raster layers
* overhauled processing algorithm for translating raster layers
* added processing algorithms for creating random points from mask and categorized raster layers
* added processing algorithm for sampling of raster layer values
* added processing algorithm for decorrelation stretching
* rename layers, map views and spectral library views with F2
* model browser: improved visualization (#645, #646, #647), array values can be copied to clipboard (#520)
* layers can be moved between maps (#437)
* updated pyqtgraph to 0.12.1

Version 3.7
-----------
* added EnMAP L1B, L1C and L2A product reader
* added PRISMA L2D product import
* added DESIS L2A product reader
* added Classification Statistics PA
* added Save As ENVI Raster PA: saves a raster in ENVI format and takes care of proper metadata storage inside ENVI header file
* added Aggregate Raster Bands PA: allows to aggregate multiband raster into a single band using aggregation functions like min, max, mean, any, all, etc.
* classification scheme is now defined by the layer renderer
* [Spectral Resampling PA] reworked spectral resampling
* [Classification Workflow] support libraries as input
* [ImageMath] added predefined code snippets
* [Subset Raster Wavebands PA] support band selection via wavelength
* LayerTreeView: enhanced context menus:
  double click on map layer opens Properties Dialog,
  double click on a vector layers' legend item opens a Symbol dialog
* GDAL raster metadata can be modified (resolves #181)
* map canvas preserves scale on window resize (#409)
* Reclassify Tool: can save and reload the class mapping, fixed (#501)
* several fixed in Image Cube App
* updated PyQtGraph to version 0.11
* Virtual Raster Builder and Image Cube can select spatial extents from other QGIS / EnMAP-Box maps
* several improvements to SpectralLibrary, e.g. to edit SpectralProfile values
* QGIS expression builder:
    added 'format_py' to create strings with python-string-format syntax,
    added spectralData() to access SpectralProfile values
    added spectralMath(...) to modify  / create new SpectralProfiles
* fixes some bugs in imageCube app


Version 3.6
-----------
(including hotfixes from 2020-06-22)

* added workaround for failed module imports, e.g. numba on windows (#405)
* EnMAP-Box plugin can be installed and started without having none-standard python packages installed (#366)
* Added installer to install missing python packages (#371)
* Map Canvas Crosshair can now show the pixel boundaries of any raster source known to QGIS
* Spectral Profile Source panel
    * is properly updated on removal/adding of raster sources or spectral libraries
    * allows to define source-specific profile plot styles (#422, #468)
* Spectral Library Viewer
    * added color schemes to set plot and profile styles
    * fixed color scheme issue (# fixed #467 )
    * profile styles can be changed per profile (#268)
    * current/temporary profiles are shown in the attribute table
    * added workaround for #345 (Spectral library create new field: problems with default fields)
    * loading profiles based in vector position is done in a background process (closed #329)
    * profile data point can be selected to show point specific information, e.g. the band number (#462, #267)
    * closed #252
* SpectralLibrary
    * implemented SpectralProfileRenderer to maintain profile-specific plot styles
* Classification Scheme Widget allows to paste/copy classification schemes from/to the clipboard.
  This can be used to copy classes from other raster or vector layers, or to set the layer renderer
  according to the classification scheme
* updated in LMU vegetation app
* updated EnPTEnMAPBoxApp (see https://git-pages.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp for documentation)
* added EnSoMAP and EnGeoMAP applications provided by GFZ
* added ONNS application provided by HZG
* removed several bugs, e.g. #285, #206,

Version 3.5
-----------

(including last hotfixes from 2019-11-12)

* removed numba imports from LMU vegetation app
* vector layer styling is loaded by default
* fixed error that was thrown when closing the EnMAP-Box
* fixed bug in SynthMixApplication
* Spectral Library Viewer: import and export of ASD, EcoSIS and SPECCHIO csv/binary files
* Spectral Profile Source panel: controls how to extract SpectralProfiles and where to show them
* supports import of multi-dimensional raster formats, like HDF and netCDF
* ImageCube viewer to visualize hyperspectral data cubes (requires opengl)
* Added CONTRIBUTORS.md and "How to contribute" section to online documention
* Documentation uses HYPERedu stylesheet (https://eo-college.org/members/hyperedu/)
* fixed start up of EO Time Series Viewer and Virtual Raster Builder QGIS Plugins from EnMAP-Box

Version 3.4
-------------------------------------------

* Spectral Library Viewer: import spectral profiles from raster file based on vector positions
* Classification Widgets: copy / paste single class informations
* Map tools to select / add vector features
* fixed critical bug in IVVRM
* several bug fixed and minor improvements

Version 3.3
-------------------------------------------

* added user +  developer example to RTF documentation
* renamed plugin folder to "EnMAP-Box"
* SpectralLibraries can be renamed and added to
  map canvases to show profile locations
* SpectraProfiles now styled like point layers:
  point color will be line color in profile plot
* Workaround for macOS bug that started
  new QGIS instances again and again and ...
* Classification Workflow App
* Re-designed Metadata Editor
* Several bug fixes

Version 3.2
-------------------------------------------

* ...

Version 3.1
-------------------------------------------

* EnMAP-Box is now based on QGIS 3, Qt 5.9,Python 3 and GDAL 2.2
* QGISP lugin Installation from ZIP File
* readthedocs documentation
  https://enmap-box.readthedocs.io/en/latest/index.html

previous versions
-------------------------------------------

* version scheme following build dates

